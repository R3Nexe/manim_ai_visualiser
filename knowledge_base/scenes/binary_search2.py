from manim import *

class UIBinarySearch(Scene):
    def construct(self):
        # ==========================================
        # SCENE 1: INTRO SEQUENCE (Full Screen)
        # [TEMPLATE NOTE]: Always center the title first, then shift it UP. 
        # This prevents text from clipping off the screen on 16:9 1080p renders.
        # ==========================================
        title = Text("Binary Search", font_size=52, weight=BOLD)
        subtitle = Text("A Divide & Conquer Algorithm", font_size=36, color=BLUE).next_to(title, DOWN)
        intro_group = VGroup(title, subtitle).center() 
        
        self.play(Write(title))
        self.play(FadeIn(subtitle, shift=UP))
        self.wait(1)
        
        # Shift up to make room for prerequisites and explanations
        self.play(intro_group.animate.to_edge(UP, buff=1.0))
        
        prereq = Text("Prerequisite: The array MUST be sorted.", font_size=32, color=YELLOW).next_to(intro_group, DOWN, buff=1.0)
        why_text = Text(
            "Why 'Divide & Conquer'?\nBecause it repeatedly halves the search space.", 
            font_size=32, line_spacing=1.5
        ).next_to(prereq, DOWN, buff=0.8)
        
        self.play(Write(prereq))
        self.play(FadeIn(why_text, shift=UP))
        self.wait(2)
        
        # [CRITICAL]: Always completely clear the screen before drawing the UI Grid.
        self.play(FadeOut(intro_group), FadeOut(prereq), FadeOut(why_text))

        # ==========================================
        # SCENE 2: DRAWING THE UI GRID
        # [TEMPLATE NOTE]: The screen is split into strict zones. 
        # Elements must NEVER cross these boundary lines.
        # ==========================================
        # Horizontal line (Y = 0) splits Top (Visuals) and Bottom (Code/Data)
        h_line = Line(LEFT * 8, RIGHT * 8, color=GRAY, stroke_width=2).move_to(ORIGIN)
        # Vertical line (X = 0, from Y=0 downwards) splits Bottom Left and Bottom Right
        v_line = Line(DOWN * 4, ORIGIN, color=GRAY, stroke_width=2)
        
        self.play(Create(h_line), Create(v_line))

        # ==========================================
        # SCENE 3: POPULATING UI ZONES
        # ==========================================
        
        # --- ZONE 1: TOP HALF (Visualization) ---
        # [TEMPLATE NOTE]: Always anchor the main data structure to UP * 2 to keep it perfectly centered in the top half.
        data = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
        target_val = 23
        
        squares = VGroup(*[Square(side_length=0.7) for _ in data]).arrange(RIGHT, buff=0.1)
        labels = VGroup(*[Text(str(x), font_size=20).move_to(squares[i]) for i, x in enumerate(data)])
        array_group = VGroup(squares, labels).move_to(UP * 2) 
        
        target_box = VGroup(
            Text(f"Target: {target_val}", font_size=24, color=GREEN)
        ).to_corner(UL).shift(DOWN * 0.2)
        
        self.play(Create(squares), Write(labels), FadeIn(target_box))

        # --- ZONE 2: BOTTOM LEFT (Code Box) ---
        code_str = """def search(arr, target):
    low, high = 0, len(arr)-1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1"""
        
        # [CRITICAL]: Title anchored safely below the mid-line (DOWN * 0.5)
        code_title = Text("Code:", font_size=20, weight=BOLD).move_to(LEFT * 5.5 + DOWN * 0.5)
        
        # [TEMPLATE NOTE]: Scale code block to 0.60 to ensure it fits the zone without overlapping.
        code_block = Code(
            code_string=code_str, tab_width=4, background="window",
            language="python", formatter_style="monokai",
            add_line_numbers=False
        ).scale(0.60).next_to(code_title, DOWN, buff=0.2).align_to(code_title, LEFT)
        
        self.play(Write(code_title), FadeIn(code_block))

        # Highlighter box starting on line 0 (Note: use code_lines, not code)
        highlighter = SurroundingRectangle(code_block.code_lines[0], color=YELLOW, fill_opacity=0.3, stroke_width=0)
        self.play(FadeIn(highlighter))

        # --- ZONE 3: BOTTOM RIGHT (State Panel) ---
        panel_title = Text("Execution State:", font_size=20, weight=BOLD).move_to(RIGHT * 1.5 + DOWN * 0.5)
        
        # Algorithm-specific variables go here
        var_low = Text("low = ?", font_size=18, color=RED)
        var_high = Text("high = ?", font_size=18, color=BLUE)
        var_mid = Text("mid = ?", font_size=18, color=YELLOW)
        
        vars_group = VGroup(var_low, var_high, var_mid).arrange(DOWN, aligned_edge=LEFT).next_to(panel_title, DOWN, buff=0.4).align_to(panel_title, LEFT)
        
        exp_text = Text("Initializing function...", font_size=18).next_to(vars_group, DOWN, buff=0.6).align_to(vars_group, LEFT)
        
        self.play(Write(panel_title), FadeIn(vars_group), Write(exp_text))
        self.wait(1)

        # --- REUSABLE UI HELPERS ---
        # [TEMPLATE NOTE]: These helpers must be used to ensure UI updates are smooth and don't break layout.
        def update_exp(new_text):
            # Keeps the explanation text perfectly aligned when the string length changes
            new_exp = Text(new_text, font_size=18).move_to(exp_text.get_center()).align_to(exp_text, LEFT)
            self.play(ReplacementTransform(exp_text, new_exp), run_time=0.5)
            return new_exp

        def move_highlight(line_num):
            # Safely moves the yellow background over the specific line of code
            self.play(highlighter.animate.move_to(code_block.code_lines[line_num]), run_time=0.5)

        def get_up_pointer(index, text, color):
            # Mathematically bounds the arrow so it never crosses the middle h_line
            start_pos = squares[index].get_bottom() + DOWN * 0.8
            end_pos = squares[index].get_bottom() + DOWN * 0.1
            arrow = Arrow(start=start_pos, end=end_pos, color=color, buff=0, max_tip_length_to_length_ratio=0.15)
            lbl = Text(text, font_size=16, color=color).next_to(arrow, DOWN, buff=0.1)
            return VGroup(arrow, lbl)

        def get_down_pointer(index, text, color):
            start_pos = squares[index].get_top() + UP * 0.8
            end_pos = squares[index].get_top() + UP * 0.1
            arrow = Arrow(start=start_pos, end=end_pos, color=color, buff=0, max_tip_length_to_length_ratio=0.15)
            lbl = Text(text, font_size=16, color=color).next_to(arrow, UP, buff=0.1)
            return VGroup(arrow, lbl)

        # ==========================================
        # SCENE 4: EXECUTING THE ALGORITHM LOOP
        # [TEMPLATE NOTE]: Every major logical step must:
        # 1. move_highlight() to the correct code line.
        # 2. update_exp() to explain the math/logic.
        # 3. Update the visual UI array.
        # ==========================================
        
        move_highlight(1)
        low, high = 0, len(data) - 1
        
        # Initializing the dynamic variable text
        new_var_low = Text(f"low = {low}", font_size=18, color=RED).move_to(var_low).align_to(var_low, LEFT)
        new_var_high = Text(f"high = {high}", font_size=18, color=BLUE).move_to(var_high).align_to(var_high, LEFT)
        exp_text = update_exp("Setting boundary pointers.")
        
        low_group = get_up_pointer(low, "low", RED)
        high_group = get_up_pointer(high, "high", BLUE)
        
        self.play(
            ReplacementTransform(var_low, new_var_low),
            ReplacementTransform(var_high, new_var_high),
            Create(low_group), Create(high_group)
        )
        var_low, var_high = new_var_low, new_var_high # Sync variable references
        self.wait(1)

        mid_group = None
        
        while low <= high:
            move_highlight(2)
            exp_text = update_exp(f"Condition: {low} <= {high} is True.")
            self.wait(0.5)
            
            move_highlight(3)
            mid = (low + high) // 2
            
            new_var_mid = Text(f"mid = {mid}", font_size=18, color=YELLOW).move_to(var_mid).align_to(var_mid, LEFT)
            exp_text = update_exp(f"mid = ({low} + {high}) // 2 = {mid}")
            
            mid_group = get_down_pointer(mid, "mid", YELLOW)
            self.play(ReplacementTransform(var_mid, new_var_mid), Create(mid_group))
            var_mid = new_var_mid
            self.wait(1)
            
            move_highlight(4)
            exp_text = update_exp(f"Check: arr[{mid}] == {target_val} ?")
            self.wait(0.5)
            
            if data[mid] == target_val:
                move_highlight(5)
                exp_text = update_exp("Target Found! Returning index.")
                self.play(squares[mid].animate.set_fill(GREEN, opacity=0.5))
                self.wait(2)
                break
                
            elif data[mid] < target_val:
                move_highlight(6)
                exp_text = update_exp(f"{data[mid]} < {target_val}. Ignoring left half.")
                self.play(Indicate(squares[mid], color=RED))
                
                move_highlight(7)
                old_low = low
                low = mid + 1
                
                new_var_low = Text(f"low = {low}", font_size=18, color=RED).move_to(var_low).align_to(var_low, LEFT)
                new_low_group = get_up_pointer(low, "low", RED)
                
                # Dimming elements keeps focus on the active search space
                discarded = VGroup(*[squares[i] for i in range(old_low, low)])
                discarded_labels = VGroup(*[labels[i] for i in range(old_low, low)])
                
                self.play(
                    ReplacementTransform(var_low, new_var_low),
                    ReplacementTransform(low_group, new_low_group),
                    discarded.animate.set_opacity(0.2),
                    discarded_labels.animate.set_opacity(0.2),
                    FadeOut(mid_group)
                )
                low_group, var_low = new_low_group, new_var_low
                
            else:
                move_highlight(8)
                move_highlight(9)
                exp_text = update_exp(f"{data[mid]} > {target_val}. Ignoring right half.")
                self.play(Indicate(squares[mid], color=RED))
                
                old_high = high
                high = mid - 1
                
                new_var_high = Text(f"high = {high}", font_size=18, color=BLUE).move_to(var_high).align_to(var_high, LEFT)
                new_high_group = get_up_pointer(high, "high", BLUE)
                
                discarded = VGroup(*[squares[i] for i in range(high + 1, old_high + 1)])
                discarded_labels = VGroup(*[labels[i] for i in range(high + 1, old_high + 1)])
                
                self.play(
                    ReplacementTransform(var_high, new_var_high),
                    ReplacementTransform(high_group, new_high_group),
                    discarded.animate.set_opacity(0.2),
                    discarded_labels.animate.set_opacity(0.2),
                    FadeOut(mid_group)
                )
                high_group, var_high = new_high_group, new_var_high

        # ==========================================
        # SCENE 5: EDUCATIONAL OUTRO (Complexity Breakdown)
        # [TEMPLATE NOTE]: Always wipe the ENTIRE grid and all UI elements before this scene.
        # ==========================================
        self.play(
            FadeOut(h_line), FadeOut(v_line),
            FadeOut(code_block), FadeOut(code_title), FadeOut(highlighter),
            FadeOut(var_low), FadeOut(var_high), FadeOut(var_mid), 
            FadeOut(panel_title), FadeOut(exp_text),
            FadeOut(low_group), FadeOut(high_group), FadeOut(target_box),
            FadeOut(squares), FadeOut(labels)
        )
        if mid_group:
            self.play(FadeOut(mid_group))
            
        # 1. Show Main Complexity Text in the center
        complexity_group = VGroup(
            Text("Time Complexity: ", font_size=40),
            MathTex(r"O(\log n)", font_size=56, color=BLUE)
        ).arrange(RIGHT, buff=0.3).center()
        
        self.play(Write(complexity_group))
        self.wait(1.5)
        
        # 2. Shift up to make room for bullet points
        self.play(complexity_group.animate.to_edge(UP, buff=1.5))
        
        # 3. Line-by-line explanation of the math
        line1 = Text("• Each comparison halves the remaining search space.", font_size=28)
        line2 = Text("• Maximum steps equal the number of times N can be divided by 2.", font_size=28)
        line3 = Text("• Mathematically, this yields a logarithmic curve.", font_size=28)
        
        bullets = VGroup(line1, line2, line3).arrange(DOWN, aligned_edge=LEFT, buff=0.4)
        
        # Final Optimization Status
        opt_title = Text("Status: Highly Optimized", font_size=32, color=GREEN, weight=BOLD)
        opt_desc = Text("It is the most efficient algorithm possible for searching sorted arrays.", font_size=28)
        opt_group = VGroup(opt_title, opt_desc).arrange(DOWN, buff=0.2)
        
        # Layout Grouping
        outro_content = VGroup(bullets, opt_group).arrange(DOWN, buff=0.8).next_to(complexity_group, DOWN, buff=1.0)
        
        # Animate sequentially
        for line in bullets:
            self.play(FadeIn(line, shift=UP))
            self.wait(1)
            
        self.play(Write(opt_group))
        self.wait(3)