import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import { mkdir, writeFile, unlink } from 'fs/promises';
import * as fs from 'fs';
import * as path from 'path';
import crypto from 'crypto';

// Helper function to check if a file exists
async function fileExists(filePath: string): Promise<boolean> {
  console.log(`🔍 Checking if file exists: ${filePath}`);
  try {
    await fs.promises.access(filePath, fs.constants.F_OK);
    console.log(`✅ File exists: ${filePath}`);
    
    // Extra check: Get file stats to verify it's a valid file with size
    const stats = await fs.promises.stat(filePath);
    console.log(`📊 File size: ${stats.size} bytes, isFile: ${stats.isFile()}`);
    
    if (stats.size === 0) {
      console.log(`⚠️ Warning: File exists but has zero size`);
    }
    
    return stats.isFile() && stats.size > 0;
  } catch (error) {
    console.log(`❌ File does not exist or cannot be accessed: ${filePath}`);
    console.log(`❌ Error: ${error}`);
    return false;
  }
}

// Helper function to convert a system file path to a public URL path
function convertToPublicPath(filePath: string): string {
  console.log(`🔍 Converting file path: ${filePath}`);
  
  // Remove the process.cwd() and 'public' part from the path
  const normalizedPath = filePath.replace(/\\/g, '/');
  const publicDir = path.join(process.cwd(), 'public').replace(/\\/g, '/');
  
  console.log(`🧮 Normalized path: ${normalizedPath}`);
  console.log(`📁 Public directory: ${publicDir}`);
  
  let publicPath = '';
  
  if (normalizedPath.includes(publicDir)) {
    publicPath = normalizedPath.replace(publicDir, '');
    console.log(`🔄 Path after replacing public dir: ${publicPath}`);
  } else {
    // Fallback: extract the filename and construct a default path
    const filename = path.basename(normalizedPath);
    publicPath = `/manim_scripts/media/videos/${filename}`;
    console.log(`📝 Using fallback path with filename: ${publicPath}`);
  }
  
  // Ensure the path starts with a slash
  if (!publicPath.startsWith('/')) {
    publicPath = '/' + publicPath;
  }
  
  console.log(`🎯 Final public URL path: ${publicPath}`);
  return publicPath;
}

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

export async function POST(req: Request) {
  try {
    const { manimCode } = await req.json();
    console.log('🔄 Regenerating animation with custom code');
    
    if (!manimCode) {
      return NextResponse.json({ error: 'No Manim code provided' }, { status: 400 });
    }
    
    // Create a unique ID for this animation
    const id = crypto.randomBytes(8).toString('hex');
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
    
    // Convert paths for command
    const scriptPathForCommand = scriptPath.replace(/\\/g, '/');
    
    // Build the command with correct flags based on manim community help
    const configPath = path.join(process.cwd(), 'public', 'manim_scripts', 'manim.cfg').replace(/\\/g, '/');
    const pythonCommand = `python -m manim render -q m "${scriptPathForCommand}" ${sceneClassName} -o ${id} --media_dir "${path.join(process.cwd(), 'public', 'manim_scripts', 'media').replace(/\\/g, '/')}" --config_file "${configPath}"`;
    
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
        // Use regular command for non-Windows platforms
        const result = await new Promise<{stdout: string, stderr: string}>((resolve, reject) => {
          exec(command, {
            timeout: 180000, // 3 minute timeout
            env: {
              ...process.env,
              PATH: `${process.env.PATH};C:\\texlive\\2023\\bin\\windows;C:\\ffmpeg\\bin`
            }
          }, (error, stdout, stderr) => {
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
      
      // Check if the output file exists
      const expectedOutputPath = path.join(process.cwd(), 'public', 'manim_scripts', 'media', 'videos', `${id}.mp4`);
      const fileExistsResult = await fileExists(expectedOutputPath);
      
      if (fileExistsResult) {
        console.log(`✅ Animation generated successfully at ${expectedOutputPath}`);
        return NextResponse.json({ success: true, videoUrl: `/manim_scripts/media/videos/${id}.mp4` });
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
              
              // Convert the path to a URL
              const publicPath = convertToPublicPath(newestFile);
              
              // Verify the file is accessible
              const fullPath = path.join(process.cwd(), 'public', publicPath.startsWith('/') ? publicPath.substring(1) : publicPath);
              console.log(`🔍 Verifying file exists at: ${fullPath}`);
              const fileVerified = await fileExists(fullPath);
              console.log(`✅ File verified: ${fileVerified}`);

              return NextResponse.json({ 
                success: true, 
                videoUrl: publicPath,
                videoVerified: fileVerified,
                fullPath: fullPath
              });
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
          // Sort by modification time (newest first)
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
            
            // Convert the path to a URL
            const publicPath = convertToPublicPath(newestFile);
            
            // Verify the file is accessible
            const fullPath = path.join(process.cwd(), 'public', publicPath.startsWith('/') ? publicPath.substring(1) : publicPath);
            console.log(`🔍 Verifying file exists at: ${fullPath}`);
            const fileVerified = await fileExists(fullPath);
            console.log(`✅ File verified: ${fileVerified}`);

            return NextResponse.json({ 
              success: true, 
              videoUrl: publicPath,
              videoVerified: fileVerified,
              fullPath: fullPath
            });
          }
        }
        
        return NextResponse.json({ 
          success: false, 
          error: 'Animation generation failed: Output file not found',
          stdout,
          stderr
        });
      }
    } catch (error: any) {
      console.error('❌ Error:', error);
      return NextResponse.json({ 
        success: false, 
        error: error.error ? error.error.message : (error.message || 'Unknown error'), 
        stdout: error.stdout || '',
        stderr: error.stderr || ''
      });
    }
  } catch (error) {
    console.error('Error regenerating animation:', error);
    return NextResponse.json(
      { 
        error: error instanceof Error ? error.message : 'Unknown error',
        status: 'error'
      }, 
      { status: 500 }
    );
  }
} 