"""
manim_test.py  —  End-to-end integration test: prompt → scene plan → Manim code

Usage:
    python manim_test.py
    python manim_test.py "explain binary search"
"""
import sys
import json
from agents.prompt_expander import expand_prompt
# from agents.manim_coder import generate_manim


print(expand_prompt("explain binary search"))

