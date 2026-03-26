from manim import *


class CPUFetchStore(Scene):
    def construct(self):
        # --- TITLE ---
        title = Text("CPU Instruction Cycle", font_size=40, color=BLUE)
        self.add(title.to_edge(UP))

        # --- MEMORY (RAM) ---
        # RAM as a vertical stack of addresses
        ram_box = Rectangle(width=3, height=5, color=GRAY_A).shift(LEFT * 4)
        ram_label = Text("RAM (Memory)", font_size=24).next_to(ram_box, UP)

        # Creating individual memory slots
        addresses = Group()
        for i in range(8):
            slot = Rectangle(width=2.5, height=0.5, stroke_width=1)
            addr_text = Text(f"0x0{i}", font_size=14, color=GRAY).shift(LEFT * 0.8)
            inst_text = Text(f"LOAD_{i}", font_size=16, color=YELLOW).shift(RIGHT * 0.4)

            # Grouping each slot's components
            mem_unit = Group(slot, addr_text, inst_text)
            addresses.add(mem_unit)

        addresses.arrange(DOWN, buff=0).move_to(ram_box)
        self.add(ram_box, ram_label, addresses)

        # --- CPU INTERNAL COMPONENTS ---
        cpu_frame = Rectangle(width=6, height=5, color=GOLD).shift(RIGHT * 2)
        cpu_title = Text("CPU", font_size=24, color=GOLD).next_to(cpu_frame, UP)

        # Program Counter (PC) - Holds the address to fetch
        pc_box = Rectangle(width=2, height=0.8)
        pc_label = Text("PC", font_size=20, color=BLUE).move_to(pc_box)
        pc_reg = Group(pc_box, pc_label).shift(RIGHT * 0.5 + UP * 1.5)
        pc_val = Text("0x00", font_size=20).next_to(pc_reg, RIGHT)

        # Instruction Register (IR) - Holds the fetched instruction
        ir_box = Rectangle(width=2, height=0.8)
        ir_label = Text("IR", font_size=20, color=RED).move_to(ir_box)
        ir_reg = Group(ir_box, ir_label).shift(RIGHT * 0.5 + DOWN * 1.5)
        ir_val = Text("EMPTY", font_size=18).next_to(ir_reg, RIGHT)

        # ALU (Arithmetic Logic Unit)
        alu = Triangle(color=WHITE).scale(0.8).shift(RIGHT * 4)
        alu_label = Text("ALU", font_size=18).move_to(alu).shift(DOWN * 0.2)

        self.add(cpu_frame, cpu_title, pc_reg, pc_val, ir_reg, ir_val, alu, alu_label)

        # --- THE FETCH-EXECUTE CYCLE ---
        for step in range(3):
            addr_hex = f"0x0{step}"
            inst_name = f"LOAD_{step}"

            # 1. Update PC (The 'Next' Pointer)
            new_pc_val = Text(addr_hex, font_size=20, color=BLUE).move_to(pc_val)
            self.play(Transform(pc_val, new_pc_val))
            self.play(Indicate(pc_reg, color=BLUE))

            # 2. FETCH: Address request sent to RAM
            pointer_arrow = Arrow(
                pc_reg.get_left(), addresses[step].get_right(), color=BLUE, buff=0.1
            )
            self.play(Create(pointer_arrow))

            # Data packet (the Instruction) traveling back to CPU IR
            data_packet = Text(inst_name, font_size=18, color=YELLOW).move_to(
                addresses[step]
            )
            self.play(
                data_packet.animate.move_to(ir_box.get_center()),
                FadeOut(pointer_arrow),
                run_time=1.2,
            )

            # 3. DECODE/STORE: IR now holds the instruction
            new_ir_val = Text(inst_name, font_size=18, color=RED).move_to(ir_val)
            self.play(Transform(ir_val, new_ir_val), FadeOut(data_packet))
            self.play(Indicate(ir_reg, color=RED))

            # 4. EXECUTE: IR sends signal to ALU
            exec_line = Line(ir_reg.get_right(), alu.get_left(), color=RED)
            self.play(Create(exec_line), run_time=0.4)
            self.play(alu.animate.set_fill(RED, opacity=0.5), run_time=0.3)
            self.play(alu.animate.set_fill(BLACK, opacity=0), FadeOut(exec_line))

            self.wait(0.5)

        # --- OUTRO ---
        self.play(FadeOut(Group(*self.mobjects)))
        summary = Text("Fetch → Decode → Execute", font_size=36, color=GREEN)
        self.play(Write(summary))
        self.wait(2)
