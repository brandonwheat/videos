from manim import *

class SquareToCircle(Scene):
    def construct(self):
        square = Square()
        square.set_fill(BLUE_E, 1)
        circle = Circle()
        circle.set_fill(RED_E, 1)

        self.play(Create(square))
        self.wait()
        self.play(Transform(square, circle))
        self.wait() 