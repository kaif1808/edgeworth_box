'use client';

import { useState } from 'react';
import EdgeworthBox from '@/components/EdgeworthBox';

export default function Home() {
  const [totalResources, setTotalResources] = useState({ x: 100, y: 100 });
  const [endowmentA, setEndowmentA] = useState({ x: 50, y: 50 });
  const [utilityParams, setUtilityParams] = useState({ alpha: 0.5, beta: 0.5 });
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState<'professional' | 'textbook'>('professional');
  const [showHelp, setShowHelp] = useState(false);

  const toggleTheme = () => {
    const newTheme = theme === 'professional' ? 'textbook' : 'professional';
    setTheme(newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dimensions: {
            total_x: totalResources.x,
            total_y: totalResources.y
          },
          agent_a: {
            type: "Cobb-Douglas",
            params: utilityParams,
            endowment: endowmentA
          },
          agent_b: {
            type: "Cobb-Douglas",
            params: utilityParams // Assuming symmetric preferences for now or using same params
          }
        }),
      });
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error calculating:', error);
      setResult({ error: 'Failed to calculate' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-row text-slate-900">
      {/* Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-8 rounded-lg max-w-2xl w-full max-h-[80vh] overflow-y-auto shadow-xl">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Edgeworth Box Concepts</h2>
              <button onClick={() => setShowHelp(false)} className="text-gray-500 hover:text-gray-700 text-xl">&times;</button>
            </div>
            <div className="space-y-4">
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
            </div>
            <button onClick={() => setShowHelp(false)} className="mt-6 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 w-full">Close</button>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div className="w-1/4 bg-slate-50 p-6 border-r border-slate-200 flex flex-col gap-6 overflow-y-auto h-screen">
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

        {/* Utility Params */}
        <div className="flex flex-col gap-2">
          <h2 className="font-semibold">Utility Params</h2>
          <div className="flex gap-2 items-center">
            <label className="w-12">Alpha:</label>
            <input 
              type="number" 
              step="0.1"
              value={utilityParams.alpha} 
              onChange={(e) => setUtilityParams({...utilityParams, alpha: Number(e.target.value)})}
              className="border p-1 rounded w-full"
            />
          </div>
          <div className="flex gap-2 items-center">
            <label className="w-12">Beta:</label>
            <input 
              type="number" 
              step="0.1"
              value={utilityParams.beta} 
              onChange={(e) => setUtilityParams({...utilityParams, beta: Number(e.target.value)})}
              className="border p-1 rounded w-full"
            />
          </div>
        </div>

        <button
          onClick={handleCalculate}
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

      {/* Main Content */}
      <div className="w-3/4 p-8 bg-white overflow-y-auto h-screen">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold mb-6 text-slate-800 border-b pb-2">Simulation Results</h2>
          {result ? (
            <div className="space-y-6">
              <div className="h-[600px] bg-white rounded-lg shadow-sm border border-slate-200 p-4">
                <EdgeworthBox
                  data={result}
                  totalResources={totalResources}
                  endowmentA={endowmentA}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 p-4 rounded border border-slate-200">
                  <h3 className="font-semibold text-slate-700 mb-2">Equilibrium Prices</h3>
                  <p>Price of X (px): <span className="font-mono">{result.equilibrium_price?.toFixed(4) || 'N/A'}</span></p>
                  <p>Price of Y (py): <span className="font-mono">1.0000</span> (Numeraire)</p>
                </div>
                <div className="bg-slate-50 p-4 rounded border border-slate-200">
                  <h3 className="font-semibold text-slate-700 mb-2">Allocation</h3>
                  <p>Agent A: (<span className="font-mono">{result.allocation?.A[0]?.toFixed(2)}</span>, <span className="font-mono">{result.allocation?.A[1]?.toFixed(2)}</span>)</p>
                  <p>Agent B: (<span className="font-mono">{result.allocation?.B[0]?.toFixed(2)}</span>, <span className="font-mono">{result.allocation?.B[1]?.toFixed(2)}</span>)</p>
                </div>
              </div>

              <div className="mt-4">
                <details className="group">
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
          ) : (
            <div className="flex flex-col items-center justify-center h-[400px] bg-slate-50 rounded-lg border-2 border-dashed border-slate-300 text-slate-400">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-16 h-16 mb-4 opacity-50">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
              <p className="text-lg font-medium">Ready to Simulate</p>
              <p className="text-sm">Adjust parameters in the sidebar and click Calculate.</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}