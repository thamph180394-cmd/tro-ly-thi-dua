import sqlite3
import os


DB_NAME = "data/thi_dua.db"


# =========================================================
# KẾT NỐI DATABASE
# =========================================================

def ket_noi():

    os.makedirs(
        "data",
        exist_ok=True
    )

    return sqlite3.connect(
        DB_NAME
    )


# =========================================================
# TẠO CƠ SỞ DỮ LIỆU
# =========================================================

def tao_co_so_du_lieu():

    conn = ket_noi()
    cursor = conn.cursor()

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
            UNIQUE(nam_hoc, tuan, lop)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS danh_sach_lop (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nam_hoc TEXT NOT NULL,
            lop TEXT NOT NULL,
            khoi TEXT,
            dang_hoat_dong INTEGER DEFAULT 1,
            UNIQUE(nam_hoc, lop)
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# THÊM / KÍCH HOẠT LỚP
# =========================================================

def them_lop(
    nam_hoc,
    lop,
    khoi
):

    lop = str(
        lop
    ).strip().upper()

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO danh_sach_lop (
            nam_hoc,
            lop,
            khoi,
            dang_hoat_dong
        )

        VALUES (?, ?, ?, 1)

        ON CONFLICT(nam_hoc, lop)

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

    lop_cu = str(
        lop_cu
    ).strip().upper()

    lop_moi = str(
        lop_moi
    ).strip().upper()

    if lop_cu == "":
        return False, "Tên lớp cũ không hợp lệ."

    if lop_moi == "":
        return False, "Tên lớp mới không được để trống."

    conn = ket_noi()
    cursor = conn.cursor()

    try:

        # -------------------------------------------------
        # KIỂM TRA LỚP CŨ CÓ TỒN TẠI KHÔNG
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM danh_sach_lop
            WHERE nam_hoc = ?
              AND lop = ?
        """, (
            nam_hoc,
            lop_cu
        ))

        lop_ton_tai = cursor.fetchone()

        if lop_ton_tai is None:

            conn.close()

            return (
                False,
                f"Không tìm thấy lớp {lop_cu}."
            )


        # -------------------------------------------------
        # NẾU ĐỔI TÊN THÌ KIỂM TRA TÊN MỚI
        # -------------------------------------------------

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

            trung_ten = cursor.fetchone()

            if trung_ten is not None:

                conn.close()

                return (
                    False,
                    f"Lớp {lop_moi} đã tồn tại."
                )


        # -------------------------------------------------
        # CẬP NHẬT DANH SÁCH LỚP
        # -------------------------------------------------

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


        # -------------------------------------------------
        # CẬP NHẬT TÊN LỚP TRONG TOÀN BỘ ĐIỂM CŨ
        # -------------------------------------------------

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
            f"Đã cập nhật lớp {lop_cu} thành {lop_moi} - {khoi_moi}."
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
        str(lop).strip().upper()
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

            ORDER BY khoi, lop
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

            ORDER BY khoi, lop
        """, (
            nam_hoc,
        ))

    du_lieu = cursor.fetchall()

    conn.close()

    return du_lieu


# =========================================================
# ẨN LỚP
# =========================================================

def an_lop(
    nam_hoc,
    lop
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE danh_sach_lop

        SET dang_hoat_dong = 0

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        nam_hoc,
        str(lop).strip().upper()
    ))

    conn.commit()
    conn.close()


# =========================================================
# KÍCH HOẠT LẠI
# =========================================================

def kich_hoat_lop(
    nam_hoc,
    lop
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE danh_sach_lop

        SET dang_hoat_dong = 1

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        nam_hoc,
        str(lop).strip().upper()
    ))

    conn.commit()
    conn.close()


# =========================================================
# XÓA KHỎI DANH SÁCH QUẢN LÝ
# KHÔNG XÓA ĐIỂM ĐÃ NHẬP
# =========================================================

def xoa_lop(
    nam_hoc,
    lop
):

    conn = ket_noi()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM danh_sach_lop

        WHERE nam_hoc = ?
          AND lop = ?
    """, (
        nam_hoc,
        str(lop).strip().upper()
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

    lop = str(
        lop
    ).strip().upper()

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

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(nam_hoc, tuan, lop)

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
        tuan,
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

        ORDER BY tong_diem DESC
    """, (
        nam_hoc,
        tuan
    ))

    du_lieu = cursor.fetchall()

    conn.close()

    return du_lieu


# =========================================================
# CHẠY TRỰC TIẾP
# =========================================================

if __name__ == "__main__":

    tao_co_so_du_lieu()

    print(
        "Đã tạo / kiểm tra cơ sở dữ liệu thi đua thành công."
    )