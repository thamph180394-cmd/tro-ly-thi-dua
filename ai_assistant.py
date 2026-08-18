def tao_nhan_xet_thi_dua(
    tuan,
    bang_hien_tai,
    bang_tuan_truoc=None
):
    """
    Tạo nhận xét thi đua tự động theo văn phong nhà trường.
    """

    if bang_hien_tai is None or len(bang_hien_tai) == 0:
        return f"Tuần {tuan} chưa có dữ liệu thi đua để nhận xét."

    noi_dung = []

    # ==================================================
    # 1. KẾT QUẢ CHUNG
    # ==================================================

    tong_so_lop = len(bang_hien_tai)

    diem_trung_binh = round(
        bang_hien_tai["Tổng điểm"].mean(),
        2
    )

    lop_dan_dau = bang_hien_tai.iloc[0]
    lop_cuoi = bang_hien_tai.iloc[-1]

    noi_dung.append(
        f"Qua tổng hợp kết quả thi đua tuần {tuan}, "
        f"có {tong_so_lop} lớp được theo dõi và xếp hạng. "
        f"Điểm trung bình của các lớp đạt {diem_trung_binh} điểm."
    )

    # ==================================================
    # 2. TUYÊN DƯƠNG LỚP DẪN ĐẦU
    # ==================================================

    noi_dung.append(
        f"Lớp {lop_dan_dau['Lớp']} dẫn đầu bảng xếp hạng "
        f"với {lop_dan_dau['Tổng điểm']} điểm. "
        f"Đây là tập thể có kết quả thi đua nổi bật trong tuần."
    )

    # ==================================================
    # 3. TÌM CÁC TIÊU CHÍ NỔI BẬT
    # ==================================================

    lop_hoc_tap_tot = bang_hien_tai.loc[
        bang_hien_tai["Học tập"].idxmax()
    ]

    lop_ky_luat_tot = bang_hien_tai.loc[
        bang_hien_tai["Kỷ luật"].idxmax()
    ]

    lop_ve_sinh_tot = bang_hien_tai.loc[
        bang_hien_tai["Vệ sinh"].idxmax()
    ]

    noi_dung.append(
        f"Về các mặt thi đua, lớp {lop_hoc_tap_tot['Lớp']} "
        f"có điểm học tập cao nhất với {lop_hoc_tap_tot['Học tập']} điểm; "
        f"lớp {lop_ky_luat_tot['Lớp']} có điểm kỷ luật cao nhất "
        f"với {lop_ky_luat_tot['Kỷ luật']} điểm; "
        f"lớp {lop_ve_sinh_tot['Lớp']} có điểm vệ sinh cao nhất "
        f"với {lop_ve_sinh_tot['Vệ sinh']} điểm."
    )

    # ==================================================
    # 4. SO SÁNH VỚI TUẦN TRƯỚC
    # ==================================================

    if (
        bang_tuan_truoc is not None
        and len(bang_tuan_truoc) > 0
    ):

        hang_tuan_truoc = dict(
            zip(
                bang_tuan_truoc["Lớp"],
                bang_tuan_truoc["Hạng"]
            )
        )

        diem_tuan_truoc = dict(
            zip(
                bang_tuan_truoc["Lớp"],
                bang_tuan_truoc["Tổng điểm"]
            )
        )

        lop_tien_bo = None
        lop_giam_nhieu = None

        muc_tien_bo_tot_nhat = None
        muc_giam_lon_nhat = None

        for _, dong in bang_hien_tai.iterrows():

            lop = dong["Lớp"]

            if lop in hang_tuan_truoc:

                hang_cu = hang_tuan_truoc[lop]
                hang_moi = dong["Hạng"]

                diem_cu = diem_tuan_truoc[lop]
                diem_moi = dong["Tổng điểm"]

                tang_hang = hang_cu - hang_moi
                tang_diem = diem_moi - diem_cu

                muc_tien_bo = (
                    tang_hang,
                    tang_diem
                )

                if (
                    muc_tien_bo_tot_nhat is None
                    or muc_tien_bo > muc_tien_bo_tot_nhat
                ):
                    muc_tien_bo_tot_nhat = muc_tien_bo

                    lop_tien_bo = {
                        "Lớp": lop,
                        "Tăng hạng": tang_hang,
                        "Tăng điểm": tang_diem
                    }

                giam_hang = hang_moi - hang_cu

                if giam_hang > 0:

                    if (
                        muc_giam_lon_nhat is None
                        or giam_hang > muc_giam_lon_nhat
                    ):
                        muc_giam_lon_nhat = giam_hang

                        lop_giam_nhieu = {
                            "Lớp": lop,
                            "Giảm hạng": giam_hang,
                            "Chênh điểm": tang_diem
                        }

        if lop_tien_bo is not None:

            if lop_tien_bo["Tăng hạng"] > 0:

                noi_dung.append(
                    f"Lớp {lop_tien_bo['Lớp']} là tập thể có sự tiến bộ "
                    f"nổi bật nhất khi tăng {lop_tien_bo['Tăng hạng']} bậc "
                    f"so với tuần trước."
                )

            elif lop_tien_bo["Tăng điểm"] > 0:

                noi_dung.append(
                    f"Lớp {lop_tien_bo['Lớp']} có chuyển biến tích cực, "
                    f"tăng {lop_tien_bo['Tăng điểm']:.1f} điểm "
                    f"so với tuần trước."
                )

        if lop_giam_nhieu is not None:

            noi_dung.append(
                f"Lớp {lop_giam_nhieu['Lớp']} giảm "
                f"{lop_giam_nhieu['Giảm hạng']} bậc so với tuần trước. "
                f"Tập thể lớp cần rà soát các nội dung còn hạn chế "
                f"để có biện pháp khắc phục trong tuần tiếp theo."
            )

    # ==================================================
    # 5. PHÂN TÍCH ĐIỂM TRỪ
    # ==================================================

    lop_diem_tru_cao = bang_hien_tai.loc[
        bang_hien_tai["Điểm trừ"].idxmax()
    ]

    if lop_diem_tru_cao["Điểm trừ"] > 0:

        noi_dung.append(
            f"Lớp {lop_diem_tru_cao['Lớp']} có số điểm trừ cao nhất "
            f"trong tuần với {lop_diem_tru_cao['Điểm trừ']} điểm. "
            f"Đề nghị tập thể lớp chú ý hạn chế các vi phạm "
            f"và nâng cao ý thức thực hiện nội quy."
        )

    # ==================================================
    # 6. SỬ DỤNG GHI CHÚ NẾU CÓ
    # ==================================================

    cac_ghi_chu = []

    for _, dong in bang_hien_tai.iterrows():

        ghi_chu = str(dong.get("Ghi chú", "")).strip()

        if (
            ghi_chu
            and ghi_chu.lower() != "nan"
        ):
            cac_ghi_chu.append(
                f"Lớp {dong['Lớp']}: {ghi_chu}"
            )

    if len(cac_ghi_chu) > 0:

        noi_dung.append(
            "Một số nội dung cần lưu ý trong tuần: "
            + "; ".join(cac_ghi_chu)
            + "."
        )

    # ==================================================
    # 7. LỚP CẦN CỐ GẮNG
    # ==================================================

    noi_dung.append(
        f"Lớp {lop_cuoi['Lớp']} hiện xếp cuối bảng với "
        f"{lop_cuoi['Tổng điểm']} điểm. "
        f"Tập thể lớp cần tiếp tục cố gắng, "
        f"đặc biệt chú trọng nâng cao kết quả học tập, "
        f"ý thức kỷ luật, vệ sinh và hạn chế điểm trừ."
    )

    # ==================================================
    # 8. ĐỀ NGHỊ CHUNG
    # ==================================================

    noi_dung.append(
        "Đề nghị các lớp tiếp tục phát huy những mặt đã thực hiện tốt, "
        "duy trì tinh thần thi đua tích cực, chấp hành nghiêm nội quy, "
        "nâng cao chất lượng học tập và giữ gìn vệ sinh lớp học. "
        "Các tập thể còn hạn chế cần chủ động khắc phục để nâng cao "
        "kết quả trong tuần tiếp theo."
    )

    return "\n\n".join(noi_dung)