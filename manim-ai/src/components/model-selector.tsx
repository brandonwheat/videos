"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";

type Model = {
  id: string;
  name: string;
};

const models: Model[] = [
    { id: "o3-mini-2025-01-31", name: "GPT-o3-mini" },
  { id: "gpt-4o", name: "GPT-4o" },
  { id: "claude-3-opus", name: "Claude 3 Opus" },
  { id: "claude-3-sonnet", name: "Claude 3 Sonnet" },
];

interface ModelSelectorProps {
  selectedModel: string;
  onModelChange: (modelId: string) => void;
}

export function ModelSelector({ selectedModel, onModelChange }: ModelSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  
  const selectedModelName = models.find(model => model.id === selectedModel)?.name || selectedModel;
  
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full px-3 py-2 text-sm border rounded-md bg-background text-foreground"
      >
        <span>{selectedModelName}</span>
        <ChevronDown className="w-4 h-4 ml-2" />
      </button>
      
      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-background border rounded-md shadow-lg">
          <ul className="py-1">
            {models.map((model) => (
              <li key={model.id}>
                <button
                  className={`block w-full px-3 py-2 text-left text-sm hover:bg-muted ${
                    model.id === selectedModel ? "bg-primary/10 text-primary" : "text-foreground"
                  }`}
                  onClick={() => {
                    onModelChange(model.id);
                    setIsOpen(false);
                  }}
                >
                  {model.name}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
} 