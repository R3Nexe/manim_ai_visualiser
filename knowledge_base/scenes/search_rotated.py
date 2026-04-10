from manim import *
 
"""
TITLE: Search in Rotated Sorted Array — Two-Phase Binary Search Visualization
CONCEPTS: binary search, rotated array, pivot finding, O(log n), divide and conquer, two-phase search
VISUAL_ELEMENTS: Square, Text, Arrow, VGroup, SurroundingRectangle, Line, MathTex, Indicate
DIFFICULTY: intermediate
"""

 
class SearchRotatedArray(Scene):
    def construct(self):
 
        # ══════════════════════════════════════════════════════════════════════
        # SCENE 1 — Educational Intro (Full Screen)
        # ══════════════════════════════════════════════════════════════════════
        title = Text("Search in Rotated Sorted Array", font_size=52, weight=BOLD)
        subtitle = Text("Two-Phase Binary Search  |  O(log n)", font_size=36, color=BLUE)
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.4).move_to(ORIGIN)
 
        self.play(FadeIn(header, shift=UP))
        self.wait(0.4)
        self.play(header.animate.shift(UP * 2.2))
 
        prereq = Text("Prerequisite: Binary Search", font_size=28, color=YELLOW)
        explain = Text(
            "Step 1: Find the rotation pivot (the smallest element).\n"
            "Step 2: Binary-search the sorted half that contains the target.",
            font_size=23,
        )
        info = VGroup(prereq, explain).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        self.play(FadeIn(info))
        self.wait(2.5)
        self.play(FadeOut(header), FadeOut(info))
        self.wait(0.2)
 
        # ══════════════════════════════════════════════════════════════════════
        # SCENE 2 — UI Grid Generation
        # ══════════════════════════════════════════════════════════════════════
        h_line = Line(LEFT * 8, RIGHT * 8, color=GRAY, stroke_width=2).move_to(ORIGIN)
        v_line = Line(DOWN * 4, ORIGIN, color=GRAY, stroke_width=2)
        self.play(Create(h_line), Create(v_line))
 
        # ══════════════════════════════════════════════════════════════════════
        # SCENE 3 — Populate UI Zones
        # ══════════════════════════════════════════════════════════════════════
 
        # ── Zone 1: Array (Top Half) ──────────────────────────────────────────
        arr = [4, 5, 6, 7, 0, 1, 2]
        n   = len(arr)
        SZ  = 0.68  # box side length
 
        boxes = VGroup(*[
            Square(side_length=SZ, color=WHITE, stroke_width=2).set_fill("#2a2a2a", opacity=1)
            for _ in arr
        ]).arrange(RIGHT, buff=0.09).move_to(UP * 2.5)
 
        val_lbs = VGroup(*[
            Text(str(arr[i]), font_size=22).move_to(boxes[i].get_center())
            for i in range(n)
        ])
        idx_lbs = VGroup(*[
            Text(str(i), font_size=15, color="#888888").next_to(boxes[i], DOWN, buff=0.1)
            for i in range(n)
        ])
        arr_ttl = Text(
            "nums = [4,5,6,7,0,1,2]    target = 0",
            font_size=22, color=YELLOW
        ).to_edge(UP, buff=0.25)
 
        self.play(FadeIn(arr_ttl))
        self.play(FadeIn(boxes), FadeIn(val_lbs), FadeIn(idx_lbs))
 
        # --- Pointer factory (initialised off-screen) ---
        def make_ptr(label, col):
            arrow = Arrow(DOWN * 0.32, UP * 0.05, color=col, buff=0,
                          stroke_width=3, max_tip_length_to_length_ratio=0.5)
            txt = Text(label, font_size=16, color=col)
            g = VGroup(txt, arrow).arrange(DOWN, buff=0.06)
            g.move_to(RIGHT * 13)   # safely off-screen
            return g
 
        ptr_L = make_ptr("L", GREEN)
        ptr_M = make_ptr("M", ORANGE)
        ptr_H = make_ptr("H", RED)
        ptr_P = make_ptr("P", PURPLE)
        self.add(ptr_L, ptr_M, ptr_H, ptr_P)
 
        def mv_ptr(ptr, idx, rt=0.3):
            dest = boxes[idx].get_bottom() + DOWN * (ptr.height / 2 + 0.06)
            self.play(ptr.animate.move_to(dest), run_time=rt)
 
        def hide_ptr(ptr):
            self.play(ptr.animate.move_to(RIGHT * 13), run_time=0.2)
 
        def flash_box(idx, col, rt=0.2):
            self.play(boxes[idx].animate.set_fill(col, opacity=0.75), run_time=rt)
 
        def reset_box(idx, rt=0.15):
            self.play(boxes[idx].animate.set_fill("#2a2a2a", opacity=1), run_time=rt)
 
        def dim_box(idx, rt=0.12):
            self.play(boxes[idx].animate.set_fill("#111111", opacity=0.85), run_time=rt)
 
        # ── Zone 2: Custom Code Block (Bottom Left) ───────────────────────────
        # Keywords deliberately narrow to avoid substring collisions.
        # "def ", "return ", "while " are all non-overlapping.
        code_lines = [
            "def pivot(arr):",
            "    low, high = 0, len(arr)-1",
            "    while low < high:",
            "        mid = low+(high-low)//2",
            "        if arr[mid] > arr[high]:",
            "            low = mid+1",
            "        else:",
            "            high = mid",
            "    return high",
            " ",
            "def binarySearch(arr,lo,hi,t):",
            "    while lo <= hi:",
            "        mid = lo+(hi-lo)//2",
            "        if arr[mid]==t: return mid",
            "        elif arr[mid] > t:",
            "            hi = mid-1",
            "        else:",
            "            lo = mid+1",
            "    return -1",
        ]
        # Line index reference (used in mv_hi calls):
        #  0  def pivot        6  else:           12  mid=lo+…
        #  1  low,high=…       7  high=mid        13  if ==t: return
        #  2  while low<high   8  return high     14  elif >t:
        #  3  mid=low+…        9  (blank)         15  hi=mid-1
        #  4  if arr[mid]>…   10  def binarySearch 16  else:
        #  5  low=mid+1       11  while lo<=hi    17  lo=mid+1
        #                                         18  return -1
 
        t2c = {"def ": ORANGE, "return ": RED, "while ": BLUE}
 
        code_mobs = VGroup(*[
            Text(ln, font="Monospace", font_size=17, t2c=t2c)
            for ln in code_lines
        ]).arrange(DOWN, aligned_edge=LEFT, buff=0.06)
 
        code_bg = SurroundingRectangle(
            code_mobs, fill_color="#1e1e1e", fill_opacity=1,
            stroke_color="#555555", stroke_width=1, buff=0.15
        )
        code_block = VGroup(code_bg, code_mobs)
        code_block.scale(0.62)
 
        code_ttl = Text("Code:", font_size=21).to_edge(LEFT, buff=0.4).set_y(-0.45)
        code_block.next_to(code_ttl, DOWN, aligned_edge=LEFT, buff=0.12)
 
        # Safety clamp: block must not cross the grey vertical line (x=0)
        if code_block.get_right()[0] > -0.08:
            code_block.shift(LEFT * (code_block.get_right()[0] + 0.12))
 
        hi_rect = SurroundingRectangle(
            code_block[1][0], color=YELLOW, buff=0.02, stroke_width=1.5
        )
        self.play(FadeIn(code_ttl), FadeIn(code_block))
        self.add(hi_rect)
 
        def mv_hi(line_idx):
            nr = SurroundingRectangle(
                code_block[1][line_idx], color=YELLOW, buff=0.02, stroke_width=1.5
            )
            self.play(Transform(hi_rect, nr), run_time=0.22)
 
        # ── Zone 3: Execution State (Bottom Right) ────────────────────────────
        st_ttl = (
            Text("Execution State:", font_size=21)
            .next_to(ORIGIN, RIGHT, buff=0.45)
            .set_y(-0.45)
        )
 
        phase_v = Text("Phase: Pivot Search", font_size=19, color=PURPLE)
        low_v   = Text("low   = 0",           font_size=19, color=GREEN)
        high_v  = Text("high  = 6",           font_size=19, color=RED)
        mid_v   = Text("mid   =  -",          font_size=19, color=ORANGE)
        pivot_v = Text("pivot =  -",          font_size=19, color=PURPLE)
 
        sv = VGroup(phase_v, low_v, high_v, mid_v, pivot_v)
        sv.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        sv.next_to(st_ttl, DOWN, aligned_edge=LEFT, buff=0.18)
 
        # Clamp: state zone must not stray left of x=0.15
        min_x = 0.15
        if sv.get_left()[0] < min_x:
            sv.shift(RIGHT * (min_x - sv.get_left()[0]))
        if st_ttl.get_left()[0] < min_x:
            st_ttl.shift(RIGHT * (min_x - st_ttl.get_left()[0]))
 
        exp_v = (
            Text("Starting pivot search...", font_size=17)
            .move_to(RIGHT * 2.8 + DOWN * 3.5)
        )
        self.play(FadeIn(st_ttl), FadeIn(sv), FadeIn(exp_v))
 
        # --- State-update helpers (Transform in-place; no reassignment needed) ---
        def uv(mob, s, col):
            nm = Text(s, font_size=19, color=col)
            nm.move_to(mob.get_center()).align_to(mob, LEFT)
            self.play(Transform(mob, nm), run_time=0.22)
 
        def ue(s):
            nm = Text(s, font_size=17).move_to(exp_v.get_center())
            self.play(Transform(exp_v, nm), run_time=0.22)
 
        def up(s, col):
            nm = Text(s, font_size=19, color=col)
            nm.move_to(phase_v.get_center()).align_to(phase_v, LEFT)
            self.play(Transform(phase_v, nm), run_time=0.28)
 
        # ══════════════════════════════════════════════════════════════════════
        # SCENE 4 — Algorithm Execution
        # ══════════════════════════════════════════════════════════════════════
 
        # ─────────────────────────────────────────────────────────────────────
        # Phase 1 : Pivot Search
        #   nums = [4,5,6,7,0,1,2]
        #   Trace: (low=0,high=6)→mid=3→low=4
        #          (low=4,high=6)→mid=5→high=5
        #          (low=4,high=5)→mid=4→high=4  EXIT  pivot=4
        # ─────────────────────────────────────────────────────────────────────
        mv_ptr(ptr_L, 0)
        mv_ptr(ptr_H, 6)
 
        # ── Iteration 1: low=0, high=6, mid=3
        mv_hi(2); ue("low=0 < high=6   enter loop")
        mv_hi(3)
        uv(mid_v, "mid   = 3", ORANGE); mv_ptr(ptr_M, 3)
        ue("mid = 0 + (6-0)//2 = 3")
        mv_hi(4)
        flash_box(3, ORANGE); flash_box(6, RED)
        ue("arr[3]=7 > arr[6]=2   True  -> take left branch")
        reset_box(3); reset_box(6)
        mv_hi(5)
        uv(low_v, "low   = 4", GREEN); mv_ptr(ptr_L, 4)
        ue("low = mid+1 = 4")
 
        # ── Iteration 2: low=4, high=6, mid=5
        mv_hi(2); ue("low=4 < high=6   continue")
        mv_hi(3)
        uv(mid_v, "mid   = 5", ORANGE); mv_ptr(ptr_M, 5)
        ue("mid = 4 + (6-4)//2 = 5")
        mv_hi(4)
        flash_box(5, ORANGE); flash_box(6, RED)
        ue("arr[5]=1 > arr[6]=2   False  -> take right branch")
        reset_box(5); reset_box(6)
        mv_hi(7)
        uv(high_v, "high  = 5", RED); mv_ptr(ptr_H, 5)
        ue("high = mid = 5")
 
        # ── Iteration 3: low=4, high=5, mid=4
        mv_hi(2); ue("low=4 < high=5   continue")
        mv_hi(3)
        uv(mid_v, "mid   = 4", ORANGE); mv_ptr(ptr_M, 4)
        ue("mid = 4 + (5-4)//2 = 4")
        mv_hi(4)
        flash_box(4, ORANGE); flash_box(5, RED)
        ue("arr[4]=0 > arr[5]=1   False  -> take right branch")
        reset_box(4); reset_box(5)
        mv_hi(7)
        uv(high_v, "high  = 4", RED); mv_ptr(ptr_H, 4)
        ue("high = mid = 4")
 
        # ── Exit pivot loop
        mv_hi(2); ue("low=4 == high=4   exit loop")
        mv_hi(8)
        uv(pivot_v, "pivot = 4", PURPLE)
        flash_box(4, PURPLE, rt=0.35); mv_ptr(ptr_P, 4)
        ue("pivot=4  (arr[4]=0 is the smallest element)")
        self.wait(0.6)
 
        # ─────────────────────────────────────────────────────────────────────
        # Phase 2 : Binary Search Left Half [0 .. pivot-1] = [0..3]
        #   Trace: mid=1 -> hi=0   mid=0 -> hi=-1   return -1
        # ─────────────────────────────────────────────────────────────────────
        up("Phase: BS Left [0..3]", BLUE)
        for i in range(4, 7): dim_box(i)     # grey out right half
 
        uv(low_v,   "low   = 0", GREEN)
        uv(high_v,  "high  = 3", RED)
        uv(mid_v,   "mid   =  -", ORANGE)
        uv(pivot_v, "pivot = 4", PURPLE)
        mv_ptr(ptr_L, 0); mv_ptr(ptr_H, 3)
        hide_ptr(ptr_M); hide_ptr(ptr_P)
        ue("Search target=0 in left half [0..3]")
 
        # ── BS left iter 1: lo=0, hi=3, mid=1
        mv_hi(11); ue("lo=0 <= hi=3   enter loop")
        mv_hi(12)
        uv(mid_v, "mid   = 1", ORANGE); mv_ptr(ptr_M, 1)
        ue("mid = 0 + (3-0)//2 = 1")
        mv_hi(13); ue("arr[1]=5 == 0?   No")
        mv_hi(14)
        flash_box(1, RED)
        ue("arr[1]=5 > 0   True  -> hi = mid-1")
        reset_box(1)
        mv_hi(15)
        uv(high_v, "high  = 0", RED); mv_ptr(ptr_H, 0)
        ue("hi = mid-1 = 0")
 
        # ── BS left iter 2: lo=0, hi=0, mid=0
        mv_hi(11); ue("lo=0 <= hi=0   continue")
        mv_hi(12)
        uv(mid_v, "mid   = 0", ORANGE); mv_ptr(ptr_M, 0)
        ue("mid = 0 + (0-0)//2 = 0")
        mv_hi(13); ue("arr[0]=4 == 0?   No")
        mv_hi(14)
        flash_box(0, RED)
        ue("arr[0]=4 > 0   True  -> hi = mid-1 = -1")
        reset_box(0)
        mv_hi(15)
        uv(high_v, "high  = -1", RED); hide_ptr(ptr_H)
        ue("hi=-1 < lo=0   exit loop")
        mv_hi(18)
        ue("return -1   (target not in left half)")
        self.wait(0.35)
 
        # ─────────────────────────────────────────────────────────────────────
        # Phase 3 : Binary Search Right Half [pivot .. n-1] = [4..6]
        #   Trace: mid=5 -> hi=4   mid=4 -> FOUND index 4
        # ─────────────────────────────────────────────────────────────────────
        up("Phase: BS Right [4..6]", TEAL)
        for i in range(4): dim_box(i)        # grey out left half
        for i in range(4, 7):
            self.play(boxes[i].animate.set_fill("#2a2a2a", opacity=1), run_time=0.1)
 
        uv(low_v,  "low   = 4", GREEN)
        uv(high_v, "high  = 6", RED)
        uv(mid_v,  "mid   =  -", ORANGE)
        mv_ptr(ptr_L, 4); mv_ptr(ptr_H, 6)
        hide_ptr(ptr_M)
        ue("Search target=0 in right half [4..6]")
 
        # ── BS right iter 1: lo=4, hi=6, mid=5
        mv_hi(11); ue("lo=4 <= hi=6   enter loop")
        mv_hi(12)
        uv(mid_v, "mid   = 5", ORANGE); mv_ptr(ptr_M, 5)
        ue("mid = 4 + (6-4)//2 = 5")
        mv_hi(13); ue("arr[5]=1 == 0?   No")
        mv_hi(14)
        flash_box(5, RED)
        ue("arr[5]=1 > 0   True  -> hi = mid-1")
        reset_box(5)
        mv_hi(15)
        uv(high_v, "high  = 4", RED); mv_ptr(ptr_H, 4)
        ue("hi = mid-1 = 4")
 
        # ── BS right iter 2: lo=4, hi=4, mid=4  → FOUND
        mv_hi(11); ue("lo=4 <= hi=4   continue")
        mv_hi(12)
        uv(mid_v, "mid   = 4", ORANGE); mv_ptr(ptr_M, 4)
        ue("mid = 4 + (4-4)//2 = 4")
        mv_hi(13)
        flash_box(4, GREEN)
        ue("arr[4]=0 == 0   TARGET FOUND at index 4!")
        self.play(Indicate(boxes[4], color=YELLOW, scale_factor=1.45))
 
        found_banner = Text("Found  target=0  at index 4", font_size=28, color=GREEN)
        found_banner.move_to(UP * 1.3)
        self.play(FadeIn(found_banner))
        self.wait(1.3)
 
        # ══════════════════════════════════════════════════════════════════════
        # SCENE 5 — Educational Outro (Complexity Breakdown)
        # ══════════════════════════════════════════════════════════════════════
        self.play(FadeOut(VGroup(
            h_line, v_line,
            arr_ttl, boxes, val_lbs, idx_lbs,
            ptr_L, ptr_M, ptr_H, ptr_P,
            code_ttl, code_block, hi_rect,
            st_ttl, sv, exp_v, found_banner,
        )))
        self.wait(0.2)
 
        complexity_tex = MathTex(
            r"\text{Time Complexity: } O(\log n)",
            font_size=46, color=YELLOW
        ).move_to(ORIGIN)
        self.play(FadeIn(complexity_tex))
        self.wait(0.35)
        self.play(complexity_tex.animate.shift(UP * 2.8))
 
        bullet_data = [
            "1.  Pivot search   : binary search on all n elements   ->  O(log n)",
            "2.  Half search    : binary search on at most n/2 elems ->  O(log n)",
            "3.  Total          : O(log n) + O(log n)  =  O(log n)  (constants drop)",
        ]
        bmobs = VGroup(*[Text(b, font_size=24) for b in bullet_data])
        bmobs.arrange(DOWN, aligned_edge=LEFT, buff=0.45).move_to(UP * 0.3)
 
        for m in bmobs:
            self.play(FadeIn(m, shift=RIGHT * 0.2))
            self.wait(0.65)
 
        opt_title = Text("Optimization Status:  Optimal", font_size=27, color=GREEN)
        opt_desc  = Text(
            "No comparison-based algorithm can search faster than O(log n).",
            font_size=21, color=GRAY,
        )
        opt_group = VGroup(opt_title, opt_desc).arrange(DOWN, buff=0.28)
        opt_group.next_to(bmobs, DOWN, buff=0.5)
        self.play(FadeIn(opt_group))
        self.wait(2.5)