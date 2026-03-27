from manim import *
"""
TITLE: Bubble Sort — Adjacent Swap with Comparison Counter
CONCEPTS: bubble sort, brute-force, adjacent comparison, element swapping, nested loops, outer pass, inner pass, quadratic time complexity
VISUAL_ELEMENTS: Square, Text, Arrow, Line, SurroundingRectangle, VGroup, Transform, Indicate, ReplacementTransform, MathTex
DIFFICULTY: beginner
DESCRIPTION: Manim animation for Bubble Sort. Uses the strict 5-scene split-screen UI with a 1D array to visualize adjacent element comparisons, swapping operations, and nested loop variable tracking for O(N^2) brute-force sorting.
"""
class BubbleSortVisualizer(Scene):
    def construct(self):
        # ==========================================
        # SCENE 1: Educational Intro
        # ==========================================
        title = Text("Bubble Sort", font_size=52, weight=BOLD)
        subtitle = Text("A Brute-Force Sorting Algorithm", font_size=36, color=BLUE)
        
        title_group = VGroup(title, subtitle).arrange(DOWN).center()
        self.play(FadeIn(title_group, shift=UP))
        self.wait(1)
        
        self.play(title_group.animate.to_edge(UP, buff=1.0))
        
        prereq = Text("Prerequisite: Basic Arrays", color=YELLOW, font_size=28)
        
        explanation = VGroup(
            Text("Repeatedly steps through the list, compares adjacent elements,", font_size=24),
            Text("and swaps them if they are in the wrong order.", font_size=24)
        ).arrange(DOWN, buff=0.2)
        
        intro_desc = VGroup(prereq, explanation).arrange(DOWN, buff=0.5).next_to(title_group, DOWN, buff=1)
        self.play(FadeIn(intro_desc))
        self.wait(3)
        self.play(FadeOut(title_group), FadeOut(intro_desc))
        self.wait(0.5)

        # ==========================================
        # SCENE 2: UI Grid Generation
        # ==========================================
        # Horizontal line at y=0, Vertical line at x=0 (bottom half only)
        h_line = Line(LEFT * 8, RIGHT * 8, color=GRAY, stroke_width=2).move_to(ORIGIN)
        v_line = Line(DOWN * 4, ORIGIN, color=GRAY, stroke_width=2)
        
        self.play(Create(h_line), Create(v_line), run_time=1.5)

        # ==========================================
        # SCENE 3: Populating UI Zones
        # ==========================================
        
        # --- Zone 1 (Top Half): Data Structure ---
        arr = [5, 2, 8, 1]
        n = len(arr)
        
        # Anchored significantly higher to ensure pointers never touch the midline
        array_mobs = VGroup(*[
            VGroup(
                Square(side_length=1.0, color=WHITE, fill_opacity=0.1),
                Text(str(val), font_size=36)
            ) for val in arr
        ]).arrange(RIGHT, buff=0.2).move_to(UP * 2.5)
        
        self.play(FadeIn(array_mobs))
        
        # Redesigned pointers: Arrows point UP towards the boxes, text is below.
        # This keeps them compact and strictly above the h_line.
        def create_pointer(label, color):
            arr_vector = Arrow(start=DOWN * 0.5, end=ORIGIN, color=color, buff=0)
            text_label = Text(label, font_size=20, color=color)
            return VGroup(text_label, arr_vector).arrange(UP, buff=0.1)

        curr_ptr = create_pointer("curr", YELLOW)
        next_ptr = create_pointer("next", BLUE)
        
        # Place pointers safely offscreen initially
        curr_ptr.move_to(RIGHT * 10)
        next_ptr.move_to(RIGHT * 10)

        # --- Zone 2 (Bottom Left): Custom Bulletproof Code Block ---
        code_lines = [
            "def BubbleSort(list):",
            "    n=len(list)",
            "    for i in range(0,n):",
            "        for currElement in range(0,n-i-1):",
            "            nextElement=currElement+1",
            "            if(list[currElement]>list[nextElement]):",
            "                temp=list[currElement]",
            "                list[currElement]=list[nextElement]",
            "                list[nextElement]=temp"
        ]
        
        syntax_colors = {
            "def": ORANGE, "for": ORANGE, "in": ORANGE, 
            "range": BLUE, "len": BLUE, "if": ORANGE
        }
        
        lines_group = VGroup(*[
            Text(line, font="Monospace", font_size=20, t2c=syntax_colors)
            for line in code_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        
        code_bg = SurroundingRectangle(lines_group, color=GRAY, fill_color="#1e1e1e", fill_opacity=1, buff=0.3)
        code_block = VGroup(code_bg, lines_group).scale(0.8)
        
        code_title = Text("Code:", font_size=28, weight=BOLD).move_to(LEFT * 5.5 + DOWN * 0.5)
        code_block.next_to(code_title, DOWN, aligned_edge=LEFT)
        
        self.play(Write(code_title), FadeIn(code_block))
        
        # Highlight State Tracker 
        current_highlight = SurroundingRectangle(lines_group[0], color=YELLOW, fill_opacity=0.3, stroke_width=0)
        self.play(FadeIn(current_highlight))

        # --- Zone 3 (Bottom Right): Execution State ---
        # Fixed alignment: Shifted significantly to the right to avoid vertical line overlap
        state_title = Text("Execution State:", font_size=28, weight=BOLD)
        state_title.next_to(ORIGIN, RIGHT, buff=0.5).set_y(-0.5) # Strictly left-bound at x=0.5
        
        var_i = Text("i = -", font_size=24, color=RED)
        var_curr = Text("currElement = -", font_size=24, color=YELLOW)
        var_next = Text("nextElement = -", font_size=24, color=BLUE)
        var_temp = Text("temp = -", font_size=24, color=PURPLE)
        
        var_group = VGroup(var_i, var_curr, var_next, var_temp).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        var_group.next_to(state_title, DOWN, aligned_edge=LEFT, buff=0.3)
        
        # Fixed alignment for dynamic text to guarantee no left-side bleed
        exp_anchor = RIGHT * 0.5 + DOWN * 3.5
        exp_text = Text("Starting execution...", font_size=22, color=GREEN).move_to(exp_anchor, aligned_edge=LEFT)
        
        self.play(Write(state_title), FadeIn(var_group), FadeIn(exp_text))
        
        # Helpers
        def move_highlight(line_idx):
            new_highlight = SurroundingRectangle(lines_group[line_idx], color=YELLOW, fill_opacity=0.3, stroke_width=0)
            self.play(Transform(current_highlight, new_highlight), run_time=0.4)

        def update_exp(new_text_str):
            new_text = Text(new_text_str, font_size=22, color=GREEN).move_to(exp_anchor, aligned_edge=LEFT)
            self.play(Transform(exp_text, new_text), run_time=0.4)
            
        def update_var(var_mob, new_text_str, color):
            # Maintains precise left-alignment upon text change
            new_var = Text(new_text_str, font_size=24, color=color).move_to(var_mob, aligned_edge=LEFT)
            self.play(ReplacementTransform(var_mob, new_var), run_time=0.4)
            return new_var

        # ==========================================
        # SCENE 4: Executing the Loop
        # ==========================================
        
        move_highlight(1)
        update_exp(f"Length of list calculated: n = {n}")
        
        for i in range(n):
            move_highlight(2)
            var_i = update_var(var_i, f"i = {i}", RED)
            update_exp(f"Outer loop pass {i + 1}")
            
            # Optimization skip for animation brevity
            if i == 3:
                update_exp("Array is completely sorted!")
                self.play(array_mobs[0][0].animate.set_fill(GREEN, opacity=0.3), run_time=0.5)
                break

            for curr in range(n - i - 1):
                move_highlight(3)
                var_curr = update_var(var_curr, f"currElement = {curr}", YELLOW)
                update_exp(f"Inner loop checking index {curr}")
                
                nxt = curr + 1
                move_highlight(4)
                var_next = update_var(var_next, f"nextElement = {nxt}", BLUE)
                
                # Move Pointers safely below the boxes
                if curr == 0 and i == 0:
                    curr_ptr.next_to(array_mobs[curr], DOWN, buff=0.1)
                    next_ptr.next_to(array_mobs[nxt], DOWN, buff=0.1)
                    self.play(FadeIn(curr_ptr), FadeIn(next_ptr))
                else:
                    self.play(
                        curr_ptr.animate.next_to(array_mobs[curr], DOWN, buff=0.1),
                        next_ptr.animate.next_to(array_mobs[nxt], DOWN, buff=0.1),
                        run_time=0.5
                    )
                
                move_highlight(5)
                update_exp(f"Compare: is {arr[curr]} > {arr[nxt]}?")
                self.play(Indicate(array_mobs[curr][0], color=YELLOW), Indicate(array_mobs[nxt][0], color=BLUE), run_time=0.5)
                
                if arr[curr] > arr[nxt]:
                    move_highlight(6)
                    var_temp = update_var(var_temp, f"temp = {arr[curr]}", PURPLE)
                    update_exp(f"Store {arr[curr]} in temp")
                    
                    move_highlight(7)
                    update_exp(f"Copy {arr[nxt]} to currElement index")
                    
                    move_highlight(8)
                    update_exp(f"Copy temp to nextElement index")
                    
                    self.play(Swap(array_mobs[curr], array_mobs[nxt]), run_time=0.8)
                    
                    # Update underlying arrays
                    arr[curr], arr[nxt] = arr[nxt], arr[curr]
                    array_mobs[curr], array_mobs[nxt] = array_mobs[nxt], array_mobs[curr]
                else:
                    update_exp(f"No swap needed: {arr[curr]} <= {arr[nxt]}")
                    self.wait(0.5)
                    
            # Mark finalized element
            sorted_idx = n - i - 1
            self.play(array_mobs[sorted_idx][0].animate.set_fill(GREEN, opacity=0.3), run_time=0.5)
            
        self.play(FadeOut(curr_ptr), FadeOut(next_ptr))
        self.wait(1)

        # ==========================================
        # SCENE 5: Educational Outro 
        # ==========================================
        
        self.play(
            FadeOut(h_line), FadeOut(v_line), 
            FadeOut(array_mobs), FadeOut(code_title), 
            FadeOut(code_block), FadeOut(current_highlight),
            FadeOut(state_title), FadeOut(var_group), 
            FadeOut(exp_text), FadeOut(var_i), FadeOut(var_curr), FadeOut(var_next), FadeOut(var_temp)
        )
        
        tc_title = Text("Time Complexity: ", font_size=40)
        tc_math = MathTex(r"\mathcal{O}(N^2)", font_size=52, color=BLUE)
        tc_group = VGroup(tc_title, tc_math).arrange(RIGHT).center()
        
        self.play(FadeIn(tc_group))
        self.wait(1)
        self.play(tc_group.animate.to_edge(UP, buff=1.5))
        
        bullet_1 = Text("• Outer loop executes N times to ensure complete passes.", font_size=28)
        bullet_2 = Text("• Inner loop checks up to N-1 adjacent pairs per pass.", font_size=28)
        bullet_3 = Text("• Total comparisons scale quadratically (N × N).", font_size=28)
        
        bullets = VGroup(bullet_1, bullet_2, bullet_3).arrange(DOWN, aligned_edge=LEFT, buff=0.4).next_to(tc_group, DOWN, buff=1.0)
        
        for bullet in bullets:
            self.play(Write(bullet), run_time=1.5)
            self.wait(0.5)
            
        status_text = Text("Optimization Status: Brute Force", font_size=32, color=RED).next_to(bullets, DOWN, buff=1.0)
        status_desc = Text(
            "Bubble Sort is generally inefficient and rarely used in production for large datasets.", 
            font_size=24
        ).next_to(status_text, DOWN, buff=0.3)
        
        self.play(FadeIn(status_text), FadeIn(status_desc))
        self.wait(3)