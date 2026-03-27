# ==========================================
# COMPONENT: Pointers (Up & Down)
# [NOTE]: Strictly bounded sizes. Pass the specific 'squares[index]' object so it knows exactly where to snap to.
# ==========================================
def get_up_pointer(target_mobject, text, color):
    start_pos = target_mobject.get_bottom() + DOWN * 0.8
    end_pos = target_mobject.get_bottom() + DOWN * 0.1
    arrow = Arrow(start=start_pos, end=end_pos, color=color, buff=0, max_tip_length_to_length_ratio=0.15)
    lbl = Text(text, font_size=16, color=color).next_to(arrow, DOWN, buff=0.1)
    return VGroup(arrow, lbl)

def get_down_pointer(target_mobject, text, color):
    start_pos = target_mobject.get_top() + UP * 0.8
    end_pos = target_mobject.get_top() + UP * 0.1
    arrow = Arrow(start=start_pos, end=end_pos, color=color, buff=0, max_tip_length_to_length_ratio=0.15)
    lbl = Text(text, font_size=16, color=color).next_to(arrow, UP, buff=0.1)
    return VGroup(arrow, lbl)