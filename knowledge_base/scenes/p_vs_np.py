from manim import *


class PVP_NP_Complexity(Scene):
    def construct(self):
        # --- INTRO SCENE ---
        title = Text("P vs NP Paradigm", font_size=52, weight=BOLD)
        subtitle = Text("Complexity Class Hierarchy", font_size=32, color=BLUE)
        intro_grp = VGroup(title, subtitle).arrange(DOWN, buff=0.5).center()

        self.play(Write(title), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP * 0.2))
        self.wait(1.5)
        self.play(FadeOut(intro_grp))

        # --- PERSISTENT LABELS ---
        vis_label = (
            Text("Euler Diagram", font_size=20, color=GRAY)
            .move_to([-6.8, 3.7, 0])
            .align_to([-6.8, 0, 0], LEFT)
        )
        code_label = (
            Text("Definitions", font_size=20, color=GRAY)
            .move_to([0.25, 3.7, 0])
            .align_to([0.25, 0, 0], LEFT)
        )
        var_label = (
            Text("The Big Question", font_size=20, color=GRAY)
            .move_to([0.25, -0.4, 0])
            .align_to([0.25, 0, 0], LEFT)
        )
        self.add(vis_label, code_label, var_label)

        # --- LEFT ZONE: SET VISUALIZATION ---
        # Base center for the sets
        set_center = [-3.5, -0.5, 0]

        # Define the circles (Sets)
        # P is the smallest, NP contains P, NP-Hard is outside but intersects at NP-Complete
        p_set = Circle(radius=1.0, color=BLUE, fill_opacity=0.2).move_to(set_center)
        p_label = Text("P", font_size=24, color=BLUE).move_to(
            p_set.get_bottom() + UP * 0.4
        )

        np_set = Circle(radius=2.0, color=GREEN, fill_opacity=0.1).move_to(set_center)
        np_label = Text("NP", font_size=24, color=GREEN).move_to(
            np_set.get_top() + DOWN * 0.4
        )

        # NP-Hard is represented as the upper region
        nph_set = Circle(radius=2.2, color=RED, fill_opacity=0.1).move_to(
            set_center + UP * 1.5
        )
        nph_label = Text("NP-Hard", font_size=24, color=RED).move_to(
            nph_set.get_top() + UP * 0.3
        )

        # NP-Complete is the intersection
        npc_label = Text("NP-Complete", font_size=20, color=YELLOW).move_to(
            set_center + UP * 1.3
        )

        # --- RIGHT-TOP: DEFINITIONS PANEL ---
        defs = [
            "P: Solvable in Polynomial time",
            "NP: Verifiable in Polynomial time",
            "NP-Hard: At least as hard as any NP",
            "NP-Complete: Both NP and NP-Hard",
            "If P = NP, all NP are P",
        ]
        def_lines = VGroup()
        for i, line in enumerate(defs):
            t = Text(line, font_size=18)
            if i == 0:
                t.move_to([0.5, 3.2, 0]).align_to([0.5, 0, 0], LEFT)
            else:
                t.next_to(def_lines[-1], DOWN, buff=0.4, aligned_edge=LEFT)
            def_lines.add(t)
        self.add(def_lines)

        hi = Rectangle(
            width=6.0, height=0.35, fill_color=YELLOW, fill_opacity=0.22, stroke_width=0
        )
        hi.move_to(def_lines[0].get_center()).align_to(def_lines, LEFT).shift(
            LEFT * 0.1
        )

        # --- RIGHT-BOTTOM: STATUS TABLE ---
        hdr_n = Text("Assumption", font_size=18, color=GRAY).move_to([1.2, -0.9, 0])
        hdr_v = Text("State", font_size=18, color=GRAY).move_to([4.5, -0.9, 0])
        self.add(hdr_n, hdr_v)

        v_p_np_n = (
            Text("P ≠ NP", font_size=18)
            .next_to(hdr_n, DOWN, buff=0.4)
            .align_to(hdr_n, LEFT)
        )
        v_p_np_v = Text("Most Likely", font_size=18, color=YELLOW).move_to(
            [4.5, v_p_np_n.get_y(), 0]
        )

        v_reward_n = (
            Text("Millennium Prize", font_size=18)
            .next_to(v_p_np_n, DOWN, buff=0.4)
            .align_to(hdr_n, LEFT)
        )
        v_reward_v = Text("$1,000,000", font_size=18, color=GREEN).move_to(
            [4.5, v_reward_n.get_y(), 0]
        )

        self.add(v_p_np_n, v_p_np_v, v_reward_n, v_reward_v)

        # --- ANIMATION SEQUENCE ---

        # 1. Introduce P
        self.play(Create(p_set), Write(p_label))
        self.play(Indicate(def_lines[0]))
        self.wait(1)

        # 2. Introduce NP
        self.play(
            hi.animate.move_to(def_lines[1].get_center())
            .align_to(def_lines, LEFT)
            .shift(LEFT * 0.1)
        )
        self.play(Create(np_set), Write(np_label))
        self.wait(1)

        # 3. Introduce NP-Hard
        self.play(
            hi.animate.move_to(def_lines[2].get_center())
            .align_to(def_lines, LEFT)
            .shift(LEFT * 0.1)
        )
        self.play(Create(nph_set), Write(nph_label))
        self.wait(1)

        # 4. Highlight NP-Complete (The Intersection)
        self.play(
            hi.animate.move_to(def_lines[3].get_center())
            .align_to(def_lines, LEFT)
            .shift(LEFT * 0.1)
        )
        # Visualizing the intersection area
        npc_intersect = Intersection(np_set, nph_set, color=YELLOW, fill_opacity=0.5)
        self.play(FadeIn(npc_intersect), Write(npc_label))
        self.wait(2)

        # 5. The "P = NP" Scenario
        self.play(
            hi.animate.move_to(def_lines[4].get_center())
            .align_to(def_lines, LEFT)
            .shift(LEFT * 0.1)
        )
        self.play(
            v_p_np_v.animate.set_text("UNKNOWN").set_color(RED),
            p_set.animate.scale(2.0).set_color(GREEN),  # Expand P to match NP
            p_label.animate.move_to(set_center + DOWN * 0.8),
        )
        self.wait(2)

        # --- OUTRO ---
        self.play(FadeOut(Group(*self.mobjects)))
        final_text = Text("Is P = NP?", font_size=48).center()
        self.play(Write(final_text))
        self.play(final_text.animate.set_color(YELLOW))
        self.wait(2)
