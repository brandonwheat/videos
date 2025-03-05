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
  
  console.log(`🔍 Testing video access for: ${videoPath}`);
  
  // Fix duplicate query parameters (sometimes we see path?t=1234?t=1234)
  if (videoPath.includes('?')) {
    const baseUrl = videoPath.split('?')[0];
    const queryParams = new URLSearchParams();
    
    // Extract any query parameters
    videoPath.split('?').slice(1).forEach(paramSet => {
      const params = new URLSearchParams('?' + paramSet);
      for (const [key, value] of params.entries()) {
        // Only keep the first occurrence of each parameter
        if (!queryParams.has(key)) {
          queryParams.set(key, value);
        }
      }
    });
    
    // Reconstruct the URL with deduplicated parameters
    videoPath = baseUrl;
    console.log(`📝 Fixed query parameters, new path without params: ${videoPath}`);
  }
  
  // Remove leading slash if present
  if (videoPath.startsWith('/')) {
    videoPath = videoPath.substring(1);
    console.log(`📝 Removed leading slash, new path: ${videoPath}`);
  }
  
  // Build the absolute path in the public directory
  const publicPath = path.join(process.cwd(), 'public', videoPath);
  console.log(`📁 Full path to check: ${publicPath}`);
  
  // Check if the file exists
  const exists = await fileExists(publicPath);
  console.log(`${exists ? '✅' : '❌'} File exists: ${exists}`);
  
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
      console.log(`📊 File info: ${JSON.stringify(fileInfo)}`);
    } catch (error) {
      console.error('❌ Error getting file stats:', error);
    }
  }
  
  // List files in the directory for debugging
  const dirPath = path.dirname(publicPath);
  let directoryContents: string[] = [];
  
  try {
    if (await fileExists(dirPath)) {
      const files = await fs.promises.readdir(dirPath);
      directoryContents = files;
      console.log(`📂 Directory contents (${files.length} files): ${files.join(', ').substring(0, 100)}${files.length > 5 ? '...' : ''}`);
    }
  } catch (error) {
    console.error('❌ Error reading directory:', error);
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