'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import EdgeworthBox, { VisualSettings } from '@/components/EdgeworthBox';
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
  const [showHelp, setShowHelp] = useState(false);
  const [mobileView, setMobileView] = useState<'controls' | 'results'>('results');
  
  const debounceTimer = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const toggleTheme = () => {
    const newTheme = theme === 'professional' ? 'textbook' : 'professional';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

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
    <main className="min-h-screen bg-slate-100 text-slate-900">
      {/* Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white p-6 sm:p-8 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Edgeworth Box Concepts</h2>
              <button onClick={() => setShowHelp(false)} className="text-gray-500 hover:text-gray-700 text-xl">&times;</button>
            </div>
            <div className="space-y-4 text-sm sm:text-base">
              <section>
                <h3 className="font-bold text-lg text-blue-600">Marginal Rate of Substitution (MRS)</h3>
                <p>The rate at which a consumer can give up some amount of one good in exchange for another good while maintaining the same level of utility. It corresponds to the slope of the indifference curve.</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600">Contract Curve</h3>
                <p>The set of all Pareto-efficient allocations. At any point on the contract curve, the MRS of both agents are equal, meaning no mutually beneficial trade is possible.</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600">Pareto Efficiency</h3>
                <p>An allocation is Pareto efficient if it is impossible to make one individual better off without making at least one individual worse off.</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600">Walrasian Equilibrium</h3>
                <p>A set of prices and an allocation where supply equals demand for all goods. It is always Pareto efficient (First Welfare Theorem).</p>
              </section>
              <section>
                <h3 className="font-bold text-lg text-blue-600">Custom Formulas</h3>
                <p>You can enter custom utility functions using LaTeX-like syntax (e.g., <code>x^2 * y</code>, <code>{`\\sqrt{x} + \\ln{y}`}</code>). Supported functions: log, ln, exp, sqrt, min, max.</p>
              </section>
            </div>
            <button onClick={() => setShowHelp(false)} className="mt-6 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 w-full">Close</button>
          </div>
        </div>
      )}

      {/* Mobile Header */}
      <div className="lg:hidden sticky top-0 z-30 bg-white border-b border-slate-200 shadow-sm">
        <div className="px-4 py-4 space-y-4">
          <div className="flex items-center justify-between gap-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-blue-600 font-semibold">Edgeworth Box</p>
              <h1 className="text-xl font-bold text-slate-900">Exchange Simulator</h1>
              <p className="text-sm text-slate-500">Tune resources, compare equilibria.</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowHelp(true)}
                className="p-2 rounded-full border border-slate-200 text-slate-500 hover:text-blue-600 hover:border-blue-200"
                aria-label="Open help"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-5 h-5">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                </svg>
              </button>
              <button
                onClick={toggleTheme}
                className="p-2 rounded-full border border-slate-200 text-slate-500 hover:text-blue-600 hover:border-blue-200"
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
                    ? 'border-blue-600 bg-blue-50 text-blue-700'
                    : 'border-slate-200 text-slate-500 bg-white'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-blue-600 animate-pulse" />
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
            />
          </div>
        </section>

        <section className={`${mobileView === 'results' ? 'block' : 'hidden'} lg:block flex-1`}>
          <div className="bg-white/90 lg:bg-white rounded-t-3xl lg:rounded-none px-4 py-6 sm:px-6 lg:px-10 lg:py-10 min-h-[60vh] shadow-inner lg:shadow-none">
            <div className="max-w-5xl mx-auto space-y-6">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <p className="text-xs uppercase tracking-wide text-blue-600 font-semibold">Live Results</p>
                  <h2 className="text-2xl lg:text-3xl font-bold text-slate-800">Simulation Insights</h2>
                </div>
                <button
                  onClick={handleCalculate}
                  disabled={loading}
                  className={`inline-flex items-center justify-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${
                    loading
                      ? 'bg-slate-200 text-slate-500 cursor-not-allowed'
                      : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm'
                  }`}
                >
                  {loading ? 'Updating…' : 'Refresh Now'}
                </button>
              </div>

              {result && !result.error ? (
                <div className="space-y-6">
                  <div className="h-[55vh] min-h-[320px] w-full bg-white rounded-3xl lg:rounded-xl shadow-sm border border-slate-200 p-3 sm:p-4 lg:h-[640px]">
                    <EdgeworthBox
                      data={result}
                      totalResources={totalResources}
                      endowmentA={endowmentA}
                      visualSettings={visualSettings}
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                      <h3 className="font-semibold text-slate-700 mb-2">Equilibrium Prices</h3>
                      <p>Price of X (px): <span className="font-mono">
                        {typeof result.walrasian_equilibrium?.price_ratio_px_py === 'number' 
                          ? result.walrasian_equilibrium.price_ratio_px_py.toFixed(4) 
                          : result.walrasian_equilibrium?.price_ratio_px_py || 'N/A'}
                      </span></p>
                      <p>Price of Y (py): <span className="font-mono">1.0000</span> (Numeraire)</p>
                    </div>
                    <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                      <h3 className="font-semibold text-slate-700 mb-2">Allocation</h3>
                      <p>Agent A: (<span className="font-mono">{result.walrasian_equilibrium?.allocation_a?.x?.toFixed(2)}</span>, <span className="font-mono">{result.walrasian_equilibrium?.allocation_a?.y?.toFixed(2)}</span>)</p>
                      <p>Agent B: (<span className="font-mono">{result.walrasian_equilibrium?.allocation_b?.x?.toFixed(2)}</span>, <span className="font-mono">{result.walrasian_equilibrium?.allocation_b?.y?.toFixed(2)}</span>)</p>
                    </div>
                  </div>
                  
                  {result.analysis && (
                      <div className={`p-4 rounded-2xl border text-sm sm:text-base ${result.analysis.pareto_efficient ? 'bg-green-50 border-green-200 text-green-800' : 'bg-yellow-50 border-yellow-200 text-yellow-800'}`}>
                          <h3 className="font-bold mb-2">{result.analysis.pareto_efficient ? '✅ Pareto Efficient' : '⚠️ Inefficient Allocation'}</h3>
                          <p className="mb-1">MRS Difference: {typeof result.analysis.mrs_difference === 'number' ? result.analysis.mrs_difference.toFixed(4) : result.analysis.mrs_difference}</p>
                          {result.analysis.trade_advice && <p className="font-medium">{result.analysis.trade_advice}</p>}
                      </div>
                  )}

                  <div className="mt-4">
                    <details className="group rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <summary className="cursor-pointer text-blue-600 hover:text-blue-800 font-medium flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4 group-open:rotate-90 transition-transform">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                        </svg>
                        View Raw JSON Data
                      </summary>
                      <pre className="bg-slate-900 text-slate-50 p-4 rounded-lg overflow-auto max-h-[300px] mt-2 text-xs font-mono shadow-inner">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </details>
                  </div>
                </div>
              ) : result && result.error ? (
                 <div className="p-6 bg-red-50 border border-red-200 rounded-2xl text-red-700">
                    <h3 className="font-bold mb-2">Error</h3>
                    <p>{result.error}</p>
                 </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-[320px] sm:h-[400px] bg-slate-50 rounded-2xl border-2 border-dashed border-slate-300 text-slate-400">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-16 h-16 mb-4 opacity-50">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
                  </svg>
                  <p className="text-lg font-medium">Ready to Simulate</p>
                  <p className="text-sm">Adjust parameters in the controls to get started.</p>
                </div>
              )}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
