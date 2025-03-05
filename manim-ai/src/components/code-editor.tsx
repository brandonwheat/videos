"use client";

import { useState, useEffect } from "react";
import { Loader2, Play, Copy, Check } from "lucide-react";

interface CodeEditorProps {
  code: string;
  onUpdate: (newCode: string) => void;
  onExecute: (code: string) => Promise<void>;
  isExecuting: boolean;
}

export function CodeEditor({ code, onUpdate, onExecute, isExecuting }: CodeEditorProps) {
  const [value, setValue] = useState(code);
  const [copied, setCopied] = useState(false);

  // Update the editor when the code prop changes
  useEffect(() => {
    setValue(code);
  }, [code]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    onUpdate(e.target.value);
  };

  const handleExecute = async () => {
    await onExecute(value);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden">
      <div className="flex justify-between items-center p-2 bg-muted">
        <h3 className="text-sm font-medium text-foreground">Manim Animation Code</h3>
        <div className="flex gap-2">
          <button
            onClick={copyToClipboard}
            className="p-1 rounded-md hover:bg-muted-foreground/20"
            title="Copy code"
          >
            {copied ? <Check size={16} /> : <Copy size={16} />}
          </button>
          <button
            onClick={handleExecute}
            disabled={isExecuting}
            className={`
              p-1 rounded-md
              ${isExecuting 
                ? 'bg-primary/50 cursor-not-allowed' 
                : 'bg-primary text-primary-foreground hover:bg-primary/90'
              }
            `}
            title="Run animation"
          >
            {isExecuting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Play size={16} />
            )}
          </button>
        </div>
      </div>
      <textarea
        value={value}
        onChange={handleChange}
        className="flex-1 p-4 font-mono text-sm w-full h-full bg-black/5 dark:bg-white/5 focus:outline-none resize-none"
        spellCheck={false}
        disabled={isExecuting}
      />
    </div>
  );
} 