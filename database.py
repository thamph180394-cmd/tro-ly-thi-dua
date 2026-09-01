import sqlite3
import os


# =========================================================
# CẤU HÌNH DATABASE
# =========================================================

DB_NAME = "data/thi_dua.db"


# =========================================================
# KẾT NỐI DATABASE
# =========================================================

def ket_noi():

    os.makedirs(
        "data",
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_NAME
    )

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    return conn


# =========================================================
# TẠO CƠ SỞ DỮ LIỆU
# =========================================================

def tao_co_so_du_lieu():

    conn = ket_noi()
    cursor = conn.cursor()

    # =====================================================
    # 1. BẢNG ĐIỂM THI ĐUA
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS diem_thi_dua (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nam_hoc TEXT NOT NULL,

            tuan INTEGER NOT NULL,

            lop TEXT NOT NULL,

            hoc_tap REAL DEFAULT 0,

            ky_luat REAL DEFAULT 0,

            ve_sinh REAL DEFAULT 0,

            diem_cong REAL DEFAULT 0,

            diem_tru REAL DEFAULT 0,

            tong_diem REAL DEFAULT 0,

            ghi_chu TEXT,

            UNIQUE(
                nam_hoc,
                tuan,
                lop
            )
        )
    """)

    # =====================================================
    # 2. BẢNG DANH SÁCH LỚP
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS danh_sach_lop (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nam_hoc TEXT NOT NULL,

            lop TEXT NOT NULL,

            khoi TEXT,

            dang_hoat_dong INTEGER DEFAULT 1,

            UNIQUE(
                nam_hoc,
                lop
            )
        )
    """)

    # =====================================================
    # 3. BẢNG QUẢN LÝ TUẦN - THÁNG
    # =====================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lich_tuan_thang (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            nam_hoc TEXT NOT NULL,

            tuan INTEGER NOT NULL,

            thang INTEGER NOT NULL,

            UNIQUE(
                nam_hoc,
                tuan
            )
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# CHUẨN HÓA TÊN LỚP
# =========================================================

def chuan_hoa_ten_lop(lop):

    return str(
        lop
    ).strip().upper()


# =========================================================
# THÊM / KÍCH HOẠT LỚP
# =========================================================

def them_lop(
    nam_hoc,
    lop,
    khoi
):

    lop = chuan_hoa_ten_lop(
        lop
    )

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO danh_sach_lop (
            nam_hoc,
            lop,
            khoi,
            dang_hoat_dong
        )

        VALUES (
            ?,
            ?,
            ?,
            1
        )

        ON CONFLICT(
            nam_hoc,
            lop
        )

        DO UPDATE SET

            khoi = excluded.khoi,

            dang_hoat_dong = 1
    """, (
        nam_hoc,
        lop,
        khoi
    ))

    conn.commit()
    conn.close()


# =========================================================
# CẬP NHẬT TÊN LỚP + KHỐI
# =========================================================

def cap_nhat_thong_tin_lop(
    nam_hoc,
    lop_cu,
    lop_moi,
    khoi_moi
):

    lop_cu = chuan_hoa_ten_lop(
        lop_cu
    )

    lop_moi = chuan_hoa_ten_lop(
        lop_moi
    )

    if lop_cu == "":

        return (
            False,
            "Tên lớp cũ không hợp lệ."
        )

    if lop_moi == "":

        return (
            False,
            "Tên lớp mới không được để trống."
        )

    conn = ket_noi()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            SELECT id

            FROM danh_sach_lop

            WHERE nam_hoc = ?
              AND lop = ?
        """, (
            nam_hoc,
            lop_cu
        ))

        lop_ton_tai = (
            cursor.fetchone()
        )

        if lop_ton_tai is None:

            conn.close()

            return (
                False,
                f"Không tìm thấy lớp {lop_cu}."
            )

        if lop_moi != lop_cu:

            cursor.execute("""
                SELECT id

                FROM danh_sach_lop

                WHERE nam_hoc = ?
                  AND lop = ?
            """, (
                nam_hoc,
                lop_moi
            ))

            trung_ten = (
                cursor.fetchone()
            )

            if trung_ten is not None:

                conn.close()

                return (
                    False,
                    f"Lớp {lop_moi} đã tồn tại."
                )

        cursor.execute("""
            UPDATE danh_sach_lop

            SET
                lop = ?,
                khoi = ?

            WHERE nam_hoc = ?
              AND lop = ?
        """, (
            lop_moi,
            khoi_moi,
            nam_hoc,
            lop_cu
        ))

        if lop_moi != lop_cu:

            cursor.execute("""
                UPDATE diem_thi_dua

                SET lop = ?

                WHERE nam_hoc = ?
                  AND lop = ?
            """, (
                lop_moi,
                nam_hoc,
                lop_cu
            ))

        conn.commit()
        conn.close()

        return (
            True,
            f"Đã cập nhật lớp {lop_cu} "
            f"thành {lop_moi} - {khoi_moi}."
        )

    except Exception as loi:

        conn.rollback()
        conn.close()

        return (
            False,
            f"Không thể cập nhật lớp: {loi}"
        )


# =========================================================
# CẬP NHẬT RIÊNG KHỐI
# =========================================================

def cap_nhat_khoi_lop(
    nam_hoc,
    lop,
    khoi_moi
):

    lop = chuan_hoa_ten_lop(
        lop
    )

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE danh_sach_lop

        SET khoi = ?

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        khoi_moi,
        nam_hoc,
        lop
    ))

    conn.commit()
    conn.close()


# =========================================================
# LẤY DANH SÁCH LỚP
# =========================================================

def lay_danh_sach_lop(
    nam_hoc,
    chi_lay_dang_hoat_dong=True
):

    conn = ket_noi()
    cursor = conn.cursor()

    if chi_lay_dang_hoat_dong:

        cursor.execute("""
            SELECT
                lop,
                khoi

            FROM danh_sach_lop

            WHERE nam_hoc = ?
              AND dang_hoat_dong = 1

            ORDER BY
                khoi,
                lop
        """, (
            nam_hoc,
        ))

    else:

        cursor.execute("""
            SELECT
                lop,
                khoi,
                dang_hoat_dong

            FROM danh_sach_lop

            WHERE nam_hoc = ?

            ORDER BY
                khoi,
                lop
        """, (
            nam_hoc,
        ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# ẨN LỚP
# =========================================================

def an_lop(
    nam_hoc,
    lop
):

    lop = chuan_hoa_ten_lop(
        lop
    )

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE danh_sach_lop

        SET dang_hoat_dong = 0

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        nam_hoc,
        lop
    ))

    conn.commit()
    conn.close()


# =========================================================
# KÍCH HOẠT LẠI LỚP
# =========================================================

def kich_hoat_lop(
    nam_hoc,
    lop
):

    lop = chuan_hoa_ten_lop(
        lop
    )

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE danh_sach_lop

        SET dang_hoat_dong = 1

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        nam_hoc,
        lop
    ))

    conn.commit()
    conn.close()


# =========================================================
# XÓA LỚP KHỎI DANH SÁCH
# KHÔNG XÓA ĐIỂM CŨ
# =========================================================

def xoa_lop(
    nam_hoc,
    lop
):

    lop = chuan_hoa_ten_lop(
        lop
    )

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM danh_sach_lop

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        nam_hoc,
        lop
    ))

    conn.commit()
    conn.close()


# =========================================================
# LƯU / CẬP NHẬT ĐIỂM
# =========================================================

def them_diem(
    nam_hoc,
    tuan,
    lop,
    hoc_tap,
    ky_luat,
    ve_sinh,
    diem_cong,
    diem_tru,
    tong_diem,
    ghi_chu=""
):

    lop = chuan_hoa_ten_lop(
        lop
    )

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO diem_thi_dua (
            nam_hoc,
            tuan,
            lop,
            hoc_tap,
            ky_luat,
            ve_sinh,
            diem_cong,
            diem_tru,
            tong_diem,
            ghi_chu
        )

        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )

        ON CONFLICT(
            nam_hoc,
            tuan,
            lop
        )

        DO UPDATE SET

            hoc_tap = excluded.hoc_tap,

            ky_luat = excluded.ky_luat,

            ve_sinh = excluded.ve_sinh,

            diem_cong = excluded.diem_cong,

            diem_tru = excluded.diem_tru,

            tong_diem = excluded.tong_diem,

            ghi_chu = excluded.ghi_chu
    """, (
        nam_hoc,
        int(tuan),
        lop,
        hoc_tap,
        ky_luat,
        ve_sinh,
        diem_cong,
        diem_tru,
        tong_diem,
        ghi_chu
    ))

    conn.commit()
    conn.close()


# =========================================================
# LẤY ĐIỂM THEO TUẦN
# =========================================================

def lay_diem_theo_tuan(
    nam_hoc,
    tuan
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            lop,
            hoc_tap,
            ky_luat,
            ve_sinh,
            diem_cong,
            diem_tru,
            tong_diem,
            ghi_chu

        FROM diem_thi_dua

        WHERE nam_hoc = ?
          AND tuan = ?

        ORDER BY
            tong_diem DESC,
            lop ASC
    """, (
        nam_hoc,
        int(tuan)
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# QUẢN LÝ TUẦN - THÁNG
# =========================================================

def luu_thang_cho_tuan(
    nam_hoc,
    tuan,
    thang
):

    tuan = int(
        tuan
    )

    thang = int(
        thang
    )

    if thang < 1 or thang > 12:

        return (
            False,
            "Tháng phải từ 1 đến 12."
        )

    if tuan < 1 or tuan > 52:

        return (
            False,
            "Tuần phải từ 1 đến 52."
        )

    conn = ket_noi()
    cursor = conn.cursor()

    try:

        cursor.execute("""
            INSERT INTO lich_tuan_thang (
                nam_hoc,
                tuan,
                thang
            )

            VALUES (
                ?,
                ?,
                ?
            )

            ON CONFLICT(
                nam_hoc,
                tuan
            )

            DO UPDATE SET
                thang = excluded.thang
        """, (
            nam_hoc,
            tuan,
            thang
        ))

        conn.commit()
        conn.close()

        return (
            True,
            f"Đã lưu Tuần {tuan} thuộc Tháng {thang}."
        )

    except Exception as loi:

        conn.rollback()
        conn.close()

        return (
            False,
            f"Không thể lưu tháng cho tuần: {loi}"
        )


# =========================================================
# LẤY THÁNG CỦA MỘT TUẦN
# =========================================================

def lay_thang_cua_tuan(
    nam_hoc,
    tuan
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT thang

        FROM lich_tuan_thang

        WHERE nam_hoc = ?
          AND tuan = ?
    """, (
        nam_hoc,
        int(tuan)
    ))

    dong = (
        cursor.fetchone()
    )

    conn.close()

    if dong is None:
        return None

    return int(
        dong[0]
    )


# =========================================================
# LẤY DANH SÁCH TUẦN - THÁNG
# =========================================================

def lay_danh_sach_tuan_thang(
    nam_hoc
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            tuan,
            thang

        FROM lich_tuan_thang

        WHERE nam_hoc = ?

        ORDER BY tuan ASC
    """, (
        nam_hoc,
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# LẤY CÁC TUẦN CỦA MỘT THÁNG
# =========================================================

def lay_cac_tuan_cua_thang(
    nam_hoc,
    thang
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT tuan

        FROM lich_tuan_thang

        WHERE nam_hoc = ?
          AND thang = ?

        ORDER BY tuan ASC
    """, (
        nam_hoc,
        int(thang)
    ))

    du_lieu = [
        dong[0]
        for dong in cursor.fetchall()
    ]

    conn.close()

    return du_lieu


# =========================================================
# XÓA CẤU HÌNH THÁNG CỦA TUẦN
# =========================================================

def xoa_thang_cua_tuan(
    nam_hoc,
    tuan
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM lich_tuan_thang

        WHERE nam_hoc = ?
          AND tuan = ?
    """, (
        nam_hoc,
        int(tuan)
    ))

    conn.commit()
    conn.close()


# =========================================================
# LẤY CÁC TUẦN CÓ ĐIỂM NHƯNG CHƯA GÁN THÁNG
# =========================================================

def lay_cac_tuan_chua_co_thang(
    nam_hoc
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT
            d.tuan

        FROM diem_thi_dua d

        LEFT JOIN lich_tuan_thang l

            ON d.nam_hoc = l.nam_hoc

           AND d.tuan = l.tuan

        WHERE d.nam_hoc = ?

          AND l.thang IS NULL

        ORDER BY d.tuan ASC
    """, (
        nam_hoc,
    ))

    du_lieu = [
        dong[0]
        for dong in cursor.fetchall()
    ]

    conn.close()

    return du_lieu


# =========================================================
# LẤY ĐIỂM THEO KHOẢNG THÁNG
# DÙNG CHO SƠ KẾT
# =========================================================

def lay_diem_theo_khoang_thang(
    nam_hoc,
    thang_bat_dau,
    thang_ket_thuc
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            d.tuan,

            l.thang,

            d.lop,

            d.hoc_tap,

            d.ky_luat,

            d.ve_sinh,

            d.diem_cong,

            d.diem_tru,

            d.tong_diem,

            d.ghi_chu

        FROM diem_thi_dua d

        INNER JOIN lich_tuan_thang l

            ON d.nam_hoc = l.nam_hoc

           AND d.tuan = l.tuan

        WHERE d.nam_hoc = ?

          AND l.thang BETWEEN ? AND ?

        ORDER BY

            d.tuan ASC,

            d.lop ASC
    """, (
        nam_hoc,
        int(thang_bat_dau),
        int(thang_ket_thuc)
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# LẤY ĐIỂM TỪ ĐẦU NĂM ĐẾN TUẦN HIỆN TẠI
# DÙNG CHO TỔNG KẾT
# =========================================================

def lay_diem_tu_dau_nam_den_tuan(
    nam_hoc,
    tuan_hien_tai
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            d.tuan,

            l.thang,

            d.lop,

            d.hoc_tap,

            d.ky_luat,

            d.ve_sinh,

            d.diem_cong,

            d.diem_tru,

            d.tong_diem,

            d.ghi_chu

        FROM diem_thi_dua d

        LEFT JOIN lich_tuan_thang l

            ON d.nam_hoc = l.nam_hoc

           AND d.tuan = l.tuan

        WHERE d.nam_hoc = ?

          AND d.tuan <= ?

        ORDER BY

            d.tuan ASC,

            d.lop ASC
    """, (
        nam_hoc,
        int(tuan_hien_tai)
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# TỔNG HỢP ĐIỂM THEO LỚP TRONG KHOẢNG THÁNG
# =========================================================

def tong_hop_diem_theo_lop_khoang_thang(
    nam_hoc,
    thang_bat_dau,
    thang_ket_thuc
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            d.lop,

            COALESCE(ds.khoi, '') AS khoi,

            COUNT(DISTINCT d.tuan) AS so_tuan,

            SUM(d.hoc_tap) AS tong_hoc_tap,

            SUM(d.ky_luat) AS tong_ky_luat,

            SUM(d.ve_sinh) AS tong_ve_sinh,

            SUM(d.diem_cong) AS tong_diem_cong,

            SUM(d.diem_tru) AS tong_diem_tru,

            SUM(d.tong_diem) AS tong_diem,

            AVG(d.tong_diem) AS diem_trung_binh

        FROM diem_thi_dua d

        INNER JOIN lich_tuan_thang l

            ON d.nam_hoc = l.nam_hoc

           AND d.tuan = l.tuan

        LEFT JOIN danh_sach_lop ds

            ON d.nam_hoc = ds.nam_hoc

           AND d.lop = ds.lop

        WHERE d.nam_hoc = ?

          AND l.thang BETWEEN ? AND ?

        GROUP BY

            d.lop,

            ds.khoi

        ORDER BY

            tong_diem DESC,

            d.lop ASC
    """, (
        nam_hoc,
        int(thang_bat_dau),
        int(thang_ket_thuc)
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# TỔNG HỢP ĐIỂM THEO LỚP ĐẾN TUẦN HIỆN TẠI
# =========================================================

def tong_hop_diem_theo_lop_den_tuan(
    nam_hoc,
    tuan_hien_tai
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            d.lop,

            COALESCE(ds.khoi, '') AS khoi,

            COUNT(DISTINCT d.tuan) AS so_tuan,

            SUM(d.hoc_tap) AS tong_hoc_tap,

            SUM(d.ky_luat) AS tong_ky_luat,

            SUM(d.ve_sinh) AS tong_ve_sinh,

            SUM(d.diem_cong) AS tong_diem_cong,

            SUM(d.diem_tru) AS tong_diem_tru,

            SUM(d.tong_diem) AS tong_diem,

            AVG(d.tong_diem) AS diem_trung_binh

        FROM diem_thi_dua d

        LEFT JOIN danh_sach_lop ds

            ON d.nam_hoc = ds.nam_hoc

           AND d.lop = ds.lop

        WHERE d.nam_hoc = ?

          AND d.tuan <= ?

        GROUP BY

            d.lop,

            ds.khoi

        ORDER BY

            tong_diem DESC,

            d.lop ASC
    """, (
        nam_hoc,
        int(tuan_hien_tai)
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# TỔNG HỢP ĐIỂM TỪNG LỚP THEO TỪNG THÁNG
# =========================================================

def tong_hop_diem_theo_thang(
    nam_hoc,
    thang_bat_dau,
    thang_ket_thuc
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT

            d.lop,

            COALESCE(ds.khoi, '') AS khoi,

            l.thang,

            SUM(d.tong_diem) AS tong_diem_thang

        FROM diem_thi_dua d

        INNER JOIN lich_tuan_thang l

            ON d.nam_hoc = l.nam_hoc

           AND d.tuan = l.tuan

        LEFT JOIN danh_sach_lop ds

            ON d.nam_hoc = ds.nam_hoc

           AND d.lop = ds.lop

        WHERE d.nam_hoc = ?

          AND l.thang BETWEEN ? AND ?

        GROUP BY

            d.lop,

            ds.khoi,

            l.thang

        ORDER BY

            d.lop ASC,

            l.thang ASC
    """, (
        nam_hoc,
        int(thang_bat_dau),
        int(thang_ket_thuc)
    ))

    du_lieu = (
        cursor.fetchall()
    )

    conn.close()

    return du_lieu


# =========================================================
# XÓA TOÀN BỘ DỮ LIỆU CỦA MỘT TUẦN
# =========================================================

def xoa_du_lieu_tuan(
    nam_hoc,
    tuan
):

    conn = ket_noi()
    cursor = conn.cursor()

    try:

        # Xóa toàn bộ điểm của tất cả các lớp trong tuần
        cursor.execute("""
            DELETE FROM diem_thi_dua

            WHERE nam_hoc = ?
              AND tuan = ?
        """, (
            nam_hoc,
            int(tuan)
        ))

        # Xóa luôn gán Tuần - Tháng của tuần đó
        cursor.execute("""
            DELETE FROM lich_tuan_thang

            WHERE nam_hoc = ?
              AND tuan = ?
        """, (
            nam_hoc,
            int(tuan)
        ))

        conn.commit()
        conn.close()

        return (
            True,
            f"Đã xóa toàn bộ dữ liệu Tuần {tuan}."
        )

    except Exception as loi:

        conn.rollback()
        conn.close()

        return (
            False,
            f"Không thể xóa dữ liệu Tuần {tuan}: {loi}"
        )


# =========================================================
# CHẠY TRỰC TIẾP DATABASE.PY
# =========================================================

if __name__ == "__main__":

    tao_co_so_du_lieu()

    print(
        "Đã tạo / kiểm tra cơ sở dữ liệu thi đua thành công."
    )

    print(
        "Đã sẵn sàng chức năng quản lý Tuần - Tháng."
    )

    print(
        "Đã sẵn sàng dữ liệu cho Sơ kết và Tổng kết thi đua."
    )

    print(
        "Đã sẵn sàng chức năng xóa dữ liệu theo tuần."
    )
