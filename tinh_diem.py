def tinh_tong_diem(
    hoc_tap,
    ky_luat,
    ve_sinh,
    diem_cong=0,
    diem_tru=0
):
    """
    Tính tổng điểm thi đua.

    Không giới hạn điểm tối đa.
    Tổng điểm được tính từ điểm thực tế nhà trường chấm.
    """

    tong_diem = (
        hoc_tap
        + ky_luat
        + ve_sinh
        + diem_cong
        - diem_tru
    )

    return round(tong_diem, 2)