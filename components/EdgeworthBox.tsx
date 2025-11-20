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
}

interface EdgeworthBoxProps {
  data: SimulationData;
  totalResources: { x: number; y: number };
  endowmentA: { x: number; y: number };
}

export default function EdgeworthBox({ data, totalResources, endowmentA }: EdgeworthBoxProps) {
  const { contract_curve, walrasian_equilibrium } = data;

  const traces = useMemo(() => {
    const plotTraces: Data[] = [];

    // 1. Contract Curve (Pareto Set)
    if (contract_curve.pareto_points.length > 0) {
      plotTraces.push({
        x: contract_curve.pareto_points.map((p) => p.x),
        y: contract_curve.pareto_points.map((p) => p.y),
        mode: 'lines',
        name: 'Contract Curve',
        line: { color: '#9333ea', width: 2, dash: 'dash' }, // Purple
        hoverinfo: 'x+y',
      });
    }

    // 2. Core (Subset of Contract Curve)
    if (contract_curve.core_points.length > 0) {
      plotTraces.push({
        x: contract_curve.core_points.map((p) => p.x),
        y: contract_curve.core_points.map((p) => p.y),
        mode: 'lines',
        name: 'Core',
        line: { color: '#9333ea', width: 4 }, // Thicker Purple
        hoverinfo: 'x+y',
      });
    }

    // 3. Initial Endowment
    plotTraces.push({
      x: [endowmentA.x],
      y: [endowmentA.y],
      mode: 'markers',
      name: 'Initial Endowment',
      marker: { color: '#ef4444', size: 12, symbol: 'square' }, // Red
      hovertemplate:
        '<b>Initial Endowment</b><br>' +
        'XA: %{x:.2f}<br>' +
        'YA: %{y:.2f}<br>' +
        '<extra></extra>',
    });

    // 4. Walrasian Equilibrium
    if (walrasian_equilibrium.exists) {
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