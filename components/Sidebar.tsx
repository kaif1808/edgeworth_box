import React, { useState } from 'react';
import { VisualSettings } from './EdgeworthBox';

interface SidebarProps {
  totalResources: { x: number; y: number };
  setTotalResources: (val: { x: number; y: number }) => void;
  endowmentA: { x: number; y: number };
  setEndowmentA: (val: { x: number; y: number }) => void;
  agentA: AgentParams;
  setAgentA: (val: AgentParams) => void;
  agentB: AgentParams;
  setAgentB: (val: AgentParams) => void;
  visualSettings: VisualSettings;
  setVisualSettings: (val: VisualSettings) => void;
  onCalculate: () => void;
  loading: boolean;
  theme: 'professional' | 'textbook';
  toggleTheme: () => void;
  setShowHelp: (val: boolean) => void;
  darkMode: boolean;
  toggleDarkMode: () => void;
}

export interface AgentParams {
  type: string;
  params: {
    alpha?: number;
    beta?: number;
    a?: number;
    b?: number;
    formula?: string;
  };
}

const UTILITY_TYPES = [
  "Cobb-Douglas",
  "Non-standard Cobb-Douglas",
  "Perfect Substitutes",
  "Perfect Complements (Min)",
  "Max Preferences (Convex)",
  "Quasi-Linear (Shifted Product)",
  "Satiation (Bliss Point)",
  "Mixed Cobb-Douglas",
  "Custom (Enter Formula)"
];

const PRESETS: Record<string, any> = {
    "Custom": {},
    "Standard Box (Shifted)": {
        dim: [5, 10], endow: [3, 3],
        A: { type: "Quasi-Linear (Shifted Product)", params: { b: 3.0 } },
        B: { type: "Quasi-Linear (Shifted Product)", params: { b: 2.0 } }
    },
    "CD vs Perf. Subs": {
        dim: [12, 12], endow: [6, 6],
        A: { type: "Mixed Cobb-Douglas", params: { alpha: 0.8 } },
        B: { type: "Perfect Substitutes", params: { alpha: 1.0, beta: 1.0 } }
    },
    "Min vs Max": {
        dim: [6, 6], endow: [4, 1],
        A: { type: "Perfect Complements (Min)", params: { alpha: 1.0, beta: 1.0 } },
        B: { type: "Max Preferences (Convex)", params: { alpha: 1.0, beta: 1.0 } }
    },
    "Leontief vs Perf. Subs": {
        dim: [10, 10], endow: [4, 4],
        A: { type: "Perfect Complements (Min)", params: { alpha: 1.0, beta: 1.0 } },
        B: { type: "Perfect Substitutes", params: { alpha: 1.0, beta: 1.0 } }
    },
    "Satiation (Bliss Point)": {
        dim: [10, 10], endow: [4, 8],
        A: { type: "Satiation (Bliss Point)", params: { a: 3.0, b: 3.0 } },
        B: { type: "Cobb-Douglas", params: { alpha: 1.0, beta: 1.0 } }
    }
};

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value));

interface NumericControlProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}

const NumericControl: React.FC<NumericControlProps> = ({ label, value, min, max, step, onChange }) => {
  const safeValue = Number.isFinite(value) ? value : min;

  const handleCommit = (next: number) => {
    if (isNaN(next)) return;
    const clamped = clamp(next, min, max);
    onChange(clamped);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleCommit(Number(e.target.value));
  };

  return (
    <div className="flex flex-col gap-1">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700 dark:text-slate-300">{label}</span>
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="px-2 py-1 border border-slate-300 dark:border-slate-600 rounded text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
            onClick={() => handleCommit(safeValue - step)}
            aria-label={`Decrease ${label}`}
          >
            −
          </button>
          <input
            type="number"
            value={Number(safeValue.toFixed(4))}
            min={min}
            max={max}
            step={step}
            onChange={handleInputChange}
            className="w-20 border border-slate-300 dark:border-slate-600 rounded px-2 py-1 text-right text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
          />
          <button
            type="button"
            className="px-2 py-1 border border-slate-300 dark:border-slate-600 rounded text-sm text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
            onClick={() => handleCommit(safeValue + step)}
            aria-label={`Increase ${label}`}
          >
            +
          </button>
        </div>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={safeValue}
        onChange={(e) => handleCommit(Number(e.target.value))}
        className="w-full accent-blue-600"
      />
    </div>
  );
};

export const Sidebar: React.FC<SidebarProps> = ({
  totalResources,
  setTotalResources,
  endowmentA,
  setEndowmentA,
  agentA,
  setAgentA,
  agentB,
  setAgentB,
  visualSettings,
  setVisualSettings,
  onCalculate,
  loading,
  theme,
  toggleTheme,
  setShowHelp,
  darkMode,
  toggleDarkMode
}) => {
  const [selectedPreset, setSelectedPreset] = useState("Custom");
  const [showVisSettings, setShowVisSettings] = useState(false);

  const loadPreset = (presetName: string) => {
    setSelectedPreset(presetName);
    const p = PRESETS[presetName];
    if (!p || Object.keys(p).length === 0) return;

    if (p.dim) setTotalResources({ x: p.dim[0], y: p.dim[1] });
    if (p.endow) setEndowmentA({ x: p.endow[0], y: p.endow[1] });
    if (p.A) setAgentA(p.A);
    if (p.B) setAgentB(p.B);
  };

  const renderParamsInput = (agent: AgentParams, setAgent: (val: AgentParams) => void, label: string) => {
    const isStandardCD = agent.type === "Cobb-Douglas";
    const isNonStandardCD = agent.type === "Non-standard Cobb-Douglas";
    
    const handleChange = (key: string, value: any) => {
      let newParams = { ...agent.params, [key]: value };

      // Standard Cobb-Douglas: Strict Alpha + Beta = 1
      if (isStandardCD) {
        if (key === 'alpha') {
           newParams.beta = Number(Math.max(0.01, 1.0 - value).toFixed(3));
        } else if (key === 'beta') {
           newParams.alpha = Number(Math.max(0.01, 1.0 - value).toFixed(3));
        }
      }

      setAgent({
        ...agent,
        params: newParams
      });
    };

      return (
        <div className="flex flex-col gap-2 border dark:border-slate-700 p-3 rounded bg-white dark:bg-slate-800">
          <h3 className="font-semibold text-sm text-slate-700 dark:text-slate-300">{label} Params</h3>
          
          {agent.type === "Custom (Enter Formula)" ? (
             <div className="flex flex-col gap-1">
               <label className="text-xs text-slate-600 dark:text-slate-400">Formula (LaTeX supported, e.g., x^2 y):</label>
               <input 
                 type="text"
                 value={agent.params.formula || ""}
                 onChange={(e) => handleChange('formula', e.target.value)}
                 placeholder="e.g. x * y^2"
                 className="border border-slate-300 dark:border-slate-600 p-1 rounded w-full text-sm bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100"
               />
               <p className="text-xs text-slate-500 dark:text-slate-500">Use x for Good X, y for Good Y.</p>
             </div>
          ) : (
            <>
              {/* Alpha/Beta are common to most */}
              {["Cobb-Douglas", "Non-standard Cobb-Douglas", "Perfect Substitutes", "Perfect Complements (Min)", "Max Preferences (Convex)", "Mixed Cobb-Douglas"].includes(agent.type) && (
                <>
                  <NumericControl
                    label="Alpha (α)"
                    value={agent.params.alpha ?? 0.5}
                    min={0.01}
                    max={isNonStandardCD ? 10.0 : 1.0}
                    step={0.05}
                    onChange={(val) => handleChange('alpha', Number(val.toFixed(3)))}
                  />
                  {agent.type !== "Mixed Cobb-Douglas" && (
                    <NumericControl
                      label="Beta (β)"
                      value={agent.params.beta ?? 0.5}
                      min={0.01}
                      max={isNonStandardCD ? 10.0 : 1.0}
                      step={0.05}
                      onChange={(val) => handleChange('beta', Number(val.toFixed(3)))}
                    />
                  )}
                </>
              )}

              {/* a/b parameters for others */}
              {["Quasi-Linear (Shifted Product)", "Satiation (Bliss Point)"].includes(agent.type) && (
                 <>
                  <NumericControl
                    label="a"
                    value={agent.params.a ?? 0}
                    min={-50}
                    max={50}
                    step={1}
                    onChange={(val) => handleChange('a', Number(val.toFixed(2)))}
                  />
                  <NumericControl
                    label="b"
                    value={agent.params.b ?? 0}
                    min={-50}
                    max={50}
                    step={1}
                    onChange={(val) => handleChange('b', Number(val.toFixed(2)))}
                  />
                 </>
              )}
            </>
          )}
        </div>
      );
  };

    return (
      <div className="w-full bg-slate-50 dark:bg-slate-900 p-4 sm:p-6 border border-slate-200 dark:border-slate-800 lg:border-r lg:border-l-0 lg:border-t-0 lg:border-b-0 flex flex-col gap-6 overflow-y-auto max-h-[calc(100vh-11rem)] lg:max-h-none lg:h-screen rounded-3xl lg:rounded-none shadow-sm lg:shadow-none min-w-0 lg:min-w-[22rem]">
      <div className="flex justify-between items-center mb-2">
        <h1 className="text-xl font-bold text-slate-800 dark:text-slate-100">Edgeworth Box</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowHelp(true)} className="text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400" title="Help">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
            </svg>
          </button>
          <button onClick={toggleTheme} className="text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400" title="Toggle Theme">
            {theme === 'professional' ? (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            )}
          </button>
          <button onClick={toggleDarkMode} className="text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400" title="Toggle Dark Mode">
             {darkMode ? (
                // Sun icon
                 <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                   <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
                 </svg>
              ) : (
                // Moon icon
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
                </svg>
              )}
          </button>
        </div>
      </div>
      
      {/* Presets */}
      <div className="flex flex-col gap-2">
        <label className="font-semibold text-sm text-slate-900 dark:text-slate-100">Load Scenario</label>
        <select 
          value={selectedPreset} 
          onChange={(e) => loadPreset(e.target.value)}
          className="border border-slate-300 dark:border-slate-600 p-2 rounded w-full text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
        >
          {Object.keys(PRESETS).map(k => <option key={k} value={k}>{k}</option>)}
        </select>
      </div>
      
        {/* Total Resources */}
        <div className="flex flex-col gap-3">
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">Total Resources</h2>
          <NumericControl
            label="Good X (Total)"
            value={totalResources.x}
            min={1}
            max={50}
            step={1}
            onChange={(val) => setTotalResources({ ...totalResources, x: Math.round(val) })}
          />
          <NumericControl
            label="Good Y (Total)"
            value={totalResources.y}
            min={1}
            max={50}
            step={1}
            onChange={(val) => setTotalResources({ ...totalResources, y: Math.round(val) })}
          />
        </div>

        {/* Endowment A */}
        <div className="flex flex-col gap-3">
          <h2 className="font-semibold text-slate-900 dark:text-slate-100">Endowment A</h2>
          <NumericControl
            label="ωₓ"
            value={clamp(endowmentA.x, 0, totalResources.x)}
            min={0}
            max={totalResources.x}
            step={0.5}
            onChange={(val) => setEndowmentA({ ...endowmentA, x: Number(val.toFixed(2)) })}
          />
          <NumericControl
            label="ωᵧ"
            value={clamp(endowmentA.y, 0, totalResources.y)}
            min={0}
            max={totalResources.y}
            step={0.5}
            onChange={(val) => setEndowmentA({ ...endowmentA, y: Number(val.toFixed(2)) })}
          />
        </div>

      {/* Agent A Settings */}
      <div className="flex flex-col gap-2">
        <h2 className="font-semibold text-blue-700 dark:text-blue-400">Agent A Preferences</h2>
        <select 
            value={agentA.type}
            onChange={(e) => setAgentA({...agentA, type: e.target.value})}
            className="border border-slate-300 dark:border-slate-600 p-2 rounded w-full text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
        >
            {UTILITY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {renderParamsInput(agentA, setAgentA, "Agent A")}
      </div>

      {/* Agent B Settings */}
      <div className="flex flex-col gap-2">
        <h2 className="font-semibold text-purple-700 dark:text-purple-400">Agent B Preferences</h2>
        <select 
            value={agentB.type}
            onChange={(e) => setAgentB({...agentB, type: e.target.value})}
            className="border border-slate-300 dark:border-slate-600 p-2 rounded w-full text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100"
        >
            {UTILITY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {renderParamsInput(agentB, setAgentB, "Agent B")}
      </div>

      {/* Visual Settings */}
      <div className="border border-slate-200 dark:border-slate-700 rounded bg-white dark:bg-slate-800">
        <button 
          className="w-full p-2 text-left font-semibold text-slate-700 dark:text-slate-300 flex justify-between items-center"
          onClick={() => setShowVisSettings(!showVisSettings)}
        >
          🎨 Visual Settings
          <svg className={`w-4 h-4 transform transition-transform ${showVisSettings ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
        </button>
        
        {showVisSettings && (
          <div className="p-2 flex flex-col gap-2 border-t border-slate-200 dark:border-slate-700">
            <div className="grid grid-cols-2 gap-2 text-sm text-slate-700 dark:text-slate-300">
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.show_endow} onChange={(e) => setVisualSettings({...visualSettings, show_endow: e.target.checked})} /> Endowment</label>
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.show_core} onChange={(e) => setVisualSettings({...visualSettings, show_core: e.target.checked})} /> Core</label>
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.show_pareto} onChange={(e) => setVisualSettings({...visualSettings, show_pareto: e.target.checked})} /> Pareto Set</label>
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.show_we} onChange={(e) => setVisualSettings({...visualSettings, show_we: e.target.checked})} /> Walrasian Eq</label>
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.show_curves_A} onChange={(e) => setVisualSettings({...visualSettings, show_curves_A: e.target.checked})} /> Curves A</label>
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.show_curves_B} onChange={(e) => setVisualSettings({...visualSettings, show_curves_B: e.target.checked})} /> Curves B</label>
               <label className="flex items-center gap-2"><input type="checkbox" checked={visualSettings.line_mode} onChange={(e) => setVisualSettings({...visualSettings, line_mode: e.target.checked})} /> Connect Lines</label>
            </div>
            
            <div className="mt-2">
                <h4 className="text-xs font-semibold mb-1 text-slate-700 dark:text-slate-300">Line Styles</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                        <span className="block text-slate-500 dark:text-slate-400 mb-1">Agent A</span>
                        <select value={visualSettings.style_A} onChange={(e) => setVisualSettings({...visualSettings, style_A: e.target.value})} className="border border-slate-300 dark:border-slate-600 rounded w-full p-1 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100">
                            <option value="solid">Solid</option>
                            <option value="dot">Dotted</option>
                            <option value="dash">Dashed</option>
                        </select>
                    </div>
                    <div>
                        <span className="block text-slate-500 dark:text-slate-400 mb-1">Agent B</span>
                        <select value={visualSettings.style_B} onChange={(e) => setVisualSettings({...visualSettings, style_B: e.target.value})} className="border border-slate-300 dark:border-slate-600 rounded w-full p-1 bg-white dark:bg-slate-700 text-slate-900 dark:text-slate-100">
                            <option value="solid">Solid</option>
                            <option value="dot">Dotted</option>
                            <option value="dash">Dashed</option>
                        </select>
                    </div>
                </div>
            </div>
            
              <div className="mt-2">
                <h4 className="text-xs font-semibold mb-1 text-slate-700 dark:text-slate-300">Indifference Curves</h4>
                <div className="flex text-xs font-semibold bg-slate-100 dark:bg-slate-700 rounded overflow-hidden">
                  {[
                    { label: 'Density', value: 'Auto (Density)' },
                    { label: 'Manual Count', value: 'Manual' }
                  ].map(option => (
                    <button
                      key={option.value}
                      type="button"
                      className={`flex-1 px-2 py-1 transition ${
                        visualSettings.ic_mode === option.value
                          ? 'bg-blue-600 text-white'
                          : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
                      }`}
                      onClick={() => setVisualSettings({ ...visualSettings, ic_mode: option.value })}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
                {visualSettings.ic_mode === 'Auto (Density)' ? (
                  <div className="mt-2">
                    <NumericControl
                      label="Curve Density"
                      value={visualSettings.n_curves}
                      min={10}
                      max={100}
                      step={5}
                      onChange={(val) => setVisualSettings({ ...visualSettings, n_curves: Math.round(val) })}
                    />
                  </div>
                ) : (
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <NumericControl
                      label="Agent A ICs"
                      value={visualSettings.n_curves_A ?? 10}
                      min={1}
                      max={50}
                      step={1}
                      onChange={(val) => setVisualSettings({ ...visualSettings, n_curves_A: Math.round(val) })}
                    />
                    <NumericControl
                      label="Agent B ICs"
                      value={visualSettings.n_curves_B ?? 10}
                      min={1}
                      max={50}
                      step={1}
                      onChange={(val) => setVisualSettings({ ...visualSettings, n_curves_B: Math.round(val) })}
                    />
                  </div>
                )}
              </div>
          </div>
        )}
      </div>

      <button
        onClick={onCalculate}
        disabled={loading}
        className={`p-3 rounded font-semibold transition-all flex justify-center items-center gap-2 ${
          loading
            ? 'bg-slate-300 dark:bg-slate-700 text-slate-500 dark:text-slate-400 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg dark:bg-blue-600 dark:hover:bg-blue-500'
        }`}
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-slate-500 dark:text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Calculating...
          </>
        ) : (
          'Calculate Equilibrium'
        )}
      </button>
    </div>
  );
};
