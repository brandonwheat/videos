/** @type {import('codefetch').CodefetchConfig} */
export default {
  // Output settings
  outputPath: "codefetch", // Directory for output files
  outputFile: "codebase.md", // Output filename
  maxTokens: 500000, // Token limit
  disableLineNumbers: false, // Toggle line numbers in output
  
  // Processing options
  verbose: 1, // Logging level (0=none, 1=basic, 2=debug)
  projectTree: 5, // Project tree depth
  defaultIgnore: true, // Use default ignore patterns
  gitignore: true, // Respect .gitignore
  dryRun: false, // Output to console instead of file
  
  // Token handling
  tokenEncoder: "o200k", // Token counting method (simple, p50k, o200k, cl100k)
  tokenLimiter: "truncated", // Token limiting strategy
  
  // File filtering
  extensions: [], // Include all file extensions
  includeFiles: ["manim-ai/src/**/*.ts"], // Only include files from src directory
  excludeFiles: [
    // Exclude media files
    "**/*.jpg", "**/*.jpeg", "**/*.png", "**/*.gif", "**/*.svg", 
    "**/*.mp3", "**/*.mp4", "**/*.wav", "**/*.avi", "**/*.mov", 
    "**/*.webm", "**/*.ogg",
    // Exclude other binary/large files
    "**/*.zip", "**/*.tar", "**/*.gz", "**/*.pdf"
  ],
  includeDirs: ["manim-ai/src"], // Only include src directory
  excludeDirs: [
    // Common directories in .gitignore
    "node_modules", ".git", "dist", "build", "coverage", 
    ".cache", "logs", ".idea", ".vscode"
  ],
  
  // AI/LLM settings
  trackedModels: [
    "chatgpt-4o-latest",
    "claude-3-5-sonnet-20241022",
    "claude-3-7-sonnet-20250219",
    "o1",
    "deepseek-v3",
    "gemini-exp-1206",
  ],
  
  // Prompt handling
  prompt: "My current codebase: ", // No default prompt
  defaultChat: "https://chat.com", // Default chat URL for Cursor
  templateVars: {}, // Variables for template substitution
}
