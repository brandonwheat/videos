# 3Blue1Brown AI Video Generator

An interactive web application that generates mathematical explanations and animations in the style of 3Blue1Brown using AI and the Manim animation library.

## Features

- Interactive chat interface for mathematical explanations
- AI-powered responses in the style of 3Blue1Brown
- Automatic generation of mathematical animations
- Support for various mathematical concepts
- Real-time streaming responses
- Video playback of generated animations

## Technology Stack

- **Frontend**: Next.js, React, TypeScript, TailwindCSS
- **Backend**: Next.js API routes
- **AI**: OpenAI API (GPT-4)
- **Animation**: Manim (Mathematical Animation Engine)

## Requirements

- Node.js 18+
- Python 3.8+
- Manim (Mathematical Animation Engine)
- OpenAI API key

## Setup

### 1. Install dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install manim
```

### 2. Configure environment variables

Create a `.env.local` file in the root directory:

```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the development server

```bash
npm run dev
```

### 4. Access the application

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Using the Application

1. Type a mathematical question or concept in the input field
2. The AI will respond with an explanation in the style of 3Blue1Brown
3. To generate an animation, include keywords like "animation", "visual", "show me", etc. in your query
4. The application will generate a Manim animation based on your query
5. Once the animation is ready, it will be displayed in the application

## Example Prompts

- "Explain the Mandelbrot set and how it relates to complex numbers"
- "Show me a visual proof of the Pythagorean theorem"
- "Create an animation explaining eigenvalues and eigenvectors"
- "Visualize the concept of e^(iπ) = -1"
- "Demonstrate how the chain rule works in calculus"

## Manim Configuration

The application includes a custom `manim.cfg` file with 3Blue1Brown-style settings. You can modify these settings in the `manim.cfg` file.

## Example Animations

The `examples` directory contains sample Manim scripts for various mathematical concepts:

- `pythagoras.py`: Visual proof of the Pythagorean theorem
- `eigenvalues.py`: Explanation of eigenvalues and eigenvectors
- `mandelbrot.py`: Visualization of the Mandelbrot set

## License

MIT

## Acknowledgements

- [3Blue1Brown](https://www.3blue1brown.com/) for inspiration
- [Manim](https://github.com/ManimCommunity/manim) for the animation engine
- [OpenAI](https://openai.com/) for the language model
