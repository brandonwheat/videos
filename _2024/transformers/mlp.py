from scipy.stats import norm

from manim_imports_ext import *
from _2024.transformers.helpers import *

class LastTwoChapters(InteractiveScene):
    def construct(self):
        # Show last two chapters
        frame = self.frame
        self.camera.light_source.set_z(15)
        self.set_floor_plane("xz")

        folder = "/Users/grant/3Blue1Brown Dropbox/3Blue1Brown/videos/2024/transformers/Thumbnails"
        images = [
            ImageMobject(str(Path(folder, "Chapter5_TN5"))),
            ImageMobject(str(Path(folder, "Chapter6_TN4"))),
        ]
        thumbnails = Group(
            Group(
                SurroundingRectangle(image, buff=0).set_stroke(WHITE, 3),
                image
            )
            for n, image in zip([5, 6], images)
        )
        thumbnails.set_height(3.5)
        thumbnails.arrange(RIGHT, buff=1.0)
        thumbnails.fix_in_frame()
        self.play(
            LaggedStartMap(FadeIn, thumbnails, shift=UP, lag_ratio=0.5)
        )
        self.wait()

        # Show transformer schematic
        blocks = Group(self.get_block() for x in range(10))
        blocks[1::2].stretch(2, 2).set_opacity(1)

        blocks.arrange(OUT, buff=0.5)
        blocks.set_depth(8, stretch=True)
        blocks.set_opacity(0.8)
        blocks.apply_depth_test()

        trans_title = Text("Transformer", font_size=96)
        trans_title.next_to(blocks, UP, buff=0.5)

        self.play(
            frame.animate.reorient(-32, 0, 0, (0.56, 2.48, 0.32), 12.75),
            thumbnails.animate.scale(0.5).arrange(RIGHT, buff=2.0).to_edge(UP, buff=0.25),
            LaggedStartMap(FadeIn, blocks, shift=0.25 * UP, scale=1.5, lag_ratio=0.1),
            FadeIn(trans_title, UP),
        )
        self.wait()

        # Break out transformer as sequence of blocks
        att_blocks = blocks[0::2]
        mlp_blocks = blocks[1::2]

        att_title = Text("Attention", font_size=72)
        mlp_title_full = Text("Multilayer Perceptron", font_size=72)
        mlp_title = Text("MLP", font_size=72)

        self.play(
            frame.animate.reorient(-3, -2, 0, (0.23, 2.57, 0.3), 12.75),
            trans_title.animate.shift(2 * UP),
            att_blocks.animate.shift(4 * LEFT),
            mlp_blocks.animate.shift(4 * RIGHT),
        )

        att_icon = self.get_att_icon(att_blocks[-1])
        mlp_icon = self.get_mlp_icon(mlp_blocks[-1])
        att_title.next_to(att_blocks[-1], UP, buff=0.75)
        for title in [mlp_title, mlp_title_full]:
            title.next_to(mlp_blocks[-1], UP, buff=0.75)
        self.play(
            FadeIn(att_icon, lag_ratio=1e-3),
            FadeIn(att_title, UP),
            trans_title.animate.scale(0.75).set_opacity(0.5)
        )
        self.wait()
        self.play(
            Write(mlp_icon),
            FadeIn(mlp_title_full, UP),
        )
        self.wait()
        self.play(
            TransformMatchingStrings(mlp_title_full, mlp_title)
        )
        self.wait()

        # Show sports facts
        sport_facts = VGroup(
            Text(line)
            for line in Path(DATA_DIR, "athlete_sports.txt").read_text().split("\n")
        )
        for fact in sport_facts:
            fact.next_to(trans_title, UP)
            fact.shift(random.uniform(-3, 3) * RIGHT)
            fact.shift(random.uniform(0, 3) * UP)

        self.play(
            FadeOut(thumbnails),
            FadeOut(trans_title),
            LaggedStart(
                (Succession(FadeIn(fact), fact.animate.scale(0.5).set_opacity(0).move_to(mlp_blocks))
                for fact in sport_facts),
                lag_ratio=0.15,
            )
        )
        self.wait()

        # Ask what is the MLP
        rect = SurroundingRectangle(Group(mlp_blocks, mlp_title), buff=1.0)
        rect.stretch(0.8, 1)
        rect.match_z(mlp_blocks[-1])
        question = Text("What are these?", font_size=90)
        question.next_to(rect, UP, buff=3.0)
        question.match_color(rect)
        question.set_fill(border_width=0.5)
        arrow = Arrow(question, rect)
        arrow.match_color(rect)

        self.play(
            Group(att_blocks, att_title).animate.fade(0.5),
            ShowCreation(rect),
            Write(question),
            GrowArrow(arrow),
        )
        self.wait()

    def get_att_icon(self, block, n_rows=8):
        att_icon = Dot().get_grid(n_rows, n_rows)
        att_icon.set_height(block.get_height() * 0.9)
        att_icon.set_backstroke(BLACK, 0.5)
        for dot in att_icon:
            dot.set_fill(opacity=random.random()**5)
        att_icon.move_to(block, OUT)
        return att_icon

    def get_mlp_icon(self, block):
        layers = VGroup(
            Dot().get_grid(5, 1, buff=0.15),
            Dot().get_grid(10, 1, buff=0.15),
            Dot().get_grid(5, 1, buff=0.15),
        )
        layers.set_height(block.get_height() * 0.9)
        layers.arrange(RIGHT, buff=1.5)
        for layer in layers:
            for dot in layer:
                dot.set_fill(opacity=random.random())
        layers.set_stroke(WHITE, 0.5)
        lines = VGroup(
            Line(dot1.get_center(), dot2.get_center(), buff=dot1.get_width() / 2)
            for l1, l2 in zip(layers, layers[1:])
            for dot1 in l1
            for dot2 in l2
        )
        for line in lines:
            line.set_stroke(
                color=value_to_color(random.uniform(-10, 10)),
                width=3 * random.random()**3
            )

        icon = VGroup(layers, lines)
        icon.move_to(block, OUT)
        return icon

    def get_block(self, width=5, height=3, depth=1, color=GREY_D, opacity=0.8):
        block = Cube(color=color, opacity=opacity)
        block.deactivate_depth_test()
        block.set_shape(width, height, depth)
        block.set_shading(0.5, 0.5, 0.0)
        block.sort(lambda p: np.dot(p, [-1, 1, 1]))
        return block


class BasicMLPWalkThrough(InteractiveScene):
    random_seed = 1

    def construct(self):
        # Init camera settings
        self.set_floor_plane("xz")
        frame = self.frame
        self.camera.light_source.set_z(15)

        # Sequence of embeddings comes in to an MLP block
        embedding_array = EmbeddingArray(shape=(6, 9))
        embedding_array.set_width(10)

        block = VCube(fill_color=GREY_D, fill_opacity=0.5)
        block.sort(lambda p: p[2])
        block[-1].set_fill(opacity=0)
        block.set_stroke(GREY_B, 2, 0.25, background=False)
        block.set_shading(0.25, 0.25, 0.5)
        block.set_shape(11, 4, 4)
        block.move_to(0.5 * IN, IN)
        block_title = Text("MLP", font_size=90)
        block_title.next_to(block, UP)

        frame.reorient(-21, -12, 0, (0.34, -0.94, -0.18), 9.79)
        frame.set_field_of_view(30 * DEGREES)
        self.add(block, block_title)
        self.play(FadeIn(embedding_array, shift=2 * OUT))
        self.wait()

        # Highlight one vector
        index = 3
        emb = embedding_array.embeddings[index]
        highlight_rect = SurroundingRectangle(emb)
        embedding_array.target = embedding_array.generate_target()
        embedding_array.target.set_stroke(width=0)
        embedding_array.target.set_opacity(0.5)
        embedding_array.target[0][index].set_backstroke(BLACK, 2)
        embedding_array.target[0][index].set_opacity(1)

        self.play(
            MoveToTarget(embedding_array),
            ShowCreation(highlight_rect),
        )
        self.wait()

        # Reorient
        rot_about_up = 89 * DEGREES
        rot_about_left = 1 * DEGREES
        up_emb = emb.copy()  # For use down below
        full_block = Group(block, embedding_array, highlight_rect, block_title)
        full_block.target = full_block.generate_target()
        full_block.target[0].set_depth(16, about_edge=IN, stretch=True)
        full_block.target[0].set_height(5, about_edge=DOWN, stretch=True)
        full_block.target.rotate(rot_about_up, UP)
        full_block.target[:3].rotate(rot_about_left, LEFT)
        full_block.target.scale(0.5)
        full_block.target[3].rotate(90 * DEGREES, DOWN).next_to(full_block.target[0], UP, buff=0.5)
        full_block.target.center().to_edge(DOWN, buff=0.75)
        full_block.target[0][4].set_opacity(0.1)

        self.play(
            frame.animate.reorient(-3, -2, 0, (-0.0, -2.0, 0.01), 6.48),
            MoveToTarget(full_block),
            run_time=2
        )

        # Preview the sequence of operations
        values = np.random.uniform(-10, 10, 9)
        values[0] = 1.0
        vects = VGroup(
            NumericEmbedding(values=values, dark_color=GREY_B),
            NumericEmbedding(values=np.clip(values, 0, np.inf), dark_color=GREY_B),
            NumericEmbedding(length=6),
        )
        vects.set_width(emb.get_depth())
        vects.arrange(RIGHT, buff=2.0)
        vects.next_to(emb, RIGHT, buff=2.0)

        arrows = VGroup(
            Arrow(v1, v2)
            for v1, v2 in zip([emb, *vects[:-1]], vects)
        )
        arrow_labels = VGroup(Text("Linear"), Text("ReLU"), Text("Linear"))
        arrow_labels.scale(0.5)

        phases = VGroup()
        simple_phases = VGroup()
        for arrow, label, vect in zip(arrows, arrow_labels, vects):
            label.next_to(arrow, UP)
            phases.add(VGroup(arrow, label, vect))
            simple_phases.add(VGroup(arrow, vect))

        self.play(
            LaggedStartMap(FadeIn, vects, shift=RIGHT, lag_ratio=0.8),
            LaggedStartMap(ShowCreation, arrows, lag_ratio=0.8),
            LaggedStartMap(FadeIn, arrow_labels, lag_ratio=0.8),
        )
        self.wait()

        # Show the sum
        sum_circuit, output_emb = self.get_sum_circuit(emb, vects[-1])

        self.play(
            frame.animate.reorient(15, -4, 0, (0.82, -1.91, 0.04), 7.18),
            ShowCreation(sum_circuit, lag_ratio=0.1),
            run_time=2
        )
        self.play(
            TransformFromCopy(emb, output_emb, path_arc=-30 * DEGREES),
            TransformFromCopy(vects[2], output_emb, path_arc=-30 * DEGREES),
            run_time=2
        )
        self.wait()

        # Show all in parallel
        simple_phases.add_to_back(highlight_rect)
        simple_phases.add(VGroup(sum_circuit, output_emb))
        simple_phase_copies = VGroup(
            simple_phases.copy().match_z(emb)
            for emb in embedding_array.embeddings
        )
        for sp_copy in simple_phase_copies:
            for group in sp_copy[1:]:
                arrow, vect = group
                for entry in vect.get_entries():
                    dot = Dot().scale(0.5)
                    dot.match_color(entry)
                    dot.set_fill(opacity=0.5)
                    dot.move_to(entry)
                    entry.become(dot)
                group.fade(0.5)

        self.play(
            frame.animate.reorient(0, -48, 0, (0.55, -2.21, 0.18), 7.05),
            LaggedStart((
                TransformFromCopy(simple_phases, sp_copy)
                for sp_copy in simple_phase_copies
            ), lag_ratio=0.1),
            FadeOut(block_title, time_span=(0, 1)),
            run_time=3,
        )
        self.play(frame.animate.reorient(9, -15, 0, (0.55, -2.21, 0.18), 7.05), run_time=4)
        block_title.next_to(block, UP)
        self.play(
            frame.animate.to_default_state(),
            LaggedStartMap(FadeOut, simple_phase_copies, lag_ratio=0.1),
            FadeIn(block_title),
            run_time=2,
        )
        self.wait()

        # Show MJ -> Basketball example
        example_fact = TexText("``Michael Jordan plays Basketball''", font_size=60)
        example_fact.to_edge(UP)

        mj = TexText("Michael Jordan", font_size=36)
        mj.next_to(emb, UL)
        mj_lines = VGroup(
            Line(char.get_bottom(), emb.get_top(), buff=0.1, path_arc=10 * DEGREES)
            for char in mj
        )
        mj_lines.set_stroke(YELLOW, 1, 0.5)

        basketball = TexText("Basketball", font_size=24)
        basketball.next_to(vects[2], UP, buff=0.2)

        self.play(Write(example_fact))
        self.wait()
        self.play(FadeTransform(example_fact[mj.get_tex()].copy(), mj))
        self.play(Write(mj_lines, stroke_width=2, stroke_color=YELLOW_B, lag_ratio=1e-2))
        self.wait()

        mover = emb.copy()
        for vect in vects:
            self.play(Transform(mover, vect, rate_func=linear))
        self.remove(mover)
        self.wait()
        self.play(FadeTransform(example_fact[basketball.get_tex()].copy(), basketball))
        self.wait(2)

        # Multiply by the up-projection
        up_proj = WeightMatrix(shape=(9, 6))
        up_proj.set_height(3)
        up_proj.to_corner(UL)
        up_emb.set_height(2)
        up_emb.next_to(up_proj, RIGHT)
        up_emb[-2:].set_fill(YELLOW)  # Brackets

        self.play(
            phases[1:].animate.set_opacity(0.1),
            sum_circuit.animate.set_stroke(opacity=0.1),
            output_emb.animate.set_opacity(0.1),
            FadeOut(mj),
            FadeOut(mj_lines),
            FadeOut(basketball),
            FadeOut(example_fact),
        )
        self.wait()
        self.play(TransformFromCopy(emb, up_emb))
        self.play(FadeIn(up_proj, lag_ratio=0.01))
        eq, rhs = show_matrix_vector_product(self, up_proj, up_emb)
        self.wait()
        data_modifying_matrix(self, up_proj, word_shape=(4, 7), fix_in_frame=True)
        self.wait()

        # Show machine
        machine = MachineWithDials(
            width=up_proj.get_width() + SMALL_BUFF,
            height=up_proj.get_height() + SMALL_BUFF,
            n_rows=8,
            n_cols=9,
        )
        machine.move_to(up_proj)

        self.play(FadeIn(machine))
        self.play(machine.random_change_animation())
        self.wait()
        self.play(FadeOut(machine))

        # Emphasize dot product with rows
        n, m = up_proj.shape
        n_rows_shown = 5
        R_labels = VGroup(
            Tex(R"\vec{\textbf{R}}_" + f"{{{n}}}")
            for n in [*range(n_rows_shown - 1), "n"]
        )
        R_labels[-2].become(Tex(R"\vdots").replace(R_labels[-2], dim_to_match=1))
        R_labels.arrange(DOWN, buff=0.5)
        R_labels.match_height(up_proj)
        R_labels.move_to(up_proj)
        h_lines = VGroup(
            Line(up_proj.get_brackets()[0], R_labels, buff=0.1),
            Line(R_labels, up_proj.get_brackets()[1], buff=0.1),
        )
        h_lines.set_stroke(GREY_A, 2)
        row_labels = VGroup(
            VGroup(R_label, h_lines.copy().match_y(R_label))
            for R_label in R_labels
        )
        row_matrix = VGroup(
            up_proj.get_brackets().copy(),
            row_labels
        )

        E_label = Tex(R"\vec{\textbf{E}}")
        E_label.match_height(R_labels[0])
        E_label.set_color(YELLOW)
        E_label.move_to(up_emb)
        E_col = VGroup(
            up_emb[-2:].copy(),
            Line(up_emb.get_top(), E_label, buff=0.1).set_stroke(GREY_A, 2),
            E_label,
            Line(E_label, up_emb.get_bottom(), buff=0.1).set_stroke(GREY_A, 2),
        )

        dot_prods = VGroup()
        for n, R_label in enumerate(R_labels):
            if n == len(R_labels) - 2:
                dot_prod = R_label.copy()
            else:
                dot_prod = VGroup(
                    R_label.copy(),
                    Tex(R"\cdot"),
                    E_label.copy(),
                )
                dot_prod.arrange(RIGHT, buff=0.1)
                dot_prod[-1].align_to(dot_prod[0][1], DOWN)
                dot_prod.set_width(rhs.get_width() * 0.75)
            dot_prod.move_to(R_label)
            dot_prods.add(dot_prod)
        dot_prods.move_to(rhs)
        dot_prod_rhs = VGroup(
            rhs.get_brackets().copy(),
            dot_prods,
        )

        self.play(LaggedStart(
            FadeOut(up_proj, scale=1.1),
            FadeIn(row_matrix, scale=1.1),
            FadeOut(up_emb, scale=1.1),
            FadeIn(E_col, scale=1.1),
            FadeOut(rhs, scale=1.1),
            FadeIn(dot_prod_rhs[0], scale=1.1),
            lag_ratio=0.1
        ))
        self.wait()
        for row_label, dot_prod in zip(row_labels, dot_prods):
            R_label = row_label[0]
            self.play(
                TransformFromCopy(R_label, dot_prod[0]),
                TransformFromCopy(R_label, dot_prod[1]),
                TransformFromCopy(E_label, dot_prod[2]),
                VShowPassingFlash(
                    Line(row_label.get_left(), row_label.get_right()).set_stroke(YELLOW, 5).insert_n_curves(100),
                    time_width=1.5
                ),
                VShowPassingFlash(
                    Line(E_col.get_top(), E_col.get_bottom()).set_stroke(YELLOW, 5).insert_n_curves(100),
                    time_width=1.5
                ),
                run_time=1
            )
        self.wait()

        # First name Michael direction
        row_rect = SurroundingRectangle(row_labels[0])
        row_rect.set_stroke(GREY_BROWN, 2)
        row_rect.set_fill(GREY_BROWN, 0.25)
        row_eq = Tex("=").rotate(PI / 2)
        row_eq.next_to(row_rect, UP, SMALL_BUFF)
        first_name_label = Tex(R"\overrightarrow{\text{First Name Michael}}")
        first_name_label.set_stroke(WHITE, 1)
        first_name_label.match_width(row_rect)
        first_name_label.next_to(row_eq, UP)

        dot_prod = dot_prods[0]
        dp_rect = SurroundingRectangle(dot_prod, buff=0.2)
        dp_rect.set_stroke(RED)
        dp_eq = Tex("=")
        dp_eq.next_to(dp_rect, RIGHT, SMALL_BUFF)
        mde_rhs = VGroup(
            Tex(R"\approx 1 \quad \text{If } \vec{\textbf{E}} \text{ encodes ``First Name Michael''}"),
            Tex(R"\le 0 \quad \text{If not}")
        )
        mde_rhs[0][R"\vec{\textbf{E}}"].set_color(YELLOW)
        mde_rhs.scale(0.75)
        mde_rhs.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        rhs_brace = Brace(mde_rhs, LEFT)
        rhs_brace.next_to(dp_eq, RIGHT, SMALL_BUFF)
        mde_rhs.next_to(rhs_brace, RIGHT, MED_SMALL_BUFF)

        self.play(
            FadeIn(row_rect, scale=2),
            FadeTransform(row_labels[0].copy(), first_name_label),
            GrowFromCenter(row_eq),
            frame.animate.reorient(0, 0, 0, (0.22, 0.54, 0.0), 9.27),
        )
        self.wait()

        self.play(TransformFromCopy(row_rect.copy().set_fill(opacity=0), dp_rect))
        self.play(
            Write(dp_eq),
            GrowFromCenter(rhs_brace),
            FadeIn(mde_rhs),
        )
        self.wait()

        # "First name Michael" + "Last name Jordan"
        fn_tex = R"\overrightarrow{\text{F.N. Michael}}"
        ln_tex = R"\overrightarrow{\text{L.N. Jordan}}"
        name_sum_label = Tex(f"{fn_tex} + {ln_tex}")
        name_sum_label.match_width(row_rect).scale(1.2)
        name_sum_label.next_to(row_eq, UP)

        self.play(
            FadeTransform(first_name_label, name_sum_label[:21]),
            FadeIn(name_sum_label[21:], shift=RIGHT, scale=2),
            FadeOut(mde_rhs),
            FadeOut(rhs_brace),
        )
        self.wait()

        dist_rhs = VGroup(
            Tex(R"(\vec{\textbf{M}} + \vec{\textbf{J}}) \cdot \vec{\textbf{E}}"),
            Tex("="),
            Tex(R"\vec{\textbf{M}} \cdot \vec{\textbf{E}} + \vec{\textbf{J}} \cdot \vec{\textbf{E}}"),
        )
        dist_rhs.scale(0.75)
        dist_rhs.arrange(RIGHT, buff=0.2)
        dist_rhs.next_to(dp_eq, RIGHT)
        for part in dist_rhs:
            part[R"\vec{\textbf{M}}"].set_color(RED_B)
            part[R"\vec{\textbf{J}}"].set_color(RED)
            part[R"\vec{\textbf{E}}"].set_color(YELLOW)
        under_brace = Brace(dist_rhs[2])

        two_condition = TexText(R"$\approx 2$ \; if $\vec{\textbf{E}}$ encodes ``Michael Jordan''")
        two_condition[R"\vec{\textbf{E}}"].set_color(YELLOW)
        else_condition = TexText(R"$\le 1$ \; Otherwise")
        VGroup(two_condition, else_condition).scale(0.75)
        two_condition.next_to(under_brace, DOWN, aligned_edge=LEFT)
        else_condition.next_to(two_condition, DOWN, MED_LARGE_BUFF, aligned_edge=LEFT)

        self.play(LaggedStart(
            FadeTransformPieces(name_sum_label[:21].copy(), dist_rhs[0][1:3]),
            FadeTransformPieces(name_sum_label[21].copy(), dist_rhs[0][3]),
            FadeTransformPieces(name_sum_label[22:].copy(), dist_rhs[0][4:6]),
            FadeTransformPieces(dot_prod[1:].copy(), dist_rhs[0][7:]),
            FadeIn(dist_rhs[0][0]),
            FadeIn(dist_rhs[0][6]),
            lag_ratio=0.2
        ))
        self.wait()
        self.play(
            TransformMatchingStrings(dist_rhs[0].copy(), dist_rhs[2], lag_ratio=0.01, path_arc=-45 * DEGREES),
            Write(dist_rhs[1])
        )
        self.wait()
        self.play(
            frame.animate.set_y(0.5),
            GrowFromCenter(under_brace),
            FadeIn(two_condition, DOWN)
        )
        self.wait()
        self.play(FadeIn(else_condition, DOWN))
        self.wait(2)

        # Go back to the numbers
        for entry in rhs.get_entries():
            entry.set_value(np.random.uniform(-10, 10))
        rhs.get_entries()[0].set_value(2.0)
        self.play(
            LaggedStart(*map(FadeOut, [
                name_sum_label, row_eq, row_rect,
                dp_rect, dp_eq, dist_rhs, under_brace,
                two_condition, else_condition,
            ]), lag_ratio=0.1, run_time=1),
            frame.animate.reorient(0, 0, 0, (-0.06, -0.06, 0.0), 8.27),
        )
        self.play(
            FadeOut(row_matrix),
            FadeIn(up_proj),
            FadeOut(E_col),
            FadeIn(up_emb),
            FadeOut(dot_prod_rhs),
            FadeIn(rhs),
        )

        # Show other rows
        questions = VGroup(*map(Text, [
            "Blah",
            "Is it English?",
            "Part of sourcecode?",
            "European country?",
            "In quotation marks?",
            "Something metalic?",
            "A four-legged animal?",
        ]))
        questions.scale(0.75)
        rows = up_proj.get_rows()
        rhs_entries = rhs.get_entries()
        last_question = VGroup()
        last_rect = VectorizedPoint(rows[1].get_top())
        for index in range(1, 7):
            for mob in [rows, rhs_entries]:
                mob.target = mob.generate_target()
                mob.target.set_opacity(0.25)
                mob.target[index].set_opacity(1)
            row_rect = SurroundingRectangle(rows[index])
            row_rect.set_stroke(PINK, 2)
            question = questions[index]
            question.next_to(rows[index], UP, buff=0.15)
            question.set_backstroke(BLACK, 3)
            self.play(
                MoveToTarget(rows),
                MoveToTarget(rhs_entries),
                FadeOut(last_question),
                FadeIn(question),
                FadeTransform(last_rect, row_rect, time_span=(0, 0.75)),
                run_time=1.0
            )
            self.wait(0.5)
            last_question = question
            last_rect = row_rect
        self.play(
            rows.animate.set_opacity(1),
            rhs.animate.set_opacity(1),
            FadeOut(last_question),
            FadeOut(last_rect),
        )
        self.wait()

        # Add a bias
        plus = Tex("+")
        plus.next_to(up_emb, RIGHT)
        bias = WeightMatrix(shape=(9, 1), ellipses_col=None)
        bias.get_entries()[0].set_value(-1).set_color(RED)
        bias.match_height(up_proj)
        bias.next_to(plus)
        bias_name = Text("Bias")
        bias_name.next_to(bias, UP)

        eq.target = eq.generate_target()
        eq.target.next_to(bias, RIGHT)
        rhs.target = vects[0].copy()
        rhs.target.replace(rhs, dim_to_match=1)
        rhs.target.next_to(eq.target, RIGHT)

        self.play(
            Write(plus),
            FadeIn(bias, lag_ratio=0.1),
            MoveToTarget(eq),
            MoveToTarget(rhs),
        )
        self.wait()
        self.play(
            frame.animate.scale(1.1, about_edge=DOWN),
            Write(bias_name),
        )
        self.wait()

        # Emphasize the parameters are learned from data
        data_modifying_matrix(self, bias, word_shape=(5, 1), alpha_maxes=(0.4, 0.9), fix_in_frame=True)
        bias.get_entries()[0].set_value(-1).set_color(RED)

        # Pull up the MJ example again
        fe_rect = SurroundingRectangle(rhs.get_entries()[0], buff=0.1)  # fe = First entry
        fe_rect.set_stroke(RED, 3)
        fe_eq = Tex("=")
        fe_eq.next_to(fe_rect, RIGHT, SMALL_BUFF)
        fe_expr = VGroup(dist_rhs[2].copy(), Tex("- 1"))
        fe_expr[1].set_height(fe_expr[0].get_height() * 0.8)
        fe_expr.arrange(RIGHT)
        fe_expr.next_to(fe_eq, RIGHT)

        bias_rect = SurroundingRectangle(bias.get_entries()[0])

        self.play(
            ShowCreation(fe_rect),
            FadeIn(fe_eq, RIGHT),
            Write(fe_expr)
        )
        self.wait()
        self.play(ShowCreation(bias_rect))
        self.wait()
        self.play(bias_rect.animate.surround(fe_expr[1]))
        self.wait()
        self.play(bias_rect.animate.surround(fe_expr))
        self.wait()

        # Show what it means, but now shifted
        conditions = VGroup(
            TexText(R"$\approx 1$ \; if $\vec{\textbf{E}}$ encodes ``Michael Jordan''"),
            TexText(R"$\le 0$ \; Otherwise"),
        )
        conditions[0][R"\vec{\textbf{E}}"].set_color(YELLOW)
        conditions.scale(0.75)
        conditions.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        under_brace = Brace(fe_expr, DOWN)
        conditions.next_to(under_brace, DOWN, aligned_edge=LEFT)

        self.play(
            FadeOut(bias_rect),
            GrowFromCenter(under_brace),
            FadeIn(conditions[0], DOWN)
        )
        self.wait()
        self.play(FadeIn(conditions[1], 0.25 * DOWN))
        self.wait(2)

        self.play(
            frame.animate.reorient(0, 0, 0, (-2.5, 0.44, 0.0), 9.33),
            LaggedStart(*map(FadeOut, [
                fe_rect, fe_eq, fe_expr,
                under_brace, *conditions
            ]))
        )

        # Show the matrix size
        up_proj.refresh_bounding_box()
        row_rects = VGroup(
            SurroundingRectangle(row, buff=0.1)
            for row in up_proj.get_rows()
        )
        row_rects.set_stroke(WHITE, 1)
        row_rects.set_fill(GREY_C, 0.25)
        row_rects[-2].match_width(row_rects, stretch=True)

        over_brace = Brace(row_rects[0], UP, buff=SMALL_BUFF)
        row_size = Integer(12288)
        row_size.next_to(over_brace, UP)
        side_brace = Brace(row_rects, LEFT)
        num_rows = Integer(4 * 12288)
        num_rows.next_to(side_brace, LEFT)
        num_rows_expr = Tex(R"4 \times 12{,}288")
        num_rows_expr.next_to(side_brace, LEFT)

        self.play(
            FadeIn(row_rects, lag_ratio=0.5),
            GrowFromCenter(side_brace),
            CountInFrom(num_rows)
        )
        self.wait()
        self.play(FadeTransform(num_rows, num_rows_expr))
        self.wait()
        self.play(
            FadeTransform(num_rows_expr["12{,}288"].copy(), row_size),
            TransformFromCopy(side_brace, over_brace),
        )
        self.wait()
        self.play(FadeOut(row_rects, lag_ratio=0.1))

        # Collapse
        substrs = [R"W_\uparrow", R"\vec{\textbf{E}}_i", "+", R"\vec{\textbf{B}}_\uparrow"]
        linear_expr = Tex(" ".join(substrs))
        globals().update(locals())
        W_up, E_i, plus2, B_up = [linear_expr[ss] for ss in substrs]
        VGroup(W_up, B_up).set_color(BLUE)
        E_i.set_color(YELLOW)
        linear_expr.move_to(plus).shift(0.6 * LEFT)

        low_emb_label = E_i.copy()
        low_emb_label.scale(0.5).next_to(emb, UP)

        self.play(
            frame.animate.reorient(0, 0, 0, (-0.03, 0.03, 0.0), 8.34),
            ReplacementTransform(up_proj, W_up, lag_ratio=1e-3),
            FadeOut(side_brace, RIGHT, scale=0.5),
            FadeOut(num_rows_expr, RIGHT, scale=0.5),
            FadeOut(over_brace, DR, scale=0.5),
            FadeOut(row_size, DR, scale=0.5),
        )
        self.wait()
        self.play(ReplacementTransform(up_emb, E_i, lag_ratio=1e-2))
        self.play(TransformFromCopy(E_i, low_emb_label))
        self.wait()
        self.play(
            ReplacementTransform(plus, plus2),
            ReplacementTransform(bias, B_up, lag_ratio=1e-2),
            FadeOut(bias_name, DL),
            VGroup(eq, rhs).animate.next_to(B_up, RIGHT).shift(0.1 * DOWN),
            run_time=2
        )
        self.wait()

        # Add parameters below first linear arrow
        self.play(
            linear_expr.animate.scale(0.5).next_to(arrows[0], DOWN, buff=0.1),
            ReplacementTransform(rhs, vects[0]),
            FadeOut(eq, 4 * DOWN + LEFT),
            run_time=2
        )
        self.wait()

        # Pull up ReLU
        self.play(phases[1].animate.set_opacity(1))
        phase1_copy = VGroup(vects[0], arrows[1], vects[1]).copy()
        phase1_copy.save_state()

        self.play(
            phase1_copy.animate.scale(2.0).next_to(full_block, UP, buff=0.5),
            frame.animate.reorient(0, 0, 0, (-0.26, 0.54, 0.0), 9.40)
        )
        self.wait()

        # Break down ReLU
        relu_arrow = phase1_copy[1]
        neg_arrows = VGroup()
        pos_arrows = VGroup()
        neg_left_rects = VGroup()
        zero_right_rects = VGroup()
        pos_left_rects = VGroup()
        pos_right_rects = VGroup()
        in_vect = phase1_copy[0]
        out_vect = phase1_copy[2]
        for e1, e2 in zip(in_vect.get_entries(), out_vect.get_entries()):
            arrow = Arrow(e1, e2, buff=0.3)
            if e1.get_value() > 0:
                arrow.set_color(BLUE)
                pos_arrows.add(arrow)
                pos_left_rects.add(SurroundingRectangle(e1, color=BLUE))
                pos_right_rects.add(SurroundingRectangle(e2, color=BLUE))
            else:
                arrow.set_color(RED)
                neg_arrows.add(arrow)
                neg_left_rects.add(SurroundingRectangle(e1, color=RED))
                zero_right_rects.add(SurroundingRectangle(e2, color=RED))
        VGroup(neg_left_rects, zero_right_rects, pos_left_rects, pos_right_rects).set_stroke(width=2)

        self.play(ShowCreation(neg_left_rects, lag_ratio=0.5))
        self.wait()
        self.play(
            TransformFromCopy(neg_left_rects, zero_right_rects, lag_ratio=0.5),
            ShowCreation(neg_arrows, lag_ratio=0.5),
            FadeOut(relu_arrow),
        )
        self.wait()
        self.play(
            FadeOut(neg_left_rects, lag_ratio=0.25),
            FadeOut(zero_right_rects, lag_ratio=0.25),
            FadeOut(neg_arrows, lag_ratio=0.25),
            ShowCreation(pos_left_rects)
        )
        self.wait()
        self.play(
            ShowCreation(pos_arrows, lag_ratio=0.5),
            TransformFromCopy(pos_left_rects, pos_right_rects, lag_ratio=0.5),
        )
        self.wait()

        # Graph ReLU
        relu_title_full = Text("Rectified\nLinear\nUnit", alignment="LEFT")
        relu_title_full.next_to(relu_arrow, UP)

        axes = Axes((-4, 4), (-1, 4))
        axes.set_width(6)
        axes.next_to(phase1_copy, RIGHT, buff=1.0)
        axes.add_coordinate_labels(font_size=16)
        relu_graph = axes.get_graph(lambda x: max(0, x), discontinuities=[0])
        relu_graph.set_stroke(YELLOW, 4)
        plot = VGroup(axes, relu_graph)

        relu_graph_label = Text("ReLU")
        relu_graph_label.match_color(relu_graph)
        relu_graph_label.move_to(axes, UL)

        self.play(
            frame.animate.set_x(2.7),
            FadeIn(relu_arrow),
            FadeIn(relu_title_full, 0.1 * UP, lag_ratio=0.1, run_time=2),
            FadeOut(pos_arrows, lag_ratio=0.25),
            FadeOut(pos_left_rects, lag_ratio=0.25),
            FadeOut(pos_right_rects, lag_ratio=0.25),
            FadeIn(plot, RIGHT),
        )
        self.wait()
        self.play(*(
            TransformFromCopy(relu_title_full[substr], relu_graph_label[substr])
            for substr in ["Re", "L", "U"]
        ))
        self.add(relu_graph_label)

        # Recall the meaning of the first entry
        mid_vect = phase1_copy[0]
        conditions_rect = SurroundingRectangle(conditions, buff=0.25)
        conditions_rect.set_stroke(YELLOW, 1)
        under_brace = Brace(conditions_rect, DOWN, buff=SMALL_BUFF)
        VGroup(conditions, conditions_rect, under_brace).next_to(mid_vect, UP)
        fe_rect = SurroundingRectangle(mid_vect.get_entries()[0])

        condition_group = VGroup(fe_rect, under_brace, conditions, conditions_rect)

        self.play(
            frame.animate.reorient(0, 0, 0, (2.61, 0.97, 0.0), 11.5),
            ShowCreation(fe_rect),
            GrowFromCenter(under_brace),
        )
        self.play(
            TransformFromCopy(fe_rect, conditions_rect),
            FadeInFromPoint(conditions, fe_rect.get_center()),
        )
        self.wait()
        self.play(condition_group.animate.match_x(phase1_copy[2]))

        equals = Tex("=")
        ineq = conditions[1][0]
        equals.replace(ineq, dim_to_match=0)
        self.play(
            FlashAround(equals, run_time=2, time_width=1.5),
            ineq.animate.become(equals)
        )
        self.wait()
        self.play(
            frame.animate.reorient(0, 0, 0, (2.48, 0.33, 0.0), 9.17),
            FadeOut(condition_group, lag_ratio=0.01)
        )

        # Graph GeLU
        gelu_title_full = Text("Gaussian\nError\nLinear\nUnit", font_size=42, alignment="LEFT")
        gelu_title_full.next_to(relu_arrow, UP)
        gelu_graph = axes.get_graph(lambda x: x * norm.cdf(x))
        gelu_graph.set_stroke(GREEN, 4)

        gelu_graph_label = Text("GELU")
        gelu_graph_label.next_to(relu_graph_label, DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        gelu_graph_label.match_color(gelu_graph)

        self.play(
            FadeTransform(relu_title_full, gelu_title_full),
            relu_graph_label.animate.set_fill(opacity=0.25),
            relu_graph.animate.set_stroke(opacity=0.25),
            ShowCreation(gelu_graph),
            TransformFromCopy(relu_graph_label, gelu_graph_label)
        )
        self.wait(2)
        self.play(
            gelu_graph.animate.set_stroke(opacity=0.25),
            gelu_graph_label.animate.set_fill(opacity=0.25),
            relu_graph.animate.set_stroke(opacity=1),
            relu_graph_label.animate.set_fill(opacity=1),
            FadeTransform(gelu_title_full, relu_title_full),
        )
        self.wait()

        # Describe these as neurons
        neuron_word = Text("Neurons", font_size=72)
        neuron_word.next_to(phase1_copy, RIGHT, buff=2.5)
        neuron_arrows = VGroup(
            Arrow(neuron_word.get_left(), entry.get_right(), buff=0.4, stroke_width=3)
            for entry in phase1_copy[2].get_entries()
        )

        self.play(
            plot.animate.set_width(2).next_to(relu_arrow, DOWN),
            FadeOut(VGroup(relu_graph_label, gelu_graph_label, gelu_graph)),
            Write(neuron_word),
            ShowCreation(neuron_arrows, lag_ratio=0.2, run_time=3),
            LaggedStartMap(
                FlashAround, phase1_copy[2].get_entries(),
                time_width=3.0,
                lag_ratio=0.05,
                time_span=(1, 4),
                run_time=4
            )
        )
        self.wait()

        # Show the classic dots picture
        blocking_rect = BackgroundRectangle(VGroup(phase1_copy), buff=0.1)
        blocking_rect.set_fill(BLACK, 1)
        up_emb.move_to(blocking_rect, LEFT)
        dots = VGroup(
            Dot(radius=0.15).move_to(entry).set_fill(WHITE, opacity=clip(entry.get_value(), 0, 1))
            for entry in phase1_copy[2].get_entries()
        )
        dots.set_stroke(WHITE, 2)
        up_emb = emb.copy()
        up_emb.rotate(PI / 2, DOWN)
        up_emb.rotate(1 * DEGREES)
        up_emb.match_width(phase1_copy[0])
        up_emb.move_to(phase1_copy[0]).shift(RIGHT)
        up_emb[-2:].set_color(YELLOW)
        lines = VGroup(
            Line(entry.get_right() + 0.05 * RIGHT, dot).set_stroke(
                color=value_to_color(random.uniform(-10, 10)),
                width=3 * random.random()**2,
            )
            for entry in up_emb.get_entries()
            for dot in dots
        )

        self.play(
            FadeIn(blocking_rect),
            Write(dots),
        )
        self.play(TransformFromCopy(emb, up_emb))
        self.play(ShowCreation(lines, lag_ratio=3 / len(lines)))
        self.wait()
        self.play(
            LaggedStart(*map(FadeOut, [up_emb, *lines, blocking_rect, *dots]), lag_ratio=0.01)
        )

        # Discuss active and inactive
        entry = phase1_copy[2].get_entries()[0]
        entry_rect = SurroundingRectangle(entry)
        entry_rect.set_stroke(YELLOW, 2)
        active_words = TexText(R"``Michael Jordan'' neuron is \emph{active}")
        active = active_words["active"][0]
        active.set_color(BLUE_B)
        active_words.next_to(entry_rect, UP, aligned_edge=LEFT)
        active_words.shift(LEFT)
        inactive = TexText(R"\emph{inactive}")
        inactive.set_color(RED)
        inactive.move_to(active, LEFT)

        self.play(
            frame.animate.reorient(0, 0, 0, (2.45, 0.58, 0.0), 9.65),
            ShowCreation(entry_rect),
            Write(active_words, run_time=1),
        )
        self.wait()
        self.play(
            ChangeDecimalToValue(entry, 0),
            ReplacementTransform(active, inactive)
        )
        active_words.add(inactive)
        self.wait()

        # Replace the ReLU diagram portion
        self.play(
            Restore(phase1_copy),
            TransformMatchingStrings(relu_title_full, arrow_labels[1]),
            plot.animate.scale(0.5).next_to(arrows[1], DOWN, SMALL_BUFF),
            FadeOut(neuron_word, DOWN),
            FadeOut(neuron_arrows, DOWN, lag_ratio=0.1),
            FadeOut(entry_rect, DOWN),
            FadeOut(active_words, DOWN, lag_ratio=0.01),
            run_time=1.5
        )
        self.remove(phase1_copy)

        # Down projection
        neurons = vects[1].copy()
        neurons.target = neurons.generate_target()
        neurons.target.set_height(4)
        neurons.target.move_to(3 * RIGHT + 2.5 * UP)
        down_proj = WeightMatrix(shape=(6, 9))
        down_proj.set_height(2.75)
        down_proj.next_to(neurons.target, LEFT)

        plus = Tex("+")
        plus.next_to(neurons.target, RIGHT)
        bias = WeightMatrix(shape=(6, 1))
        bias.match_height(down_proj)
        bias.next_to(plus, RIGHT)

        equals = Tex("=")
        equals.next_to(bias, RIGHT)
        rhs = vects[2].copy()
        rhs.set_opacity(1)
        rhs.match_height(bias)
        rhs.next_to(equals, RIGHT)

        self.play(phases[2].animate.set_opacity(1))
        self.play(MoveToTarget(neurons))
        self.play(FadeTransform(arrows[2].copy(), down_proj))
        self.wait()
        temp_eq, temp_rhs = show_matrix_vector_product(self, down_proj, neurons)
        self.wait()
        self.play(
            FadeOut(temp_eq, DOWN),
            FadeOut(temp_rhs, DOWN),
            Write(plus),
            FadeIn(bias, RIGHT),
        )
        self.wait()
        self.play(
            Write(equals),
            TransformFromCopy(vects[2], rhs),
        )
        self.wait()

        # Name it as the down-projection
        over_brace = Brace(down_proj, UP)
        name = TexText("``Down projection''")
        name.next_to(over_brace, UP)

        side_brace = Brace(rhs, RIGHT)
        dim_count = Integer(12288)
        dim_count.next_to(side_brace, RIGHT)

        self.play(
            CountInFrom(dim_count),
            GrowFromCenter(side_brace),
        )
        self.wait()
        self.play(
            Write(name),
            GrowFromCenter(over_brace),
        )
        self.wait()

        # Show column-by-column
        col_matrix = self.get_col_matrix(down_proj, 7)
        bias_as_col = self.get_col_matrix(bias, 1, dots_index=None, sym="B", top_index="", width_multiple=0.7)
        n_labels = VGroup(
            Tex(f"n_{{{m}}}")
            for m in [*range(6), "m"]
        )
        n_labels.arrange(DOWN, buff=0.5)
        n_labels.match_height(neurons.get_entries())
        n_labels.move_to(neurons.get_entries())
        n_labels.replace_submobject(-2, Tex(R"\vdots").move_to(n_labels[-2]))
        n_labels.set_color(BLUE)
        n_vect = VGroup(neurons[-2:].copy(), n_labels)

        self.play(
            LaggedStart(*map(FadeOut, [over_brace, name, side_brace, dim_count])),
            LaggedStart(
                FadeOut(down_proj),
                FadeIn(col_matrix),
                FadeOut(neurons),
                FadeIn(n_vect),
                FadeOut(bias),
                FadeIn(bias_as_col),
            )
        )
        self.wait()

        # Expand the column interpretation
        over_brace = Brace(VGroup(col_matrix, n_vect), UP)
        scaled_cols = VGroup(
            VGroup(n_label, col_label[0]).copy()
            for n_label, col_label in zip(n_labels, col_matrix[1])
        )
        scaled_cols.target = VGroup()
        for pair in scaled_cols:
            pair.target = pair.generate_target()
            pair.target[0].scale(1.5)
            pair.target.arrange(RIGHT, buff=0.1, aligned_edge=DOWN)
            scaled_cols.target.add(pair.target)
        scaled_cols.target[-2].become(Tex(R"\dots"))
        scaled_cols.target.arrange(RIGHT, buff=0.75)
        scaled_cols.target.set_width(1.25 * over_brace.get_width())
        scaled_cols.target.next_to(over_brace, UP, buff=0.5)

        plusses = VGroup(
            Tex("+").move_to(midpoint(m1.get_right(), m2.get_left()))
            for m1, m2 in zip(scaled_cols.target, scaled_cols.target[1:])
        )

        self.play(
            frame.animate.reorient(0, 0, 0, (-0.27, 1.04, 0.0), 11.06),
            GrowFromCenter(over_brace),
            LaggedStartMap(MoveToTarget, scaled_cols, lag_ratio=0.7, run_time=5),
            LaggedStartMap(FadeIn, plusses, lag_ratio=0.7, run_time=5),
        )
        self.wait()

        # Highlight each set
        last_rects = VGroup()
        all_rect_groups = VGroup()
        for tup in zip(col_matrix[1], n_labels, scaled_cols):
            rects = VGroup(SurroundingRectangle(mob) for mob in tup)
            rects.set_stroke(YELLOW, 2)
            self.play(
                FadeOut(last_rects),
                FadeIn(rects),
            )
            self.wait(0.5)
            all_rect_groups.add(rects)
            last_rects = rects
        self.play(FadeOut(last_rects))

        # First column as basketball
        col_rect, n_rect, prod_rect = rects = all_rect_groups[0]
        basketball = Text("Basketball", font_size=60)
        basketball.set_color("#F88158")
        basketball.next_to(col_rect, LEFT)
        basketball.save_state()
        basketball.rotate(-PI / 2)
        basketball.move_to(col_rect)
        basketball.set_opacity(0)

        n0_term = scaled_cols[0][0]
        n0_term.save_state()
        one = Tex("1", font_size=60).move_to(n0_term, DR).set_color(BLUE)
        zero = Tex("0", font_size=60).move_to(n0_term, DR).set_color(RED)

        self.play(
            ShowCreation(col_rect),
            col_matrix[1][1:].animate.set_opacity(0.5),
            n_labels[1:].animate.set_opacity(0.5),
            scaled_cols[1:].animate.set_opacity(0.5),
            plusses.animate.set_opacity(0.5)
        )
        self.play(Restore(basketball, path_arc=PI / 2))
        self.wait()
        self.play(TransformFromCopy(col_rect, n_rect))
        self.wait()
        self.play(
            TransformFromCopy(col_rect, prod_rect),
            TransformFromCopy(n_rect, prod_rect),
        )
        self.play(Transform(n0_term, one))
        self.wait()
        self.play(Transform(n0_term, zero))
        self.wait()
        self.play(Restore(n0_term))
        n0_term.restore()
        self.wait()

        # Cycle through columns one more time
        rects.add(basketball)
        for index in range(1, len(all_rect_groups)):
            self.play(
                FadeOut(all_rect_groups[index - 1]),
                FadeIn(all_rect_groups[index]),
                col_matrix[1][index].animate.set_opacity(1),
                n_labels[index].animate.set_opacity(1),
                scaled_cols[index].animate.set_opacity(1),
                plusses[index - 1].animate.set_opacity(1),
            )
            self.wait(0.5)
        self.play(FadeOut(all_rect_groups[-1]))

        # Highlight bias
        bias_rect = SurroundingRectangle(bias)
        bias_brace = Brace(bias_rect, UP)
        bias_word = Text("Bias")
        bias_word.next_to(bias_brace, UP, MED_SMALL_BUFF)

        self.play(
            ReplacementTransform(over_brace, bias_brace),
            FadeIn(bias_rect),
            FadeOut(plusses, lag_ratio=0.1),
            FadeOut(scaled_cols, lag_ratio=0.1),
        )
        self.play(FadeIn(bias_word, 0.5 * UP))
        self.wait()
        self.play(LaggedStart(*map(FadeOut, [bias_word, bias_brace, bias_rect])))

        # Collpase the down projection
        W_down = Tex(R"W_\downarrow", font_size=60).set_color(BLUE)
        B_down = Tex(R"\vec{\textbf{B}}_\downarrow", font_size=60).set_color(BLUE_B)
        W_down.next_to(neurons, LEFT)
        B_down.move_to(bias_as_col)
        WB_down = VGroup(W_down, B_down)
        n_rect = Rectangle(1, 1)
        n_rect.set_height(W_down.get_height())
        n_rect.move_to(n_vect)
        n_rect.set_fill(GREY_C)
        n_rect.set_stroke(WHITE, 1)

        down_proj_expr = VGroup(W_down, n_vect, plus, B_down)
        down_proj_expr.target = down_proj_expr.generate_target()
        down_proj_expr.target[1].become(VGroup(n_rect))
        down_proj_expr.target.arrange(RIGHT, buff=SMALL_BUFF)
        down_proj_expr.target.scale(0.4)
        down_proj_expr.target.next_to(arrows[2], DOWN)

        self.play(ReplacementTransform(col_matrix, W_down, lag_ratio=5e-3, run_time=2))
        self.play(ReplacementTransform(bias_as_col, B_down, lag_ratio=1e-2))
        self.wait()
        self.play(
            LaggedStart(
                MoveToTarget(down_proj_expr),
                FadeOut(equals, 2 * DOWN + 0.5 * LEFT),
                ReplacementTransform(rhs, vects[2]),
                lag_ratio=0.25,
                time_span=(0, 1.5),
            ),
            frame.animate.reorient(0, -14, 0, (-0.1, -2.03, 0.01), 6.31),
            run_time=2,
        )
        self.wait()

        # Add it to the original
        faded_sum_circuit = sum_circuit.copy()
        sum_circuit.set_stroke(opacity=1)
        sum_circuit.insert_n_curves(20)

        self.add(faded_sum_circuit)
        self.play(
            frame.animate.reorient(13, -8, 0, (0.15, -2.05, 0.0), 6.52),
            ShowCreation(sum_circuit, lag_ratio=0.5),
            low_emb_label.animate.shift(0.2 * LEFT).set_anim_args(time_span=(0, 1)),
            FadeOut(output_emb),
            run_time=2,
        )
        self.remove(faded_sum_circuit)
        output_emb.set_fill(opacity=1)
        self.play(LaggedStart(
            TransformFromCopy(emb, output_emb, path_arc=-45 * DEGREES),
            TransformFromCopy(vects[2], output_emb, path_arc=-45 * DEGREES),
            run_time=2,
            lag_ratio=0.2,
        ))
        self.wait()

        # Yet again, emphasize the MJ example
        m_color = interpolate_color_by_hsl(GREY_BROWN, WHITE, 0.5)
        j_color = RED_B
        b_color = basketball.get_color()
        m_tex = Tex(R"\overrightarrow{\text{F.N. Michael}}").set_color(m_color)
        j_tex = Tex(R"\overrightarrow{\text{L.N. Jordan}}").set_color(j_color)
        b_tex = Tex(R"\overrightarrow{\text{Basketball}}").set_color(b_color)
        mj = VGroup(m_tex, Tex("+"), j_tex).copy()
        mjb = VGroup(m_tex, Tex("+"), j_tex, Tex("+"), b_tex).copy()
        for tex_mob in [mj, mjb]:
            tex_mob.set_height(0.45)
            tex_mob.arrange(RIGHT, buff=SMALL_BUFF)
            tex_mob.set_fill(border_width=1)
        mj.next_to(low_emb_label, UP, buff=1.0).shift(0.5 * LEFT)
        mjb.next_to(output_emb, UP, buff=1.5).shift(1.0 * RIGHT)
        mj_arrow = Arrow(mj.get_bottom(), low_emb_label, buff=0.1)
        mjb_arrow = Arrow(output_emb.get_top(), mjb.get_bottom(), buff=0.15)

        self.play(
            frame.animate.reorient(4, -6, 0, (-0.29, -1.76, 0.02), 7.70),
            FadeIn(mj, lag_ratio=0.1),
            ShowCreation(mj_arrow)
        )
        self.play(Transform(mj.copy(), emb.copy().set_opacity(0), lag_ratio=0.005, remover=True, run_time=2))
        mover = emb.copy()
        for vect in [*vects, output_emb]:
            self.play(Transform(mover, vect, rate_func=linear))
        self.remove(mover)
        self.play(
            frame.animate.reorient(-3, -5, 0, (1.09, -1.48, -0.03), 9.61),
            FadeTransform(mj.copy(), mjb[:3]),
            FadeTransformPieces(mj.copy()[-1:], mjb[3:]),
            ShowCreation(mjb_arrow),
            run_time=2,
        )
        self.wait(2)
        self.play(
            frame.animate.reorient(21, -14, 0, (-0.13, -2.21, 0.11), 6.91).set_anim_args(run_time=5),
            LaggedStartMap(FadeOut, VGroup(mj, mj_arrow, mjb_arrow, mjb)),
        )

        # Show it done in parallel to all embeddings
        self.play(
            frame.animate.reorient(14, -12, 0, (0.55, -2.21, 0.18), 7.05),
            LaggedStart((
                TransformFromCopy(simple_phases, sp_copy)
                for sp_copy in simple_phase_copies
            ), lag_ratio=0.1),
            FadeOut(block_title, time_span=(0, 1)),
            run_time=5,
        )
        self.play(
            frame.animate.reorient(42, -23, 0, (0.55, -2.21, 0.18), 7.05),
            run_time=8
        )

        self.wait()

        # Show neurons?
        sum_circuits = VGroup(
            sum_circuit,
            *(sp[0] for sp in simple_phase_copies),
            *(sp[-1] for sp in simple_phase_copies),
        )
        n_vects = VGroup(vects[1], *(sp[2][1] for sp in simple_phase_copies))

        neuron_points = np.array([
            entry.get_center()
            for vect in n_vects[1:]
            for entry in vect.get_entries()
        ])
        neurons = DotCloud(neuron_points)
        neurons.set_radius(0.075)
        neurons.set_shading(0.25, 0.25, 0.5)
        neurons.apply_depth_test()
        rgbas = np.random.random(len(neuron_points))
        rgbas = rgbas.repeat(4).reshape((rgbas.size, 4))
        rgbas[:, 3] = 1
        neurons.set_rgba_array(rgbas)
        neuron_ellipses = VGroup(
            n_vect.get_ellipses()
            for n_vect in n_vects[1:]
        )

        self.play(
            frame.animate.reorient(11, -5, 0, (0.55, -2.21, 0.18), 7.05),
            sum_circuits.animate.set_stroke(width=1, opacity=0.2),
            FadeOut(block[4]),
            run_time=2
        )
        self.play(
            frame.animate.reorient(-11, -5, 0, (0.55, -2.21, 0.18), 7.05).set_anim_args(run_time=4),
            FadeOut(n_vects),
            ShowCreation(neurons, run_time=2),
            FadeIn(neuron_ellipses, time_span=(1, 2)),
        )
        self.add(neuron_ellipses)
        self.play(frame.animate.reorient(13, -7, 0, (0.55, -2.21, 0.18), 7.05), run_time=4)
        self.wait()

    def get_sum_circuit(
        self, in_vect, diff_vect,
        v_buff=0.15,
        h_buff=0.5,
        y_diff=0.65,
        color=YELLOW
    ):
        plus = VGroup(Line(UP, DOWN), Line(LEFT, RIGHT))
        plus.scale(0.6)
        circle = Circle(radius=1)
        oplus = VGroup(circle, plus)
        oplus.set_height(0.3)
        oplus.next_to(diff_vect, RIGHT, buff=h_buff)

        p0 = in_vect.get_top() + v_buff * UP
        p1 = in_vect.get_top() + y_diff * UP
        p2 = oplus.get_center()
        p2[1] = p1[1]
        p3 = oplus.get_top()
        top_line = VMobject()
        top_line.set_points_as_corners([p0, p1, p2, p3])

        oplus.refresh_bounding_box()  # Why?
        h_line1 = Line(diff_vect.get_right(), oplus.get_left())
        h_line2 = Line(oplus.get_right(), oplus.get_right() + h_buff * RIGHT)

        output = diff_vect.copy()
        output.next_to(h_line2, RIGHT, buff=0)
        for e1, e2, e3 in zip(in_vect.get_entries(), diff_vect.get_entries(), output.get_entries()):
            e3.set_value(e1.get_value() + e2.get_value())

        circuit = VGroup(top_line, oplus, h_line1, h_line2)
        circuit.set_stroke(color, 3)

        return circuit, output

    def get_col_matrix(self, matrix, n_cols_shown, dots_index=-2, sym="C", top_index="m", width_multiple=1.0):
        C_labels = VGroup(
            Tex(Rf"\vec{{\textbf{{{sym}}}}}_{{{n}}}")
            for n in [*range(n_cols_shown - 1), top_index]
        )
        C_labels.arrange(RIGHT, buff=0.5)
        C_labels.move_to(matrix.get_entries())
        C_labels.set_width(matrix.get_entries().get_width() * width_multiple)


        v_lines = VGroup(
            Line(matrix.get_bottom(), C_labels.get_bottom() + SMALL_BUFF * DOWN),
            Line(C_labels.get_top() + SMALL_BUFF * UP, matrix.get_top()),
        )
        v_lines.set_stroke(WHITE, 1)
        col_labels = VGroup(
            VGroup(C_label, v_lines.copy().match_x(C_label))
            for C_label in C_labels
        )
        if dots_index is not None:
            dots = Tex(R"\hdots")
            dots.move_to(col_labels[dots_index])
            col_labels.replace_submobject(dots_index, dots)

        return VGroup(matrix.get_brackets().copy(), col_labels)


# Show classic neural net picture
class ClassicNeuralNetworksPicture(InteractiveScene):
    def construct(self):
        pass


## Maybe not needed?
class ShowBiasBakedIntoWeightMatrix(InteractiveScene):
    def construct(self):
        pass





class AlmostOrthogonal(InteractiveScene):
    def construct(self):
        # From Stephens notebook
        import torch  # Need to figure this out
        import matplotlib.pyplot as plt
        from tqdm import tqdm

        # Big example
        num_vectors = 10000
        vector_len = 100

        # Quick optimization loop
        big_matrix = torch.randn(num_vectors, vector_len)
        big_matrix /= big_matrix.norm(p=2, dim=1, keepdim=True)  # Normalize
        big_matrix.requires_grad_(True)

        optimizer = torch.optim.Adam([big_matrix], lr=0.01)
        num_steps = 50

        losses = []
        big_id = torch.eye(num_vectors, num_vectors)

        min_dot = 0.01

        for step_num in tqdm(range(num_steps)):
            optimizer.zero_grad()

            dot_products = big_matrix @ big_matrix.T
            # Punishment deveation from othogonal
            diff = dot_products - big_id
            loss = (diff.abs() - min_dot).relu().sum() + diff.pow(2).sum()
            # loss = diff.pow(2).sum()

            # Extra incentive to keep rows normlaized
            loss += num_vectors * diff.diag().pow(2).sum()

            loss.backward();
            optimizer.step()  
            losses.append(loss.item())

        # Loss curve
        plt.plot(losses); plt.grid(1); plt.show();

        # Angle distribution
        dot_products = big_matrix @ big_matrix.T
        norms = torch.sqrt(torch.diag(dot_products))
        normed_dot_products = dot_products / torch.outer(norms, norms)
        angles_degrees = torch.rad2deg(torch.acos(normed_dot_products.detach()))
        self_orthogonality_mask = ~(big_id.bool()) #use this to ignore self-orthogonality.
        plt.hist(angles_degrees[self_orthogonality_mask].numpy().ravel(), bins=1000);
        plt.grid(1);
        plt.show()

        # Look at angles
        d_degree = 1
        in_range = (90 - d_degree < angles_degrees) & (angles_degrees < 90 + d_degree)
        in_range.sum() / (num_vectors**2 - num_vectors)
