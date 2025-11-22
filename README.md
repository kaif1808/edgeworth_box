# Edgeworth Box Simulator

An interactive general-equilibrium sandbox that visualizes Edgeworth Box dynamics in the browser. The app couples a Next.js frontend with a Python (Flask) serverless backend to compute utility grids, Pareto sets, multi-equilibria, and annotated analytical walkthroughs for any pair of agents and endowments.

## Highlights
- **Multi-equilibrium insights:** Backend logic scans logarithmic price grids and returns every Walrasian equilibrium plus per-equilibrium allocations, prices, and utilities.
- **Analytical workflow:** The UI mirrors textbook derivations (Primitives → Contract Curve → Core → Walrasian Equilibrium) with LaTeX-rendered math and status messaging for infeasible states.
- **Rich visualization:** `EdgeworthBox` renders contract curves, indifference curves, Exchange Lens shading, multiple equilibrium markers, and dynamic annotations for solver failures.
- **Modern UX:** Responsive sidebar controls with linked sliders/inputs, dark-mode support, random favicon themes, and SEO enhancements (structured data, sitemap, robots).
- **Full-stack on Vercel:** Next.js App Router frontend plus Python serverless functions deployed together for a single origin experience.

## Architecture
- **Frontend:** Next.js 14 App Router, React 18, `react-plotly.js`, `react-katex`, Tailwind, Vercel Analytics & Speed Insights.
- **Backend:** Flask serverless handler (`api/index.py`) that delegates to `api/core/economics.py` (NumPy/SciPy, custom solvers, Pareto checks).
- **Communication:** The frontend POSTs `/api/calculate` requests describing the Edgeworth Box state; responses include equilibria, grids, contract/core sets, and textual analysis consumed by the React components.

## Project Structure
```
edgeworth_box/
├── api/                # Python serverless functions (Flask + SciPy)
│   ├── index.py
│   └── core/economics.py
├── app/                # Next.js App Router entry points
│   ├── page.tsx
│   └── layout.tsx
├── components/         # React visualization + control components
│   ├── EdgeworthBox.tsx
│   └── Sidebar.tsx
├── tests/              # Backend unit tests (pytest)
├── development_status.md
├── architecture_design.md
└── README.md
```

## Requirements
- Node.js 18+ (Next.js 14 requires modern Node LTS)
- Python 3.10+ with `pip` (serverless backend + tests)
- Optional: Vercel CLI for running backend + frontend locally via `vercel dev`

## Setup
Clone the repo, then install dependencies for both stacks:

```bash
# Frontend (Next.js)
npm install

# Backend (Flask serverless)
python -m venv venv
source venv/bin/activate
pip install -r api/requirements.txt
```

## Running Locally
```bash
# Option A: Frontend only (API calls hit deployed backend)
npm run dev

# Option B: Full stack with local Python serverless functions
npm install -g vercel
vercel dev
```

- Next.js dev server listens on `http://localhost:3000`.
- When using `vercel dev`, both the frontend and `/api/*` Python handlers run in one process so local API mutations reflect instantly.

## Testing & Quality
- **Frontend lint/typecheck:** `npm run lint`
- **Build verification:** `npm run build`
- **Backend unit tests:** `pytest tests/test_pareto_examples.py`
- **Manual QA:** adjust sidebar parameters, toggle dark mode, confirm multiple equilibria render, and observe status cards for infeasible scenarios.

## Deployment
1. Ensure `npm run build` and backend tests succeed locally.
2. Commit + push to the tracked branch; Vercel automatically builds the Next.js app and packages `api/` as serverless functions.
3. Monitor the deployment dashboard for analytics (Speed Insights, structured data) and production logs.

## Additional References
- `architecture_design.md` – deeper design notes, API schemas, and future work.
- `development_status.md` – day-by-day changelog of major features and fixes.
- `tests/test_pareto_examples.py` – canonical economic scenarios that validate solver correctness.

