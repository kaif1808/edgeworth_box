# Development Status

## 2025-11-21
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
