from manim import *

"""
TITLE: Fibonacci Sequence — Dynamic Programming with Memoization
CONCEPTS: fibonacci sequence, memoization, dynamic programming, recursion tree, top-down approach, redundancy, time-space tradeoff, pruning, complexity reduction
VISUAL_ELEMENTS: Circle, Line, Text, Square, Group, Arrow, Cross, FadeIn, Create, Transform, Indicate, set_fill
DIFFICULTY: intermediate
"""

class FibonacciCleanLayout(Scene):
    def construct(self):
        # --- 1. TITLE ZONE (TOP CENTER) ---
        title = Text("Fibonacci with Memoization", font_size=36, color=BLUE)
        subtitle = Text("F(n) = F(n-1) + F(n-2)", font_size=20, color=GRAY)
        header = Group(title, subtitle).arrange(DOWN, buff=0.1).to_edge(UP, buff=0.2)

        self.play(FadeIn(header))

        # --- 2. EXPLANATION ZONE (BOTTOM CENTER) ---
        action_text = Text(
            "Building Naive Execution Tree for F(4)...", font_size=20, color=WHITE
        ).to_edge(DOWN, buff=0.3)
        self.play(FadeIn(action_text))

        # --- 3. THE TREE ZONE (CENTER) ---
        # Carefully spaced coordinates to prevent ANY overlap
        # X-spread is wide, Y-spread leaves room for top/bottom UI
        pos = {
            "F4": [0, 1.2, 0],
            "F3": [-3, 0.0, 0],
            "F2_R": [3, 0.0, 0],
            "F2_L": [-4.5, -1.2, 0],
            "F1_R1": [-1.5, -1.2, 0],
            "F1_R2": [1.5, -1.2, 0],
            "F0_R": [4.5, -1.2, 0],
            "F1_L": [-5.5, -2.4, 0],
            "F0_L": [-3.5, -2.4, 0],
        }

        # Helper function for pretty nodes
        def make_node(label_str, p, border_color=WHITE):
            circ = Circle(
                radius=0.35,
                color=border_color,
                fill_color=BLACK,
                fill_opacity=1,
                stroke_width=2,
            )
            lbl = Text(label_str, font_size=16).move_to(circ)
            return Group(circ, lbl).move_to(p)

        # Generate Node Dictionary
        nodes = {}
        for key, p in pos.items():
            # Format "F2_L" -> "F(2)"
            clean_label = key.split("_")[0].replace("F", "F(") + ")"
            nodes[key] = make_node(clean_label, p)

        # Explicitly define edges to match the nodes
        edges = (
            VGroup(
                Line(nodes["F4"][0].get_bottom(), nodes["F3"][0].get_top()),
                Line(nodes["F4"][0].get_bottom(), nodes["F2_R"][0].get_top()),
                Line(nodes["F3"][0].get_bottom(), nodes["F2_L"][0].get_top()),
                Line(nodes["F3"][0].get_bottom(), nodes["F1_R1"][0].get_top()),
                Line(nodes["F2_L"][0].get_bottom(), nodes["F1_L"][0].get_top()),
                Line(nodes["F2_L"][0].get_bottom(), nodes["F0_L"][0].get_top()),
                Line(nodes["F2_R"][0].get_bottom(), nodes["F1_R2"][0].get_top()),
                Line(nodes["F2_R"][0].get_bottom(), nodes["F0_R"][0].get_top()),
            )
            .set_color(GRAY)
            .set_stroke(width=2)
        )

        # Animate Tree Creation
        self.play(FadeIn(nodes["F4"]))
        self.play(
            Create(edges),
            FadeIn(Group(*[nodes[k] for k in nodes if k != "F4"])),
            run_time=2,
        )
        self.wait(1)

        # Highlight Redundant Work
        self.play(
            Transform(
                action_text,
                Text(
                    "Naive Approach: Notice how F(2) is calculated twice!",
                    font_size=20,
                    color=RED,
                ).to_edge(DOWN, buff=0.3),
            )
        )

        self.play(
            nodes["F2_L"][0].animate.set_color(RED).set_stroke(width=4),
            nodes["F2_R"][0].animate.set_color(RED).set_stroke(width=4),
            run_time=1,
        )
        self.play(
            Indicate(nodes["F2_L"], color=RED), Indicate(nodes["F2_R"], color=RED)
        )
        self.wait(1.5)

        # Reset Tree Colors
        self.play(
            nodes["F2_L"][0].animate.set_color(WHITE).set_stroke(width=2),
            nodes["F2_R"][0].animate.set_color(WHITE).set_stroke(width=2),
        )

        # --- 4. THE CACHE ZONE (TOP RIGHT) ---
        self.play(
            Transform(
                action_text,
                Text(
                    "Introducing Memoization Cache...", font_size=20, color=YELLOW
                ).to_edge(DOWN, buff=0.3),
            )
        )

        cache_boxes = (
            Group(*[Square(side_length=0.45) for _ in range(5)])
            .arrange(RIGHT, buff=0)
            .to_corner(UR, buff=0.5)
            .shift(DOWN * 0.5)
        )
        cache_label = Text("Cache", font_size=18, color=YELLOW).next_to(
            cache_boxes, LEFT, buff=0.2
        )
        cache_indices = Group(
            *[
                Text(str(i), font_size=14, color=GRAY).next_to(
                    cache_boxes[i], UP, buff=0.1
                )
                for i in range(5)
            ]
        )
        cache_vals = Group(
            *[Text("?", font_size=16).move_to(cache_boxes[i]) for i in range(5)]
        )

        cache_group = Group(cache_label, cache_boxes, cache_indices, cache_vals)
        self.play(FadeIn(cache_group))

        # --- 5. EXECUTION TRACE & PRUNING ---
        self.play(
            Transform(
                action_text,
                Text(
                    "Tracing Execution: Storing answers as we find them.",
                    font_size=20,
                    color=GREEN,
                ).to_edge(DOWN, buff=0.3),
            )
        )

        # Compute Left side
        for n_key, val, idx in [("F1_L", "1", 1), ("F0_L", "0", 0), ("F2_L", "1", 2)]:
            self.play(Indicate(nodes[n_key], color=GREEN), run_time=0.6)
            new_val = Text(val, font_size=18, color=GREEN).move_to(cache_boxes[idx])
            self.play(
                Transform(cache_vals[idx], new_val),
                nodes[n_key][0].animate.set_color(GREEN).set_fill(GREEN, opacity=0.2),
                run_time=0.6,
            )

        # The Cache Hit
        self.play(
            Transform(
                action_text,
                Text(
                    "Wait! F(2) is already in the cache! (Cache Hit)",
                    font_size=20,
                    color=YELLOW,
                ).to_edge(DOWN, buff=0.3),
            )
        )
        self.play(Indicate(nodes["F2_R"], color=YELLOW))

        hit_arrow = Arrow(
            cache_boxes[2].get_bottom(), nodes["F2_R"].get_top(), color=YELLOW, buff=0.1
        )
        self.play(GrowArrow(hit_arrow))
        self.play(
            nodes["F2_R"][0].animate.set_color(GREEN).set_fill(GREEN, opacity=0.2)
        )

        # Pruning the Tree
        self.play(
            Transform(
                action_text,
                Text(
                    "Pruning redundant branches (Transforms O(2^n) -> O(n))",
                    font_size=20,
                    color=GREEN,
                ).to_edge(DOWN, buff=0.3),
            )
        )

        cross1 = Cross(nodes["F1_R2"], color=RED)
        cross2 = Cross(nodes["F0_R"], color=RED)
        self.play(
            Create(cross1),
            Create(cross2),
            edges[6].animate.set_stroke(opacity=0.1),
            edges[7].animate.set_stroke(opacity=0.1),
            nodes["F1_R2"].animate.set_opacity(0.2),
            nodes["F0_R"].animate.set_opacity(0.2),
            FadeOut(hit_arrow),
        )
        self.wait(1)

        # Finish Up
        for n_key, val, idx in [("F3", "2", 3), ("F4", "3", 4)]:
            new_val = Text(val, font_size=18, color=GREEN).move_to(cache_boxes[idx])
            self.play(
                Transform(cache_vals[idx], new_val),
                nodes[n_key][0].animate.set_color(GREEN).set_fill(GREEN, opacity=0.2),
                run_time=0.6,
            )

        # --- 6. OUTRO ---
        self.wait(1)
        self.play(
            FadeOut(
                Group(*nodes.values(), edges, cross1, cross2, action_text, cache_group)
            )
        )

        summary = Group(
            Text("Memoization Impact", font_size=36, color=BLUE),
            Text("Naive Recursive: O(2^n)", font_size=28, color=RED),
            Text("Memoized (DP): O(n)", font_size=28, color=GREEN),
            Text(
                "Massive speedup achieved by trading O(n) memory.",
                font_size=20,
                color=GRAY,
            ),
        ).arrange(DOWN, buff=0.5)

        self.play(FadeIn(summary))
        self.wait(3)
