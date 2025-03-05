from manim import *
import numpy as np

class Eigenvalues(Scene):
    def construct(self):
        # Title
        title = Text("Eigenvalues and Eigenvectors", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        # Create a 2D coordinate system
        axes = Axes(
            x_range=[-4, 4, 1],
            y_range=[-4, 4, 1],
            axis_config={"include_tip": True},
        ).scale(0.8)

        # Add grid lines and labels
        grid = axes.get_grid()
        x_label = axes.get_x_axis_label("x")
        y_label = axes.get_y_axis_label("y")
        
        coord_system = VGroup(axes, grid, x_label, y_label)
        coord_system.shift(DOWN * 0.5)
        
        self.play(Create(axes))
        self.play(Create(grid), Write(x_label), Write(y_label))
        self.wait(1)

        # Define a 2x2 matrix
        matrix = np.array([[2, 1], [1, 2]])
        matrix_tex = MathTex(
            "A = \\begin{pmatrix} 2 & 1 \\\\ 1 & 2 \\end{pmatrix}",
            font_size=42
        ).next_to(title, DOWN)
        
        self.play(Write(matrix_tex))
        self.wait(1)

        # Explain eigenvectors and eigenvalues
        eigen_eq = MathTex(
            "A\\vec{v} = \\lambda\\vec{v}",
            font_size=42
        ).next_to(matrix_tex, DOWN)
        
        self.play(Write(eigen_eq))
        self.wait(1)

        # Create vectors to transform
        vectors = []
        vector_colors = [RED, GREEN, BLUE, YELLOW, PURPLE]
        num_vectors = 5
        
        for i in range(num_vectors):
            angle = i * 2 * PI / num_vectors
            vec = np.array([np.cos(angle), np.sin(angle)])
            vec_obj = Arrow(
                axes.c2p(0, 0),
                axes.c2p(vec[0], vec[1]),
                buff=0,
                color=vector_colors[i % len(vector_colors)]
            )
            vectors.append(vec_obj)
        
        self.play(*[Create(vec) for vec in vectors])
        self.wait(1)

        # Show transformation by matrix
        transformed_vectors = []
        for i, vec_obj in enumerate(vectors):
            angle = i * 2 * PI / num_vectors
            vec = np.array([np.cos(angle), np.sin(angle)])
            
            # Apply the matrix transformation
            transformed_vec = np.dot(matrix, vec)
            
            transformed_vec_obj = Arrow(
                axes.c2p(0, 0),
                axes.c2p(transformed_vec[0], transformed_vec[1]),
                buff=0,
                color=vector_colors[i % len(vector_colors)]
            )
            transformed_vectors.append(transformed_vec_obj)
        
        self.play(
            *[Transform(vectors[i], transformed_vectors[i]) for i in range(num_vectors)]
        )
        self.wait(1)

        # Highlight eigenvectors
        # For the matrix [[2, 1], [1, 2]], eigenvalues are 3 and 1
        # Eigenvector for λ=3 is [1, 1]
        # Eigenvector for λ=1 is [1, -1]
        
        eigenvalue1 = 3
        eigenvector1 = np.array([1, 1]) / np.sqrt(2)  # normalized
        
        eigenvalue2 = 1
        eigenvector2 = np.array([1, -1]) / np.sqrt(2)  # normalized
        
        # Create eigenvector objects
        eigen_vec1 = Arrow(
            axes.c2p(0, 0),
            axes.c2p(eigenvector1[0], eigenvector1[1]),
            buff=0,
            color=BLUE,
            stroke_width=6
        )
        
        eigen_vec2 = Arrow(
            axes.c2p(0, 0),
            axes.c2p(eigenvector2[0], eigenvector2[1]),
            buff=0,
            color=GREEN,
            stroke_width=6
        )
        
        # Fade out the regular vectors
        self.play(*[FadeOut(vec) for vec in vectors])
        
        # Show eigenvectors
        eigen_vec1_label = MathTex("\\vec{v}_1", color=BLUE, font_size=36).next_to(eigen_vec1.get_end(), UP+RIGHT)
        eigen_vec2_label = MathTex("\\vec{v}_2", color=GREEN, font_size=36).next_to(eigen_vec2.get_end(), DOWN+RIGHT)
        
        self.play(
            Create(eigen_vec1),
            Create(eigen_vec2),
            Write(eigen_vec1_label),
            Write(eigen_vec2_label)
        )
        self.wait(1)
        
        # Show the effect of transformation on eigenvectors
        scaled_eigen_vec1 = Arrow(
            axes.c2p(0, 0),
            axes.c2p(eigenvalue1 * eigenvector1[0], eigenvalue1 * eigenvector1[1]),
            buff=0,
            color=BLUE,
            stroke_width=6
        )
        
        scaled_eigen_vec2 = Arrow(
            axes.c2p(0, 0),
            axes.c2p(eigenvalue2 * eigenvector2[0], eigenvalue2 * eigenvector2[1]),
            buff=0,
            color=GREEN,
            stroke_width=6
        )
        
        eigen_val1_label = MathTex(f"\\lambda_1 = {eigenvalue1}", color=BLUE, font_size=36).next_to(matrix_tex, RIGHT, buff=1.5)
        eigen_val2_label = MathTex(f"\\lambda_2 = {eigenvalue2}", color=GREEN, font_size=36).next_to(eigen_val1_label, DOWN)
        
        self.play(
            Transform(eigen_vec1, scaled_eigen_vec1),
            Write(eigen_val1_label)
        )
        self.wait(1)
        
        self.play(
            Transform(eigen_vec2, scaled_eigen_vec2),
            Write(eigen_val2_label)
        )
        self.wait(1)
        
        # Final explanation
        explanation = VGroup(
            Text("Eigenvectors maintain their direction", font_size=28, color=YELLOW),
            Text("and are only scaled by their eigenvalues", font_size=28, color=YELLOW)
        ).arrange(DOWN).to_edge(DOWN)
        
        self.play(Write(explanation[0]))
        self.wait(0.5)
        self.play(Write(explanation[1]))
        self.wait(2) 