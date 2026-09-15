def is_blocked(selected_arrow, all_arrows):
    """判断选中箭头的前进方向上是否存在其他箭头"""

    selected_row = selected_arrow["row"]
    selected_col = selected_arrow["col"]
    direction = selected_arrow["direction"]

    for other_arrow in all_arrows:
        # 不检查箭头自身
        if other_arrow is selected_arrow:
            continue

        other_row = other_arrow["row"]
        other_col = other_arrow["col"]

        if direction == "UP":
            if other_col == selected_col and other_row < selected_row:
                return True

        elif direction == "DOWN":
            if other_col == selected_col and other_row > selected_row:
                return True

        elif direction == "LEFT":
            if other_row == selected_row and other_col < selected_col:
                return True

        elif direction == "RIGHT":
            if other_row == selected_row and other_col > selected_col:
                return True

    return False
