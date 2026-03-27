from manim import *
"""
TITLE: Kruskal's Algorithm — Minimum Spanning Tree with Union-Find
CONCEPTS: kruskal's algorithm, minimum spanning tree (mst), greedy algorithm, union-find, cycle detection, edge sorting, graph theory, disjoint set union
VISUAL_ELEMENTS: Dot, Line, Text, Rectangle, RoundedRectangle, Group, Indicate, Transform, set_stroke, Write
DIFFICULTY: advanced
"""

class KruskalThreeZone(Scene):
    def construct(self):
        # --- INTRO ---
        title = Text("Kruskal's Algorithm", font_size=48, color=BLUE_B)
        subtitle = Text("Minimum Spanning Tree (MST)", font_size=28, color=GRAY)
        intro = Group(title, subtitle).arrange(DOWN).center()

        self.play(Write(title), FadeIn(subtitle))
        self.wait(1.5)
        self.play(FadeOut(intro))

        # --- PERSISTENT LABELS & ZONES ---
        vis_label = (
            Text("Graph Visualization", font_size=20, color=GRAY)
            .move_to([-6.8, 3.7, 0])
            .align_to([-6.8, 0, 0], LEFT)
        )
        logic_label = (
            Text("Algorithm Logic", font_size=20, color=GRAY)
            .move_to([0.25, 3.7, 0])
            .align_to([0.25, 0, 0], LEFT)
        )
        trace_label = (
            Text("Edge Trace (Sorted)", font_size=20, color=GRAY)
            .move_to([0.25, -0.4, 0])
            .align_to([0.25, 0, 0], LEFT)
        )
        self.add(vis_label, logic_label, trace_label)

        # --- LEFT ZONE: THE GRAPH ---
        pos = {
            "A": [-5.5, 1.5, 0],
            "B": [-2.5, 2.5, 0],
            "C": [-1.0, 0.5, 0],
            "D": [-5.0, -1.5, 0],
            "E": [-2.0, -1.0, 0],
        }

        # FIXED: Using Group for the collection of node Groups
        nodes = Group(
            *[
                Group(
                    Dot(point=pos[k], radius=0.2, color=WHITE),
                    Text(k, font_size=20).next_to(pos[k], UP, buff=0.1),
                )
                for k in pos
            ]
        )

        edges_data = [
            ("A", "D", 1),
            ("D", "E", 2),
            ("B", "C", 3),
            ("B", "E", 4),
            ("A", "B", 5),
            ("C", "E", 6),
        ]

        edge_objs = {}
        all_edges_grp = Group()
        for u, v, w in edges_data:
            line = Line(pos[u], pos[v], color=GRAY, stroke_opacity=0.3)
            lbl = (
                Text(str(w), font_size=16, color=YELLOW)
                .move_to(line.get_center())
                .shift(UP * 0.2)
            )
            edge_bundle = Group(line, lbl)
            edge_objs[(u, v)] = edge_bundle
            all_edges_grp.add(edge_bundle)

        self.play(FadeIn(nodes), FadeIn(all_edges_grp))

        # --- RIGHT-TOP: ALGORITHM LOGIC ---
        logic_steps = [
            "1. Sort all edges by weight",
            "2. Pick smallest edge",
            "3. Check for cycles (Union-Find)",
            "4. If no cycle, add to MST",
            "5. Repeat until V-1 edges",
        ]
        logic_lines = Group(*[Text(s, font_size=18) for s in logic_steps])
        logic_lines.arrange(DOWN, aligned_edge=LEFT, buff=0.3).move_to(
            [0.5, 2.2, 0]
        ).align_to([0.5, 0, 0], LEFT)
        self.add(logic_lines)

        hi = Rectangle(
            width=6.0, height=0.3, fill_color=YELLOW, fill_opacity=0.2, stroke_width=0
        )
        hi.move_to(logic_lines[0].get_center()).align_to(logic_lines, LEFT).shift(
            LEFT * 0.1
        )
        self.add(hi)

        # --- RIGHT-BOTTOM: EDGE TRACE ---
        trace_headers = Group(
            Text("Edge", font_size=18, color=GRAY).move_to([1.2, -0.9, 0]),
            Text("Weight", font_size=18, color=GRAY).move_to([3.0, -0.9, 0]),
            Text("Action", font_size=18, color=GRAY).move_to([5.0, -0.9, 0]),
        )
        self.add(trace_headers)

        trace_rows = Group()
        for i, (u, v, w) in enumerate(edges_data):
            row = Group(
                Text(f"{u}-{v}", font_size=17).move_to([1.2, -1.4 - (i * 0.4), 0]),
                Text(str(w), font_size=17).move_to([3.0, -1.4 - (i * 0.4), 0]),
                Text("-", font_size=17).move_to([5.0, -1.4 - (i * 0.4), 0]),
            )
            trace_rows.add(row)
        self.add(trace_rows)

        # --- EXECUTION ---
        parent = {n: n for n in pos}

        def find(i):
            if parent[i] == i:
                return i
            return find(parent[i])

        for i, (u, v, w) in enumerate(edges_data):
            # Step 2: Pick smallest
            self.play(
                hi.animate.move_to(logic_lines[1].get_center())
                .align_to(logic_lines, LEFT)
                .shift(LEFT * 0.1)
            )
            self.play(Indicate(edge_objs[(u, v)]), run_time=0.6)

            # Step 3: Check Cycle
            self.play(
                hi.animate.move_to(logic_lines[2].get_center())
                .align_to(logic_lines, LEFT)
                .shift(LEFT * 0.1)
            )

            root_u, root_v = find(u), find(v)
            if root_u != root_v:
                # Step 4: Add to MST (Union)
                parent[root_u] = root_v
                self.play(
                    hi.animate.move_to(logic_lines[3].get_center())
                    .align_to(logic_lines, LEFT)
                    .shift(LEFT * 0.1)
                )
                self.play(
                    edge_objs[(u, v)][0]
                    .animate.set_color(GREEN)
                    .set_stroke(width=6, opacity=1),
                    Transform(
                        trace_rows[i][2],
                        Text("ACCEPT", font_size=17, color=GREEN).move_to(
                            trace_rows[i][2]
                        ),
                    ),
                )
            else:
                # Cycle found (Reject)
                self.play(
                    edge_objs[(u, v)][0].animate.set_color(RED).set_stroke(opacity=0.2),
                    Transform(
                        trace_rows[i][2],
                        Text("REJECT", font_size=17, color=RED).move_to(
                            trace_rows[i][2]
                        ),
                    ),
                )
            self.wait(0.5)

        # --- OUTRO & COMPLEXITY ---
        self.play(FadeOut(Group(*self.mobjects)))

        final_title = Text("MST Completed", font_size=44, color=GREEN).shift(UP * 1.5)
        complexity_box = RoundedRectangle(
            width=7, height=2.5, color=WHITE, fill_opacity=0.05
        ).shift(DOWN * 0.5)

        comp_text = (
            Group(
                Text("Time Complexity: O(E log E)", font_size=32, color=YELLOW),
                Text("• Sorting edges takes O(E log E)", font_size=22),
                Text("• Union-Find takes O(E α(V))", font_size=22),
                Text("Total: O(E log E) or O(E log V)", font_size=24, color=BLUE_B),
            )
            .arrange(DOWN, aligned_edge=LEFT, buff=0.2)
            .move_to(complexity_box)
        )

        self.play(Write(final_title))
        self.play(Create(complexity_box), FadeIn(comp_text))
        self.wait(3)
