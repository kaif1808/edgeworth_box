'use client';

import React, { useMemo, useState } from 'react';
import dynamic from 'next/dynamic';
import { Layout, Data } from 'plotly.js';
import 'katex/dist/katex.min.css';
import { InlineMath, BlockMath } from 'react-katex';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

interface Point {
  x: number;
  y: number;
}

interface SimulationData {
  initial_state: {
    utility_a: number | string;
    utility_b: number | string;
    mrs_a: number | string;
    mrs_b: number | string;
  };
  walrasian_equilibrium: {
    exists: boolean;
    price_ratio_px_py: number | string;
    allocation_a: Point;
    allocation_b: Point;
    trade_a: {
      net_x: number | string;
      net_y: number | string;
    };
    utility_a?: number | string;
    utility_b?: number | string;
    mrs_a?: number | string;
    mrs_b?: number | string;
  };
  contract_curve: {
    pareto_points: Point[];
    core_points: Point[];
  };
  z_grid_a?: number[][];
  z_grid_b?: number[][];
  analysis?: {
    pareto_efficient: boolean;
    mrs_difference: number | string;
    trade_advice: string;
  };
  workings?: {
    [key: string]: {
      title: string;
      content: string[];
    };
  };
}

export interface VisualSettings {
  show_endow: boolean;
  show_core: boolean;
  show_pareto: boolean;
  show_lens: boolean;
  show_curves_A: boolean;
  show_curves_B: boolean;
  line_mode: boolean;
  show_we: boolean;
  style_A: string;
  style_B: string;
  ic_mode: string;
  n_curves: number;
  n_curves_A: number;
  n_curves_B: number;
}

interface EdgeworthBoxProps {
  data: SimulationData;
  totalResources: { x: number; y: number };
  endowmentA: { x: number; y: number };
  visualSettings?: VisualSettings;
  darkMode?: boolean;
}

export default function EdgeworthBox({ data, totalResources, endowmentA, visualSettings, darkMode }: EdgeworthBoxProps) {
  const { contract_curve, walrasian_equilibrium, z_grid_a, z_grid_b, initial_state, workings } = data;
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

  const traces = useMemo(() => {
    const plotTraces: Data[] = [];
    const settings = visualSettings || {
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
    };

    const sanitizeCurves = (value?: number, fallback = 30) => {
      const raw = typeof value === 'number' ? value : fallback;
      return Math.max(1, Math.min(100, raw));
    };

    const curvesCountA = settings.ic_mode === 'Manual'
      ? sanitizeCurves(settings.n_curves_A, settings.n_curves)
      : sanitizeCurves(settings.n_curves);
    const curvesCountB = settings.ic_mode === 'Manual'
      ? sanitizeCurves(settings.n_curves_B, settings.n_curves)
      : sanitizeCurves(settings.n_curves);

    // 0. Grids & Lens (Bottom Layer)
    if (z_grid_a && z_grid_b && z_grid_a.length > 0 && z_grid_b.length > 0) {
        const N = z_grid_a.length;
        const xVec = Array.from({length: N}, (_, i) => i * totalResources.x / (N - 1));
        const yVec = Array.from({length: N}, (_, i) => i * totalResources.y / (N - 1));
        
          const uA_w = Number(initial_state.utility_a);
          const uB_w = Number(initial_state.utility_b);

        // Exchange Lens (Shaded Area)
        if (settings.show_lens && !isNaN(uA_w) && !isNaN(uB_w)) {
            // Create a binary grid for the lens
            const z_lens = z_grid_a.map((row, i) => 
                row.map((valA, j) => {
                    const valB = z_grid_b[i][j];
                    // Check Pareto improvement condition
                    return (valA >= uA_w && valB >= uB_w) ? 1 : 0; // 1 inside lens, 0 outside
                })
            );

            // Use a filled contour for the lens to ensure smooth edges
            plotTraces.push({
                z: z_lens,
                x: xVec,
                y: yVec,
                type: 'contour',
                showscale: false,
                autocontour: false,
                contours: {
                    start: 0.5,
                    end: 1.5,
                    size: 1,
                    coloring: 'fill',
                    showlines: false
                },
                colorscale: [[0, 'rgba(0,0,0,0)'], [1, darkMode ? 'rgba(255, 215, 0, 0.2)' : 'rgba(255, 215, 0, 0.3)']], // Transparent to Gold
                hoverinfo: 'skip',
                name: 'Mutually Beneficial Trade Area'
            });
        }

        // Indifference Curves A
        if (settings.show_curves_A) {
            plotTraces.push({
                z: z_grid_a,
                x: xVec,
                y: yVec,
                type: 'contour',
                showscale: false,
                colorscale: 'Reds',
                  ncontours: curvesCountA,
                contours: {
                    coloring: 'lines',
                    showlabels: false,
                },
                line: {
                    width: 1,
                    color: darkMode ? 'rgba(239, 68, 68, 0.5)' : 'rgba(211, 47, 47, 0.3)', // Red A
                    dash: settings.style_A === 'dot' ? 'dot' : (settings.style_A === 'dash' ? 'dash' : 'solid')
                },
                hoverinfo: 'skip',
                name: 'UA Map'
            });

            // Specific IC for Endowment A
            if (!isNaN(uA_w)) {
                plotTraces.push({
                    z: z_grid_a,
                    x: xVec,
                    y: yVec,
                    type: 'contour',
                    showscale: false,
                    autocontour: false,
                    contours: {
                        start: uA_w,
                        end: uA_w,
                        size: 0,
                        coloring: 'lines',
                        showlabels: true
                    },
                    line: {
                        width: 2,
                        color: darkMode ? 'rgba(239, 68, 68, 1)' : 'rgba(211, 47, 47, 1)', // Solid Red
                    },
                    hoverinfo: 'skip',
                    name: 'UA(Endowment)'
                });
            }
        }

        // Indifference Curves B
        if (settings.show_curves_B) {
            // For B, the grid is already computed as Z_B(x,y). 
            plotTraces.push({
                z: z_grid_b,
                x: xVec,
                y: yVec,
                type: 'contour',
                showscale: false,
                colorscale: 'Blues',
                  ncontours: curvesCountB,
                contours: {
                    coloring: 'lines',
                    showlabels: false,
                },
                line: {
                    width: 1,
                    color: darkMode ? 'rgba(59, 130, 246, 0.5)' : 'rgba(25, 118, 210, 0.3)', // Blue B
                    dash: settings.style_B === 'dot' ? 'dot' : (settings.style_B === 'dash' ? 'dash' : 'solid')
                },
                hoverinfo: 'skip',
                name: 'UB Map'
            });

            // Specific IC for Endowment B
            if (!isNaN(uB_w)) {
                plotTraces.push({
                    z: z_grid_b,
                    x: xVec,
                    y: yVec,
                    type: 'contour',
                    showscale: false,
                    autocontour: false,
                    contours: {
                        start: uB_w,
                        end: uB_w,
                        size: 0,
                        coloring: 'lines',
                        showlabels: true
                    },
                    line: {
                        width: 2,
                        color: darkMode ? 'rgba(59, 130, 246, 1)' : 'rgba(25, 118, 210, 1)', // Solid Blue
                    },
                    hoverinfo: 'skip',
                    name: 'UB(Endowment)'
                });
            }
        }
    }

    // 1. Contract Curve (Pareto Set)
    if (settings.show_pareto && contract_curve.pareto_points.length > 0) {
      plotTraces.push({
        x: contract_curve.pareto_points.map((p) => p.x),
        y: contract_curve.pareto_points.map((p) => p.y),
        mode: settings.line_mode ? 'lines+markers' : 'markers',
        name: 'Pareto Set',
        line: { color: '#2e7d32', width: 4 }, // Green
        marker: { color: '#2e7d32', size: 6 },
        hoverinfo: 'x+y',
      });
    }

    // 2. Core (Subset of Contract Curve)
    if (settings.show_core && contract_curve.core_points.length > 0) {
      plotTraces.push({
        x: contract_curve.core_points.map((p) => p.x),
        y: contract_curve.core_points.map((p) => p.y),
        mode: settings.line_mode ? 'lines+markers' : 'markers',
        name: 'Core',
        line: { color: '#fbc02d', width: 8 }, // Amber/Gold
        marker: { color: '#fbc02d', size: 9 },
        hoverinfo: 'x+y',
      });
    }

    // 3. Initial Endowment
    if (settings.show_endow) {
        plotTraces.push({
          x: [endowmentA.x],
          y: [endowmentA.y],
          mode: 'markers',
          name: 'Endowment',
          marker: { color: darkMode ? '#94a3b8' : '#374151', size: 12, symbol: 'circle', line: {width: 2, color: darkMode ? '#0f172a' : 'white'} }, 
          hovertemplate:
            '<b>Endowment</b><br>' +
            'XA: %{x:.2f}<br>' +
            'YA: %{y:.2f}<br>' +
            '<extra></extra>',
        });
        
        // Endowment Indifference Curves (Specific Level)
        // We need the Utility Level at Endowment.
        // We can try to find it from z_grid if available or pass it.
        // For now, let's skip the specific thick line unless we pass uA_w, uB_w explicitly or infer from grid.
    }

    // 4. Walrasian Equilibrium
    if (settings.show_we && walrasian_equilibrium.exists) {
      plotTraces.push({
        x: [walrasian_equilibrium.allocation_a.x],
        y: [walrasian_equilibrium.allocation_a.y],
        mode: 'markers',
        name: 'Walrasian Equilibrium',
        marker: { color: '#22c55e', size: 14, symbol: 'star' }, // Green
        hovertemplate:
          '<b>Equilibrium</b><br>' +
          'XA: %{x:.2f}<br>' +
          'YA: %{y:.2f}<br>' +
          'Price Ratio (Px/Py): ' +
          (typeof walrasian_equilibrium.price_ratio_px_py === 'number'
            ? walrasian_equilibrium.price_ratio_px_py.toFixed(2)
            : walrasian_equilibrium.price_ratio_px_py) +
          '<br>' +
          '<extra></extra>',
      });
      
      // Budget Line (passing through endowment with slope -Px/Py)
      // y - y0 = -px/py * (x - x0) => y = y0 - px/py * (x - x0)
      const px_py = Number(walrasian_equilibrium.price_ratio_px_py);
      if (!isNaN(px_py) && px_py !== Infinity) {
          const xRange = [0, totalResources.x];
          const yAt0 = endowmentA.y - px_py * (0 - endowmentA.x);
          const yAtMax = endowmentA.y - px_py * (totalResources.x - endowmentA.x);
          
          plotTraces.push({
              x: [0, totalResources.x],
              y: [yAt0, yAtMax],
              mode: 'lines',
              name: 'Budget Line',
              line: { color: darkMode ? '#9ca3af' : '#6b7280', width: 1, dash: 'dot' }, // Gray
              hoverinfo: 'skip'
          });
      }
    }

    return plotTraces;
  }, [totalResources, endowmentA, contract_curve, walrasian_equilibrium, z_grid_a, z_grid_b, initial_state, visualSettings, darkMode]);

  const layout: Partial<Layout> = {
    title: { 
        text: 'Edgeworth Box',
        font: { color: darkMode ? '#e2e8f0' : '#1e293b' }
    },
    autosize: true,
    paper_bgcolor: darkMode ? '#0f172a' : 'white',
    plot_bgcolor: darkMode ? '#0f172a' : 'white',
    xaxis: {
      title: { 
        text: 'Agent A - Good X',
        font: { color: darkMode ? '#cbd5e1' : '#334155' }
      },
      range: [0, totalResources.x],
      showgrid: true,
      gridcolor: darkMode ? '#334155' : '#e2e8f0',
      zeroline: true,
      zerolinecolor: darkMode ? '#475569' : '#94a3b8',
      tickfont: { color: darkMode ? '#cbd5e1' : '#334155' }
    },
    yaxis: {
      title: { 
        text: 'Agent A - Good Y',
        font: { color: darkMode ? '#cbd5e1' : '#334155' }
      },
      range: [0, totalResources.y],
      showgrid: true,
      gridcolor: darkMode ? '#334155' : '#e2e8f0',
      zeroline: true,
      zerolinecolor: darkMode ? '#475569' : '#94a3b8',
      tickfont: { color: darkMode ? '#cbd5e1' : '#334155' }
    },
    // We can add a second axis for Agent B if we want to be fancy, 
    // but standard Edgeworth box usually just implies it by the box limits.
    // Let's add annotations for Agent B's origin.
    annotations: [
      {
        x: totalResources.x,
        y: totalResources.y,
        xref: 'x',
        yref: 'y',
        text: 'Agent B Origin',
        showarrow: false,
        xanchor: 'left',
        yanchor: 'bottom',
        font: {
            color: darkMode ? '#94a3b8' : '#666'
        }
      },
      {
        x: 0,
        y: 0,
        xref: 'x',
        yref: 'y',
        text: 'Agent A Origin',
        showarrow: false,
        xanchor: 'right',
        yanchor: 'top',
        font: {
            color: darkMode ? '#94a3b8' : '#666'
        }
      }
    ],
    shapes: [
        {
            type: 'rect',
            x0: 0,
            y0: 0,
            x1: totalResources.x,
            y1: totalResources.y,
            line: {
                color: darkMode ? '#e2e8f0' : 'black',
                width: 2
            }
        }
    ],
    legend: {
        orientation: 'h',
        y: -0.2,
        font: { color: darkMode ? '#cbd5e1' : '#334155' }
    },
    margin: {
        l: 50,
        r: 50,
        b: 100,
        t: 50
    }
  };

  return (
    <div className="w-full h-full bg-white dark:bg-slate-900 rounded-lg shadow-sm border border-gray-200 dark:border-slate-800 p-4 flex flex-col">
      <div className="flex-grow min-h-[400px]">
        <Plot
            data={traces}
            layout={layout}
            useResizeHandler={true}
            style={{ width: '100%', height: '100%' }}
            config={{ responsive: true }}
        />
      </div>
      
      {workings && Object.keys(workings).length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-slate-700">
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
      )}
    </div>
  );
}
