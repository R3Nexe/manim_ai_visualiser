from manim import *
"""
TITLE: Moore's Voting Algorithm — Majority Element Selection
CONCEPTS: moore's voting algorithm, majority element, boyer-moore, linear time search, stream processing, frequency cancellation, constant space complexity, array iteration
VISUAL_ELEMENTS: Square, Arrow, Text, SurroundingRectangle, Line, VGroup, Transform, Indicate, ReplacementTransform, MathTex
DIFFICULTY: intermediate
"""
class MooresVotingVisualizer(Scene):
    def construct(self):
        # ==========================================
        # SCENE 1: Educational Intro (Full Screen)
        # ==========================================
        title = Text("Moore's Voting Algorithm", font_size=52, weight=BOLD)
        subtitle = Text("Finding the Majority Element", font_size=36, color=BLUE)
        
        title_group = VGroup(title, subtitle).arrange(DOWN).center()
        self.play(FadeIn(title_group, shift=UP))
        self.wait(1)
        
        self.play(title_group.animate.to_edge(UP, buff=1.0))
        
        prereq = Text("Prerequisite: Basic Arrays", color=YELLOW, font_size=28)
        
        explanation = VGroup(
            Text("Finds the majority element (appears > N/2 times) in linear time.", font_size=24),
            Text("It tracks a candidate and a frequency, canceling out differing elements.", font_size=24)
        ).arrange(DOWN, buff=0.2)
        
        intro_desc = VGroup(prereq, explanation).arrange(DOWN, buff=0.5).next_to(title_group, DOWN, buff=1)
        self.play(FadeIn(intro_desc))
        self.wait(3)
        self.play(FadeOut(title_group), FadeOut(intro_desc))
        self.wait(0.5)

        # ==========================================
        # SCENE 2: UI Grid Generation
        # ==========================================
        h_line = Line(LEFT * 8, RIGHT * 8, color=GRAY, stroke_width=2).move_to(ORIGIN)
        v_line = Line(DOWN * 4, ORIGIN, color=GRAY, stroke_width=2)
        
        self.play(Create(h_line), Create(v_line), run_time=1.5)

        # ==========================================
        # SCENE 3: Populating UI Zones
        # ==========================================
        
        # --- Zone 1 (Top Half - Data) ---
        arr_vals = [2, 2, 1, 1, 2]
        
        array_mobs = VGroup(*[
            VGroup(
                Square(side_length=1.0, color=WHITE, fill_opacity=0.1),
                Text(str(val), font_size=36)
            ) for val in arr_vals
        ]).arrange(RIGHT, buff=0.2).move_to(UP * 2.5)
        
        self.play(FadeIn(array_mobs))
        
        def create_pointer(label_text, color):
            arr_vector = Arrow(start=DOWN * 0.5, end=ORIGIN, color=color, buff=0)
            text_label = Text(label_text, font_size=20, color=color)
            return VGroup(text_label, arr_vector).arrange(UP, buff=0.1)

        ptr_i = create_pointer("i", YELLOW)
        ptr_i.move_to(RIGHT * 10) # Start safely offscreen

        # --- Zone 2 (Bottom Left - Code) ---
        code_lines = [
            "def MooresVotingAlgo(list):",
            "    frequency, answer = 0, 0",
            "    for i in list:",
            "        if frequency == 0:",
            "            answer = i",
            "        if answer == i:",
            "            frequency += 1",
            "        else:",
            "            frequency -= 1",
            "    return answer"
        ]
        
        syntax_colors = {
            "def ": ORANGE, "for ": ORANGE, "in ": ORANGE, 
            "if ": ORANGE, "else:": ORANGE, "return ": ORANGE
        }
        
        lines_group = VGroup(*[
            Text(line, font="Monospace", font_size=20, t2c=syntax_colors)
            for line in code_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        code_bg = SurroundingRectangle(lines_group, color=GRAY, fill_color="#1e1e1e", fill_opacity=1, buff=0.3)
        
        # FIX: Scaled down to 0.65 and explicitly anchored to the left edge to prevent center-line crossing
        code_block = VGroup(code_bg, lines_group).scale(0.65)
        
        # Position title safely below the h_line, then anchor code_block directly below it
        code_title = Text("Code:", font_size=28, weight=BOLD).to_edge(LEFT, buff=0.5).set_y(-0.5)
        code_block.next_to(code_title, DOWN, aligned_edge=LEFT)
        
        self.play(Write(code_title), FadeIn(code_block))
        
        current_highlight = SurroundingRectangle(lines_group[0], color=YELLOW, fill_opacity=0.3, stroke_width=0)
        self.play(FadeIn(current_highlight))

        # --- Zone 3 (Bottom Right - State) ---
        state_title = Text("Execution State:", font_size=28, weight=BOLD)
        state_title.next_to(ORIGIN, RIGHT, buff=0.5).set_y(-0.5)
        
        var_i = Text("i = -", font_size=24, color=YELLOW)
        var_ans = Text("answer = -", font_size=24, color=GREEN)
        var_freq = Text("frequency = -", font_size=24, color=RED)
        
        var_group = VGroup(var_i, var_ans, var_freq).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        var_group.next_to(state_title, DOWN, aligned_edge=LEFT, buff=0.3)
        
        exp_anchor = RIGHT * 0.5 + DOWN * 3.5
        exp_text = Text("Starting execution...", font_size=22, color=BLUE).move_to(exp_anchor, aligned_edge=LEFT)
        
        self.play(Write(state_title), FadeIn(var_group), FadeIn(exp_text))
        
        # --- Helpers ---
        def move_highlight(line_idx):
            new_highlight = SurroundingRectangle(lines_group[line_idx], color=YELLOW, fill_opacity=0.3, stroke_width=0)
            self.play(Transform(current_highlight, new_highlight), run_time=0.4)

        def update_exp(new_text_str):
            new_text = Text(new_text_str, font_size=22, color=BLUE).move_to(exp_anchor, aligned_edge=LEFT)
            self.play(Transform(exp_text, new_text), run_time=0.4)
            
        def update_var(var_mob, new_text_str, color):
            new_var = Text(new_text_str, font_size=24, color=color).move_to(var_mob, aligned_edge=LEFT)
            self.play(ReplacementTransform(var_mob, new_var), run_time=0.4)
            return new_var

        # ==========================================
        # SCENE 4: Executing the Loop
        # ==========================================
        frequency = 0
        answer = 0
        
        move_highlight(1)
        update_exp("Initialize frequency and answer to 0")
        var_freq = update_var(var_freq, f"frequency = {frequency}", RED)
        var_ans = update_var(var_ans, f"answer = {answer}", GREEN)
        self.wait(0.5)
        
        for idx, val in enumerate(arr_vals):
            move_highlight(2)
            update_exp(f"Looping: current element i = {val}")
            var_i = update_var(var_i, f"i = {val}", YELLOW)
            
            if idx == 0:
                ptr_i.next_to(array_mobs[idx], DOWN, buff=0.1)
                self.play(FadeIn(ptr_i))
            else:
                self.play(ptr_i.animate.next_to(array_mobs[idx], DOWN, buff=0.1), run_time=0.5)
            
            self.play(Indicate(array_mobs[idx][0], color=YELLOW), run_time=0.4)
            
            # if frequency == 0:
            move_highlight(3)
            if frequency == 0:
                update_exp("Frequency is 0, updating candidate answer")
                
                move_highlight(4)
                answer = val
                var_ans = update_var(var_ans, f"answer = {answer}", GREEN)
            else:
                update_exp(f"Frequency is {frequency}, skipping candidate update")
                self.wait(0.3)
                
            # if answer == i:
            move_highlight(5)
            if answer == val:
                update_exp(f"Matches candidate ({answer}), increment frequency")
                
                move_highlight(6)
                frequency += 1
                var_freq = update_var(var_freq, f"frequency = {frequency}", RED)
            else:
                update_exp(f"Differs from candidate ({answer}), decrement frequency")
                move_highlight(7)
                self.wait(0.2)
                
                move_highlight(8)
                frequency -= 1
                var_freq = update_var(var_freq, f"frequency = {frequency}", RED)
                
            self.play(array_mobs[idx].animate.set_opacity(0.3), run_time=0.3)

        move_highlight(9)
        update_exp(f"Return final majority candidate: {answer}")
        self.play(Indicate(var_ans, color=GREEN, scale_factor=1.2))
        self.wait(1.5)

        # ==========================================
        # SCENE 5: Educational Outro (Complexity Breakdown)
        # ==========================================
        self.play(
            FadeOut(h_line), FadeOut(v_line), 
            FadeOut(array_mobs), FadeOut(code_title), 
            FadeOut(code_block), FadeOut(current_highlight),
            FadeOut(state_title), FadeOut(var_group), 
            FadeOut(exp_text), FadeOut(ptr_i), 
            FadeOut(var_i), FadeOut(var_ans), FadeOut(var_freq)
        )
        
        tc_title = Text("Time Complexity: ", font_size=40)
        tc_math = MathTex(r"\mathcal{O}(N)", font_size=52, color=BLUE)
        tc_group = VGroup(tc_title, tc_math).arrange(RIGHT).center()
        
        self.play(FadeIn(tc_group))
        self.wait(1)
        self.play(tc_group.animate.to_edge(UP, buff=1.5))
        
        bullet_1 = Text("• Evaluates each element exactly once.", font_size=28)
        bullet_2 = Text("• Maintains only two tracking variables.", font_size=28)
        bullet_3 = Text("• Avoids the extra memory cost of Hash Maps.", font_size=28)
        
        bullets = VGroup(bullet_1, bullet_2, bullet_3).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(tc_group, DOWN, buff=1.0)
        
        for bullet in bullets:
            self.play(Write(bullet), run_time=1.5)
            self.wait(0.5)
            
        status_text = Text("Optimization Status: Highly Optimized", font_size=32, color=GREEN).next_to(bullets, DOWN, buff=1.0)
        status_desc = Text(
            "Achieves optimal O(N) time and O(1) space for finding a majority element.", 
            font_size=24
        ).next_to(status_text, DOWN, buff=0.3)
        
        self.play(FadeIn(status_text), FadeIn(status_desc))
        self.wait(3)