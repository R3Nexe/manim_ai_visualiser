from manim import *


class APIGatewayLifecycle(Scene):
    def construct(self):
        # --- SHARED COMPONENTS SETUP ---
        client = Group(
            Dot(color=BLUE), Text("Client", font_size=18).next_to(ORIGIN, DOWN)
        ).shift(LEFT * 5)
        gateway_hex = (
            RegularPolygon(n=6, color=GOLD, fill_opacity=0.2)
            .scale(1.2)
            .shift(LEFT * 0.5)
        )
        gateway_label = Text("GATEWAY", font_size=20, weight=BOLD).move_to(gateway_hex)
        gateway = Group(gateway_hex, gateway_label)

        service_box = RoundedRectangle(width=2.5, height=1.2, color=GREEN)
        service_label = Text("Service", font_size=20).move_to(service_box)
        service = Group(service_box, service_label).shift(RIGHT * 4)

        # ==========================================
        # SCENE 1: NORMAL LOGIC (CLOSED STATE)
        # ==========================================
        title1 = Text("State 1: CLOSED (Normal)", color=GREEN, font_size=32).to_edge(UP)
        self.play(Write(title1), FadeIn(client, gateway, service))

        req1 = Dot(color=WHITE).move_to(client)
        self.play(req1.animate.move_to(gateway_hex), run_time=0.8)
        self.play(Indicate(gateway_hex, color=GREEN))
        self.play(req1.animate.move_to(service), run_time=0.8)

        res1 = Dot(color=GREEN).move_to(service)
        self.play(res1.animate.move_to(client), FadeOut(req1), run_time=1.2)
        self.play(FadeOut(res1), FadeOut(title1))
        self.wait(1)

        # ==========================================
        # SCENE 2: CIRCUIT BREAK (OPEN STATE)
        # ==========================================
        title2 = Text("State 2: OPEN (Tripped)", color=RED, font_size=32).to_edge(UP)
        failure_x = Cross(service, stroke_width=6).set_color(RED)

        self.play(Write(title2), Create(failure_x), service_box.animate.set_color(RED))
        self.play(gateway_hex.animate.set_stroke(RED, width=8))  # Visual "Trip"

        req2 = Dot(color=WHITE).move_to(client)
        self.play(req2.animate.move_to(gateway_hex), run_time=0.8)

        # Gateway REJECTS immediately (Fallback)
        fallback_txt = Text("Fallback Response", font_size=16, color=ORANGE).next_to(
            gateway_hex, DOWN
        )
        self.play(Write(fallback_txt), Flash(gateway_hex, color=RED))

        res2 = Dot(color=ORANGE).move_to(gateway_hex)
        self.play(res2.animate.move_to(client), FadeOut(req2), run_time=0.8)
        self.play(FadeOut(res2), FadeOut(fallback_txt), FadeOut(title2))
        self.wait(1)

        # ==========================================
        # SCENE 3: HALF-OPEN (TESTING RECOVERY)
        # ==========================================
        title3 = Text(
            "State 3: HALF-OPEN (Testing)", color=YELLOW, font_size=32
        ).to_edge(UP)
        self.play(Write(title3))
        self.play(
            gateway_hex.animate.set_stroke(YELLOW, width=5),
            FadeOut(failure_x),
            service_box.animate.set_color(YELLOW),
        )

        # Limited trial request
        req3 = Dot(color=YELLOW).move_to(client)
        trial_txt = Text("Trial Request", font_size=16, color=YELLOW).next_to(req3, UP)

        self.play(FadeIn(trial_txt), req3.animate.move_to(gateway_hex), run_time=0.8)
        self.play(req3.animate.move_to(service), run_time=1.2)  # Allow ONE through

        # Service succeeds!
        success_flash = Flash(service, color=GREEN)
        self.play(success_flash, service_box.animate.set_color(GREEN))

        # Recovery: Close the circuit again
        self.play(
            gateway_hex.animate.set_stroke(GREEN, width=2),
            FadeOut(trial_txt),
            FadeOut(req3),
        )

        final_msg = Text("Circuit Reset to CLOSED", color=GREEN, font_size=24).next_to(
            gateway_hex, UP
        )
        self.play(Write(final_msg))
        self.wait(2)
