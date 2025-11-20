# Edgeworth Box Architecture Design

## 1. Overview
This document outlines the architecture for the Edgeworth Box application pivot to a Vercel-hosted solution.
- **Frontend:** Next.js (React)
- **Backend:** Python Serverless Functions (Vercel)
- **Deployment:** Vercel (Monorepo structure)

## 2. API Specification

### Endpoint: Calculate Equilibrium & Contract Curve
- **URL:** `/api/calculate`
- **Method:** `POST`
- **Description:** Performs all economic calculations (Utility, MRS, Walrasian Equilibrium, Contract Curve) based on the provided simulation state.

### Request Schema (JSON)
```json
{
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
    "trade_a": { "net_x": 0.0, "net_y": 0.0 }
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
  }
}
```

## 3. Project Structure

The project will be restructured to support Next.js and Vercel Serverless Functions. The existing `core/` logic will be moved to be accessible by the API functions.

```
edgeworth_box/
├── api/                        # Python Serverless Functions
│   ├── index.py                # Entry point (handler for /api/calculate)
│   ├── core/                   # Moved from root core/
│   │   ├── __init__.py
│   │   └── economics.py        # Existing logic (NumPy/SciPy)
│   └── requirements.txt        # Python dependencies (numpy, scipy)
├── app/                        # Next.js App Router
│   ├── page.tsx                # Main UI
│   ├── layout.tsx
│   └── components/             # React Components
│       ├── EdgeworthBox.tsx    # Plotly Visualization
│       └── Controls.tsx        # Input forms
├── public/                     # Static assets
├── package.json                # Frontend dependencies
├── next.config.js              # Next.js configuration
└── tsconfig.json
```

### Key Changes
1.  **`core/` Migration:** The `core/` directory containing `economics.py` will be moved inside `api/` so it can be imported by the serverless function `index.py`.
2.  **`api/index.py`:** This file will handle the HTTP request, parse the JSON body, call functions from `api/core/economics.py`, and return the JSON response.
3.  **Frontend State:** The state management logic currently in `ui/state.py` will be reimplemented in React (using `useState` or `Zustand`) within `app/`.

## 4. Implementation Steps
1.  **Move Core Logic:** Move `core/` to `api/core/`.
2.  **Create API Handler:** Implement `api/index.py` using standard Python HTTP handling (or a lightweight framework like Flask/FastAPI if preferred, though raw Vercel functions work well for simple cases).
3.  **Setup Next.js:** Initialize the Next.js app in the root (or `app/` if using a src directory structure).
4.  **Frontend Integration:** Build the React components to consume `/api/calculate`.