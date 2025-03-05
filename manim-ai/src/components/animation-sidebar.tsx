"use client";

import { useState, useEffect, useRef } from "react";
import { X, Code, Video, ExternalLink, Loader2 } from "lucide-react";
import { CodeEditor } from "./code-editor";

interface AnimationSidebarProps {
  videoUrl: string | null;
  manimCode: string | null;
  isOpen: boolean;
  isGenerating: boolean;
  onClose: () => void;
  onRegenerateAnimation: (code: string) => Promise<void>;
  initialTab?: 'video' | 'code';
}

export function AnimationSidebar({
  videoUrl,
  manimCode,
  isOpen,
  isGenerating,
  onClose,
  onRegenerateAnimation,
  initialTab
}: AnimationSidebarProps) {
  const [activeTab, setActiveTab] = useState<'video' | 'code'>(
    initialTab || (videoUrl ? 'video' : 'code')
  );
  const [editedCode, setEditedCode] = useState('');
  const [codeChanged, setCodeChanged] = useState(false);
  const [videoTestResult, setVideoTestResult] = useState<any>(null);
  const [testingVideo, setTestingVideo] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [videoKey, setVideoKey] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const lastVideoUrl = useRef<string | null>(null);

  useEffect(() => {
    if (initialTab) {
      setActiveTab(initialTab);
    }
  }, [initialTab]);

  useEffect(() => {
    if (manimCode) {
      console.log('AnimationSidebar: Code updated', manimCode.substring(0, 30) + '...');
      setEditedCode(manimCode);
      setCodeChanged(false);
    }
  }, [manimCode]);

  useEffect(() => {
    if (videoUrl) {
      const baseCurrentUrl = videoUrl.split('?')[0];
      const baseLastUrl = lastVideoUrl.current?.split('?')[0] || '';
      const isNewVideo = baseCurrentUrl !== baseLastUrl;
      
      console.log(`AnimationSidebar: Video URL updated`, {
        current: videoUrl,
        previous: lastVideoUrl.current,
        isNewVideo
      });
      
      lastVideoUrl.current = videoUrl;
      
      setVideoError(null);
      setVideoLoaded(false);
      
      setVideoKey(prev => prev + 1);
      
      setActiveTab('video');
      
      const timeoutId = setTimeout(() => {
        if (videoUrl && isOpen) {
          testVideoUrl(videoUrl);
        }
      }, 500);
      
      return () => clearTimeout(timeoutId);
    }
  }, [videoUrl, isOpen]);

  useEffect(() => {
    if (isOpen) {
      if (videoUrl) {
        setActiveTab('video');
        testVideoUrl(videoUrl);
      } else if (manimCode) {
        setActiveTab('code');
      }
    }
  }, [isOpen, videoUrl, manimCode]);

  if (!isOpen) return null;

  const handleCodeUpdate = (newCode: string) => {
    setEditedCode(newCode);
    setCodeChanged(newCode !== manimCode);
  };

  const handleExecute = async (code: string) => {
    await onRegenerateAnimation(code);
    setCodeChanged(false);
  };

  const testVideoUrl = async (url: string) => {
    try {
      setTestingVideo(true);
      const testUrl = `/api/test-video?path=${encodeURIComponent(url)}`;
      const response = await fetch(testUrl);
      const result = await response.json();
      setVideoTestResult(result);
    } catch (error) {
      console.error('Error testing video URL:', error);
      setVideoTestResult({ error: String(error) });
    } finally {
      setTestingVideo(false);
    }
  };

  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement>) => {
    const videoElement = e.currentTarget;
    const errorMessage = videoElement.error 
      ? `Error loading video: ${videoElement.error.message || 'Unknown error'} (code: ${videoElement.error.code})`
      : 'Video failed to load (unknown error)';
    
    setVideoError(errorMessage);
    setVideoLoaded(false);
    console.error('Video error:', errorMessage, videoElement.error);
    
    if (videoUrl) {
      testVideoUrl(videoUrl);
    }
  };

  const handleVideoLoaded = () => {
    console.log('Video loaded successfully');
    setVideoLoaded(true);
    setVideoError(null);
  };

  return (
    <div 
      className={`animation-sidebar ${isOpen ? 'open' : ''}`}
      style={{
        position: 'fixed',
        right: 0,
        top: 0,
        bottom: 0,
        width: '400px',
        height: '100vh',
        zIndex: 999,
        backgroundColor: 'var(--background)',
        boxShadow: '-5px 0 15px rgba(0, 0, 0, 0.1)',
        transform: isOpen ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.3s ease',
        display: 'flex',
        flexDirection: 'column',
        overflowY: 'auto'
      }}
    >
      {/* Header */}
      <div className="animation-sidebar-header">
        <h2 className="text-lg font-bold">Animation Studio</h2>
        <button
          onClick={onClose}
          className="p-1 rounded-full hover:bg-muted"
          title="Close panel"
        >
          <X size={18} />
        </button>
      </div>

      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('video')}
          className={`flex items-center gap-2 px-4 py-2 ${
            activeTab === 'video' 
              ? 'border-b-2 border-primary font-medium' 
              : 'text-muted-foreground'
          }`}
          disabled={!videoUrl}
        >
          <Video size={18} />
          Animation
        </button>
        <button
          onClick={() => setActiveTab('code')}
          className={`flex items-center gap-2 px-4 py-2 ${
            activeTab === 'code' 
              ? 'border-b-2 border-primary font-medium' 
              : 'text-muted-foreground'
          }`}
        >
          <Code size={18} />
          Code {codeChanged && '•'}
        </button>
      </div>

      {/* Content */}
      <div className="animation-sidebar-content">
        {activeTab === 'video' && videoUrl ? (
          <div className="flex flex-col gap-4 p-4">
            <div className="video-container mb-4 bg-black/10 dark:bg-black/30 rounded-lg flex items-center justify-center aspect-video">
              {isGenerating ? (
                <div className="flex flex-col items-center justify-center p-4 text-center">
                  <Loader2 className="h-8 w-8 animate-spin mb-2" />
                  <p>Generating animation...</p>
                </div>
              ) : (
                <video 
                  key={videoKey}
                  ref={videoRef}
                  src={videoUrl} 
                  controls 
                  className="w-full h-full rounded"
                  autoPlay
                  loop
                  onError={handleVideoError}
                  onLoadedData={handleVideoLoaded}
                >
                  Your browser does not support the video tag.
                </video>
              )}
            </div>

            <div className="mt-2 flex justify-between">
              <a 
                href={videoUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-sm text-primary hover:underline"
              >
                Open video in new tab
              </a>
            </div>
          </div>
        ) : activeTab === 'video' ? (
          <div className="flex flex-col h-full items-center justify-center text-muted-foreground">
            No animation available
          </div>
        ) : (
          <div className="editor-container p-4 h-full flex flex-col">
            {manimCode ? (
              <>
                {/* Debug info - hidden by default, can be toggled */}
                <div className="mb-4 p-3 bg-yellow-100 dark:bg-yellow-900/30 rounded-md text-sm">
                  <details>
                    <summary className="font-medium cursor-pointer">Debug Info</summary>
                    <div className="mt-2">
                      <p>Code length: {manimCode.length} characters</p>
                      <p>First 100 chars: <code className="text-xs">{manimCode.substring(0, 100)}...</code></p>
                      <p>Code updated: {new Date().toLocaleTimeString()}</p>
                    </div>
                  </details>
                </div>
                
                <CodeEditor 
                  code={editedCode} 
                  onUpdate={handleCodeUpdate}
                  onExecute={handleExecute}
                  isExecuting={isGenerating} 
                />
                
                <div className="mt-4">
                  <button
                    onClick={() => handleExecute(editedCode)}
                    disabled={isGenerating}
                    className="w-full py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50 flex items-center justify-center gap-2"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="animate-spin h-4 w-4" />
                        Generating Animation...
                      </>
                    ) : (
                      <>
                        <Video className="h-4 w-4" />
                        Regenerate Animation
                      </>
                    )}
                  </button>
                </div>
              </>
            ) : (
              <div className="flex flex-col h-full items-center justify-center text-muted-foreground">
                <p>No code available</p>
                <p className="text-sm mt-2">The Manim code will appear here when an animation is generated.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}