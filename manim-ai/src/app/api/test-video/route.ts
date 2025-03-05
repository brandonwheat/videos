import { NextResponse } from 'next/server';
import * as path from 'path';
import * as fs from 'fs';

// Helper function to check if a file exists
async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.promises.access(filePath, fs.constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

export async function GET(req: Request) {
  const url = new URL(req.url);
  let videoPath = url.searchParams.get('path');
  
  if (!videoPath) {
    return NextResponse.json({ error: 'No video path provided' }, { status: 400 });
  }
  
  // Remove leading slash if present
  if (videoPath.startsWith('/')) {
    videoPath = videoPath.substring(1);
  }
  
  // Build the absolute path in the public directory
  const publicPath = path.join(process.cwd(), 'public', videoPath);
  
  // Check if the file exists
  const exists = await fileExists(publicPath);
  
  // Get additional file info if it exists
  let fileInfo = null;
  if (exists) {
    try {
      const stats = await fs.promises.stat(publicPath);
      fileInfo = {
        size: stats.size,
        isFile: stats.isFile(),
        created: stats.birthtime,
        modified: stats.mtime
      };
    } catch (error) {
      console.error('Error getting file stats:', error);
    }
  }
  
  // List files in the directory for debugging
  const dirPath = path.dirname(publicPath);
  let directoryContents: string[] = [];
  
  try {
    if (await fileExists(dirPath)) {
      const files = await fs.promises.readdir(dirPath);
      directoryContents = files;
    }
  } catch (error) {
    console.error('Error reading directory:', error);
  }
  
  return NextResponse.json({
    requestedPath: videoPath,
    absolutePath: publicPath,
    exists,
    fileInfo,
    directoryPath: dirPath,
    directoryContents
  });
} 