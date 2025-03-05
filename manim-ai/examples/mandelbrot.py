from manim import *
import numpy as np

class Mandelbrot(Scene):
    def construct(self):
        # Title
        title = Text("The Mandelbrot Set", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Create a complex plane
        plane = ComplexPlane(
            x_range=[-2.5, 1.5, 1],
            y_range=[-1.5, 1.5, 1],
            background_line_style={
                "stroke_width": 1,
                "stroke_opacity": 0.5,
            }
        ).scale(2.5)
        
        # Labels for the complex plane
        plane_labels = plane.get_coordinate_labels(
            x_values=[-2, -1, 0, 1],
            y_values=[-1, 0, 1]
        )
        
        # Show the plane
        self.play(
            Create(plane),
            Create(plane_labels)
        )
        self.wait(1)

        # Mandelbrot function explanation
        function_text = MathTex(
            r"z_{n+1} = z_n^2 + c", 
            font_size=36
        ).next_to(title, DOWN)
        
        explanation = Text(
            "Starting with z₀ = 0, we iterate this function and see if the sequence remains bounded.",
            font_size=24,
            line_spacing=1
        ).next_to(function_text, DOWN)
        
        self.play(Write(function_text))
        self.wait(0.5)
        self.play(Write(explanation))
        self.wait(1)
        
        # Create the Mandelbrot set using a pixel grid
        mandelbrot = self.get_mandelbrot_pixels(plane, resolution=20)
        
        self.play(
            FadeOut(explanation),
            function_text.animate.to_edge(UP, buff=0.1),
            title.animate.next_to(function_text, UP, buff=0.1)
        )
        
        # Show the Mandelbrot set
        self.play(FadeIn(mandelbrot))
        self.wait(1)

        # Zoom in to a section
        zoom_point = plane.c2p(-0.7436447860, 0.1318259043)
        self.play(
            plane.animate.scale(10).move_to(zoom_point),
            plane_labels.animate.scale(0.5),
            mandelbrot.animate.scale(10).move_to(zoom_point),
            run_time=4
        )
        self.wait(1)
        
        # Highlight fractal nature with text
        fractal_text = Text(
            "The Mandelbrot set is a fractal - it has infinite complexity at its boundary.",
            font_size=24
        ).to_edge(DOWN)
        
        self.play(Write(fractal_text))
        self.wait(2)
        
        # Final message
        self.play(
            FadeOut(title),
            FadeOut(function_text),
            FadeOut(fractal_text),
            FadeOut(plane),
            FadeOut(plane_labels)
        )
        
        final_text = Text(
            "Beautiful mathematics emerges from simple rules.",
            font_size=36
        )
        
        self.play(FadeIn(final_text))
        self.wait(2)
        
    def get_mandelbrot_pixels(self, plane, resolution=20, max_iter=100):
        """
        Create a pixel grid representing the Mandelbrot set
        """
        # Create a grid of squares to represent pixels
        x_range = np.linspace(-2.5, 1.5, resolution * 4)
        y_range = np.linspace(-1.5, 1.5, resolution * 3)
        
        pixels = VGroup()
        
        for x in x_range:
            for y in y_range:
                c = complex(x, y)
                iterations = self.mandelbrot_iterations(c, max_iter)
                
                if iterations == max_iter:
                    color = BLACK  # In the set
                else:
                    # Color based on how quickly the point escapes
                    color = self.iteration_color(iterations, max_iter)
                
                # Create a small square for each point
                pixel_size = 4 / resolution
                pixel = Square(
                    side_length=pixel_size,
                    fill_color=color,
                    fill_opacity=1,
                    stroke_width=0
                ).move_to(plane.c2p(x, y))
                
                pixels.add(pixel)
        
        return pixels
    
    def mandelbrot_iterations(self, c, max_iter):
        """
        Calculate how many iterations it takes for a point c to escape
        """
        z = 0
        for n in range(max_iter):
            z = z**2 + c
            if abs(z) > 2:
                return n
        return max_iter
    
    def iteration_color(self, iterations, max_iter):
        """
        Convert iteration count to a color
        """
        if iterations == max_iter:
            return BLACK
        
        # Create a smooth color gradient based on iteration count
        ratio = iterations / max_iter
        # Use a color scheme similar to traditional Mandelbrot visualizations
        if ratio < 0.16:
            return interpolate_color(BLUE_E, BLUE, ratio * 6)
        elif ratio < 0.42:
            return interpolate_color(BLUE, GREEN, (ratio - 0.16) * 4)
        elif ratio < 0.6425:
            return interpolate_color(GREEN, YELLOW, (ratio - 0.42) * 4)
        elif ratio < 0.8575:
            return interpolate_color(YELLOW, RED, (ratio - 0.6425) * 4)
        else:
            return interpolate_color(RED, PURPLE, (ratio - 0.8575) * 8) 