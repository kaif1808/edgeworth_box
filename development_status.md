# Development Status

## 2025-11-21
- **Security**: Updated `next` and `eslint-config-next` to version 14.2.33 to fix critical security vulnerabilities.
- **Feature**: Added Vercel `SpeedInsights` component to `app/layout.tsx` for performance monitoring.
- **Backend**: Fixed Pareto efficiency verification for convex utility functions (concave indifference curves).
  - Increased epsilon step size in `verify_pareto_efficiency` to robustly detect second-order improvements, ensuring inefficient interior tangency points (utility minima) are correctly rejected in favor of corner solutions.
- **Backend**: Robustified Pareto set calculation logic in `api/core/economics.py`.
  - Added `is_convex_preference` to better handle non-convex utility functions (e.g., Max Preferences).
  - Implemented a gradient-based `verify_pareto_efficiency` check to robustly identify Pareto-efficient points, including corner solutions.
  - Updated `solve_contract_curve` to explicitly sample boundary edges and verify candidates, ensuring correct rendering for complex preference structures (Quasi-Linear, Satiation, etc.).
- **Test**: Created `tests/test_pareto_examples.py` to verify backend logic against analytical solutions from standard economic examples.
- **Feature**: Implemented comprehensive **Dark Mode** support.
  - Added a toggle in the Sidebar (Sun/Moon).
  - Configured global dark theme styles using Tailwind CSS.
  - Updated `EdgeworthBox` (Plotly) to dynamically switch chart backgrounds, axes, and text colors for legibility in dark mode.
  - Ensured UI consistency across Sidebar, Modals, and Mobile views.
- **Feature**: Integrated live updates for Edgeworth Box simulation with debounced API calls.
- **Feature**: Added slider controls for Total Resources and Endowments in the Sidebar.
- **Visualization**: Implemented "Exchange Lens" (mutually beneficial trade area) shading.
- **Visualization**: Added specific indifference curves passing through the initial endowment.
- **Backend**: Improved contract curve solver to explicitly check and include efficient corner solutions (origins).
- **Fix**: Resolved "Object of type bool is not JSON serializable" error in API by explicitly casting NumPy boolean to Python boolean in `api/index.py`.
- **Fix**: Reduced serverless function bundle size by removing unused heavy dependencies (`streamlit`, `plotly`, `pandas`) from `requirements.txt`, resolving Vercel deployment errors.
- **UI**: Rebuilt all sidebar parameter controls with synchronized sliders, manual inputs, and +/- nudge buttons to match the Streamlit reference workflow.
- **Visualization**: Added a Density vs Manual toggle for indifference-curve rendering and plumbed manual curve counts through `EdgeworthBox`.
- **Test**: `npm run build` (runs lint + typecheck) to verify the updated UI/visualization logic.
- **UI**: Began mobile website experience with a responsive layout, mobile header/tabs, and adaptive Sidebar styling plus resized EdgeworthBox container.
- **Test**: `npm run lint`

## 2025-11-20
- **Feature**: Added support for custom LaTeX utility functions and expanded utility types (Cobb-Douglas, Perfect Substitutes, Complements, etc.) in the frontend.
- **Fix**: Resolved Vercel deployment issues (404/405 errors) by adding CORS support and defensive routing in `api/index.py`.
- **Architecture**: Validated Flask + Next.js on Vercel architecture.
- **Refactor**: Extracted `Sidebar` component for better maintainability.

## Previous
- **Bug Fix**: Fixed a critical data mismatch between the API response structure and the Frontend component in `app/page.tsx`. The app was expecting a flat structure but the API returns a nested `walrasian_equilibrium` object.
- **Pivot**: Shifted architecture strategy from Streamlit to **React + FastAPI**.
- **Plan**: Created `modernization_plan.md` detailing the split-stack architecture.
  - **Backend**: Python/FastAPI on Render.
  - **Frontend**: React/TypeScript on Vercel.
  - **Visualization**: `react-plotly.js`.
- **Current State**: 
  - Prototypes (`edgeworth.py`, `edgeworth_bokeh.py`) are functional reference implementations.
  - Next steps involve extracting logic and initializing the new project structure.
