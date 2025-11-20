import React from 'react';

interface SidebarProps {
  totalResources: { x: number; y: number };
  setTotalResources: (val: { x: number; y: number }) => void;
  endowmentA: { x: number; y: number };
  setEndowmentA: (val: { x: number; y: number }) => void;
  agentA: AgentParams;
  setAgentA: (val: AgentParams) => void;
  agentB: AgentParams;
  setAgentB: (val: AgentParams) => void;
  onCalculate: () => void;
  loading: boolean;
  theme: 'professional' | 'textbook';
  toggleTheme: () => void;
  setShowHelp: (val: boolean) => void;
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
  "Perfect Substitutes",
  "Perfect Complements (Min)",
  "Max Preferences (Convex)",
  "Quasi-Linear (Shifted Product)",
  "Satiation (Bliss Point)",
  "Mixed Cobb-Douglas",
  "Custom (Enter Formula)"
];

export const Sidebar: React.FC<SidebarProps> = ({
  totalResources,
  setTotalResources,
  endowmentA,
  setEndowmentA,
  agentA,
  setAgentA,
  agentB,
  setAgentB,
  onCalculate,
  loading,
  theme,
  toggleTheme,
  setShowHelp
}) => {
  
  const renderParamsInput = (agent: AgentParams, setAgent: (val: AgentParams) => void, label: string) => {
    const handleChange = (key: string, value: any) => {
      setAgent({
        ...agent,
        params: { ...agent.params, [key]: value }
      });
    };

    return (
      <div className="flex flex-col gap-2 border p-2 rounded bg-white">
        <h3 className="font-semibold text-sm text-slate-700">{label} Params</h3>
        
        {agent.type === "Custom (Enter Formula)" ? (
           <div className="flex flex-col gap-1">
             <label className="text-xs">Formula (LaTeX supported, e.g., x^2 y):</label>
             <input 
               type="text"
               value={agent.params.formula || ""}
               onChange={(e) => handleChange('formula', e.target.value)}
               placeholder="e.g. x * y^2"
               className="border p-1 rounded w-full text-sm"
             />
             <p className="text-xs text-slate-500">Use x for Good X, y for Good Y.</p>
           </div>
        ) : (
          <>
            {/* Alpha/Beta are common to most */}
            {["Cobb-Douglas", "Perfect Substitutes", "Perfect Complements (Min)", "Max Preferences (Convex)", "Mixed Cobb-Douglas"].includes(agent.type) && (
              <>
                <div className="flex gap-2 items-center">
                  <label className="w-12 text-sm">Alpha:</label>
                  <input 
                    type="number" step="0.1"
                    value={agent.params.alpha ?? 0.5} 
                    onChange={(e) => handleChange('alpha', Number(e.target.value))}
                    className="border p-1 rounded w-full text-sm"
                  />
                </div>
                <div className="flex gap-2 items-center">
                  <label className="w-12 text-sm">Beta:</label>
                  <input 
                    type="number" step="0.1"
                    value={agent.params.beta ?? 0.5} 
                    onChange={(e) => handleChange('beta', Number(e.target.value))}
                    className="border p-1 rounded w-full text-sm"
                  />
                </div>
              </>
            )}

            {/* a/b parameters for others */}
            {["Quasi-Linear (Shifted Product)", "Satiation (Bliss Point)"].includes(agent.type) && (
               <>
                <div className="flex gap-2 items-center">
                  <label className="w-12 text-sm">a:</label>
                  <input 
                    type="number" step="1"
                    value={agent.params.a ?? 0} 
                    onChange={(e) => handleChange('a', Number(e.target.value))}
                    className="border p-1 rounded w-full text-sm"
                  />
                </div>
                <div className="flex gap-2 items-center">
                  <label className="w-12 text-sm">b:</label>
                  <input 
                    type="number" step="1"
                    value={agent.params.b ?? 0} 
                    onChange={(e) => handleChange('b', Number(e.target.value))}
                    className="border p-1 rounded w-full text-sm"
                  />
                </div>
               </>
            )}
          </>
        )}
      </div>
    );
  };

  return (
    <div className="w-1/4 bg-slate-50 p-6 border-r border-slate-200 flex flex-col gap-6 overflow-y-auto h-screen min-w-[300px]">
      <div className="flex justify-between items-center mb-2">
        <h1 className="text-xl font-bold text-slate-800">Edgeworth Box</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowHelp(true)} className="text-slate-500 hover:text-blue-600" title="Help">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
            </svg>
          </button>
          <button onClick={toggleTheme} className="text-slate-500 hover:text-blue-600" title="Toggle Theme">
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
        </div>
      </div>
      
      {/* Total Resources */}
      <div className="flex flex-col gap-2">
        <h2 className="font-semibold">Total Resources</h2>
        <div className="flex gap-2 items-center">
          <label className="w-8">X:</label>
          <input 
            type="number" 
            value={totalResources.x} 
            onChange={(e) => setTotalResources({...totalResources, x: Number(e.target.value)})}
            className="border p-1 rounded w-full"
          />
        </div>
        <div className="flex gap-2 items-center">
          <label className="w-8">Y:</label>
          <input 
            type="number" 
            value={totalResources.y} 
            onChange={(e) => setTotalResources({...totalResources, y: Number(e.target.value)})}
            className="border p-1 rounded w-full"
          />
        </div>
      </div>

      {/* Endowment A */}
      <div className="flex flex-col gap-2">
        <h2 className="font-semibold">Endowment A</h2>
        <div className="flex gap-2 items-center">
          <label className="w-8">X:</label>
          <input 
            type="number" 
            value={endowmentA.x} 
            onChange={(e) => setEndowmentA({...endowmentA, x: Number(e.target.value)})}
            className="border p-1 rounded w-full"
          />
        </div>
        <div className="flex gap-2 items-center">
          <label className="w-8">Y:</label>
          <input 
            type="number" 
            value={endowmentA.y} 
            onChange={(e) => setEndowmentA({...endowmentA, y: Number(e.target.value)})}
            className="border p-1 rounded w-full"
          />
        </div>
      </div>

      {/* Agent A Settings */}
      <div className="flex flex-col gap-2">
        <h2 className="font-semibold text-blue-700">Agent A Preferences</h2>
        <select 
            value={agentA.type}
            onChange={(e) => setAgentA({...agentA, type: e.target.value})}
            className="border p-2 rounded w-full text-sm"
        >
            {UTILITY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {renderParamsInput(agentA, setAgentA, "Agent A")}
      </div>

      {/* Agent B Settings */}
      <div className="flex flex-col gap-2">
        <h2 className="font-semibold text-purple-700">Agent B Preferences</h2>
        <select 
            value={agentB.type}
            onChange={(e) => setAgentB({...agentB, type: e.target.value})}
            className="border p-2 rounded w-full text-sm"
        >
            {UTILITY_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        {renderParamsInput(agentB, setAgentB, "Agent B")}
      </div>

      <button
        onClick={onCalculate}
        disabled={loading}
        className={`p-3 rounded font-semibold transition-all flex justify-center items-center gap-2 ${
          loading
            ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
            : 'bg-blue-600 text-white hover:bg-blue-700 shadow-md hover:shadow-lg'
        }`}
      >
        {loading ? (
          <>
            <svg className="animate-spin h-5 w-5 text-slate-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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

