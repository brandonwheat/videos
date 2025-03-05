
import os
import subprocess
import sys

# Function to prompt for API key if not already set
def ensure_api_key():
    if "OPENAI_API_KEY" not in os.environ:
        print("OpenAI API key not found in environment variables.")
        api_key = input("Please enter your OpenAI API key: ")
        os.environ["OPENAI_API_KEY"] = api_key
        print("API key set for this session.")
    else:
        print("OpenAI API key found in environment variables.")

# Ensure API key is set
ensure_api_key()

# Get the path to the current Python interpreter
python_executable = sys.executable

# Construct the command to run
cmd = [
    python_executable, 
    "-m", 
    "manim",
    "mandelbrot_manim.py",
    "MandelbrotSet",
    "-qm",  # Medium quality
    "--write_to_movie",  # Save to file
    "--disable_caching"  # Required flag for manim-voiceover to work properly
]

print("Running command:", " ".join(cmd))

# Run the command with the API key in the environment
subprocess.run(cmd, env=os.environ)

print("
Rendering complete!")
print("The video should be saved in the 'media' directory.")
