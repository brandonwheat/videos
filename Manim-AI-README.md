# Manim AI Web App

This is an AI-powered web application that generates mathematical animations in the style of 3Blue1Brown using the Manim animation library.

## Running the Application

### Quick Start

1. **Use the batch file**: Simply run the `run-app.bat` file in this directory:

```bash
.\run-app.bat
```

This will automatically navigate to the `manim-ai` directory and start the application.

### Manual Run

If you prefer to run the application manually:

1. Navigate to the `manim-ai` directory:

```bash
cd manim-ai
```

2. Run the development server:

```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Troubleshooting

- **"npm not found"**: Make sure you have Node.js installed.
- **"Error: ENOENT: no such file or directory, open 'package.json'"**: You're likely trying to run `npm run dev` from the root directory. Either use the `run-app.bat` file or navigate to the `manim-ai` directory first.
- **Video not showing**: Check the browser console for errors. The sidebar should automatically open when a video is ready.

## Debugging

- The application includes a debug panel that can be opened by clicking the info icon.
- Console logs provide detailed information about the animation generation process.
- The sidebar includes video test functionality to check if the video URL is accessible.

## More Information

For more details about the application, see the README.md file in the `manim-ai` directory. 