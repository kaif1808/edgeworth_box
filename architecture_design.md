# Edgeworth Box Architecture Design

## 1. Overview
This document outlines the architecture for the Edgeworth Box application hosted on Vercel.
- **Frontend:** Next.js (React) with Vercel Speed Insights
- **Backend:** Python Flask Serverless Functions (Vercel)
- **Deployment:** Vercel (Monorepo structure)

## 2. API Specification

### Endpoint: Calculate Equilibrium & Contract Curve
- **URL:** `/api/calculate`
- **Method:** `POST`
- **Description:** Performs all economic calculations (Utility, MRS, Walrasian Equilibrium, Contract Curve, Utility Grids) based on the provided simulation state.

### Request Schema (JSON)
```json
{
  "include_grid": true,
  "dimensions": {
    "total_x": 10.0,
    "total_y": 10.0
  },
  "agent_a": {
    "type": "Cobb-Douglas",
    "params": { "alpha": 1.0, "beta": 1.0 },
    "endowment": { "x": 5.0, "y": 5.0 }
  },
  "agent_b": {
    "type": "Cobb-Douglas",
    "params": { "alpha": 1.0, "beta": 1.0 }
    // Endowment for B is derived: Total - A
  }
}
```

### Response Schema (JSON)
```json
{
  "initial_state": {
    "utility_a": 5.0,
    "utility_b": 5.0,
    "mrs_a": 1.0,
    "mrs_b": 1.0
  },
  "walrasian_equilibrium": {
    "exists": true,
    "price_ratio_px_py": 1.0,
    "allocation_a": { "x": 5.0, "y": 5.0 },
    "allocation_b": { "x": 5.0, "y": 5.0 },
    "trade_a": { "net_x": 0.0, "net_y": 0.0 },
    "utility_a": 5.0,
    "utility_b": 5.0,
    "mrs_a": 1.0,
    "mrs_b": 1.0
  },
  "contract_curve": {
    "pareto_points": [
      { "x": 0.0, "y": 0.0 },
      { "x": 10.0, "y": 10.0 }
    ],
    "core_points": [
      { "x": 4.0, "y": 4.0 },
      { "x": 6.0, "y": 6.0 }
    ]
  },
  "z_grid_a": [[0.0, 0.1], [0.1, 0.2]], // 2D array for heatmap/contours
  "z_grid_b": [[0.0, 0.1], [0.1, 0.2]], // 2D array for heatmap/contours
  "analysis": {
    "pareto_efficient": false,
    "mrs_difference": 0.5,
    "trade_advice": "Agent A should buy X and sell Y."
  }
}
```

## 3. Project Structure

The project is structured to support Next.js App Router and Vercel Serverless Functions.

```
edgeworth_box/
├── api/                        # Python Serverless Functions
│   ├── index.py                # Entry point (Flask app handler for /api/calculate)
│   ├── core/                   # Core logic moved from root
│   │   ├── __init__.py
│   │   └── economics.py        # NumPy/SciPy economic logic
│   └── requirements.txt        # Python dependencies
├── app/                        # Next.js App Router
│   ├── page.tsx                # Main Page (State & Layout)
│   ├── layout.tsx              # Root Layout (w/ Analytics)
│   └── globals.css             # Global Styles
├── components/                 # React Components
│   ├── EdgeworthBox.tsx        # Plotly Visualization
│   └── Sidebar.tsx             # Input controls
├── public/                     # Static assets
├── package.json                # Frontend dependencies
├── next.config.js              # Next.js configuration
└── tsconfig.json
```

### Key Components
1.  **`api/index.py`:** A Flask application serving as the serverless function entry point. It handles CORS, request parsing, calls `core.economics`, and formats the JSON response.
2.  **`components/EdgeworthBox.tsx`:** The primary visualization component using `react-plotly.js`. It handles rendering the contract curve, indifference curves, endowments, and allocations.
3.  **`components/Sidebar.tsx`:** Contains all user input controls (sliders, manual inputs) for configuring agent preferences and endowments.

## 4. Implementation Status

### Completed
- [x] **Core Logic Migration:** `economics.py` moved to `api/core/` and adapted for stateless usage.
- [x] **API Implementation:** Flask-based handler in `api/index.py` serving `/api/calculate`.
- [x] **Next.js Setup:** App Router initialized with `page.tsx` and `layout.tsx`.
- [x] **Frontend Integration:** React components (`EdgeworthBox`, `Sidebar`) fully integrated with the API.
- [x] **State Management:** Reimplemented in React using `useState` in `page.tsx`.
- [x] **Visualization:** Plotly graphs for Contract Curve, Core, and Indifference Curves (contours).

### Future Improvements
- **Performance:** Optimize grid calculations for higher resolution heatmaps.
- **Testing:** Expand `tests/` to cover API endpoints integration.
