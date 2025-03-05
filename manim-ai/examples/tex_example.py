from manim import *

class MathTexExample(Scene):
    def construct(self):
        # Create a MathTex object
        math_tex = MathTex(
            r"\int_{a}^{b} f(x) \, dx = F(b) - F(a)",
            font_size=72
        )

        # Add the object to the scene
        self.play(Write(math_tex))
        self.wait(1)

        # Transform to another equation
        new_math_tex = MathTex(
            r"e^{i\pi} + 1 = 0",
            font_size=72
        )
        self.play(Transform(math_tex, new_math_tex))
        self.wait(2) 