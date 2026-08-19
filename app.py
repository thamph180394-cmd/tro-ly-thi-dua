import os
import streamlit as st
import pandas as pd
import altair as alt

from tinh_diem import tinh_tong_diem

from database import (
    tao_co_so_du_lieu,
    them_diem,
    lay_diem_theo_tuan,
    them_lop,
    lay_danh_sach_lop,
    an_lop,
    kich_hoat_lop,
    xoa_lop,
    cap_nhat_thong_tin_lop,

    # PHẦN MỚI: TUẦN - THÁNG
    luu_thang_cho_tuan,
    lay_thang_cua_tuan,
    lay_danh_sach_tuan_thang,
    lay_cac_tuan_chua_co_thang
)

from ai_assistant import tao_nhan_xet_thi_dua
from export_dashboard import tao_anh_dashboard
from export_word import tao_bao_cao_word_toan_truong
from export_excel import tao_excel_so_ket, tao_excel_tong_ket


# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Trợ lý AI xét thi đua",
    page_icon="🏆",
    layout="wide"
)

tao_co_so_du_lieu()


# =========================================================
# HÀM HỖ TRỢ
# =========================================================

def tao_bang_xep_hang(du_lieu):

    if not du_lieu:
        return pd.DataFrame()

    bang = pd.DataFrame(
        du_lieu,
        columns=[
            "Lớp",
            "Học tập",
            "Kỷ luật",
            "Vệ sinh",
            "Điểm cộng",
            "Điểm trừ",
            "Tổng điểm",
            "Ghi chú"
        ]
    )

    bang = bang.sort_values(
        by=[
            "Tổng điểm",
            "Lớp"
        ],
        ascending=[
            False,
            True
        ],
        kind="stable"
    ).reset_index(
        drop=True
    )

    # =====================================================
    # ĐỒNG ĐIỂM = ĐỒNG HẠNG
    #
    # Ví dụ:
    # 275 -> Hạng 1
    # 275 -> Hạng 1
    # 270 -> Hạng 3
    # =====================================================

    bang["Hạng"] = (
        bang["Tổng điểm"]
        .rank(
            method="min",
            ascending=False
        )
        .astype(int)
    )

    cot_hang = bang.pop(
        "Hạng"
    )

    bang.insert(
        0,
        "Hạng",
        cot_hang
    )

    return bang


def xac_dinh_khoi(ten_lop):

    ten_lop = str(
        ten_lop
    ).strip().upper()

    if ten_lop.startswith("6"):
        return "Khối 6"

    if ten_lop.startswith("7"):
        return "Khối 7"

    if ten_lop.startswith("8"):
        return "Khối 8"

    if ten_lop.startswith("9"):
        return "Khối 9"

    return "Khác"


def dong_bo_danh_sach_lop_cu(nam_hoc):

    danh_sach_hien_co = lay_danh_sach_lop(
        nam_hoc,
        chi_lay_dang_hoat_dong=False
    )

    if len(danh_sach_hien_co) > 0:
        return

    cac_lop = set()

    for so_tuan in range(
        1,
        53
    ):

        du_lieu = lay_diem_theo_tuan(
            nam_hoc,
            so_tuan
        )

        for dong in du_lieu:

            if len(dong) > 0:

                lop = str(
                    dong[0]
                ).strip().upper()

                if lop:
                    cac_lop.add(
                        lop
                    )

    for lop in sorted(
        cac_lop
    ):

        them_lop(
            nam_hoc,
            lop,
            xac_dinh_khoi(
                lop
            )
        )


def lay_khoi_tu_danh_sach(
    nam_hoc,
    ten_lop
):

    danh_sach = lay_danh_sach_lop(
        nam_hoc,
        chi_lay_dang_hoat_dong=False
    )

    for dong in danh_sach:

        if (
            str(
                dong[0]
            ).strip().upper()
            ==
            str(
                ten_lop
            ).strip().upper()
        ):

            return dong[1]

    return xac_dinh_khoi(
        ten_lop
    )


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.block-container {
    padding-top: 1.4rem;
    padding-bottom: 2rem;
    max-width: 1600px;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

[data-testid="stToolbar"] {
    visibility: hidden;
    height: 0px;
}

[data-testid="stHeader"] {
    background: rgba(255,255,255,0);
}

.tieu-de-chinh {
    text-align: center;
    color: #0b459b;
    font-size: 40px;
    font-weight: 900;
    margin-top: 8px;
    margin-bottom: 2px;
}

.tieu-de-phu {
    text-align: center;
    color: #5d6675;
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 20px;
}

.tieu-de-muc {
    color: #0b459b;
    font-size: 23px;
    font-weight: 900;
    margin-top: 16px;
    margin-bottom: 9px;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #d6e2f4;
    padding: 14px 16px;
    border-radius: 12px;
    min-height: 120px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.045);
}

[data-testid="stMetricValue"] {
    color: #0b459b;
    font-weight: 900;
}

[data-testid="stDataFrame"] {
    border: 1px solid #d7e3f3;
    border-radius: 10px;
    overflow: hidden;
}

[data-testid="stExpander"] {
    border: 1px solid #d7e3f3;
    border-radius: 10px;
    background: #ffffff;
}

.stButton > button {
    border-radius: 8px;
    font-weight: 700;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TIÊU ĐỀ
# =========================================================

st.markdown(
    '<div class="tieu-de-chinh">🏆 BẢNG THEO DÕI THI ĐUA CÁC LỚP</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tieu-de-phu">TRỢ LÝ AI XÉT THI ĐUA NHÀ TRƯỜNG</div>',
    unsafe_allow_html=True
)


# =========================================================
# NĂM HỌC - TUẦN
# =========================================================

cot_nam, cot_tuan = st.columns(
    [2, 1]
)

with cot_nam:

    nam_hoc = st.selectbox(
        "Năm học",
        [
            "2026 - 2027",
            "2027 - 2028",
            "2028 - 2029",
            "2029 - 2030"
        ]
    )

with cot_tuan:

    tuan = st.number_input(
        "Tuần",
        min_value=1,
        max_value=52,
        value=2,
        step=1
    )


# =========================================================
# ĐỒNG BỘ DANH SÁCH LỚP CŨ
# =========================================================

dong_bo_danh_sach_lop_cu(
    nam_hoc
)


# =========================================================
# PHẦN MỚI
# QUẢN LÝ TUẦN - THÁNG
# =========================================================

with st.expander(
    "📅 THÁNG CỦA TUẦN",
    expanded=False
):

    st.info(
        "Mỗi tuần cần được gán vào đúng tháng để cuối học kỳ "
        "và cuối năm có thể xuất Sơ kết thi đua và Tổng kết thi đua."
    )

    thang_da_luu = lay_thang_cua_tuan(
        nam_hoc,
        tuan
    )

    cac_thang_nam_hoc = [
        9,
        10,
        11,
        12,
        1,
        2,
        3,
        4,
        5
    ]

    if thang_da_luu in cac_thang_nam_hoc:

        chi_so_thang = (
            cac_thang_nam_hoc.index(
                thang_da_luu
            )
        )

    else:

        chi_so_thang = 0

    c1, c2 = st.columns(
        [2, 1]
    )

    with c1:

        thang_chon = st.selectbox(
            f"Tuần {tuan} thuộc tháng",
            cac_thang_nam_hoc,
            index=chi_so_thang,
            format_func=lambda x: f"Tháng {x}",
            key=f"thang_tuan_{nam_hoc}_{tuan}"
        )

    with c2:

        st.write("")

        st.write("")

        if st.button(
            "💾 LƯU THÁNG CHO TUẦN",
            type="primary",
            key=f"luu_thang_{nam_hoc}_{tuan}"
        ):

            thanh_cong, thong_bao = (
                luu_thang_cho_tuan(
                    nam_hoc,
                    tuan,
                    thang_chon
                )
            )

            if thanh_cong:

                st.success(
                    thong_bao
                )

                st.rerun()

            else:

                st.error(
                    thong_bao
                )


    # =====================================================
    # HIỂN THỊ TRẠNG THÁI TUẦN HIỆN TẠI
    # =====================================================

    if thang_da_luu is None:

        st.warning(
            f"⚠️ Tuần {tuan} chưa được gán tháng."
        )

    else:

        st.success(
            f"✅ Tuần {tuan} hiện đang thuộc Tháng {thang_da_luu}."
        )


    # =====================================================
    # DANH SÁCH TUẦN - THÁNG ĐÃ CẤU HÌNH
    # =====================================================

    ds_tuan_thang = lay_danh_sach_tuan_thang(
        nam_hoc
    )

    if ds_tuan_thang:

        st.divider()

        st.markdown(
            "### 📋 DANH SÁCH TUẦN - THÁNG ĐÃ LƯU"
        )

        df_tuan_thang = pd.DataFrame(
            ds_tuan_thang,
            columns=[
                "Tuần",
                "Tháng"
            ]
        )

        df_tuan_thang[
            "Tháng"
        ] = df_tuan_thang[
            "Tháng"
        ].apply(
            lambda x: f"Tháng {x}"
        )

        st.dataframe(
            df_tuan_thang,
            width="stretch",
            hide_index=True
        )


    # =====================================================
    # KIỂM TRA TUẦN CÓ ĐIỂM NHƯNG CHƯA GÁN THÁNG
    # =====================================================

    cac_tuan_chua_co_thang = (
        lay_cac_tuan_chua_co_thang(
            nam_hoc
        )
    )

    if cac_tuan_chua_co_thang:

        st.warning(
            "Các tuần đã có dữ liệu điểm nhưng chưa gán tháng: "
            + ", ".join(
                [
                    f"Tuần {x}"
                    for x in cac_tuan_chua_co_thang
                ]
            )
        )

    else:

        st.caption(
            "✅ Các tuần đang có dữ liệu điểm đều đã được gán tháng."
        )


# =========================================================
# QUẢN LÝ DANH SÁCH LỚP
# =========================================================

with st.expander(
    "🏫 QUẢN LÝ DANH SÁCH LỚP",
    expanded=False
):

    st.info(
        "Bạn có thể thêm lớp, sửa tên lớp, sửa khối, "
        "ẩn lớp hoặc kích hoạt lại mà không cần sửa chương trình."
    )

    # =====================================================
    # THÊM LỚP MỚI
    # =====================================================

    st.markdown(
        "### ➕ THÊM LỚP MỚI"
    )

    c_ten_lop, c_khoi = st.columns(
        2
    )

    with c_ten_lop:

        lop_moi = st.text_input(
            "Tên lớp mới",
            placeholder="Ví dụ: 6A4",
            key="them_ten_lop"
        )

    with c_khoi:

        khoi_moi = st.selectbox(
            "Khối",
            [
                "Khối 6",
                "Khối 7",
                "Khối 8",
                "Khối 9",
                "Khác"
            ],
            key="them_khoi"
        )

    if st.button(
        "➕ THÊM LỚP",
        type="primary",
        key="nut_them_lop"
    ):

        ten_lop_them = (
            lop_moi
            .strip()
            .upper()
        )

        if ten_lop_them == "":

            st.error(
                "Bạn chưa nhập tên lớp."
            )

        else:

            them_lop(
                nam_hoc,
                ten_lop_them,
                khoi_moi
            )

            st.success(
                f"Đã thêm lớp {ten_lop_them} - {khoi_moi}."
            )

            st.rerun()


    # =====================================================
    # DANH SÁCH LỚP HIỆN TẠI
    # =====================================================

    tat_ca_lop = lay_danh_sach_lop(
        nam_hoc,
        chi_lay_dang_hoat_dong=False
    )

    if len(tat_ca_lop) > 0:

        st.divider()

        st.markdown(
            "### 📋 DANH SÁCH LỚP HIỆN TẠI"
        )

        df_lop = pd.DataFrame(
            tat_ca_lop,
            columns=[
                "Lớp",
                "Khối",
                "Hoạt động"
            ]
        )

        df_lop["Trạng thái"] = (
            df_lop["Hoạt động"]
            .apply(
                lambda x:
                "✅ Đang sử dụng"
                if x == 1
                else "⛔ Đã ẩn"
            )
        )

        st.dataframe(
            df_lop[
                [
                    "Lớp",
                    "Khối",
                    "Trạng thái"
                ]
            ],
            width="stretch",
            hide_index=True
        )


        # =================================================
        # CẬP NHẬT THÔNG TIN LỚP
        # =================================================

        st.divider()

        st.markdown(
            "### ✏️ CẬP NHẬT THÔNG TIN LỚP"
        )

        st.caption(
            "Nếu nhập sai tên lớp hoặc sai khối, "
            "hãy sửa tại đây. Khi đổi tên lớp, "
            "dữ liệu điểm cũ của lớp cũng được cập nhật."
        )

        danh_sach_ten_lop = (
            df_lop["Lớp"]
            .tolist()
        )

        lop_can_sua = st.selectbox(
            "Chọn lớp cần sửa",
            danh_sach_ten_lop,
            key="lop_can_sua"
        )

        dong_lop_sua = df_lop[
            df_lop["Lớp"]
            == lop_can_sua
        ].iloc[0]

        khoi_hien_tai = str(
            dong_lop_sua["Khối"]
        )

        cac_khoi = [
            "Khối 6",
            "Khối 7",
            "Khối 8",
            "Khối 9",
            "Khác"
        ]

        if khoi_hien_tai not in cac_khoi:

            khoi_hien_tai = (
                xac_dinh_khoi(
                    lop_can_sua
                )
            )

        if khoi_hien_tai not in cac_khoi:
            khoi_hien_tai = "Khác"

        chi_so_khoi = (
            cac_khoi.index(
                khoi_hien_tai
            )
        )

        s1, s2 = st.columns(
            2
        )

        with s1:

            ten_lop_sau_khi_sua = (
                st.text_input(
                    "Tên lớp",
                    value=lop_can_sua,
                    key=(
                        "ten_lop_sua_"
                        + str(
                            lop_can_sua
                        )
                    )
                )
            )

        with s2:

            khoi_sau_khi_sua = (
                st.selectbox(
                    "Khối mới",
                    cac_khoi,
                    index=chi_so_khoi,
                    key=(
                        "khoi_sua_"
                        + str(
                            lop_can_sua
                        )
                    )
                )
            )

        st.write(
            f"**Hiện tại:** "
            f"{lop_can_sua} - {khoi_hien_tai}"
        )

        st.write(
            "**Sau khi cập nhật:** "
            f"{ten_lop_sau_khi_sua.strip().upper()} "
            f"- {khoi_sau_khi_sua}"
        )

        if st.button(
            "💾 CẬP NHẬT THÔNG TIN LỚP",
            type="primary",
            key="nut_cap_nhat_lop"
        ):

            ten_moi = (
                ten_lop_sau_khi_sua
                .strip()
                .upper()
            )

            if ten_moi == "":

                st.error(
                    "Tên lớp không được để trống."
                )

            else:

                thanh_cong, thong_bao = (
                    cap_nhat_thong_tin_lop(
                        nam_hoc,
                        lop_can_sua,
                        ten_moi,
                        khoi_sau_khi_sua
                    )
                )

                if thanh_cong:

                    st.success(
                        thong_bao
                    )

                    st.rerun()

                else:

                    st.error(
                        thong_bao
                    )


        # =================================================
        # QUẢN LÝ TRẠNG THÁI LỚP
        # =================================================

        st.divider()

        st.markdown(
            "### ⚙️ QUẢN LÝ TRẠNG THÁI LỚP"
        )

        lop_quan_ly = st.selectbox(
            "Chọn lớp",
            danh_sach_ten_lop,
            key="lop_quan_ly_trang_thai"
        )

        q1, q2, q3 = st.columns(
            3
        )

        with q1:

            if st.button(
                "🙈 ẨN LỚP",
                key="nut_an_lop"
            ):

                an_lop(
                    nam_hoc,
                    lop_quan_ly
                )

                st.success(
                    f"Đã ẩn lớp {lop_quan_ly}."
                )

                st.rerun()

        with q2:

            if st.button(
                "✅ KÍCH HOẠT LẠI",
                key="nut_kich_hoat"
            ):

                kich_hoat_lop(
                    nam_hoc,
                    lop_quan_ly
                )

                st.success(
                    f"Đã kích hoạt lại lớp {lop_quan_ly}."
                )

                st.rerun()

        with q3:

            if st.button(
                "🗑️ XÓA KHỎI DANH SÁCH",
                key="nut_xoa_lop"
            ):

                xoa_lop(
                    nam_hoc,
                    lop_quan_ly
                )

                st.success(
                    f"Đã xóa lớp {lop_quan_ly} "
                    "khỏi danh sách quản lý."
                )

                st.warning(
                    "Dữ liệu điểm đã nhập trước đây vẫn được giữ."
                )

                st.rerun()

    else:

        st.info(
            "Năm học này chưa có lớp nào. "
            "Hãy thêm lớp mới ở phía trên."
        )


st.divider()


# =========================================================
# LẤY DỮ LIỆU TUẦN
# =========================================================

du_lieu_hien_tai = lay_diem_theo_tuan(
    nam_hoc,
    tuan
)

bang = tao_bang_xep_hang(
    du_lieu_hien_tai
)


if tuan > 1:

    bang_tuan_truoc = (
        tao_bang_xep_hang(
            lay_diem_theo_tuan(
                nam_hoc,
                tuan - 1
            )
        )
    )

else:

    bang_tuan_truoc = (
        pd.DataFrame()
    )


# =========================================================
# DASHBOARD
# =========================================================

if not bang.empty:

    # =====================================================
    # KHỐI
    # =====================================================

    bang["Khối"] = bang[
        "Lớp"
    ].apply(
        lambda lop:
        lay_khoi_tu_danh_sach(
            nam_hoc,
            lop
        )
    )

    bang["Tăng/Giảm"] = "—"

    tong_so_lop = len(
        bang
    )

    diem_trung_binh = round(
        bang["Tổng điểm"].mean(),
        2
    )

    lop_tien_bo_nhat = None
    lop_on_dinh_nhat = None

    tang_hang_lon_nhat = None
    bien_dong_nho_nhat = None


    # =====================================================
    # SO SÁNH TUẦN TRƯỚC
    # =====================================================

    if not bang_tuan_truoc.empty:

        hang_cu = dict(
            zip(
                bang_tuan_truoc[
                    "Lớp"
                ],
                bang_tuan_truoc[
                    "Hạng"
                ]
            )
        )

        diem_cu = dict(
            zip(
                bang_tuan_truoc[
                    "Lớp"
                ],
                bang_tuan_truoc[
                    "Tổng điểm"
                ]
            )
        )

        for i, dong in bang.iterrows():

            lop_hien_tai = (
                dong["Lớp"]
            )

            if lop_hien_tai in hang_cu:

                thay_doi = (
                    hang_cu[
                        lop_hien_tai
                    ]
                    - dong["Hạng"]
                )

                if thay_doi > 0:

                    bang.at[
                        i,
                        "Tăng/Giảm"
                    ] = (
                        f"▲ {thay_doi}"
                    )

                elif thay_doi < 0:

                    bang.at[
                        i,
                        "Tăng/Giảm"
                    ] = (
                        f"▼ {abs(thay_doi)}"
                    )

                else:

                    bang.at[
                        i,
                        "Tăng/Giảm"
                    ] = "—"

                tang_diem = (
                    dong["Tổng điểm"]
                    - diem_cu[
                        lop_hien_tai
                    ]
                )

                muc_tien_bo = (
                    thay_doi,
                    tang_diem
                )

                if (
                    tang_hang_lon_nhat
                    is None
                    or muc_tien_bo
                    > tang_hang_lon_nhat
                ):

                    tang_hang_lon_nhat = (
                        muc_tien_bo
                    )

                    lop_tien_bo_nhat = {
                        "Lớp": lop_hien_tai,
                        "Tăng hạng": thay_doi,
                        "Tăng điểm": tang_diem
                    }

                bien_dong = abs(
                    tang_diem
                )

                if (
                    bien_dong_nho_nhat
                    is None
                    or bien_dong
                    < bien_dong_nho_nhat
                ):

                    bien_dong_nho_nhat = (
                        bien_dong
                    )

                    lop_on_dinh_nhat = {
                        "Lớp": lop_hien_tai,
                        "Biến động": bien_dong
                    }


    # =====================================================
    # TỔNG QUAN
    # =====================================================

    st.markdown(
        '<div class="tieu-de-muc">'
        '📊 TỔNG QUAN THI ĐUA'
        '</div>',
        unsafe_allow_html=True
    )

    a1, a2, a3 = st.columns(
        3
    )

    with a1:

        st.metric(
            "👥 Tổng số lớp có điểm",
            tong_so_lop
        )

    with a2:

        st.metric(
            "📈 Điểm trung bình",
            diem_trung_binh
        )

    with a3:

        cac_lop_hang_1 = bang[
            bang["Hạng"] == 1
        ]

        ten_cac_lop_hang_1 = ", ".join(
            cac_lop_hang_1[
                "Lớp"
            ].astype(str).tolist()
        )

        diem_hang_1 = (
            cac_lop_hang_1.iloc[0][
                "Tổng điểm"
            ]
        )

        st.metric(
            "🏆 Lớp dẫn đầu",
            ten_cac_lop_hang_1,
            f"{diem_hang_1} điểm",
            delta_color="off"
        )


    a4, a5, a6 = st.columns(
        3
    )

    with a4:

        if lop_tien_bo_nhat is not None:

            if (
                lop_tien_bo_nhat[
                    "Tăng hạng"
                ]
                > 0
            ):

                noi_dung_tien_bo = (
                    f'▲ '
                    f'{lop_tien_bo_nhat["Tăng hạng"]} '
                    f'bậc'
                )

            else:

                noi_dung_tien_bo = (
                    f'{lop_tien_bo_nhat["Tăng điểm"]:+.1f} '
                    f'điểm'
                )

            st.metric(
                "🌟 Lớp tiến bộ nhất",
                lop_tien_bo_nhat[
                    "Lớp"
                ],
                noi_dung_tien_bo,
                delta_color="off"
            )

        else:

            st.metric(
                "🌟 Lớp tiến bộ nhất",
                "Chưa có dữ liệu"
            )


    with a5:

        if lop_on_dinh_nhat is not None:

            st.metric(
                "🎯 Lớp ổn định nhất",
                lop_on_dinh_nhat[
                    "Lớp"
                ],
                (
                    f'{lop_on_dinh_nhat["Biến động"]:.1f} '
                    f'điểm'
                ),
                delta_color="off"
            )

        else:

            st.metric(
                "🎯 Lớp ổn định nhất",
                "Chưa có dữ liệu"
            )


    with a6:

        diem_cuoi = (
            bang["Tổng điểm"].min()
        )

        cac_lop_cuoi = bang[
            bang["Tổng điểm"]
            == diem_cuoi
        ]

        ten_cac_lop_cuoi = ", ".join(
            cac_lop_cuoi[
                "Lớp"
            ].astype(str).tolist()
        )

        st.metric(
            "⚠️ Lớp cần cố gắng",
            ten_cac_lop_cuoi,
            f"{diem_cuoi} điểm",
            delta_color="off"
        )


    # =====================================================
    # BẢNG XẾP HẠNG
    # =====================================================

    st.markdown(
        (
            '<div class="tieu-de-muc">'
            f'🏆 BẢNG XẾP HẠNG TOÀN TRƯỜNG - TUẦN {tuan}'
            '</div>'
        ),
        unsafe_allow_html=True
    )

    bang_hien_thi = bang[
        [
            "Hạng",
            "Lớp",
            "Khối",
            "Học tập",
            "Kỷ luật",
            "Vệ sinh",
            "Điểm cộng",
            "Điểm trừ",
            "Tổng điểm",
            "Tăng/Giảm"
        ]
    ].copy()

    st.dataframe(
        bang_hien_thi,
        width="stretch",
        hide_index=True,
        height=min(
            650,
            90
            + len(
                bang_hien_thi
            ) * 35
        )
    )


    # =====================================================
    # TOP 5
    # =====================================================

    st.markdown(
        '<div class="tieu-de-muc">'
        '⭐ TOP 5 THI ĐUA TOÀN TRƯỜNG'
        '</div>',
        unsafe_allow_html=True
    )

    top5 = bang[
        bang["Hạng"] <= 5
    ].copy()

    st.dataframe(
        top5[
            [
                "Hạng",
                "Lớp",
                "Khối",
                "Tổng điểm",
                "Tăng/Giảm"
            ]
        ],
        width="stretch",
        hide_index=True
    )


    # =====================================================
    # BIỂU ĐỒ TỔNG ĐIỂM
    # =====================================================

    st.markdown(
        '<div class="tieu-de-muc">'
        '📊 TỔNG ĐIỂM TOÀN TRƯỜNG'
        '</div>',
        unsafe_allow_html=True
    )

    bieu_do_tong = (
        alt.Chart(
            bang
        )
        .mark_bar(
            cornerRadiusTopRight=5,
            cornerRadiusBottomRight=5
        )
        .encode(

            y=alt.Y(
                "Lớp:N",
                sort=alt.SortField(
                    field="Tổng điểm",
                    order="descending"
                ),
                title="Lớp"
            ),

            x=alt.X(
                "Tổng điểm:Q",
                title="Tổng điểm"
            ),

            tooltip=[
                alt.Tooltip(
                    "Hạng:Q",
                    title="Hạng"
                ),
                alt.Tooltip(
                    "Lớp:N",
                    title="Lớp"
                ),
                alt.Tooltip(
                    "Khối:N",
                    title="Khối"
                ),
                alt.Tooltip(
                    "Tổng điểm:Q",
                    title="Tổng điểm"
                )
            ]
        )
        .properties(
            height=max(
                350,
                len(bang) * 32
            )
        )
    )

    st.altair_chart(
        bieu_do_tong,
        width="stretch"
    )


    # =====================================================
    # HỌC TẬP - KỶ LUẬT - VỆ SINH
    # =====================================================

    st.markdown(
        '<div class="tieu-de-muc">'
        '📚 HỌC TẬP - KỶ LUẬT - VỆ SINH TOÀN TRƯỜNG'
        '</div>',
        unsafe_allow_html=True
    )

    du_lieu_dai = bang[
        [
            "Lớp",
            "Học tập",
            "Kỷ luật",
            "Vệ sinh"
        ]
    ].melt(
        id_vars="Lớp",
        var_name="Nội dung",
        value_name="Điểm"
    )

    bieu_do_thanh_phan = (
        alt.Chart(
            du_lieu_dai
        )
        .mark_bar()
        .encode(

            x=alt.X(
                "Lớp:N",
                title="Lớp",
                axis=alt.Axis(
                    labelAngle=-45
                )
            ),

            xOffset=alt.XOffset(
                "Nội dung:N"
            ),

            y=alt.Y(
                "Điểm:Q",
                title="Điểm"
            ),

            color=alt.Color(
                "Nội dung:N",
                title="Nội dung"
            ),

            tooltip=[
                alt.Tooltip(
                    "Lớp:N",
                    title="Lớp"
                ),
                alt.Tooltip(
                    "Nội dung:N",
                    title="Nội dung"
                ),
                alt.Tooltip(
                    "Điểm:Q",
                    title="Điểm"
                )
            ]
        )
        .properties(
            height=350
        )
    )

    st.altair_chart(
        bieu_do_thanh_phan,
        width="stretch"
    )


    # =====================================================
    # XU HƯỚNG QUA CÁC TUẦN
    # =====================================================

    st.markdown(
        '<div class="tieu-de-muc">'
        '📈 XU HƯỚNG TỔNG ĐIỂM QUA CÁC TUẦN'
        '</div>',
        unsafe_allow_html=True
    )

    du_lieu_xu_huong = []

    for so_tuan in range(
        1,
        tuan + 1
    ):

        du_lieu_tuan = (
            lay_diem_theo_tuan(
                nam_hoc,
                so_tuan
            )
        )

        if not du_lieu_tuan:
            continue

        bang_tuan = (
            tao_bang_xep_hang(
                du_lieu_tuan
            )
        )

        for _, dong in bang_tuan.iterrows():

            du_lieu_xu_huong.append(
                {
                    "Tuần": so_tuan,
                    "Lớp": dong["Lớp"],
                    "Tổng điểm": dong[
                        "Tổng điểm"
                    ]
                }
            )

    if du_lieu_xu_huong:

        df_xu_huong = pd.DataFrame(
            du_lieu_xu_huong
        )

        cac_lop_xu_huong = sorted(
            df_xu_huong[
                "Lớp"
            ].unique().tolist()
        )

        lop_xem = st.multiselect(
            "Chọn lớp cần xem xu hướng",
            cac_lop_xu_huong,
            default=cac_lop_xu_huong[
                :min(
                    5,
                    len(
                        cac_lop_xu_huong
                    )
                )
            ]
        )

        if lop_xem:

            df_loc = df_xu_huong[
                df_xu_huong[
                    "Lớp"
                ].isin(
                    lop_xem
                )
            ]

            bieu_do_xu_huong = (
                alt.Chart(
                    df_loc
                )
                .mark_line(
                    point=True
                )
                .encode(

                    x=alt.X(
                        "Tuần:O",
                        title="Tuần"
                    ),

                    y=alt.Y(
                        "Tổng điểm:Q",
                        title="Tổng điểm"
                    ),

                    color=alt.Color(
                        "Lớp:N",
                        title="Lớp"
                    ),

                    tooltip=[
                        alt.Tooltip(
                            "Tuần:O",
                            title="Tuần"
                        ),
                        alt.Tooltip(
                            "Lớp:N",
                            title="Lớp"
                        ),
                        alt.Tooltip(
                            "Tổng điểm:Q",
                            title="Tổng điểm"
                        )
                    ]
                )
                .properties(
                    height=320
                )
            )

            st.altair_chart(
                bieu_do_xu_huong,
                width="stretch"
            )


    # =====================================================
    # NHẬN XÉT AI
    # =====================================================

    noi_dung_nhan_xet = (
        tao_nhan_xet_thi_dua(
            tuan,
            bang,
            bang_tuan_truoc
        )
    )

    with st.expander(
        "🤖 NHẬN XÉT CỦA TRỢ LÝ AI",
        expanded=False
    ):

        st.text_area(
            "Nội dung nhận xét",
            value=noi_dung_nhan_xet,
            height=300
        )


    # =====================================================
    # XUẤT ẢNH
    # =====================================================

    with st.expander(
        "🖼️ XUẤT ẢNH TỔNG KẾT TOÀN TRƯỜNG",
        expanded=False
    ):

        st.write(
            f"Ảnh sẽ lấy toàn bộ {len(bang)} lớp "
            f"có dữ liệu ở Tuần {tuan}."
        )

        if st.button(
            "🖼️ TẠO ẢNH TỔNG KẾT",
            type="primary",
            key="tao_anh"
        ):

            try:

                anh_png = (
                    tao_anh_dashboard(
                        nam_hoc,
                        tuan,
                        bang
                    )
                )

                if anh_png is not None:

                    st.session_state[
                        "anh_dashboard"
                    ] = anh_png

                    st.success(
                        "Đã tạo ảnh tổng kết thành công."
                    )

            except Exception as loi:

                st.error(
                    f"Lỗi khi tạo ảnh: {loi}"
                )


        if (
            "anh_dashboard"
            in st.session_state
        ):

            st.image(
                st.session_state[
                    "anh_dashboard"
                ],
                width="stretch"
            )

            st.download_button(
                "⬇️ TẢI ẢNH PNG",
                data=st.session_state[
                    "anh_dashboard"
                ],
                file_name=(
                    f"tong_ket_thi_dua_tuan_{tuan}.png"
                ),
                mime="image/png",
                type="primary"
            )


    # =====================================================
    # XUẤT WORD
    # =====================================================

    with st.expander(
        "📄 XUẤT BÁO CÁO WORD TOÀN TRƯỜNG",
        expanded=False
    ):

        st.write(
            "Báo cáo lấy toàn bộ lớp có dữ liệu, "
            "xếp hạng từ cao xuống thấp và có Top 5."
        )

        ten_truong = st.text_input(
            "Tên trường",
            value="TRƯỜNG TH&THCS AN LINH",
            key="word_ten_truong"
        )

        dia_danh = st.text_input(
            "Địa danh",
            value="An Linh",
            key="word_dia_danh"
        )

        w1, w2, w3 = st.columns(
            3
        )

        with w1:

            ngay = st.text_input(
                "Ngày",
                value=".....",
                key="word_ngay"
            )

        with w2:

            thang = st.text_input(
                "Tháng",
                value=".....",
                key="word_thang"
            )

        with w3:

            nam = st.text_input(
                "Năm",
                value="2026",
                key="word_nam"
            )

        nguoi_tong_hop = (
            st.text_input(
                "Người tổng hợp",
                value="",
                key="word_nguoi_tong_hop"
            )
        )

        lua_chon_ky = st.selectbox(
            "Chức danh người ký",
            [
                (
                    "KT. HIỆU TRƯỞNG - "
                    "PHÓ HIỆU TRƯỞNG"
                ),
                "HIỆU TRƯỞNG",
                "PHÓ HIỆU TRƯỞNG"
            ],
            key="word_chuc_danh"
        )

        if lua_chon_ky == (
            "KT. HIỆU TRƯỞNG - "
            "PHÓ HIỆU TRƯỞNG"
        ):

            chuc_danh_ky = (
                "KT. HIỆU TRƯỞNG\n"
                "PHÓ HIỆU TRƯỞNG"
            )

        else:

            chuc_danh_ky = (
                lua_chon_ky
            )


        if st.button(
            "📄 TẠO BÁO CÁO WORD TOÀN TRƯỜNG",
            type="primary",
            key="tao_word"
        ):

            try:

                duong_dan_word = (
                    tao_bao_cao_word_toan_truong(
                        nam_hoc,
                        tuan,
                        bang,
                        noi_dung_nhan_xet,
                        ten_truong,
                        dia_danh,
                        ngay,
                        thang,
                        nam,
                        chuc_danh_ky,
                        nguoi_tong_hop
                    )
                )

                if (
                    duong_dan_word
                    and os.path.exists(
                        duong_dan_word
                    )
                ):

                    st.session_state[
                        "duong_dan_word_toan_truong"
                    ] = duong_dan_word

                    st.success(
                        "Đã tạo báo cáo Word "
                        "toàn trường thành công."
                    )

                else:

                    st.error(
                        "Không tạo được file Word."
                    )

            except Exception as loi:

                st.error(
                    f"Lỗi khi tạo Word: {loi}"
                )


        if (
            "duong_dan_word_toan_truong"
            in st.session_state
        ):

            duong_dan_word = (
                st.session_state[
                    "duong_dan_word_toan_truong"
                ]
            )

            if os.path.exists(
                duong_dan_word
            ):

                with open(
                    duong_dan_word,
                    "rb"
                ) as tep:

                    st.download_button(
                        label=(
                            "⬇️ TẢI BÁO CÁO WORD "
                            "TOÀN TRƯỜNG"
                        ),
                        data=tep,
                        file_name=(
                            f"bao_cao_toan_truong_"
                            f"tuan_{tuan}.docx"
                        ),
                        mime=(
                            "application/vnd."
                            "openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                        type="primary"
                    )


else:

    st.info(
        f"Chưa có dữ liệu thi đua của Tuần {tuan}."
    )


# =========================================================
# NHẬP / CẬP NHẬT ĐIỂM
# =========================================================

st.divider()

with st.expander(
    "📝 NHẬP / CẬP NHẬT ĐIỂM THI ĐUA",
    expanded=False
):

    danh_sach_lop = (
        lay_danh_sach_lop(
            nam_hoc,
            chi_lay_dang_hoat_dong=True
        )
    )

    ten_cac_lop = [
        dong[0]
        for dong in danh_sach_lop
    ]

    if ten_cac_lop:

        lop_nhap_diem = (
            st.selectbox(
                "Chọn lớp",
                ten_cac_lop
            )
        )

    else:

        st.warning(
            "Chưa có lớp nào đang hoạt động. "
            "Hãy thêm lớp trong mục "
            "Quản lý danh sách lớp."
        )

        lop_nhap_diem = ""

    d1, d2, d3 = st.columns(
        3
    )

    with d1:

        hoc_tap = st.number_input(
            "📚 Học tập",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    with d2:

        ky_luat = st.number_input(
            "🛡️ Kỷ luật",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    with d3:

        ve_sinh = st.number_input(
            "🧹 Vệ sinh",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    d4, d5 = st.columns(
        2
    )

    with d4:

        diem_cong = st.number_input(
            "➕ Điểm cộng",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    with d5:

        diem_tru = st.number_input(
            "➖ Điểm trừ",
            min_value=0.0,
            value=0.0,
            step=1.0
        )

    ghi_chu = st.text_area(
        "Ghi chú"
    )

    tong_diem = tinh_tong_diem(
        hoc_tap,
        ky_luat,
        ve_sinh,
        diem_cong,
        diem_tru
    )

    st.metric(
        "🏆 Tổng điểm",
        tong_diem
    )

    st.caption(
        "Tổng điểm = Học tập + Kỷ luật + "
        "Vệ sinh + Điểm cộng - Điểm trừ"
    )

    if st.button(
        "💾 LƯU / CẬP NHẬT ĐIỂM",
        type="primary"
    ):

        if lop_nhap_diem == "":

            st.error(
                "Chưa có lớp để lưu."
            )

        else:

            them_diem(
                nam_hoc,
                tuan,
                lop_nhap_diem,
                hoc_tap,
                ky_luat,
                ve_sinh,
                diem_cong,
                diem_tru,
                tong_diem,
                ghi_chu
            )

            st.success(
                f"Đã lưu điểm lớp "
                f"{lop_nhap_diem} - Tuần {tuan}."
            )

            st.rerun()


# =========================================================
# SƠ KẾT / TỔNG KẾT THI ĐUA
# =========================================================

st.divider()

with st.expander(
    "📘 SƠ KẾT - 📕 TỔNG KẾT THI ĐUA",
    expanded=False
):

    st.info(
        "📘 Sơ kết: tổng hợp kết quả thi đua từ Tháng 9 đến hết Tháng 12.\n\n"
        "📕 Tổng kết: tổng hợp kết quả từ đầu năm học đến Tuần đang chọn."
    )

    cac_tuan_chua_co_thang = (
        lay_cac_tuan_chua_co_thang(
            nam_hoc
        )
    )

    if cac_tuan_chua_co_thang:

        st.warning(
            "⚠️ Còn các tuần có dữ liệu điểm nhưng chưa gán tháng: "
            + ", ".join(
                [
                    f"Tuần {x}"
                    for x in cac_tuan_chua_co_thang
                ]
            )
            + ". Hãy gán tháng đầy đủ trước khi xuất báo cáo."
        )

    else:

        st.success(
            "✅ Các tuần có dữ liệu điểm đã được gán tháng. "
            "Có thể tạo báo cáo Sơ kết hoặc Tổng kết."
        )

    so_ket_col, tong_ket_col = st.columns(2)

    # =====================================================
    # SƠ KẾT THI ĐUA
    # =====================================================

    with so_ket_col:

        st.markdown(
            "### 📘 SƠ KẾT THI ĐUA"
        )

        st.caption(
            "Tổng hợp Tháng 9 → Tháng 12, "
            "có xếp hạng toàn trường, tổng hợp theo tháng "
            "và chi tiết từng tuần."
        )

        nut_so_ket_bi_khoa = (
            len(cac_tuan_chua_co_thang) > 0
        )

        if st.button(
            "📘 TẠO EXCEL SƠ KẾT",
            type="primary",
            use_container_width=True,
            disabled=nut_so_ket_bi_khoa,
            key="tao_excel_so_ket"
        ):

            try:

                duong_dan_so_ket = (
                    tao_excel_so_ket(
                        nam_hoc
                    )
                )

                if (
                    duong_dan_so_ket
                    and os.path.exists(
                        duong_dan_so_ket
                    )
                ):

                    with open(
                        duong_dan_so_ket,
                        "rb"
                    ) as tep:

                        st.session_state[
                            "excel_so_ket_bytes"
                        ] = tep.read()

                    st.session_state[
                        "excel_so_ket_ten"
                    ] = os.path.basename(
                        duong_dan_so_ket
                    )

                    st.success(
                        "✅ Đã tạo Excel Sơ kết thi đua thành công."
                    )

                else:

                    st.error(
                        "Không tạo được file Excel Sơ kết."
                    )

            except Exception as loi:

                st.error(
                    f"Lỗi khi tạo Excel Sơ kết: {loi}"
                )

        if (
            "excel_so_ket_bytes"
            in st.session_state
        ):

            st.download_button(
                "⬇️ TẢI EXCEL SƠ KẾT",
                data=st.session_state[
                    "excel_so_ket_bytes"
                ],
                file_name=st.session_state.get(
                    "excel_so_ket_ten",
                    "so_ket_thi_dua.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                type="primary",
                use_container_width=True,
                key="tai_excel_so_ket"
            )

    # =====================================================
    # TỔNG KẾT THI ĐUA
    # =====================================================

    with tong_ket_col:

        st.markdown(
            "### 📕 TỔNG KẾT THI ĐUA"
        )

        st.caption(
            f"Tổng hợp từ đầu năm học đến Tuần {tuan} đang chọn, "
            "không lấy các tuần chưa diễn ra."
        )

        nut_tong_ket_bi_khoa = (
            len(cac_tuan_chua_co_thang) > 0
        )

        if st.button(
            f"📕 TẠO EXCEL TỔNG KẾT ĐẾN TUẦN {tuan}",
            type="primary",
            use_container_width=True,
            disabled=nut_tong_ket_bi_khoa,
            key="tao_excel_tong_ket"
        ):

            try:

                duong_dan_tong_ket = (
                    tao_excel_tong_ket(
                        nam_hoc,
                        tuan
                    )
                )

                if (
                    duong_dan_tong_ket
                    and os.path.exists(
                        duong_dan_tong_ket
                    )
                ):

                    with open(
                        duong_dan_tong_ket,
                        "rb"
                    ) as tep:

                        st.session_state[
                            "excel_tong_ket_bytes"
                        ] = tep.read()

                    st.session_state[
                        "excel_tong_ket_ten"
                    ] = os.path.basename(
                        duong_dan_tong_ket
                    )

                    st.success(
                        "✅ Đã tạo Excel Tổng kết thi đua thành công."
                    )

                else:

                    st.error(
                        "Không tạo được file Excel Tổng kết."
                    )

            except Exception as loi:

                st.error(
                    f"Lỗi khi tạo Excel Tổng kết: {loi}"
                )

        if (
            "excel_tong_ket_bytes"
            in st.session_state
        ):

            st.download_button(
                "⬇️ TẢI EXCEL TỔNG KẾT",
                data=st.session_state[
                    "excel_tong_ket_bytes"
                ],
                file_name=st.session_state.get(
                    "excel_tong_ket_ten",
                    f"tong_ket_thi_dua_den_tuan_{tuan}.xlsx"
                ),
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                type="primary",
                use_container_width=True,
                key="tai_excel_tong_ket"
            )


# =========================================================
# CHÂN TRANG
# =========================================================

st.divider()

st.caption(
    "Trợ lý AI xét thi đua • "
    "Quản lý lớp linh hoạt • "
    "Quản lý Tuần - Tháng • "
    "Xếp hạng đồng hạng • "
    "Top 5 • Xuất ảnh • Xuất Word • "
    "Sơ kết Excel • Tổng kết Excel."
)