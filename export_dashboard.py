from datetime import datetime
from io import BytesIO
from pathlib import Path
import re
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

# =========================================================
# CẤU HÌNH & TỌA ĐỘ
# =========================================================

BASE_W = 1102
BASE_H = 715

THU_MUC_GOC = Path(__file__).resolve().parent

ASSETS_DIR = THU_MUC_GOC / "tài sản"
if not ASSETS_DIR.exists():
    ASSETS_DIR = THU_MUC_GOC / "assets"

TEMPLATE_PATH = ASSETS_DIR / "dashboard_template.png"
if not TEMPLATE_PATH.exists():
    TEMPLATE_PATH = THU_MUC_GOC / "dashboard_template.png"


# =========================================================
# LOAD FONT TIẾNG VIỆT CHUẨN
# =========================================================

def tim_font():
    ds = [
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        THU_MUC_GOC / "arial.ttf",
        ASSETS_DIR / "arial.ttf",
        r"C:\Windows\Fonts\arial.ttf"
    ]
    for p in ds:
        if Path(p).exists():
            return str(p)
    return None

FONT_PATH = tim_font()

def font(size, bold=False):
    if FONT_PATH:
        try:
            return ImageFont.truetype(FONT_PATH, size)
        except Exception:
            pass
    return ImageFont.load_default()


# =========================================================
# HÀM HỖ TRỢ DỮ LIỆU
# =========================================================

def hien_thi_so(gia_tri):
    try:
        so = float(gia_tri)
        if so.is_integer():
            return str(int(so))
        return f"{so:.2f}".rstrip("0").rstrip(".")
    except Exception:
        return str(gia_tri)


def chuan_hoa_bang(bang):
    if bang is None:
        return pd.DataFrame()

    df = bang.copy()
    if df.empty:
        return df

    cac_cot_so = [
        "Học tập",
        "Kỷ luật",
        "Vệ sinh",
        "Điểm cộng",
        "Điểm trừ",
        "Tổng điểm"
    ]

    for cot in cac_cot_so:
        if cot in df.columns:
            df[cot] = pd.to_numeric(df[cot], errors="coerce").fillna(0)

    df = df.sort_values(
        ["Tổng điểm", "Lớp"],
        ascending=[False, True],
        kind="stable"
    ).reset_index(drop=True)

    df["Hạng"] = df["Tổng điểm"].rank(method="min", ascending=False).astype(int)
    return df


def ghep_lop(ds):
    ds = [str(x) for x in ds]
    return ", ".join(ds)


def doc_thay_doi(gia_tri):
    text = str(gia_tri).strip()
    if text in ["", "—", "-"]:
        return 0

    match = re.search(r"(\d+)", text)
    if not match:
        return 0

    so = int(match.group(1))
    if "▲" in text:
        return so
    if "▼" in text:
        return -so
    return 0


def tim_tien_bo(df):
    if "Tăng/Giảm" not in df.columns:
        return "—", ""

    tam = df.copy()
    tam["_doi"] = tam["Tăng/Giảm"].apply(doc_thay_doi)
    max_doi = tam["_doi"].max()

    if max_doi <= 0:
        return "—", ""

    dong = tam[tam["_doi"] == max_doi].iloc[0]
    return (str(dong["Lớp"]), f"▲ {max_doi} bậc")


def tim_on_dinh(df):
    if "Tăng/Giảm" not in df.columns:
        return "—", ""

    tam = df.copy()
    tam["_doi"] = tam["Tăng/Giảm"].apply(doc_thay_doi)
    on_dinh = tam[tam["_doi"] == 0]

    if on_dinh.empty:
        return "—", ""

    dong = on_dinh.iloc[0]
    return (str(dong["Lớp"]), "Ổn định")


# =========================================================
# HÀM VẼ CHỮ
# =========================================================

def text_center(draw, xy, text, font_obj, fill):
    x, y = xy
    bbox = draw.textbbox((0, 0), str(text), font=font_obj)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((x - w / 2, y - h / 2), str(text), font=font_obj, fill=fill)


def text_right(draw, xy, text, font_obj, fill):
    x, y = xy
    bbox = draw.textbbox((0, 0), str(text), font=font_obj)
    w = bbox[2] - bbox[0]
    draw.text((x - w, y), str(text), font=font_obj, fill=fill)


# =========================================================
# XÓA CÁC VÙNG DỮ LIỆU CŨ TRÊN MẪU
# =========================================================

def xoa_noi_dung_dong(img):
    draw = ImageDraw.Draw(img)

    # 1. Ruy băng Năm học & Tuần
    draw.rectangle((438, 89, 635, 108), fill="#11479B")
    draw.rectangle((638, 89, 760, 108), fill="#D7222D")

    # 2. Xóa chữ trên dải banner bảng xếp hạng
    draw.rectangle((95, 222, 380, 246), fill="#0757B8")

    # 3. Lịch tuần góc phải
    draw.rectangle((982, 50, 1048, 84), fill="#FFFFFF")
    draw.rectangle((956, 94, 1076, 111), fill="#174997")

    # 4. 6 ô thông số tổng quan
    cac_vung = [
        (105, 151, 194, 205, "#F8FCFF"),
        (274, 151, 365, 205, "#F9FFF9"),
        (444, 151, 550, 205, "#FFFDF6"),
        (614, 151, 723, 205, "#FCF9FF"),
        (786, 151, 895, 205, "#F8FDFF"),
        (956, 151, 1074, 205, "#FFF9F6"),
    ]
    for vung in cac_vung:
        x1, y1, x2, y2, mau = vung
        draw.rectangle((x1, y1, x2, y2), fill=mau)

    # 5. Khung bảng xếp hạng
    draw.rectangle((48, 270, 1082, 499), fill="#FFFFFF")

    # 6. Bảng Top 5
    draw.rectangle((108, 557, 478, 669), fill="#FFFDF8")

    # 7. Khung biểu đồ
    draw.rectangle((513, 530, 954, 686), fill="#FFFFFF")

    return img


# =========================================================
# VẼ THÔNG TIN
# =========================================================

def ve_thong_tin_dau(img, nam_hoc, tuan, df):
    draw = ImageDraw.Draw(img)

    tong_lop = len(df)
    diem_tb = df["Tổng điểm"].mean() if not df.empty else 0

    dau = df[df["Hạng"] == 1]
    lop_dau = ghep_lop(dau["Lớp"].tolist()) if not dau.empty else "—"
    diem_dau = dau.iloc[0]["Tổng điểm"] if not dau.empty else 0

    diem_cuoi = df["Tổng điểm"].min() if not df.empty else 0
    cuoi = df[df["Tổng điểm"] == diem_cuoi]
    lop_cuoi = ghep_lop(cuoi["Lớp"].tolist()) if not cuoi.empty else "—"

    lop_tien_bo, chi_tiet_tien_bo = tim_tien_bo(df)
    lop_on_dinh, chi_tiet_on_dinh = tim_on_dinh(df)

    text_center(draw, (536, 98), f"NĂM HỌC {nam_hoc}", font(14, True), "#FFFFFF")
    text_center(draw, (699, 98), f"TUẦN {tuan}", font(14, True), "#FFFFFF")

    text_center(draw, (1015, 66), str(tuan), font(28, True), "#D5222E")
    ngay = datetime.now().strftime("%d/%m/%Y")
    text_center(draw, (1015, 102), f"Ngày cập nhật: {ngay}", font(9, False), "#FFFFFF")

    text_center(draw, (157, 166), hien_thi_so(tong_lop), font(32, True), "#174EAA")
    text_center(draw, (157, 195), "LỚP", font(12, True), "#174EAA")

    text_center(draw, (320, 166), hien_thi_so(diem_tb), font(26, True), "#258A39")
    text_center(draw, (320, 195), "điểm", font(11, False), "#333333")

    text_center(draw, (498, 164), lop_dau, font(22, True), "#C98200")
    text_center(draw, (498, 194), f"{hien_thi_so(diem_dau)} điểm", font(11, False), "#333333")

    text_center(draw, (666, 164), lop_tien_bo, font(23, True), "#5C2897")
    if chi_tiet_tien_bo:
        text_center(draw, (666, 194), chi_tiet_tien_bo, font(11, True), "#258A39")

    text_center(draw, (838, 164), lop_on_dinh, font(23, True), "#118DA6")
    if chi_tiet_on_dinh:
        text_center(draw, (838, 194), chi_tiet_on_dinh, font(10, False), "#333333")

    text_center(draw, (1010, 164), lop_cuoi, font(23, True), "#D63D20")
    text_center(draw, (1010, 194), f"{hien_thi_so(diem_cuoi)} điểm", font(11, False), "#333333")


def ve_bang_xep_hang(img, df, tuan):
    draw = ImageDraw.Draw(img)

    draw.text(
        (105, 227),
        f"BẢNG XẾP HẠNG TOÀN TRƯỜNG - TUẦN {tuan}",
        font=font(12, True),
        fill="#FFFFFF"
    )

    cot_x = [50, 128, 241, 370, 491, 610, 727, 846, 964, 1081]
    tieu_de = [
        "Hạng", "Lớp", "Khối", "Học tập", "Kỷ luật",
        "Vệ sinh", "Điểm cộng", "Điểm trừ", "Tổng điểm"
    ]

    draw.rectangle((50, 252, 1081, 270), fill="#0755B6")
    for i in range(len(tieu_de)):
        x1 = cot_x[i]
        x2 = cot_x[i + 1]
        text_center(
            draw,
            ((x1 + x2) / 2, 260),
            tieu_de[i],
            font(10, True),
            "#FFFFFF"
        )
        draw.line((x2, 252, x2, 499), fill="#B8CCE2", width=1)

    y_start = 270
    row_h = 16.35

    for i, row in df.iterrows():
        y1 = int(y_start + i * row_h)
        y2 = int(y_start + (i + 1) * row_h)
        mau_nen = "#FFFFFF" if i % 2 == 0 else "#EAF3FB"

        draw.rectangle((50, y1, 1081, y2), fill=mau_nen)
        draw.line((50, y2, 1081, y2), fill="#C6D4E3", width=1)

        gia_tri = [
            row["Hạng"],
            row["Lớp"],
            row.get("Khối", ""),
            row.get("Học tập", 0),
            row.get("Kỷ luật", 0),
            row.get("Vệ sinh", 0),
            row.get("Điểm cộng", 0),
            row.get("Điểm trừ", 0),
            row["Tổng điểm"]
        ]

        for c, value in enumerate(gia_tri):
            x1 = cot_x[c]
            x2 = cot_x[c + 1]
            mau = "#202020"
            bold = False

            if c == 0:
                if int(row["Hạng"]) == 1:
                    mau = "#CE8300"
                    bold = True
                elif int(row["Hạng"]) == 3:
                    mau = "#B6651C"
                    bold = True

            if c == 8:
                mau = "#D71920"
                bold = True

            text_center(
                draw,
                ((x1 + x2) / 2, (y1 + y2) / 2),
                hien_thi_so(value),
                font(10, bold),
                mau
            )


def ve_top5(img, df):
    draw = ImageDraw.Draw(img)
    top5 = df[df["Hạng"] <= 5].copy()

    cot_x = [109, 183, 291, 389, 478]
    headers = ["Hạng", "Lớp", "Khối", "Tổng điểm"]

    draw.rectangle((109, 536, 478, 557), fill="#E01A17")
    for i, h in enumerate(headers):
        text_center(
            draw,
            ((cot_x[i] + cot_x[i + 1]) / 2, 546),
            h,
            font(10, True),
            "#FFFFFF"
        )

    y_start = 557
    row_h = 21.5
    for i, (_, row) in enumerate(top5.iterrows()):
        y1 = int(y_start + i * row_h)
        y2 = int(y_start + (i + 1) * row_h)
        mau_nen = "#FFFFFF" if i % 2 == 0 else "#FFF7E6"

        draw.rectangle((109, y1, 478, y2), fill=mau_nen)
        draw.line((109, y2, 478, y2), fill="#E8CA79", width=1)

        values = [
            row["Hạng"],
            row["Lớp"],
            row.get("Khối", ""),
            row["Tổng điểm"]
        ]

        for c, value in enumerate(values):
            mau = "#D71920" if c == 3 else "#202020"
            text_center(
                draw,
                ((cot_x[c] + cot_x[c + 1]) / 2, (y1 + y2) / 2),
                hien_thi_so(value),
                font(11, c in [0, 3]),
                mau
            )


def ve_bieu_do(img, df):
    draw = ImageDraw.Draw(img)
    if df.empty:
        return

    chart = df.sort_values("Tổng điểm", ascending=False).reset_index(drop=True)
    max_diem = max(chart["Tổng điểm"])

    x_label = 514
    x_bar = 547
    x_max = 924
    y_start = 545
    row_h = 9.6

    mau = [
        "#1559C5", "#1559C5", "#1766CE", "#1D78D8", "#2A93D1",
        "#39AFC9", "#46B7A7", "#54B98B", "#63BA70", "#73B94F",
        "#F3C62C", "#F4A527", "#EF7823", "#E63327"
    ]

    for i, row in chart.iterrows():
        y = int(y_start + i * row_h)
        lop = str(row["Lớp"])
        diem = float(row["Tổng điểm"])

        text_right(draw, (x_label, y - 4), lop, font(8, False), "#202020")

        bar_w = int((diem / max_diem) * (x_max - x_bar)) if max_diem > 0 else 0

        draw.rounded_rectangle(
            (x_bar, y - 4, x_bar + bar_w, y + 3),
            radius=2,
            fill=mau[min(i, len(mau) - 1)]
        )

        draw.text(
            (x_bar + bar_w + 5, y - 5),
            hien_thi_so(diem),
            font=font(8, True),
            fill="#202020"
        )


# =========================================================
# HÀM XUẤT DASHBOARD
# =========================================================

def tao_anh_dashboard(nam_hoc, tuan, bang):
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy file template:\n{TEMPLATE_PATH}")

    df = chuan_hoa_bang(bang)
    if df.empty:
        return None

    img = Image.open(TEMPLATE_PATH).convert("RGB")
    if img.size != (BASE_W, BASE_H):
        img = img.resize((BASE_W, BASE_H), Image.Resampling.LANCZOS)

    img = xoa_noi_dung_dong(img)

    ve_thong_tin_dau(img, nam_hoc, tuan, df)
    ve_bang_xep_hang(img, df, tuan)
    ve_top5(img, df)
    ve_bieu_do(img, df)

    bo_nho = BytesIO()
    img.save(bo_nho, format="PNG", optimize=True)
    bo_nho.seek(0)

    return bo_nho.getvalue()
