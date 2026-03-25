from manim import *


class AnimationScene(Scene):
    def construct(self):
        # --- INTRO SCENE ---
        title = Text("Merge Sort", font_size=52, weight=BOLD)
        subtitle = Text("Divide and Conquer Strategy", font_size=32, color=BLUE)
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
        # Starting with a smaller subset to demonstrate the depth of recursion
        values = [38, 27, 43, 3, 9, 82, 10]
        squares = VGroup(*[Square(side_length=0.6) for _ in range(len(values))])
        squares.arrange(RIGHT, buff=0.1).move_to([-3.6, 2.5, 0])
        val_labels = VGroup(*[Text(str(v), font_size=18).move_to(sq) for v, sq in zip(values, squares)])
        self.add(squares, val_labels)

        # --- RIGHT-TOP: CODE PANEL ---
        code_snippet = [
            "def merge_sort(arr):",
            "    if len(arr) <= 1: return arr",
            "    mid = len(arr) // 2",
            "    left = merge_sort(arr[:mid])",
            "    right = merge_sort(arr[mid:])",
            "    return merge(left, right)"
        ]
        code_lines = VGroup()
        for i, line in enumerate(code_snippet):
            t = Text(line, font_size=16)
            if i == 0:
                t.move_to([0.5, 3.2, 0]).align_to([0.5, 0, 0], LEFT)
            else:
                t.next_to(code_lines[-1], DOWN, buff=0.2, aligned_edge=LEFT)
            code_lines.add(t)
        self.add(code_lines)

        # Highlighting Rectangle
        hi = Rectangle(width=5.5, height=0.3, fill_color=YELLOW, fill_opacity=0.22, stroke_width=0)
        hi.move_to(code_lines[0].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1)
        self.add(hi)

        # --- RIGHT-BOTTOM: VARIABLE TABLE ---
        hdr_n = Text("Variable", font_size=18, color=GRAY).move_to([1.2, -0.9, 0])
        hdr_v = Text("Value", font_size=18, color=GRAY).move_to([4.5, -0.9, 0])
        self.add(hdr_n, hdr_v)

        v_phase_n = Text("Phase", font_size=18).next_to(hdr_n, DOWN, buff=0.4).align_to(hdr_n, LEFT)
        v_phase_v = Text("Divide", font_size=18, color=YELLOW).move_to([4.5, v_phase_n.get_y(), 0])

        v_mid_n = Text("mid", font_size=18).next_to(v_phase_n, DOWN, buff=0.4).align_to(hdr_n, LEFT)
        v_mid_v = Text("-", font_size=18, color=YELLOW).move_to([4.5, v_mid_n.get_y(), 0])

        self.add(v_phase_n, v_phase_v, v_mid_n, v_mid_v)

        # --- ANIMATION: STEP 1 (Initial Split) ---
        self.play(hi.animate.move_to(code_lines[2].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        self.play(Transform(v_mid_v, Text("3", font_size=18, color=YELLOW).move_to(v_mid_v)))

        left_branch = VGroup(squares[:4], val_labels[:4])
        right_branch = VGroup(squares[4:], val_labels[4:])

        self.play(
            left_branch.animate.shift(LEFT * 0.8 + DOWN * 1.5),
            right_branch.animate.shift(RIGHT * 0.8 + DOWN * 1.5),
            run_time=1.2
        )
        self.wait(0.5)

        # --- ANIMATION: STEP 2 (Recursive Split on Left) ---
        self.play(hi.animate.move_to(code_lines[3].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))

        sub_left = VGroup(squares[:2], val_labels[:2])
        sub_right = VGroup(squares[2:4], val_labels[2:4])

        self.play(
            sub_left.animate.shift(LEFT * 0.4 + DOWN * 1.5),
            sub_right.animate.shift(RIGHT * 0.4 + DOWN * 1.5),
            run_time=1.0
        )
        self.wait(0.5)

        # --- ANIMATION: STEP 3 (Merge Action Example) ---
        # Update Table to Merge Phase
        strike = Line(v_phase_v.get_left(), v_phase_v.get_right(), color=RED, stroke_width=2)
        v_phase_v_new = Text("Merge", font_size=18, color=GREEN).next_to(v_phase_v, RIGHT, buff=0.2)

        self.play(hi.animate.move_to(code_lines[5].get_center()).align_to(code_lines, LEFT).shift(LEFT * 0.1))
        self.play(Create(strike), FadeIn(v_phase_v_new))

        # Show Merge: Sort [43, 3] -> [3, 43]
        target_vgroup = VGroup(squares[2:4], val_labels[2:4])
        self.play(Indicate(target_vgroup))

        # Swap values
        self.play(
            val_labels[2].animate.move_to(squares[3].get_center()),
            val_labels[3].animate.move_to(squares[2].get_center()),
            squares[2:4].animate.set_color(GREEN),
            run_time=1.0
        )
        # Internal update for consistency
        val_labels[2], val_labels[3] = val_labels[3], val_labels[2]

        self.wait(1)

        # --- OUTRO ---
        self.play(FadeOut(Group(*self.mobjects)))

        success_text = Text("Merge Sort: Divide & Conquer", font_size=42, color=GREEN).center()
        comp_text = Text("Time: O(n log n) | Space: O(n)", font_size=28, color=GRAY).next_to(success_text, DOWN,
                                                                                             buff=0.5)

        self.play(Write(success_text))
        self.play(FadeIn(comp_text))
        self.wait(2)