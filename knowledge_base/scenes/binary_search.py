from manim import *


class AnimationScene(Scene):
    def construct(self):
        # --- INTRO SCENE ---
        title = Text("Binary Search", font_size=52, weight=BOLD)
        subtitle = Text("Target = 72", font_size=32, color=BLUE)
        intro_grp = VGroup(title, subtitle).arrange(DOWN, buff=0.5).center()

        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(intro_grp))

        # --- PERSISTENT LABELS ---
        vis_label = Text("Visualization", font_size=20, color=GRAY).move_to([-6.8, 3.7, 0]).align_to([-6.8, 0, 0], LEFT)
        code_label = Text("Code", font_size=20, color=GRAY).move_to([0.25, 3.7, 0]).align_to([0.25, 0, 0], LEFT)
        var_label = Text("Variables", font_size=20, color=GRAY).move_to([0.25, -0.4, 0]).align_to([0.25, 0, 0], LEFT)
        self.add(vis_label, code_label, var_label)

        # --- LEFT ZONE: ARRAY ---
        values = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
        squares = VGroup(*[Square(side_length=0.6) for _ in range(len(values))])
        squares.arrange(RIGHT, buff=0).move_to([-3.6, 0, 0])
        val_labels = VGroup(*[Text(str(v), font_size=18).move_to(sq) for v, sq in zip(values, squares)])
        idx_labels = VGroup(
            *[Text(str(i), font_size=14, color=GRAY).next_to(sq, DOWN, buff=0.2) for i, sq in enumerate(squares)])
        self.add(squares, val_labels, idx_labels)

        # --- RIGHT-TOP: CODE PANEL ---
        code_snippet = [
            "low = 0",
            "high = len(arr) - 1",
            "while low <= high:",
            "    mid = (low + high) // 2",
            "    if arr[mid] == target:",
            "        return mid",
            "    elif arr[mid] < target:",
            "        low = mid + 1",
            "    else:",
            "        high = mid - 1"
        ]
        code_lines = VGroup()
        for i, line in enumerate(code_snippet):
            t = Text(line, font_size=16)
            if i == 0:
                t.move_to([0.5, 3.2, 0]).align_to([0.5, 0, 0], LEFT)
            else:
                t.next_to(code_lines[-1], DOWN, buff=0.18, aligned_edge=LEFT)
            code_lines.add(t)
        self.add(code_lines)

        # Shorter highlight rectangle to fit within the zone boundary
        hi = Rectangle(width=5.5, height=0.28, fill_color=YELLOW, fill_opacity=0.22, stroke_width=0)
        hi.move_to(code_lines[0].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1)
        self.add(hi)

        # --- RIGHT-BOTTOM: VARIABLE TABLE ---
        hdr_n = Text("Variable", font_size=18, color=GRAY).move_to([1.2, -0.9, 0])
        hdr_v = Text("Value", font_size=18, color=GRAY).move_to([4.5, -0.9, 0])
        self.add(hdr_n, hdr_v)

        v_low_n = Text("low", font_size=18).next_to(hdr_n, DOWN, buff=0.4).align_to(hdr_n, LEFT)
        v_low_v = Text("0", font_size=18, color=YELLOW).move_to([4.5, v_low_n.get_y(), 0])
        v_high_n = Text("high", font_size=18).next_to(v_low_n, DOWN, buff=0.4).align_to(hdr_n, LEFT)
        v_high_v = Text("9", font_size=18, color=YELLOW).move_to([4.5, v_high_n.get_y(), 0])
        v_mid_n = Text("mid", font_size=18).next_to(v_high_n, DOWN, buff=0.4).align_to(hdr_n, LEFT)
        v_mid_v = Text("-", font_size=18, color=YELLOW).move_to([4.5, v_mid_n.get_y(), 0])
        v_targ_n = Text("target", font_size=18).next_to(v_mid_n, DOWN, buff=0.4).align_to(hdr_n, LEFT)
        v_targ_v = Text("72", font_size=18, color=GREEN).move_to([4.5, v_targ_n.get_y(), 0])
        self.add(v_low_n, v_low_v, v_high_n, v_high_v, v_mid_n, v_mid_v, v_targ_n, v_targ_v)

        # --- POINTER HELPER ---
        def create_ptr(label_text, color, direction=UP, target_sq=squares[0]):
            arrow = Arrow(start=ORIGIN, end=direction * 0.7, color=color, buff=0)
            if np.array_equal(direction, UP):
                arrow.rotate(PI)  # Point down if starting from top
                lbl = Text(label_text, font_size=14, color=color).next_to(arrow, UP, buff=0.1)
                ptr_grp = VGroup(arrow, lbl).next_to(target_sq, UP, buff=0.1)
            else:
                lbl = Text(label_text, font_size=14, color=color).next_to(arrow, DOWN, buff=0.1)
                ptr_grp = VGroup(arrow, lbl).next_to(target_sq, DOWN, buff=0.1)
            return ptr_grp

        # Initial Pointers
        low_grp = create_ptr("low", BLUE, UP, squares[0])
        high_grp = create_ptr("high", BLUE, UP, squares[9])
        self.play(FadeIn(low_grp), FadeIn(high_grp))

        # --- ITERATION 1 ---
        self.play(hi.animate.move_to(code_lines[3].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        mid_grp = create_ptr("mid", TEAL, DOWN, squares[4])
        self.play(Transform(v_mid_v, Text("4", font_size=18, color=YELLOW).move_to(v_mid_v)), FadeIn(mid_grp))
        self.play(Indicate(squares[4]))

        # Discard Left
        self.play(hi.animate.move_to(code_lines[7].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        shade1 = Rectangle(width=3.0, height=0.8, fill_color=BLACK, fill_opacity=0.7, stroke_width=0).move_to(
            squares[0:5].get_center())
        strike1 = Line(v_low_v.get_left(), v_low_v.get_right(), color=RED)
        v_low_v_2 = Text("5", font_size=18, color=YELLOW).next_to(v_low_v, RIGHT, buff=0.3)

        self.play(
            FadeIn(shade1), Create(strike1), FadeIn(v_low_v_2),
            low_grp.animate.next_to(squares[5], UP, buff=0.1),
            FadeOut(mid_grp)
        )

        # --- ITERATION 2 ---
        self.play(hi.animate.move_to(code_lines[3].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        mid_grp = create_ptr("mid", TEAL, DOWN, squares[7])
        self.play(Transform(v_mid_v, Text("7", font_size=18, color=YELLOW).move_to(v_mid_v)), FadeIn(mid_grp))
        self.play(Indicate(squares[7]))

        # Discard more left
        self.play(hi.animate.move_to(code_lines[7].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        shade2 = Rectangle(width=1.8, height=0.8, fill_color=BLACK, fill_opacity=0.7, stroke_width=0).move_to(
            squares[5:8].get_center())
        strike2 = Line(v_low_v_2.get_left(), v_low_v_2.get_right(), color=RED)
        v_low_v_3 = Text("8", font_size=18, color=YELLOW).next_to(v_low_v_2, RIGHT, buff=0.3)

        self.play(
            FadeIn(shade2), Create(strike2), FadeIn(v_low_v_3),
            low_grp.animate.next_to(squares[8], UP, buff=0.1),
            FadeOut(mid_grp)
        )

        # --- ITERATION 3 ---
        self.play(hi.animate.move_to(code_lines[3].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        mid_grp = create_ptr("mid", TEAL, DOWN, squares[8])
        self.play(Transform(v_mid_v, Text("8", font_size=18, color=YELLOW).move_to(v_mid_v)), FadeIn(mid_grp))
        self.play(Indicate(squares[8]))

        # Found
        self.play(hi.animate.move_to(code_lines[4].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        self.play(squares[8].animate.set_color(GREEN), val_labels[8].animate.set_color(GREEN))
        self.play(hi.animate.move_to(code_lines[5].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        self.wait(2)

        # --- OUTRO ---
        self.play(FadeOut(Group(*self.mobjects)))
        success = Text("Binary Search Successful", color=GREEN).center()
        self.play(Write(success))
        self.wait(2)