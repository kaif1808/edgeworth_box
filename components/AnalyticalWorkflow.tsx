import React, { useState } from 'react';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

interface WorkingsData {
  [key: string]: {
    title: string;
    content: string[];
  };
}

interface AnalyticalWorkflowProps {
  workings: WorkingsData;
  darkMode?: boolean;
}

export default function AnalyticalWorkflow({ workings, darkMode }: AnalyticalWorkflowProps) {
  const [expandedSection, setExpandedSection] = useState<string | null>(null);

  const toggleSection = (key: string) => {
    setExpandedSection(expandedSection === key ? null : key);
  };

  const renderLatexLine = (line: string, index: number) => {
    const parts = line.split(/\$(\$)?/); // Split by $$ or $
    return (
      <div key={index} className="text-sm text-slate-600 dark:text-slate-300 mb-2 leading-relaxed">
        {parts.map((part, i) => {
          if (i % 4 === 2) { // Block math: $$...$$
             // Remove empty strings if split caused them
             if (!part) return null;
             return <div key={i} className="my-2"><BlockMath>{part}</BlockMath></div>;
          } else if (i % 2 === 1) { // Inline math: $...$
             if (!part) return null;
             return <span key={i}><InlineMath>{part}</InlineMath></span>;
          } else {
             if (!part) return null;
             return <span key={i}>{part}</span>;
          }
        })}
      </div>
    );
  };

  if (!workings || Object.keys(workings).length === 0) {
    return null;
  }

  return (
    <div className="mt-6 pt-4 border-t border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-900 rounded-lg shadow-sm p-4">
      <h3 className="text-md font-semibold text-slate-800 dark:text-slate-200 mb-3">Analytical Workflow</h3>
      <div className="flex flex-col gap-2">
        {Object.entries(workings).map(([key, { title, content }]) => (
          <div key={key} className="border border-slate-200 dark:border-slate-700 rounded-md overflow-hidden">
            <button
              onClick={() => toggleSection(key)}
              className="w-full px-4 py-3 text-left bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors flex justify-between items-center"
            >
              <span className="font-medium text-sm text-slate-700 dark:text-slate-300">{title}</span>
              <svg 
                className={`w-4 h-4 transform transition-transform duration-200 text-slate-500 ${expandedSection === key ? 'rotate-180' : ''}`} 
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            {expandedSection === key && (
              <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-700">
                {content.map(renderLatexLine)}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

