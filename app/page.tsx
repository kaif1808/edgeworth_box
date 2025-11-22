'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import EdgeworthBox, { VisualSettings } from '@/components/EdgeworthBox';
import AnalyticalWorkflow from '@/components/AnalyticalWorkflow';
import { Sidebar, AgentParams } from '@/components/Sidebar';

export default function Home() {
  const [totalResources, setTotalResources] = useState({ x: 10, y: 10 });
  const [endowmentA, setEndowmentA] = useState({ x: 5, y: 5 });
  
  // Initialize agents with default Cobb-Douglas
  const [agentA, setAgentA] = useState<AgentParams>({
    type: 'Cobb-Douglas',
    params: { alpha: 0.5, beta: 0.5 }
  });
  const [agentB, setAgentB] = useState<AgentParams>({
    type: 'Cobb-Douglas',
    params: { alpha: 0.5, beta: 0.5 }
  });

  const [visualSettings, setVisualSettings] = useState<VisualSettings>({
    show_endow: true,
    show_core: true,
    show_pareto: true,
    show_lens: true,
    show_curves_A: true,
    show_curves_B: true,
    line_mode: false,
    show_we: false,
    style_A: 'solid',
    style_B: 'dot',
    ic_mode: 'Auto (Density)',
    n_curves: 30,
    n_curves_A: 10,
    n_curves_B: 10
  });

  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState<'professional' | 'textbook'>('professional');
  const [darkMode, setDarkMode] = useState(false); // Dark mode state
  const [showHelp, setShowHelp] = useState(false);
  const [mobileView, setMobileView] = useState<'controls' | 'results'>('results');
  
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const toggleTheme = () => {
    const newTheme = theme === 'professional' ? 'textbook' : 'professional';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Sync dark mode with HTML class
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleCalculate = useCallback(async () => {
    // Cancel previous request if it exists
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setLoading(true);
    try {
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          include_grid: true,
          dimensions: {
            total_x: totalResources.x,
            total_y: totalResources.y
          },
          agent_a: {
            type: agentA.type,
            params: agentA.params,
            endowment: endowmentA
          },
          agent_b: {
            type: agentB.type,
            params: agentB.params
            // Endowment B is inferred in backend
          }
        }),
        signal: controller.signal
      });
      
      if (!response.ok) {
        let errorMessage = `Server error: ${response.status} ${response.statusText}`;
        try {
          const errorData = await response.json();
          if (errorData && errorData.error) {
            errorMessage = errorData.error;
          }
        } catch (e) {
          // Fallback to status text if JSON parsing fails
        }
        throw new Error(errorMessage);
      }
      
      const data = await response.json();

      // Validate response structure
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response format');
      }

      if (data.error) {
        throw new Error(data.error);
      }

      if (!data.contract_curve || !data.contract_curve.pareto_points || !data.walrasian_equilibrium) {
        throw new Error('Response missing required simulation data');
      }

      setResult(data);
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
        return;
      }
      console.error('Error calculating:', error);
      setResult({
        error: error instanceof Error ? error.message : 'Failed to calculate. Please check your inputs and try again.'
      });
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
    }
  }, [totalResources, endowmentA, agentA, agentB]);

  // Live Update Effect
  useEffect(() => {
    if (debounceTimer.current) clearTimeout(debounceTimer.current);
    
    debounceTimer.current = setTimeout(() => {
        handleCalculate();
    }, 800); // 800ms debounce

    return () => {
        if (debounceTimer.current) clearTimeout(debounceTimer.current);
    };
  }, [totalResources, endowmentA, agentA, agentB, handleCalculate]);


  return (
    <main className="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      {/* Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white dark:bg-slate-800 p-6 sm:p-8 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Edgeworth Box Concepts</h2>
              <button onClick={() => setShowHelp(false)} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-xl">&times;</button>
            </div>
            <div className="space-y-4 text-sm sm:text-base text-slate-700 dark:text-slate-300">
              <section>
                <h3 className="font-bold text-lg text-blue-600 dark:text-blue-400">Marginal Rate of Substitution (MRS)</h3>
                <p>The rate at which a consumer can give up some amount of one good in exchange for another good while maintaining the same level of utility. It corresponds to the slope of the indifference curve.</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600 dark:text-blue-400">Contract Curve</h3>
                <p>The set of all Pareto-efficient allocations. At any point on the contract curve, the MRS of both agents are equal, meaning no mutually beneficial trade is possible.</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600 dark:text-blue-400">Pareto Efficiency</h3>
                <p>An allocation is Pareto efficient if it is impossible to make one individual better off without making at least one individual worse off.</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600 dark:text-blue-400">Walrasian Equilibrium</h3>
                <p>A set of prices and an allocation where supply equals demand for all goods. It is always Pareto efficient (First Welfare Theorem).</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600 dark:text-blue-400">Custom Formulas</h3>
                <p>You can enter custom utility functions using LaTeX-like syntax (e.g., <code>x^2 * y</code>, <code>{`\\sqrt{x} + \\ln{y}`}</code>). Supported functions: log, ln, exp, sqrt, min, max.</p>
              </section>
            </div>
            <button onClick={() => setShowHelp(false)} className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 w-full dark:bg-blue-500 dark:hover:bg-blue-600">Close</button>
          </div>
        </div>
      )}

      {/* Mobile Header */}
      <div className="lg:hidden sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 shadow-sm">
        <div className="px-4 py-4 space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-blue-600 dark:text-blue-400 font-semibold">Edgeworth Box</p>
              <h1 className="text-xl font-bold text-slate-900 dark:text-slate-100">Simulator & Solver</h1>
              <p className="text-sm text-slate-500 dark:text-slate-400">Tune resources, compare equilibria.</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHelp(true)}
                className="p-2 rounded-full border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:border-blue-200 dark:hover:border-blue-800"
                aria-label="Open help"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                </svg>
              </button>
              <button
                onClick={toggleTheme}
                className="p-2 rounded-full border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:border-blue-200 dark:hover:border-blue-800"
                aria-label="Toggle theme"
              >
                {theme === 'professional' ? (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                  </svg>
                )}
              </button>
              <button
                onClick={toggleDarkMode}
                className="p-2 rounded-full border border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:border-blue-200 dark:hover:border-blue-800"
                aria-label="Toggle Dark Mode"
              >
                {darkMode ? (
                  // Sun icon
                   <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                     <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
                   </svg>
                ) : (
                  // Moon icon
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
                  </svg>
                )}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-sm font-semibold">
            {[
              { label: 'Controls', value: 'controls' },
              { label: 'Results', value: 'results' }
            ].map((tab) => (
              <button
                key={tab.value}
                onClick={() => setMobileView(tab.value as 'controls' | 'results')}
                className={`py-2 rounded-full border transition ${
                  mobileView === tab.value
                    ? 'border-blue-600 bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-500'
                    : 'border-slate-200 text-slate-500 bg-white dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-blue-600 dark:bg-blue-400 animate-pulse" />
              Live updates
            </span>
            <span>Debounce 0.8s</span>
          </div>
        </div>
      </div>

      <div className="flex flex-col lg:flex-row lg:min-h-screen">
        <section className={`${mobileView === 'controls' ? 'block' : 'hidden'} lg:block lg:w-[28rem] lg:max-w-[32rem] lg:shrink-0`}>
          <div className="lg:sticky lg:top-0">
            <Sidebar 
              totalResources={totalResources}
              setTotalResources={setTotalResources}
              endowmentA={endowmentA}
              setEndowmentA={setEndowmentA}
              agentA={agentA}
              setAgentA={setAgentA}
              agentB={agentB}
              setAgentB={setAgentB}
              visualSettings={visualSettings}
              setVisualSettings={setVisualSettings}
              onCalculate={handleCalculate}
              loading={loading}
              theme={theme}
              toggleTheme={toggleTheme}
              setShowHelp={setShowHelp}
              darkMode={darkMode}
              toggleDarkMode={toggleDarkMode}
            />
          </div>
        </section>

        <section className={`${mobileView === 'results' ? 'block' : 'hidden'} lg:block flex-1`}>
          <div className="bg-white/90 lg:bg-white dark:bg-slate-900/90 lg:dark:bg-slate-900 rounded-t-3xl lg:rounded-none px-4 py-6 sm:px-6 lg:px-10 lg:py-10 min-h-[60vh] shadow-inner lg:shadow-none transition-colors duration-300">
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wide text-blue-600 dark:text-blue-400 font-semibold">Live Results</p>
                  <h2 className="text-2xl lg:text-3xl font-bold text-slate-800 dark:text-slate-100">Simulation Insights</h2>
                </div>
                <button
                  onClick={handleCalculate}
                  disabled={loading}
                  className={`inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                    loading
                      ? 'bg-slate-200 text-slate-500 cursor-not-allowed dark:bg-slate-800 dark:text-slate-400'
                      : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm dark:bg-blue-600 dark:hover:bg-blue-500'
                  }`}
                >
                  {loading ? 'Updating…' : 'Refresh Now'}
                </button>
              </div>

              {result && !result.error ? (
                <div className="space-y-6">
                  <div className="w-full bg-white dark:bg-slate-900 rounded-3xl lg:rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 p-3 sm:p-4 h-auto">
                    <EdgeworthBox
                      data={result}
                      totalResources={totalResources}
                      endowmentA={endowmentA}
                      visualSettings={visualSettings}
                      darkMode={darkMode}
                    />
                  </div>
                  
                  {result.workings && (
                    <AnalyticalWorkflow workings={result.workings} darkMode={darkMode} />
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {result.walrasian_equilibrium?.exists ? (
                      <>
                        <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-700">
                          <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-2">Equilibrium Prices</h3>
                          <p className="text-slate-900 dark:text-slate-100">Price of X (px): <span className="font-mono">
                            {typeof result.walrasian_equilibrium?.price_ratio_px_py === 'number' 
                              ? result.walrasian_equilibrium.price_ratio_px_py.toFixed(4) 
                              : result.walrasian_equilibrium?.price_ratio_px_py || 'N/A'}
                          </span></p>
                          <p className="text-slate-900 dark:text-slate-100">Price of Y (py): <span className="font-mono">1.0000</span> (Numeraire)</p>
                        </div>
                        <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-700">
                          <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-2">Allocation</h3>
                          <p className="text-slate-900 dark:text-slate-100">Agent A: (<span className="font-mono">{result.walrasian_equilibrium?.allocation_a?.x?.toFixed(2)}</span>, <span className="font-mono">{result.walrasian_equilibrium?.allocation_a?.y?.toFixed(2)}</span>)</p>
                          <p className="text-slate-900 dark:text-slate-100">Agent B: (<span className="font-mono">{result.walrasian_equilibrium?.allocation_b?.x?.toFixed(2)}</span>, <span className="font-mono">{result.walrasian_equilibrium?.allocation_b?.y?.toFixed(2)}</span>)</p>
                        </div>
                        <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-700 md:col-span-2">
                          <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-2">Utility & MRS</h3>
                          <div className="grid grid-cols-2 gap-2 text-xs sm:text-sm text-slate-900 dark:text-slate-100">
                            <div>
                                <p className="font-medium text-slate-500 dark:text-slate-400">Agent A</p>
                                <p>U: <span className="font-mono">{typeof result.walrasian_equilibrium?.utility_a === 'number' ? result.walrasian_equilibrium.utility_a.toFixed(2) : result.walrasian_equilibrium?.utility_a || 'N/A'}</span></p>
                                <p>MRS: <span className="font-mono">{typeof result.walrasian_equilibrium?.mrs_a === 'number' ? result.walrasian_equilibrium.mrs_a.toFixed(2) : result.walrasian_equilibrium?.mrs_a || 'N/A'}</span></p>
                            </div>
                            <div>
                                <p className="font-medium text-slate-500 dark:text-slate-400">Agent B</p>
                                <p>U: <span className="font-mono">{typeof result.walrasian_equilibrium?.utility_b === 'number' ? result.walrasian_equilibrium.utility_b.toFixed(2) : result.walrasian_equilibrium?.utility_b || 'N/A'}</span></p>
                                <p>MRS: <span className="font-mono">{typeof result.walrasian_equilibrium?.mrs_b === 'number' ? result.walrasian_equilibrium.mrs_b.toFixed(2) : result.walrasian_equilibrium?.mrs_b || 'N/A'}</span></p>
                            </div>
                          </div>
                        </div>
                      </>
                    ) : (
                      <div className="md:col-span-2 bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-2xl border border-yellow-200 dark:border-yellow-800">
                        <h3 className="font-bold text-yellow-800 dark:text-yellow-300 mb-2 flex items-center gap-2">
                          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                            <path fillRule="evenodd" d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
                          </svg>
                          Walrasian Equilibrium Not Found
                        </h3>
                        <p className="text-yellow-900 dark:text-yellow-100 text-sm">
                          {result.walrasian_equilibrium?.message || "The solver failed to find a market-clearing price. This can happen with non-convex preferences or extreme parameters."}
                        </p>
                      </div>
                    )}
                  </div>
                  
                  {result.analysis && (
                      <div className={`p-4 rounded-2xl border text-sm sm:text-base ${
                        result.analysis.pareto_efficient 
                          ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300' 
                          : 'bg-yellow-50 border-yellow-200 text-yellow-800 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300'
                      }`}>
                          <h3 className="font-bold mb-2">{result.analysis.pareto_efficient ? '✅ Pareto Efficient' : '⚠️ Inefficient Allocation'}</h3>
                          <p className="mb-1">MRS Difference: {typeof result.analysis.mrs_difference === 'number' ? result.analysis.mrs_difference.toFixed(4) : result.analysis.mrs_difference}</p>
                          {result.analysis.trade_advice && <p className="font-medium">{result.analysis.trade_advice}</p>}
                      </div>
                  )}

                  <div className="mt-4">
                    <details className="group rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4">
                      <summary className="cursor-pointer text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 group-open:rotate-90 transition-transform">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                        View Raw JSON Data
                      </summary>
                      <pre className="bg-slate-900 text-slate-50 p-4 rounded-lg overflow-auto max-h-[300px] mt-2 text-xs font-mono shadow-inner dark:bg-black dark:text-slate-300">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </details>
                  </div>
                </div>
              ) : result && result.error ? (
                 <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-2xl text-red-700 dark:text-red-300">
                    <h3 className="font-bold mb-2">Error</h3>
                    <p>{result.error}</p>
                 </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[320px] sm:h-[400px] bg-slate-50 dark:bg-slate-800/50 rounded-2xl border-2 border-dashed border-slate-300 dark:border-slate-700 text-slate-400 dark:text-slate-500">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-16 h-16 mb-4 opacity-50">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                  </svg>
                  <p className="text-lg font-medium">Ready to Simulate</p>
                  <p className="text-sm">Adjust parameters in the controls to get started.</p>
                </div>
              )}
              
              <section className="mt-8 border-t border-slate-200 dark:border-slate-800 pt-6">
                <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-200 mb-2">About this Edgeworth Box Simulator & Solver</h3>
                <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">
                  This <strong>Edgeworth Box Simulator</strong> is a powerful <strong>economics demonstrator</strong> and <strong>solver</strong> designed to visualize general equilibrium concepts. 
                  It calculates and displays the <strong>Contract Curve</strong>, identifying all <strong>Pareto efficient</strong> allocations where the marginal rates of substitution (MRS) are equal.
                  The tool also solves for the <strong>Walrasian Equilibrium</strong> (Competitive Equilibrium), finding the specific price ratio and allocation that clears the market for both goods.
                  Ideal for students and researchers, this simulation provides instant feedback on how endowments and utility functions (like Cobb-Douglas, Perfect Complements, or Substitutes) affect market outcomes.
                </p>
              </section>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
