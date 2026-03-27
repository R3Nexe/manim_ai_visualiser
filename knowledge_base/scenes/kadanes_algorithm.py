from manim import *
"""
TITLE: Kadane's Algorithm — Maximum Subarray Sum (Linear Pass)
CONCEPTS: kadane's algorithm, dynamic programming, maximum subarray, sliding window, contiguous subarray, global maximum, local maximum, time complexity
VISUAL_ELEMENTS: Square, Text, Arrow, Line, SurroundingRectangle, VGroup, ReplacementTransform, Indicate, MathTex, Code
DIFFICULTY: intermediate
"""
class KadanesAlgorithm(Scene):
    def construct(self):
        # ==========================================
        # SCENE 1: Educational Intro (Full Screen)
        # ==========================================
        title = Text("Kadane's Algorithm", font_size=52, weight=BOLD)
        subtitle = Text("Dynamic Programming (Maximum Subarray)", font_size=36, color=BLUE)
        intro_group = VGroup(title, subtitle).arrange(DOWN).center()
        
        self.play(FadeIn(intro_group, shift=UP))
        self.wait(1)
        self.play(intro_group.animate.to_edge(UP, buff=1.0))
        
        prereq = Text("Prerequisite: Arrays & Contiguous Subarrays", font_size=28, color=YELLOW)
        explanation = Text(
            "Finds the contiguous subarray with the largest sum\nin a single pass by tracking local and global maximums.", 
            font_size=24, line_spacing=1.5
        )
        intro_desc = VGroup(prereq, explanation).arrange(DOWN, buff=0.5).next_to(intro_group, DOWN, buff=1.0)
        
        self.play(FadeIn(intro_desc))
        self.wait(2.5)
        
        # Clear screen for UI Grid
        self.play(FadeOut(intro_group), FadeOut(intro_desc))

        # ==========================================
        # SCENE 2: UI Grid Generation
        # ==========================================
        h_line = Line(LEFT * 8, RIGHT * 8, color=GRAY, stroke_width=2).move_to(ORIGIN)
        v_line = Line(DOWN * 4, ORIGIN, color=GRAY, stroke_width=2)
        
        self.play(Create(h_line), Create(v_line))

        # ==========================================
        # SCENE 3: Populating UI Zones
        # ==========================================
        
        # --- Zone 1 (Top Half): Data Structure ---
        data = [-2, 4, -1, 2, -5]
        squares = VGroup(*[Square(side_length=0.7) for _ in data]).arrange(RIGHT, buff=0.1)
        labels = VGroup(*[Text(str(x), font_size=20).move_to(squares[i]) for i, x in enumerate(data)])
        array_group = VGroup(squares, labels).move_to(UP * 2.5) 
        
        self.play(FadeIn(array_group))

        # Compact pointer generator
        def get_up_pointer(target_mobject, text, color):
            start_pos = target_mobject.get_bottom() + DOWN * 0.5
            end_pos = target_mobject.get_bottom() + DOWN * 0.1
            arrow = Arrow(start=start_pos, end=end_pos, color=color, buff=0, max_tip_length_to_length_ratio=0.2)
            lbl = Text(text, font_size=16, color=color).next_to(arrow, DOWN, buff=0.1)
            return VGroup(arrow, lbl)

        # --- Zone 2 (Bottom Left): Custom Code Block ---
        code_lines_text = [
            "def maxSubArray(arr):",
            "    curSum = 0",
            "    maxSum = -inf",
            "    for i in arr:",
            "        curSum += i",
            "        maxSum = max(maxSum, curSum)",
            "        if curSum < 0:",
            "            curSum = 0",
            "    return maxSum"
        ]
        
        syntax_colors = {
            "def ": ORANGE, "for ": ORANGE, "if ": ORANGE, 
            "return ": ORANGE, "max": BLUE, "0": PURPLE
        }
        
        lines_group = VGroup(*[
            Text(line, font="Monospace", font_size=20, t2c=syntax_colors)
            for line in code_lines_text
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        code_bg = SurroundingRectangle(lines_group, color=GRAY, fill_color="#1e1e1e", fill_opacity=1, buff=0.3)
        code_block = VGroup(code_bg, lines_group).scale(0.60)
        
        code_title = Text("Code:", font_size=20, weight=BOLD).move_to(LEFT * 5.5 + DOWN * 0.5)
        code_block.next_to(code_title, DOWN, buff=0.2).align_to(code_title, LEFT)
        
        self.play(Write(code_title), FadeIn(code_block))

        highlighter = SurroundingRectangle(lines_group[0], color=YELLOW, fill_opacity=0.3, stroke_width=0)
        self.play(FadeIn(highlighter))

        # --- Zone 3 (Bottom Right): Execution State ---
        state_title = Text("Execution State:", font_size=20, weight=BOLD)
        state_title.next_to(ORIGIN, RIGHT, buff=0.5).set_y(-0.5)
        
        var_i = Text("i = ?", font_size=18, color=YELLOW)
        var_cur = Text("curSum = ?", font_size=18, color=GREEN)
        var_max = Text("maxSum = ?", font_size=18, color=RED)
        
        vars_group = VGroup(var_i, var_cur, var_max).arrange(DOWN, aligned_edge=LEFT).next_to(state_title, DOWN, buff=0.4).align_to(state_title, LEFT)
        
        exp_text = Text("Initializing algorithm...", font_size=18, color=WHITE).move_to(RIGHT * 0.5 + DOWN * 3.5, aligned_edge=LEFT)
        
        self.play(Write(state_title), FadeIn(vars_group), Write(exp_text))
        self.wait(1)

        # --- Reusable UI Helpers ---
        def move_highlight(line_idx):
            self.play(highlighter.animate.move_to(lines_group[line_idx]), run_time=0.4)

        def update_exp(new_text_str):
            nonlocal exp_text
            new_exp = Text(new_text_str, font_size=18, color=WHITE).move_to(RIGHT * 0.5 + DOWN * 3.5, aligned_edge=LEFT)
            self.play(ReplacementTransform(exp_text, new_exp), run_time=0.4)
            exp_text = new_exp

        def update_var(var_mob, new_text_str, color):
            new_var = Text(new_text_str, font_size=18, color=color).move_to(var_mob, aligned_edge=LEFT)
            self.play(ReplacementTransform(var_mob, new_var), run_time=0.4)
            return new_var

        # ==========================================
        # SCENE 4: Executing the Loop
        # ==========================================
        
        move_highlight(1)
        curSum = 0
        var_cur = update_var(var_cur, f"curSum = {curSum}", GREEN)
        update_exp("Initialize curSum to 0")
        self.wait(0.5)
        
        move_highlight(2)
        maxSum = float('-inf')
        var_max = update_var(var_max, f"maxSum = -inf", RED)
        update_exp("Initialize maxSum to lowest possible value")
        self.wait(0.5)

        i_ptr = None

        for idx, val in enumerate(data):
            move_highlight(3)
            var_i = update_var(var_i, f"i = {val} (idx {idx})", YELLOW)
            update_exp(f"Iterating over array: Processing {val}")
            
            new_ptr = get_up_pointer(squares[idx], "i", YELLOW)
            if i_ptr is None:
                self.play(FadeIn(new_ptr), run_time=0.4)
            else:
                self.play(ReplacementTransform(i_ptr, new_ptr), run_time=0.4)
            i_ptr = new_ptr
            
            self.play(Indicate(squares[idx], color=YELLOW), run_time=0.4)
            
            move_highlight(4)
            curSum += val
            var_cur = update_var(var_cur, f"curSum = {curSum}", GREEN)
            update_exp(f"Add current element ({val}) to curSum")
            self.wait(0.5)
            
            move_highlight(5)
            old_max = maxSum
            maxSum = max(maxSum, curSum)
            if maxSum > old_max:
                var_max = update_var(var_max, f"maxSum = {maxSum}", RED)
                update_exp(f"New maxSum found! ({maxSum})")
                self.play(squares[idx].animate.set_fill(GREEN, opacity=0.3), run_time=0.3)
            else:
                update_exp(f"{curSum} is not > {maxSum}. maxSum unchanged.")
            self.wait(0.5)
            
            move_highlight(6)
            update_exp("Check if curSum has dropped below 0")
            self.wait(0.4)
            
            if curSum < 0:
                move_highlight(7)
                curSum = 0
                var_cur = update_var(var_cur, f"curSum = 0", GREEN)
                update_exp("curSum < 0. Reset to 0 (discard negative prefix)")
                self.play(squares[idx].animate.set_fill(RED, opacity=0.3), run_time=0.3)
            self.wait(0.5)

        move_highlight(8)
        update_exp(f"Array iteration complete. Return maxSum: {maxSum}")
        self.wait(1.5)

        # ==========================================
        # SCENE 5: Educational Outro (Complexity Breakdown)
        # ==========================================
        self.play(
            FadeOut(h_line), FadeOut(v_line),
            FadeOut(array_group), FadeOut(i_ptr),
            FadeOut(code_title), FadeOut(code_block), FadeOut(highlighter),
            FadeOut(state_title), FadeOut(var_i), FadeOut(var_cur), FadeOut(var_max), FadeOut(exp_text)
        )
        
        tc_title = Text("Time Complexity: ", font_size=40)
        tc_math = MathTex(r"O(N)", font_size=56, color=BLUE)
        complexity_group = VGroup(tc_title, tc_math).arrange(RIGHT, buff=0.3).center()
        
        self.play(Write(complexity_group))
        self.wait(1.5)
        
        self.play(complexity_group.animate.to_edge(UP, buff=1.5))
        
        line1 = Text("• The algorithm iterates through the input array exactly once.", font_size=28)
        line2 = Text("• At each step, it performs constant time O(1) mathematical operations.", font_size=28)
        line3 = Text("• Therefore, execution time scales strictly linearly with the input size N.", font_size=28)
        
        bullets = VGroup(line1, line2, line3).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        
        opt_title = Text("Optimization Status: Highly Optimized", font_size=32, color=GREEN, weight=BOLD)
        opt_desc = Text("It avoids the O(N²) or O(N³) nested loops of brute force approaches.", font_size=24)
        opt_group = VGroup(opt_title, opt_desc).arrange(DOWN, buff=0.2)
        
        outro_content = VGroup(bullets, opt_group).arrange(DOWN, buff=0.8).next_to(complexity_group, DOWN, buff=1.0)
        
        for line in bullets:
            self.play(FadeIn(line, shift=UP))
            self.wait(1)
            
        self.play(Write(opt_group))
        self.wait(3)