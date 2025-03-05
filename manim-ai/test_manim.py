
from manim import Scene, Text, Write, Create, config

class TestScene(Scene):
    def construct(self):
        text = Text("Manim installed successfully!")
        self.play(Write(text))
        self.wait(2)

