'use client';

import React, { useMemo } from 'react';
import dynamic from 'next/dynamic';
import { Layout, Data } from 'plotly.js';

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
}

export default function EdgeworthBox({ data, totalResources, endowmentA, visualSettings }: EdgeworthBoxProps) {
  const { contract_curve, walrasian_equilibrium, z_grid_a, z_grid_b } = data;

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
        
        const uA_w = Number(data.initial_state.utility_a);
        const uB_w = Number(data.initial_state.utility_b);

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
                colorscale: [[0, 'rgba(0,0,0,0)'], [1, 'rgba(255, 215, 0, 0.3)']], // Transparent to Gold
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
                    color: 'rgba(211, 47, 47, 0.3)', // Red A
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
                        color: 'rgba(211, 47, 47, 1)', // Solid Red
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
                    color: 'rgba(25, 118, 210, 0.3)', // Blue B
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
                        color: 'rgba(25, 118, 210, 1)', // Solid Blue
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
          marker: { color: '#374151', size: 12, symbol: 'circle', line: {width: 2, color: 'white'} }, 
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
              line: { color: '#6b7280', width: 1, dash: 'dot' }, // Gray
              hoverinfo: 'skip'
          });
      }
    }

    return plotTraces;
  }, [data, totalResources, endowmentA]);

  const layout: Partial<Layout> = {
    title: { text: 'Edgeworth Box' },
    autosize: true,
    height: 600,
    xaxis: {
      title: { text: 'Agent A - Good X' },
      range: [0, totalResources.x],
      showgrid: true,
      zeroline: true,
    },
    yaxis: {
      title: { text: 'Agent A - Good Y' },
      range: [0, totalResources.y],
      showgrid: true,
      zeroline: true,
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
            color: '#666'
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
            color: '#666'
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
                color: 'black',
                width: 2
            }
        }
    ],
    legend: {
        orientation: 'h',
        y: -0.2
    },
    margin: {
        l: 50,
        r: 50,
        b: 100,
        t: 50
    }
  };

  return (
    <div className="w-full h-full bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <Plot
        data={traces}
        layout={layout}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
        config={{ responsive: true }}
      />
    </div>
  );
}