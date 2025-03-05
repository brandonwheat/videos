from manim import *

class PythagoreanTheorem(Scene):
    def construct(self):
        # Create a right triangle
        triangle = Polygon(
            ORIGIN,
            RIGHT * 3,
            RIGHT * 3 + UP * 4,
            color=WHITE
        )

        # Label the sides
        a_label = MathTex("a", font_size=36).next_to(triangle, DOWN, buff=0.5)
        b_label = MathTex("b", font_size=36).next_to(triangle, RIGHT, buff=0.5)
        c_label = MathTex("c", font_size=36)
        c_label.move_to(triangle.get_center() + UP + LEFT)

        # Draw the squares on each side
        a_square = Square(side_length=3).shift(1.5 * RIGHT + 2 * DOWN)
        a_square.set_fill(RED, opacity=0.5)
        b_square = Square(side_length=4).shift(5 * RIGHT + 2 * UP)
        b_square.set_fill(GREEN, opacity=0.5)
        c_square = Square(side_length=5).shift(1.5 * RIGHT + 2 * UP)
        c_square.rotate(np.arctan(4/3), about_point=triangle.get_vertices()[0])
        c_square.set_fill(BLUE, opacity=0.5)

        # Create area labels
        a_squared = MathTex("a^2 = 9", font_size=36).move_to(a_square.get_center())
        b_squared = MathTex("b^2 = 16", font_size=36).move_to(b_square.get_center())
        c_squared = MathTex("c^2 = 25", font_size=36).move_to(c_square.get_center())

        # Title
        title = Text("Pythagorean Theorem", font_size=48).to_edge(UP)
        formula = MathTex("a^2 + b^2 = c^2", font_size=48).next_to(title, DOWN)

        # Build the scene
        self.play(Write(title))
        self.wait(0.5)
        self.play(Write(formula))
        self.wait(1)

        # Draw the triangle
        self.play(Create(triangle))
        self.play(Write(a_label), Write(b_label), Write(c_label))
        self.wait(1)

        # Show the squares
        self.play(
            Create(a_square),
            Create(b_square),
            Create(c_square)
        )
        self.wait(1)

        # Fill the squares
        self.play(
            FadeIn(a_square),
            FadeIn(b_square),
            FadeIn(c_square)
        )
        self.wait(1)

        # Show the areas
        self.play(
            Write(a_squared),
            Write(b_squared),
            Write(c_squared)
        )
        self.wait(1)

        # Verify the theorem
        verification = MathTex("9 + 16 = 25", font_size=48).next_to(formula, DOWN)
        self.play(Write(verification))
        self.wait(1)

        # Conclusion
        check = Text("✓", font_size=72, color=GREEN).next_to(verification, RIGHT)
        self.play(Write(check))
        self.wait(2) 