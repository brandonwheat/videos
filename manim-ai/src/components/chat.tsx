"use client";

import { useState, useRef, useEffect } from "react";
import { SendIcon, RefreshCw, Settings, Loader2, AlertCircle, Info, Code, Video } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { ModelSelector } from "./model-selector";
import { useChat } from "@ai-sdk/react";
import { AnimationSidebar } from "./animation-sidebar";

type Message = {
  role: 'user' | 'assistant' | 'system';
  content: string;
};

type ChatState = {
  videoUrl: string | null;
  generatingAnimation: boolean;
  animationStatus: string;
  selectedModel: string;
  manimCode: string | null;
};

// Define the expected data type
interface ChatData {
  videoUrl?: string;
  status?: string;
  error?: string;
  manimCode?: string;
  videoTimestamp?: string;
  newAnimation?: boolean;
  [key: string]: any;
}

export default function Chat() {
  const [state, setState] = useState<ChatState>({
    videoUrl: null,
    generatingAnimation: false,
    animationStatus: '',
    selectedModel: "gpt-4o",
    manimCode: null
  });
  
  const [showSettings, setShowSettings] = useState(false);
  const [showSidebar, setShowSidebar] = useState(false);
  const [sidebarTab, setSidebarTab] = useState<'video' | 'code'>('video');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [debugInfo, setDebugInfo] = useState<string[]>([]);
  const [showDebug, setShowDebug] = useState(false);
  const [videoTestResult, setVideoTestResult] = useState<any>(null);
  const [testingVideo, setTestingVideo] = useState(false);

  // Function to add debug info
  const addDebugInfo = (info: string) => {
    console.log(`[DEBUG] ${info}`);
    setDebugInfo(prev => [...prev, `${new Date().toLocaleTimeString()}: ${info}`]);
  };

  // Function to extract Manim code from message content
  const extractManimCode = (content: string): string | null => {
    // Look for code blocks with python or no language specified
    const codeBlockRegex = /```(?:python)?([\s\S]*?)```/g;
    const matches = [...content.matchAll(codeBlockRegex)];
    
    if (matches.length === 0) {
      console.log('No code blocks found in message');
      return null;
    }
    
    console.log(`Found ${matches.length} code blocks in message`);
    
    // Find the code block that contains Manim-specific imports or class definitions
    for (const match of matches) {
      const code = match[1].trim();
      // Check for common Manim patterns
      if (
        (code.includes('manim') || code.includes('Scene')) && 
        (code.includes('class') || code.includes('def'))
      ) {
        console.log('Found Manim code block:', code.substring(0, 100) + '...');
        return code;
      }
    }
    
    // If no specific Manim code block found, use the largest code block as a fallback
    let largestBlock = matches[0][1].trim();
    let largestLength = largestBlock.length;
    
    for (const match of matches) {
      const code = match[1].trim();
      if (code.length > largestLength) {
        largestBlock = code;
        largestLength = code.length;
      }
    }
    
    console.log('Using largest code block as fallback:', largestBlock.substring(0, 100) + '...');
    return largestBlock;
  };

  // Use AI SDK's useChat hook
  const { 
    messages, 
    input, 
    handleInputChange, 
    handleSubmit, 
    isLoading, 
    error,
    data,
    reload
  } = useChat({
    api: '/api/chat',
    body: {
      model: state.selectedModel
    },
    id: "manim-chat",
    streamProtocol: "data",
    onFinish: (message) => {
      addDebugInfo(`Chat finished: ${message.content.substring(0, 30)}...`);
      // Reset generating animation state if we were generating one
      if (state.generatingAnimation) {
        setState(prev => ({ 
          ...prev, 
          generatingAnimation: prev.videoUrl ? false : prev.generatingAnimation,
          animationStatus: prev.videoUrl ? 'complete' : 'error'
        }));
      }
      
      // Extract Manim code from the response if available
      const code = extractManimCode(message.content);
      if (code) {
        console.log('Setting manimCode in state:', code.substring(0, 30) + '...');
        setState(prev => ({ ...prev, manimCode: code }));
        addDebugInfo(`Extracted Manim code: ${code.substring(0, 30)}...`);
      }
    },
    onError: (err) => {
      addDebugInfo(`Error: ${err.message}`);
      console.error('Chat error:', err);
      // Reset generating animation state
      if (state.generatingAnimation) {
        setState(prev => ({ 
          ...prev, 
          generatingAnimation: false,
          animationStatus: 'error'
        }));
      }
    }
  });

  // Function to get the display status message
  const getStatusMessage = () => {
    if (!state.generatingAnimation) return null;
    
    switch (state.animationStatus) {
      case 'starting':
        return 'Starting animation generation...';
      case 'generating_manim_code':
        return 'Generating Manim code...';
      case 'running_manim':
        return 'Running Manim to create animation...';
      case 'animation_complete':
        return 'Animation complete!';
      case 'animation_failed':
        return 'Animation generation failed';
      case 'animation_error':
        return 'Error generating animation';
      case 'generating_text':
        return 'Generating explanation...';
      case 'completed':
        return 'Process completed';
      default:
        return 'Generating animation... this may take a few minutes';
    }
  };

  // Add a safety timeout to reset animation state if it gets stuck
  useEffect(() => {
    if (state.generatingAnimation) {
      // Set a timeout to reset the state after 2 minutes if still generating
      const timeoutId = setTimeout(() => {
        if (state.generatingAnimation) {
          addDebugInfo('Resetting stuck animation state after timeout');
          setState(prev => ({
            ...prev,
            generatingAnimation: false,
            animationStatus: 'timeout'
          }));
        }
      }, 120000); // 2 minutes
      
      return () => clearTimeout(timeoutId);
    }
  }, [state.generatingAnimation]);

  // Listen for data updates (video URL and status)
  useEffect(() => {
    if (!data) return;
    
    // Handle data that comes as an array (batch of updates)
    if (Array.isArray(data)) {
      addDebugInfo(`Data update received: ${JSON.stringify(data)}`);
      
      // Process the array to find the most important update (video URL first, then latest status)
      const mostRecentData = data.reduce((acc, item) => {
        // Make sure item is an object before accessing properties
        if (item && typeof item === 'object') {
          // If we already have a videoUrl, keep it
          if (acc.videoUrl) {
            // Just update status if present in current item
            if ('status' in item && item.status) acc.status = item.status as string;
            if ('error' in item && item.error) acc.error = item.error as string;
          } else {
            // Otherwise merge everything
            return { ...acc, ...item as ChatData };
          }
        }
        return acc;
      }, {} as ChatData);
      
      // Now process this single consolidated object
      handleDataUpdate(mostRecentData);
      return;
    }
    
    // Handle data that comes as a single object
    handleDataUpdate(data as ChatData);
    
  }, [data]);

  // Extract the data handling logic to prevent repeated code
  const handleDataUpdate = (chatData: ChatData) => {
    // Check for the special "new animation available" status first
    if ('status' in chatData && chatData.status === 'new_animation_available' && 'videoUrl' in chatData && chatData.videoUrl) {
      const videoUrl = chatData.videoUrl as string;
      addDebugInfo(`NEW ANIMATION AVAILABLE: ${videoUrl}`);
      
      // Force state update with the new video URL and trigger UI refresh
      setState(prevState => ({
        ...prevState,
        videoUrl: videoUrl + (chatData.videoTimestamp ? `?t=${chatData.videoTimestamp}` : ''),
        generatingAnimation: false,
        animationStatus: 'animation_complete'
      }));
      
      // Force the sidebar to open with video tab
      addDebugInfo("Opening sidebar with NEW video");
      setSidebarTab('video');
      setShowSidebar(true);
      return; // Skip other processing for this special event
    }
    
    // Check if we have Manim code in the data
    if ('manimCode' in chatData && chatData.manimCode) {
      const code = chatData.manimCode as string;
      console.log(`[DIRECT] Received Manim code from API (${code.length} chars)`);
      
      // Update state with the code
      setState(prevState => ({
        ...prevState,
        manimCode: code
      }));
      
      // No need to open the sidebar yet, we'll do that when the video is ready
    }
    
    // Immediately handle video URL if it exists
    if ('videoUrl' in chatData && chatData.videoUrl) {
      const videoUrl = chatData.videoUrl as string;
      addDebugInfo(`Video URL received: ${videoUrl}`);
      
      // Check if the URL appears valid
      const isValidUrl = videoUrl.startsWith('/') || videoUrl.startsWith('http');
      addDebugInfo(`Is video URL valid format? ${isValidUrl}`);
      
      // Add timestamp parameter to force reload if provided
      const finalVideoUrl = chatData.videoTimestamp 
        ? `${videoUrl}?t=${chatData.videoTimestamp}` 
        : videoUrl;
      
      // Mark as a new animation if specified
      const isNewAnimation = Boolean(chatData.newAnimation);
      if (isNewAnimation) {
        addDebugInfo(`This is a NEW animation (${finalVideoUrl})`);
      }
      
      // Directly update state with the video URL
      setState(prevState => ({
        ...prevState,
        videoUrl: finalVideoUrl,
        generatingAnimation: false,
        animationStatus: 'animation_complete'
      }));
      
      // Force the sidebar to open with video tab
      addDebugInfo("Opening sidebar with video");
      setSidebarTab('video');
      setShowSidebar(true);
    } 
    // Handle status updates - only if we don't have a video URL update in the same batch
    else if ('status' in chatData && chatData.status) {
      const status = chatData.status as string;
      addDebugInfo(`Status update: ${status}`);
      
      // Check if it's a terminal status
      const isTerminalStatus = ['completed', 'animation_complete', 'animation_failed', 'error'].includes(status);
      
      setState(prevState => ({
        ...prevState,
        animationStatus: status,
        // If we get a terminal status, update the generating flag
        generatingAnimation: isTerminalStatus ? false : prevState.generatingAnimation
      }));
      
      // If the animation is completed and we have a video, open the sidebar
      if (status === 'completed' && state.videoUrl) {
        addDebugInfo("Animation completed with video, opening sidebar");
        setSidebarTab('video');
        setShowSidebar(true);
      }
    }
    
    // Handle error
    if ('error' in chatData && chatData.error) {
      const errorMessage = chatData.error as string;
      addDebugInfo(`Error message received: ${errorMessage}`);
      
      setState(prevState => ({
        ...prevState,
        generatingAnimation: false,
        animationStatus: 'error'
      }));
    }
  };

  // Check if animation might be needed before submitting
  const handleSubmitWithAnimationCheck = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if animation keywords are in the input
    const animationKeywords = [
      'animation', 
      'visual', 
      'visualize',
      'animate',
      'show me',
      'create a video',
      'generate a video',
      'demonstrate',
      'illustrate',
      'diagram',
      'display',
      'visualization'
    ];
    
    const needsAnimation = animationKeywords.some(keyword => 
      input.toLowerCase().includes(keyword)
    );
    
    if (needsAnimation) {
      addDebugInfo(`Animation requested: "${input.substring(0, 30)}..."`);
      setState(prev => ({ 
        ...prev, 
        generatingAnimation: true,
        animationStatus: 'starting'
      }));
    }
    
    // Reset video URL when sending a new message
    setState(prev => ({ ...prev, videoUrl: null }));
    
    // Submit the message
    handleSubmit(e);
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
    
    // Log last message for debugging
    if (messages.length > 0) {
      const lastMessage = messages[messages.length - 1];
      console.log(`Last message (${lastMessage.role}):`, lastMessage.content.substring(0, 100) + '...');
      
      // Check if the last message might contain a videoUrl
      if (lastMessage.role === 'assistant' && lastMessage.content.includes('/media/videos')) {
        addDebugInfo(`Last message might contain a video URL: ${lastMessage.content.substring(0, 100)}...`);
      }
    }
  }, [messages]);
  
  // Function to regenerate the last response
  const regenerateLastResponse = () => {
    addDebugInfo("Regenerating response");
    setState(prev => ({ 
      ...prev, 
      videoUrl: null,
      animationStatus: ''
    }));
    reload();
  };
  
  const handleModelChange = (modelId: string) => {
    addDebugInfo(`Model changed to: ${modelId}`);
    setState(prev => ({ ...prev, selectedModel: modelId }));
  };
  
  // Function to test if the video URL is accessible
  const testVideoUrl = async (url: string) => {
    try {
      setTestingVideo(true);
      const testUrl = `/api/test-video?path=${encodeURIComponent(url)}`;
      const response = await fetch(testUrl);
      const result = await response.json();
      setVideoTestResult(result);
      addDebugInfo(`Video test result: ${JSON.stringify(result)}`);
    } catch (error) {
      console.error('Error testing video URL:', error);
      const errorMessage = error instanceof Error ? error.message : String(error);
      setVideoTestResult({ error: errorMessage });
      addDebugInfo(`Error testing video URL: ${errorMessage}`);
    } finally {
      setTestingVideo(false);
    }
  };

  // Function to regenerate an animation with updated code
  const regenerateAnimation = async (code: string): Promise<void> => {
    addDebugInfo(`Regenerating animation with updated code`);
    
    // Batch state updates to minimize re-renders
    setState(prev => ({
      ...prev,
      manimCode: code,
      generatingAnimation: true,
      animationStatus: 'starting'
      // Don't clear videoUrl yet to avoid flickering
    }));
    
    try {
      addDebugInfo(`Sending code to API for regeneration`);
      const response = await fetch('/api/regenerate-animation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ manimCode: code }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to regenerate animation: ${response.statusText}`);
      }
      
      const result = await response.json();
      addDebugInfo(`Received API response: ${JSON.stringify(result)}`);
      
      // Add a timestamp to force the video to reload
      if (result.videoUrl) {
        result.videoUrl = `${result.videoUrl}?t=${Date.now()}`;
        addDebugInfo(`Added timestamp to video URL: ${result.videoUrl}`);
      }
      
      // Update state with the result
      setState(prev => ({
        ...prev,
        videoUrl: result.videoUrl || null,
        generatingAnimation: false,
        animationStatus: result.status || 'completed'
      }));
      
      // Show the video tab
      setSidebarTab('video');
      setShowSidebar(true);
      
    } catch (error) {
      addDebugInfo(`Error regenerating animation: ${error instanceof Error ? error.message : String(error)}`);
      
      setState(prev => ({
        ...prev,
        generatingAnimation: false,
        animationStatus: 'error'
      }));
    }
  };

  // Handler for toggling the code tab in the sidebar
  const showCodeTab = () => {
    if (state.manimCode) {
      setSidebarTab('code');
      setShowSidebar(true);
    }
  };

  // Handler for toggling the animation/video tab in the sidebar
  const showVideoTab = () => {
    if (state.videoUrl) {
      setSidebarTab('video');
      setShowSidebar(true);
    }
  };

  // Add a convenient check for the animation details
  const hasAnimation = !!state.videoUrl;
  const hasCode = !!state.manimCode;
  
  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] max-w-5xl mx-auto p-4">
      <div className="flex justify-between items-center mb-2">
        <h1 className="text-3xl font-bold text-primary">
          3Blue1Brown AI Video Generator
        </h1>
        <div className="flex gap-2">
          {/* Animation sidebar toggle button when video is available */}
          {hasAnimation && (
            <button 
              onClick={() => { setSidebarTab('video'); setShowSidebar(!showSidebar); }}
              className={`p-2 rounded-lg ${(showSidebar && sidebarTab === 'video') ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}
              title="View Animation"
            >
              <Video className="h-5 w-5" />
            </button>
          )}
          
          {/* Code editor button when code is available */}
          {hasCode && (
            <button 
              onClick={showCodeTab}
              className={`p-2 rounded-lg ${(showSidebar && sidebarTab === 'code') ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}
              title="Edit Animation Code"
            >
              <Code className="h-5 w-5" />
            </button>
          )}
          
          {/* Settings button */}
        <button 
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 rounded-lg bg-muted text-muted-foreground"
          title="Settings"
        >
          <Settings className="h-5 w-5" />
        </button>
        </div>
      </div>
      
      {showSettings && (
        <div className="mb-4 p-4 border rounded-lg">
          <h2 className="text-lg font-medium mb-2">Settings</h2>
          <div className="grid grid-cols-[120px_1fr] gap-4 items-center">
            <label htmlFor="model-selector" className="text-sm">Model:</label>
            <ModelSelector 
              selectedModel={state.selectedModel} 
              onModelChange={handleModelChange} 
            />
          </div>
        </div>
      )}
      
      {/* Main chat area */}
      <div className="flex flex-col flex-1 overflow-hidden">
      <p className="text-center text-muted-foreground mb-6">
        Chat with AI to generate mathematical explanations in the style of 3Blue1Brown
      </p>

        {/* Show a notice when we have Manim code but the sidebar is closed */}
        {hasCode && !showSidebar && (
          <div className="mb-4 px-4 py-2 bg-primary/10 rounded-md text-sm flex items-center justify-between">
            <span>Manim code is available for this animation</span>
            <button 
              onClick={showCodeTab}
              className="px-3 py-1 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 text-xs"
            >
              View Code
            </button>
        </div>
      )}

        {/* Video display when available */}
        {state.videoUrl && !showSidebar && (
          <div className="mb-4">
            <h2 className="text-lg font-medium mb-2">Generated Animation</h2>
            
            <div className="p-4 bg-black rounded-lg">
          <video
            src={state.videoUrl}
            controls
                className="w-full max-h-[50vh] rounded-lg"
            autoPlay
              >
                Your browser does not support the video tag.
              </video>
        </div>
        </div>
      )}

        {/* Loading indicator */}
        {state.generatingAnimation && (
          <div className="mb-4 flex items-center justify-center p-4 bg-primary/10 rounded-lg">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            <span>{getStatusMessage()}</span>
          </div>
        )}
        
        {/* Messages container */}
        <div className="flex-1 overflow-auto border rounded-lg mb-4 p-4">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-8">
              <h2 className="text-2xl font-bold mb-2">Welcome to ManimAI!</h2>
              <p className="text-muted-foreground mb-8 max-w-md">
                Ask me to explain math concepts or generate animations in the style of 3Blue1Brown. 
                For example, try "Create an animation explaining the Pythagorean theorem"
              </p>
            </div>
          ) : (
            messages.map((message, index) => (
              <div 
                key={index} 
                className={`mb-4 ${message.role === 'user' ? 'text-right' : ''}`}
          >
            <div
                  className={`
                    inline-block p-3 rounded-lg max-w-[80%] 
                    ${message.role === 'user' 
                      ? 'bg-primary text-primary-foreground rounded-br-none' 
                      : 'bg-muted text-foreground text-left rounded-bl-none'
                    }
                  `}
                >
                  {message.role === 'assistant' ? (
                    <div className="prose dark:prose-invert">
                  <ReactMarkdown>
                        {message.content}
                  </ReactMarkdown>
                </div>
                  ) : (
                    <div>{message.content}</div>
              )}
            </div>
              </div>
            ))
        )}
        <div ref={messagesEndRef} />
      </div>

        {/* Input form */}
      <form
          onSubmit={handleSubmitWithAnimationCheck} 
        className="flex items-center space-x-2"
      >
        <input
            type="text"
          value={input}
          onChange={handleInputChange}
            placeholder="Ask about math concepts or request an animation..."
            className="flex-1 p-2 border rounded-l-lg focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isLoading}
        />
        <button
          type="submit"
            className="bg-primary text-primary-foreground p-2 rounded-r-lg hover:bg-primary/90 disabled:opacity-50"
            disabled={isLoading || !input.trim()}
        >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
          <SendIcon className="h-5 w-5" />
            )}
        </button>
          
          {messages.length > 0 && (
        <button
          type="button"
          onClick={regenerateLastResponse}
              className="bg-muted text-muted-foreground p-2 rounded-lg hover:bg-muted/90 disabled:opacity-50"
              disabled={isLoading}
              title="Regenerate last response"
        >
          <RefreshCw className="h-5 w-5" />
        </button>
          )}
      </form>
        
        {/* Error message */}
        {error && (
          <div className="mt-4 p-4 bg-destructive/10 text-destructive rounded-lg">
            Error: {error.message || "An error occurred"}
          </div>
        )}
        
        {/* Animation Sidebar */}
        <AnimationSidebar
          videoUrl={state.videoUrl}
          manimCode={state.manimCode}
          isOpen={showSidebar}
          isGenerating={state.generatingAnimation}
          onClose={() => setShowSidebar(false)}
          onRegenerateAnimation={regenerateAnimation}
          initialTab={sidebarTab}
        />
      </div>
    </div>
  );
} 