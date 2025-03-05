from manim import *
from manim_voiceover import VoiceoverScene
from manim_voiceover.services.openai import OpenAIService
import numpy as np

class MandelbrotSet(VoiceoverScene):
    def construct(self):
        # Set up the OpenAI voice service
        openai_service = OpenAIService(
            voice="alloy",  # Options: alloy, echo, fable, onyx, nova, shimmer
            model="tts-1-hd"
        )
        self.set_speech_service(openai_service)
        
        # Title
        title = Text("The Mandelbrot Set", font_size=40)
        subtitle = Text("A Beautiful Mathematical Object", font_size=30)
        
        with self.voiceover("Welcome to an exploration of the Mandelbrot Set, one of the most famous and beautiful mathematical objects in the world.") as tracker:
            self.play(Write(title))
            self.wait(1)
        
        with self.voiceover("This fractal structure reveals infinite complexity and has fascinated mathematicians and artists alike since its discovery.") as tracker:
            self.play(title.animate.to_edge(UP))
            self.play(Write(subtitle))
            self.wait(1)
            self.play(FadeOut(subtitle))
        
        # Define the recursive formula
        formula = MathTex(
            "z_{n+1} = z_n^2 + c", 
            "\quad", 
            "z_0 = 0", 
            font_size=36
        )
        formula.next_to(title, DOWN)
        
        with self.voiceover("The Mandelbrot Set is defined by a simple recursive formula: z subscript n+1 equals z subscript n squared plus c, where z starts at zero.") as tracker:
            self.play(Write(formula))
            self.wait_until_bookmark("z starts at zero")
        
        # Explain the Mandelbrot set definition
        definition = MathTex(
            "\text{The Mandelbrot set is the set of complex numbers } c \text{ for which the sequence}", 
            font_size=26
        )
        definition2 = MathTex(
            "\{z_n\} \text{ remains bounded as } n \to \infty",
            font_size=26
        )
        
        definition.next_to(formula, DOWN, buff=0.5)
        definition2.next_to(definition, DOWN, buff=0.2)
        
        with self.voiceover("Formally, the Mandelbrot set is defined as the set of complex numbers c for which the sequence z_n remains bounded as n approaches infinity.") as tracker:
            self.play(Write(definition))
            self.play(Write(definition2))
            self.wait(1)
        
        # Move all the text explanations to the top
        explanation_group = VGroup(formula, definition, definition2)
        with self.voiceover("In simpler terms, we're asking: for which values of c does the sequence stay finite, and for which does it escape to infinity?") as tracker:
            self.play(explanation_group.animate.scale(0.8).to_edge(UP))
            self.wait(1)
        
        # Create coordinate system for plotting the Mandelbrot set
        axes = Axes(
            x_range=[-2.5, 1.5, 0.5],
            y_range=[-1.5, 1.5, 0.5],
            x_length=10,
            y_length=6,
            axis_config={"include_tip": False},
        )
        
        axes_labels = axes.get_axis_labels(x_label="\Re(c)", y_label="\Im(c)")
        
        with self.voiceover("Let's visualize this in the complex plane, where the horizontal axis represents the real part of c, and the vertical axis represents the imaginary part.") as tracker:
            self.play(Create(axes), Write(axes_labels))
            self.wait(1)
        
        # Create the Mandelbrot set
        # This is a simplified version for demonstration purposes
        # A full implementation would use a pixel-based approach
        resolution = 20
        max_iter = 100
        mandelbrot_dots = []
        
        for i in range(-25, 16):
            for j in range(-15, 16):
                c_real = i / 10
                c_imag = j / 10
                c = complex(c_real, c_imag)
                
                z = 0
                for k in range(max_iter):
                    z = z**2 + c
                    if abs(z) > 2:
                        break
                
                if abs(z) <= 2:  # Point is in Mandelbrot set
                    dot = Dot(axes.c2p(c_real, c_imag), radius=0.05, color=BLUE)
                    mandelbrot_dots.append(dot)
        
        mandelbrot = VGroup(*mandelbrot_dots)
        
        with self.voiceover("Now, let's plot the Mandelbrot set. Each point in blue represents a complex number c for which the sequence remains bounded. Notice the characteristic cardioid shape with a circular bulb attached to it.") as tracker:
            self.play(FadeIn(mandelbrot), run_time=2)
            self.wait(1)
        
        # Show zooming in on interesting part of the set
        zoom_box = Rectangle(
            width=1.5, height=1, 
            stroke_color=YELLOW
        ).move_to(axes.c2p(-0.75, 0))
        
        with self.voiceover("One of the most fascinating properties of the Mandelbrot set is its infinite complexity at the boundary. Let's focus on this region.") as tracker:
            self.play(Create(zoom_box))
            self.wait(1)
        
        # Create a zoomed view of the set
        zoom_text = Text("Infinite complexity at the boundary", font_size=28)
        zoom_text.to_edge(DOWN)
        with self.voiceover("If we were to zoom in on this boundary, we would discover intricate patterns that repeat at all scales, revealing smaller copies of the entire set.") as tracker:
            self.play(Write(zoom_text))
            self.wait(1)
        
        # Demonstrate the iterative process with a point example
        example_point = Dot(axes.c2p(-0.6, 0.5), color=RED, radius=0.08)
        example_label = MathTex("c = -0.6 + 0.5i", color=RED).next_to(example_point, RIGHT)
        
        with self.voiceover("Let's examine a specific example to understand how we determine whether a point belongs to the Mandelbrot set. Here's the point c equals negative 0.6 plus 0.5i.") as tracker:
            self.play(FadeOut(zoom_box), FadeOut(zoom_text))
            self.play(FadeIn(example_point), Write(example_label))
            self.wait(1)
        
        # Show the iteration steps
        iterations = VGroup()
        z = 0
        for i in range(10):
            z_old = z
            z = z**2 + complex(-0.6, 0.5)
            
            if i < 5:  # Only show first few iterations
                iter_text = MathTex(
                    f"z_{i+1} = ({z_old:.2f})^2 + (-0.6+0.5i) = {z:.2f}",
                    font_size=24
                )
                iterations.add(iter_text)
        
        iterations.arrange(DOWN, aligned_edge=LEFT).to_edge(RIGHT)
        
        with self.voiceover("We start with z_0 equals 0, and apply our recursive formula to generate a sequence. Let's compute the first few iterations.") as tracker:
            self.play(Write(iterations[0]))
            for i in range(1, len(iterations)):
                self.play(Write(iterations[i]))
                self.wait(0.3)
        
        # Show that this point escapes
        escape_text = Text("This point escapes to infinity!", font_size=28, color=RED)
        escape_text.to_edge(DOWN)
        with self.voiceover("As we continue this process, we notice that the absolute value of z grows larger with each iteration. Eventually, it would exceed any finite bound, meaning this point escapes to infinity and is therefore not part of the Mandelbrot set.") as tracker:
            self.play(Write(escape_text))
            self.wait(1)
        
        # Fade out everything and show a beautiful coloring of the Mandelbrot set
        with self.voiceover("Let's clear our workspace and return to the full Mandelbrot set.") as tracker:
            self.play(
                FadeOut(iterations), 
                FadeOut(example_point),
                FadeOut(example_label),
                FadeOut(escape_text)
            )
        
        final_text = Text("Explore the infinite detail of the Mandelbrot set...", font_size=30)
        final_text.to_edge(DOWN)
        
        with self.voiceover("The Mandelbrot set contains infinite detail and mathematical beauty. As you zoom in on its boundary, you discover self-similar structures, miniature copies of the whole set, and intricate patterns that never end. This mathematical object truly represents the infinite complexity that can arise from simple rules.") as tracker:
            self.play(Write(final_text))
            self.wait(2)