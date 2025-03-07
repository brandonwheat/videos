import { NextResponse } from 'next/server';
import { z } from 'zod';
import { exec } from 'child_process';
import { mkdir, writeFile, access, readdir, unlink } from 'fs/promises';
import path from 'path';
import { createParser } from 'eventsource-parser';
import { createDataStreamResponse, streamText, generateId, tool, CoreMessage, DataStreamWriter } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';
import { createAnthropic } from '@ai-sdk/anthropic';
import crypto from 'crypto';
import { nanoid } from 'nanoid';
import * as fs from 'fs';

// Initialize OpenAI with AI SDK
const openai = createOpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Initialize Anthropic with AI SDK
const anthropic = createAnthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

// Check if we're running on Windows
const isWindows = process.platform === 'win32';

// Global data stream for updates
let globalDataStream: DataStreamWriter | null = null;

// System prompts
const baseSystemPrompt = `You are ManimAI, an assistant that generates mathematical explanations and animations in the style of 3Blue1Brown.

Your primary goal is to help users understand mathematical concepts by providing intuitive explanations that focus on building deep understanding rather than just formulas and procedures.

When responding to questions:
1. Focus on building intuition first - help users see and feel the concepts 
2. Use visual language that paints a mental picture - describe shapes, movements, and transformations
3. Connect new ideas to concepts the user likely already understands
4. Present formal definitions and equations only after establishing intuition
5. Acknowledge the beauty and elegance of mathematical ideas
6. Use conversational and engaging language, as if explaining to a curious friend
7. Format your responses using Markdown for better readability

You have access to a tool that generates animations using the Manim library. When users request to see or visualize concepts, or when a visual explanation would be helpful, you should use this tool by providing proper Manim code.
Before generating Manim code, carefully and comprehensively plan out the scenes for the animation.
IMPORTANT: When your Manim code generates an error, DO NOT just show the fixed code to the user. Instead, call the generateManimAnimation tool again with the corrected code. Always execute the tool with your corrected code to actually generate the animation.

When writing Manim code, ensure it:
1. Uses the Manim Community Edition syntax with "from manim import *" (not ManimGL)
2. Creates a Scene class with a construct method
3. Includes proper imports
4. Has helpful comments explaining key parts of the animation
5. Makes the animation visually appealing with good colors, transitions, and timing
6. Is complete and runnable
7. Keeps animations under 30 seconds total
8. Makes the animation educational and focused on building intuition
9. Uses reasonable font sizes and clear layout for readability
10. Follows 3Blue1Brown's style with elegant transitions, clean visuals, and thoughtful pacing

Technical requirements for the Manim code:
- Use descriptive class names for Scene classes
- Use MathTex() for mathematical expressions
- Verify that animations are properly sequenced and won't cause runtime errors
- Keep the total animation length reasonable (15-30 seconds is ideal)
- Test all mathematical formulas for correctness
- Always use the --disable_caching flag when rendering animations due to a known bug

LaTeX syntax guidelines:
- Always use double backslashes (\\\\) or raw strings (r"...") when writing LaTeX in Python
- For mathematical operators like multiplication, use \\times (not times)
- For fractions, use \\frac{numerator}{denominator}
- For square roots, use \\sqrt{expression}
- For powers, use x^{power}
- For subscripts, use x_{subscript}
- Always check that LaTeX commands have proper backslashes
- Common errors include missing backslashes before LaTeX commands (e.g., "times" instead of "\\times")`;

// Claude-specific system prompt
const claudeSystemPrompt = `You are ManimAI, an assistant that generates mathematical explanations and animations in the style of 3Blue1Brown.

Your primary goal is to help users understand mathematical concepts by providing intuitive explanations that focus on building deep understanding rather than just formulas and procedures.

When responding to questions:
1. Focus on building intuition first - help users see and feel the concepts 
2. Use visual language that paints a mental picture - describe shapes, movements, and transformations
3. Connect new ideas to concepts the user likely already understands
4. Present formal definitions and equations only after establishing intuition
5. Acknowledge the beauty and elegance of mathematical ideas
6. Use conversational and engaging language, as if explaining to a curious friend
7. Format your responses using Markdown for better readability

You have access to a tool that generates animations using the Manim library. When users request to see or visualize concepts, or when a visual explanation would be helpful, you should use this tool by providing proper Manim code.
Before generating Manim code, carefully and comprehensively plan out the scenes for the animation.
IMPORTANT: When your Manim code generates an error, DO NOT just show the fixed code to the user. Instead, call the generateManimAnimation tool again with the corrected code. Always execute the tool with your corrected code to actually generate the animation.

When writing Manim code, ensure it:
1. Uses the Manim Community Edition syntax with "from manim import *" (not ManimGL)
2. Creates a Scene class with a construct method
3. Includes proper imports
4. Has helpful comments explaining key parts of the animation
5. Makes the animation visually appealing with good colors, transitions, and timing
6. Is complete and runnable
7. Keeps animations under 30 seconds total
8. Makes the animation educational and focused on building intuition
9. Uses reasonable font sizes and clear layout for readability
10. Follows 3Blue1Brown's style with elegant transitions, clean visuals, and thoughtful pacing

Technical requirements for the Manim code:
- Use descriptive class names for Scene classes
- Use MathTex() for mathematical expressions
- Verify that animations are properly sequenced and won't cause runtime errors
- Keep the total animation length reasonable (15-30 seconds is ideal)
- Test all mathematical formulas for correctness
- Always use the --disable_caching flag when rendering animations due to a known bug

LaTeX syntax guidelines:
- Always use double backslashes (\\\\) or raw strings (r"...") when writing LaTeX in Python
- For mathematical operators like multiplication, use \\times (not times)
- For fractions, use \\frac{numerator}{denominator}
- For square roots, use \\sqrt{expression}
- For powers, use x^{power}
- For subscripts, use x_{subscript}
- Always check that LaTeX commands have proper backslashes
- Common errors include missing backslashes before LaTeX commands (e.g., "times" instead of "\\times")`;

// Voiceover instructions
const voiceoverInstructions = `
VOICEOVER INSTRUCTIONS:
You have access to Manim Voiceover which integrates speech narration with Manim animations. 
When creating animations, include voiceover narration to explain the mathematical concepts as they're visualized.

To use voiceovers in your animations:
1. Import the VoiceoverScene and OpenAI speech service:
   \`\`\`python
   from manim import *
   from manim_voiceover import VoiceoverScene
   from manim_voiceover.services.openai import OpenAIService
   \`\`\`

2. Extend VoiceoverScene instead of Scene:
   \`\`\`python
   class YourScene(VoiceoverScene):
   \`\`\`

3. In the construct method, set up the OpenAI speech service:
   \`\`\`python
   def construct(self):
       # Set up the speech service
       service = OpenAIService(voice="alloy", model="tts-1-hd")
       self.set_speech_service(service)
   \`\`\`

4. Use the voiceover context manager to add narration at specific points:
   \`\`\`python
   with self.voiceover("This is a circle.") as tracker:
       self.play(Create(circle))
   \`\`\`

5. You can also wait for voiceovers to finish or use bookmarks:
   \`\`\`python
   # Wait for the voiceover to finish
   self.wait_for_voiceover()
   
   # Or use SSML with bookmarks
   with self.voiceover("""
       Here we have a circle <bookmark mark='circle_created'/> 
       and we can transform it <bookmark mark='transform_started'/> 
       into a square.
   """) as tracker:
       self.play(Create(circle))
       self.wait_until_bookmark("circle_created")
       self.play(circle.animate.become(square))
       self.wait_until_bookmark("transform_started")
   \`\`\`

6. Synchronize animations with speech for a natural flow
7. Keep narration concise and focused on explaining the current visual elements
8. Use clear, simple language that complements the visualization
9. Remember to add the --disable_caching flag when rendering animations due to a known bug

Make sure the voiceover text aligns perfectly with what's being shown on screen at each moment.`;

// Define a schema for the request body
const schema = z.object({
  messages: z.array(
    z.object({
      role: z.enum(['user', 'assistant', 'system', 'function', 'tool']),
      content: z.string(),
    })
  ),
  model: z.string().optional().default('gpt-4o'),
  voiceoverEnabled: z.boolean().optional().default(false),
});

// Define our message type
type Message = {
  role: 'user' | 'assistant' | 'system' | 'function' | 'tool';
  content: string;
};

// Function to execute a command on Windows using a batch file
async function executeWindowsCommand(command: string): Promise<{stdout: string, stderr: string}> {
  const batchDir = path.join(process.cwd(), 'public', 'batch_scripts');
  await mkdir(batchDir, { recursive: true });
  
  const batchFile = path.join(batchDir, `run_${Date.now()}.bat`);
  // Add cd command to ensure we're in the project root directory
  const batchContent = `@echo off\ncd "${process.cwd().replace(/\\/g, '/')}"\n${command}\n`;
  
  await writeFile(batchFile, batchContent);
  
  return new Promise((resolve, reject) => {
    exec(batchFile, {
      env: {
        ...process.env,
        PATH: `${process.env.PATH};C:\\texlive\\2023\\bin\\windows;C:\\ffmpeg\\bin`
      }
    }, (error, stdout, stderr) => {
      // Clean up the batch file
      try {
        unlink(batchFile).catch(err => {
          console.error(`Error deleting batch file: ${err}`);
        });
      } catch (err) {
        console.error(`Error deleting batch file: ${err}`);
      }
      
      if (error) {
        reject({ error, stdout, stderr });
      } else {
        resolve({ stdout, stderr });
      }
    });
  });
}

// Function to extract Manim code from a response
function extractManimCode(text: string): string | null {
  const codeBlockRegex = /```python\s*([\s\S]*?)```/g;
  const match = codeBlockRegex.exec(text);
  return match ? match[1].trim() : null;
}

// Helper function to generate Manim animation
async function generateManimAnimation(manimCode: string, prompt: string): Promise<string | null | {error: string, stdout: string, stderr: string}> {
  console.log('🎥 Starting Manim animation generation process');
  
  // Generate a unique ID for this animation
  const id = nanoid(16);
  console.log(`🆔 Generated animation ID: ${id}`);
  
  // Create directories
  const scriptDir = path.join(process.cwd(), 'public', 'manim_scripts');
  const mediaDir = path.join(scriptDir, 'media');
  console.log(`📁 Creating script directory: ${scriptDir}`);
  await mkdir(scriptDir, { recursive: true });
  console.log(`📁 Creating media directory: ${mediaDir}`);
  await mkdir(mediaDir, { recursive: true });

  // Write Manim script to file
  const scriptPath = path.join(scriptDir, `${id}.py`);
  console.log(`📄 Writing Manim script to ${scriptPath}`);
  await writeFile(scriptPath, manimCode);

  const isWindows = process.platform === 'win32';
  console.log(`🖥️ Running on platform: ${process.platform}`);

  // Extract the scene class name from the Manim code
  const sceneClassMatch = manimCode.match(/class\s+(\w+)\s*\(\s*Scene\s*\)/);
  const sceneClassName = sceneClassMatch ? sceneClassMatch[1] : 'Scene';
  console.log(`🎬 Detected scene class name: ${sceneClassName}`);

  // Set Manim output directories 
  const videoDir = path.join(process.cwd(), 'public', 'manim_scripts', 'media', 'videos').replace(/\\/g, '/');
  
  // The expected path where Manim will save the video
  // Manim places videos in a nested structure: videos/ID/720p30/ID.mp4
  const expectedOutputPath = path.join(process.cwd(), 'public', 'manim_scripts', 'media', 'videos', `${id}`, '720p30', `${id}.mp4`);
  
  const publicVideoUrl = `/manim_scripts/media/videos/${id}/720p30/${id}.mp4`;
  
  // Convert paths for command
  const scriptPathForCommand = scriptPath.replace(/\\/g, '/');
  
  // Build the command with correct flags based on manim community help
  const configPath = path.join(process.cwd(), 'public', 'manim_scripts', 'manim.cfg').replace(/\\/g, '/');
  const pythonCommand = `python -m manim render -q m "${scriptPathForCommand}" ${sceneClassName} -o ${id} --media_dir "${path.join(process.cwd(), 'public', 'manim_scripts', 'media').replace(/\\/g, '/')}" --config_file "${configPath}" --disable_caching`;
  
  const command = isWindows
    ? `cd "${process.cwd().replace(/\\/g, '/')}" && ${pythonCommand}`
    : `cd "${process.cwd().replace(/\\/g, '/')}" && ${pythonCommand}`;
  console.log(`🚀 Executing Manim command: ${command}`);

  try {
    let stdout, stderr;
    
    if (isWindows) {
      // Use the batch file approach for Windows
      const result = await executeWindowsCommand(pythonCommand);
      stdout = result.stdout;
      stderr = result.stderr;
    } else {
      // Use the regular approach for non-Windows platforms
      const result = await new Promise<{stdout: string, stderr: string}>((resolve, reject) => {
        exec(command, {
          timeout: 300000, // 6 minute timeout
          env: {
            ...process.env,
            // Add LaTeX and other necessary paths to the PATH
            PATH: `${process.env.PATH};C:\\texlive\\2023\\bin\\windows;C:\\ffmpeg\\bin`
          }
        }, async (error, stdout, stderr) => {
          if (error) {
            reject({ error, stdout, stderr });
          } else {
            resolve({ stdout, stderr });
          }
        });
      });
      
      stdout = result.stdout;
      stderr = result.stderr;
    }
    
    // Check if output file exists
    const fileExistsResult = await fileExists(expectedOutputPath);
    if (fileExistsResult) {
      console.log(`✅ Animation generated successfully at ${expectedOutputPath}`);
      return publicVideoUrl;
    } else {
      console.log(`❓ Output file not found at expected path: ${expectedOutputPath}`);
      
      // Search for any MP4 files that might have been created matching the current ID
      const findCurrentIdCommand = isWindows 
        ? `dir "${path.join(process.cwd(), 'public', 'manim_scripts', 'media', 'videos')}" /s /b | findstr "${id}"`
        : `find "${path.join(process.cwd(), 'public', 'manim_scripts', 'media', 'videos')}" -name "*${id}*" -type f | grep ".mp4"`;
      
      try {
        const currentIdResult = await new Promise<string>((resolve, reject) => {
          exec(findCurrentIdCommand, (error, stdout, stderr) => {
            if (error) {
              console.log(`ℹ️ No files found matching current ID: ${id}`);
              resolve('');
            } else {
              resolve(stdout);
            }
          });
        });
        
        if (currentIdResult.trim()) {
          const idMatchFiles = currentIdResult.trim().split('\n');
          // Sort by modification time (newest first)
          const sortedFiles = await Promise.all(idMatchFiles.map(async (filePath) => {
            try {
              const stats = await fs.promises.stat(filePath.trim());
              return { path: filePath.trim(), mtime: stats.mtime };
            } catch (err) {
              console.error(`Error getting stats for ${filePath}: ${err}`);
              return { path: filePath.trim(), mtime: new Date(0) };
            }
          }));
          sortedFiles.sort((a, b) => b.mtime.getTime() - a.mtime.getTime());
          
          if (sortedFiles.length > 0) {
            const newestFile = sortedFiles[0].path;
            console.log(`🎬 Found matching video for current ID: ${newestFile}`);
            return convertToPublicPath(newestFile);
          }
        }
      } catch (err) {
        console.error(`Error searching for current ID files: ${err}`);
      }
      
      // Fallback: Search for any MP4 files
      const findMp4Command = isWindows 
        ? `dir "${path.join(process.cwd(), 'public', 'manim_scripts', 'media')}" /s /b | findstr ".mp4$"`
        : `find "${path.join(process.cwd(), 'public', 'manim_scripts', 'media')}" -name "*.mp4" -type f`;
      
      const mp4Result = await new Promise<string>((resolve, reject) => {
        exec(findMp4Command, (error, stdout, stderr) => {
          if (error) {
            console.log(`❌ Error searching for MP4 files: ${error.message}`);
            reject(error);
          } else {
            resolve(stdout);
          }
        });
      });
      
      if (mp4Result.trim()) {
        const mp4Files = mp4Result.trim().split('\n');
        // Sort by modification time instead of just taking the last one
        const sortedFiles = await Promise.all(mp4Files.map(async (filePath) => {
          try {
            const stats = await fs.promises.stat(filePath.trim());
            return { path: filePath.trim(), mtime: stats.mtime };
          } catch (err) {
            console.error(`Error getting stats for ${filePath}: ${err}`);
            return { path: filePath.trim(), mtime: new Date(0) };
          }
        }));
        sortedFiles.sort((a, b) => b.mtime.getTime() - a.mtime.getTime());
        
        if (sortedFiles.length > 0) {
          const newestFile = sortedFiles[0].path;
          console.log(`🎬 Found most recent video: ${newestFile}`);
          return convertToPublicPath(newestFile);
        }
      }
      
      console.log(`⚠️ No MP4 files found.`);
      // Return error information directly to let the LLM handle it
      return { error: "No video files were generated", stdout, stderr };
    }
  } catch (error: any) {
    console.log(`❌ Error running Manim: ${error}`);
    console.log(`📊 STDERR: ${error.stderr || 'No stderr available'}`);
    
    console.log(`❌ Failed to generate animation: ${error.error ? error.error.message : error.message}`);
    
    // Return error information directly
    return { 
      error: error.error ? error.error.message : error.message,
      stdout: error.stdout || '',
      stderr: error.stderr || ''
    };
  }
}

// Helper function to convert a system file path to a public URL path
function convertToPublicPath(filePath: string): string {
  // Remove the process.cwd() and 'public' part from the path
  const normalizedPath = filePath.replace(/\\/g, '/');
  const publicDir = path.join(process.cwd(), 'public').replace(/\\/g, '/');
  
  let publicPath = '';
  if (normalizedPath.includes(publicDir)) {
    publicPath = normalizedPath.replace(publicDir, '');
  } else {
    // Extract the ID from the filename
    const filename = path.basename(normalizedPath);
    const fileId = filename.split('.')[0]; // Get the ID from the filename
    
    // Use the correct nested path structure
    publicPath = `/manim_scripts/media/videos/${fileId}/720p30/${filename}`;
  }
  
  // Ensure the path ends with .mp4
  if (!publicPath.endsWith('.mp4')) {
    publicPath = publicPath.split('?')[0]; // Remove any query parameters
    publicPath = `${publicPath}.mp4`;
  }
  
  return publicPath;
}

// Helper function to check if a file exists
async function fileExists(filePath: string): Promise<boolean> {
  try {
    await access(filePath, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

// Define types for tool execution
interface ManimToolResult {
  videoUrl?: string;
  error?: string;
  status?: string;
  stdout?: string;
  stderr?: string;
}

// Keep track of the most recently generated Manim code
interface ManimContext {
  latestManimCode?: string;
}

// Store the latest Manim code
let globalManimContext: ManimContext = {
  latestManimCode: undefined
};

// Function to ensure multiple videos get displayed
function updateStreamWithVideoData(dataStream: any, resultData: ManimToolResult) {
  console.log('🎬 Updating stream with video data');
  
  // Create basic status update with a special status for completed animations
  const dataToSend: any = { 
    status: resultData.videoUrl ? 'animation_complete' : resultData.status 
  };
  
  // Add additional fields if they exist
  if (resultData.videoUrl) {
    // Ensure the video URL ends with .mp4
    let videoUrl = resultData.videoUrl;
    if (!videoUrl.endsWith('.mp4')) {
      // Extract the base path without any query parameters
      const basePath = videoUrl.split('?')[0];
      // Ensure it ends with .mp4
      videoUrl = basePath.endsWith('.mp4') ? basePath : `${basePath}.mp4`;
      console.log(`🔧 Fixed video URL to ensure .mp4 extension: ${videoUrl}`);
    }
    
    // Create a fresh timestamp for this video URL to ensure the frontend treats it as new
    const timestamp = Date.now();
    
    // Add a timestamp parameter to force browser cache invalidation
    const videoUrlWithTimestamp = `${videoUrl}?t=${timestamp}`;
    dataToSend.videoUrl = videoUrlWithTimestamp;
    dataToSend.videoTimestamp = timestamp.toString();
    dataToSend.newAnimation = true; // Explicit flag for the frontend
    
    console.log(`🔗 Sending new video URL: ${videoUrlWithTimestamp}`);
    
    // First, explicitly notify that a new animation is available
    // This allows the frontend to prepare for the incoming video
    dataStream.writeData({ 
      status: 'new_animation_available', 
      videoUrl: videoUrlWithTimestamp,
      videoTimestamp: timestamp.toString()
    });
    
    // Then send the full data update with a small delay
    setTimeout(() => {
      dataStream.writeData(dataToSend);
      
      // Send an additional update after a delay to ensure frontend receives it
      setTimeout(() => {
        dataStream.writeData({
          status: 'animation_ready',
          videoUrl: videoUrlWithTimestamp,
          videoTimestamp: timestamp.toString(),
          refreshVideo: true
        });
      }, 200);
    }, 100);
    
    return; // Return early since we're sending the data after a delay
  }
  
  if (resultData.error) dataToSend.error = resultData.error;
  if (resultData.stdout) dataToSend.stdout = resultData.stdout;
  if (resultData.stderr) dataToSend.stderr = resultData.stderr;
  
  dataStream.writeData(dataToSend);
}

export async function POST(req: Request) {
  console.log('📥 Receiving chat request');
  
  try {
    // Parse the request body
    const body = await req.json();
    console.log('🚀 Chat API request received');
    
    // Validate request body
    const result = schema.safeParse(body);
    if (!result.success) {
      return NextResponse.json(
        { error: 'Invalid request body', details: result.error.format() },
        { status: 400 }
      );
    }
    
    // Extract messages and model from validated body
    const { messages: validatedMessages, model: validatedModel, voiceoverEnabled } = result.data;
    console.log(`📱 Using model: ${validatedModel}`);
    console.log(`🔊 Voiceover is ${voiceoverEnabled ? 'enabled' : 'disabled'}`);
    
    // Create our Manim tool
    const generateManimTool = tool({
      description: 'Generate a Manim animation to visualize and explain mathematical concepts. You can provide new code or modify previously generated code based on user feedback.', 
      parameters: z.object({
        manimCode: z.string().describe('Complete, runnable Python code using the Manim library that will create an animation. The code should be ready to execute without modifications.'),
      }),
      execute: async ({ manimCode }, { messages }) => {
        // Find the user's original prompt from the last user message
        const lastUserMessage = messages
          .filter(msg => msg.role === 'user')
          .pop();
        
        const userPromptContent = typeof lastUserMessage?.content === 'string' 
          ? lastUserMessage.content 
          : 'mathematical concept';
        
        console.log(`🔄 Executing Manim generation tool with code length: ${manimCode.length} characters`);
        console.log(`🔊 Voiceover is ${voiceoverEnabled ? 'enabled' : 'disabled'}`);
        
        // Store the latest Manim code for future reference
        globalManimContext.latestManimCode = manimCode;
        console.log(`📝 Storing Manim code for future reference (${manimCode.length} chars)`);
        
        try {
          // Generate the animation using the provided Manim code
          const result = await generateManimAnimation(manimCode, userPromptContent);
          
          if (typeof result === 'string') {
            console.log(`✅ Animation generated successfully: ${result}`);
            return { videoUrl: result, status: 'animation_complete' } as ManimToolResult;
          } else if (result !== null && typeof result === 'object') {
            // This is an error object with stdout and stderr
            console.log(`❌ Failed to generate animation: ${result.error}`);
            return {
              error: result.error,
              status: 'animation_failed',
              stdout: result.stdout,
              stderr: result.stderr
            } as ManimToolResult;
          } else {
            console.log('❌ Failed to generate animation (unknown error)');
            return {
              error: 'Unknown error during animation generation',
              status: 'animation_failed'
            } as ManimToolResult;
          }
        } catch (error) {
          console.error('❌ Error executing Manim tool:', error);
          return {
            error: error instanceof Error ? error.message : 'Unknown error',
            status: 'animation_failed'
          } as ManimToolResult;
        }
      }
    });
    
    // Determine if we're using a Claude model (for system prompt selection only)
    const isClaudeModel = validatedModel.includes('claude');
    
    // Get the appropriate AI model
    const aiModel = isClaudeModel 
      ? anthropic(validatedModel)
      : openai(validatedModel);
    
    // Create and return the data stream response
    const response = await createDataStreamResponse({
      execute: async (dataStream: DataStreamWriter) => {
        // Store the stream globally
        globalDataStream = dataStream;
        
        // Send initial status
        dataStream.writeData({ status: 'starting' });
        
        // Deep copy messages to avoid mutation issues
        const messagesToSend = JSON.parse(JSON.stringify(validatedMessages));
        
        // Add system message if it doesn't exist at the beginning
        if (messagesToSend.length === 0 || messagesToSend[0].role !== 'system') {
          messagesToSend.unshift({
            role: 'system',
            content: isClaudeModel ? claudeSystemPrompt : baseSystemPrompt,
          });
        }

        // Add voiceover instructions if enabled
        if (voiceoverEnabled) {
          // Find the system message index
          const systemMessageIndex = messagesToSend.findIndex((m: Message) => m.role === 'system');
          if (systemMessageIndex !== -1) {
            messagesToSend[systemMessageIndex].content += voiceoverInstructions;
          }
        }

        // Stream response with potential tool usage - same for both model types
        console.log('💬 Generating text response...');
        
        const textResult = await streamText({
          model: aiModel,
          messages: messagesToSend,
          maxSteps: 5, // Allow for tool call and final response
          maxTokens: isClaudeModel ? 60000 : 15000,
          tools: {
            generateManimAnimation: generateManimTool
          },
          onStepFinish: ({ toolCalls, toolResults }) => {
            // Update status based on tool calls and results
            if (toolCalls.length > 0) {
              console.log(`🔧 Tool call detected: ${toolCalls[0].toolName}`);
              
              // If we're generating an animation, capture the Manim code from the tool call
              if (toolCalls[0].toolName === 'generateManimAnimation' && 
                  toolCalls[0].args && 
                  'manimCode' in toolCalls[0].args) {
                
                const manimCode = toolCalls[0].args.manimCode as string;
                console.log(`📝 Manim code captured (${manimCode.length} chars)`);
                
                // Send the code to the frontend with a unique identifier
                const toolCallId = Date.now();
                dataStream.writeData({ 
                  status: 'generating_manim_code',
                  manimCode: manimCode,
                  toolCallId: toolCallId // Use a consistent ID for this tool call
                });
              } else {
                dataStream.writeData({ status: 'generating_manim_code' });
              }
            }
            
            if (toolResults.length > 0) {
              const toolResult = toolResults[0];
              
              // Log the entire tool result for debugging
              console.log(`🔨 Full tool result:`, JSON.stringify(toolResult));
              
              if (toolResult && typeof toolResult === 'object' && 'result' in toolResult) {
                const resultData = (toolResult as any).result as ManimToolResult;
                console.log(`📊 Tool result data:`, JSON.stringify(resultData));
                
                // Handle successful animations and errors differently
                if (resultData) {
                  if (resultData.videoUrl) {
                    console.log('✅ Animation generated successfully');
                    // This is a successful animation - send it with the dedicated function
                    updateStreamWithVideoData(dataStream, resultData);
                  } else if (resultData.error) {
                    console.log(`❌ Animation generation failed: ${resultData.error}`);
                    // This is an error - send it directly
                    dataStream.writeData({
                      status: 'animation_failed',
                      error: resultData.error,
                      stdout: resultData.stdout || '',
                      stderr: resultData.stderr || '',
                      errorTimestamp: Date.now()
                    });
                  } else {
                    // Handle other statuses
                    dataStream.writeData({ 
                      status: resultData.status || 'unknown',
                      timestamp: Date.now()
                    });
                  }
                }
              }
            }
          },
          onFinish: () => {
            console.log('✅ Text generation completed');
            dataStream.writeData({ status: 'completed' });
          }
        });
        
        console.log('🔄 Merging text stream into data stream');
        textResult.mergeIntoDataStream(dataStream);
      }
    });
    
    // Return the response
    return new Response(response.body, {
      headers: { 'Content-Type': 'text/event-stream' }
    });
  } catch (error) {
    console.error('❌ Error in chat API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 