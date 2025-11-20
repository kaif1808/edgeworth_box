# Edgeworth Box Simulation: Modernization Roadmap

**Architecture:** React (Frontend) + FastAPI (Backend)
**Deployment:** Vercel (Frontend) + Render (Backend)
**Goal:** Create a production-grade, scalable web application for economic simulation.

## 1. Architecture Overview

The application will be split into two distinct services:

1.  **Backend (Python/FastAPI):**
    *   **Responsibility:** Handles all heavy mathematical lifting, economic logic, solver algorithms (optimization, root finding), and data validation.
    *   **Why:** Keeps the complex `scipy`/`numpy` logic in Python where it belongs, ensuring scientific accuracy and performance.
    *   **Hosting:** Render (Free Web Service tier).

2.  **Frontend (React/Vite):**
    *   **Responsibility:** User interface, state management, and interactive visualization.
    *   **Why:** React provides a rich, responsive UI ecosystem. `react-plotly.js` offers the best compatibility with our existing plotting logic.
    *   **Hosting:** Vercel (Free tier).

## 2. Technical Specification

### Backend (`/backend`)
*   **Framework:** FastAPI
*   **Runtime:** Python 3.10+
*   **Key Libraries:**
    *   `numpy`, `scipy`: For numerical optimization and matrix operations.
    *   `pydantic`: For strict data validation of API inputs/outputs.
    *   `uvicorn`: ASGI server.
*   **API Structure:**
    *   `POST /api/calculate`: Accepts full simulation state (endowments, preferences); returns calculated data (Pareto points, Core points, Equilibrium, Contour lines).
    *   `GET /api/health`: Simple health check for uptime monitoring.

### Frontend (`/frontend`)
*   **Framework:** React 18+ (via Vite)
*   **Language:** TypeScript
*   **State Management:** Zustand (Simple, performant global state).
*   **Visualization:** `react-plotly.js` (Direct port of existing Plotly logic).
*   **UI Component Library:** Material UI (MUI) or Tailwind CSS (for rapid, clean styling).
*   **Networking:** Axios (for API requests).

## 3. Implementation Roadmap

### Phase 1: Core Logic Extraction & Backend Setup
*   [ ] **Refactor:** Extract `utility_func`, `get_demand`, `solve_contract_curve`, and `solve_walrasian_equilibrium` from `edgeworth.py` into a pure Python module `economics.py`.
*   [ ] **API Setup:** Initialize FastAPI app.
*   [ ] **Models:** Define Pydantic models:
    ```python
    class AgentParams(BaseModel):
        type: str
        alpha: float = 1.0
        beta: float = 1.0
        # ... other params
    
    class SimulationState(BaseModel):
        total_x: float
        total_y: float
        agent_a: AgentParams
        agent_b: AgentParams
        endowment: Tuple[float, float]
    ```
*   [ ] **Endpoints:** Implement the calculation endpoints.

### Phase 2: Frontend Skeleton
*   [ ] **Init:** `npm create vite@latest frontend -- --template react-ts`
*   [ ] **Store:** Set up Zustand store to mirror the `SimulationState` model.
*   [ ] **UI Shell:** Create the main layout (Sidebar for controls, Main area for chart).
*   [ ] **Controls:** Build reusable slider/input components for modifying parameters.

### Phase 3: Visualization & Integration
*   [ ] **Plotting:** Create `EdgeworthBox.tsx` using `react-plotly.js`.
*   [ ] **Data Fetching:** Connect the frontend to the backend.
    *   *Optimization:* Implement `debounce` on the API calls so we don't flood the backend while dragging a slider.
*   [ ] **Parity Check:** Ensure the React chart looks and behaves exactly like the Python prototype.

### Phase 4: Deployment & Polish
*   [ ] **Docker (Optional):** Create a `docker-compose.yml` for easy local development of both services.
*   [ ] **Vercel:** Connect GitHub repo to Vercel for frontend deployment.
*   [ ] **Render:** Create a `render.yaml` or manually configure the web service to build the Python backend.
*   [ ] **Environment:** Set `VITE_API_URL` to point to the Render URL in production and `localhost` in development.

## 4. Directory Structure

```
edgeworth_box/
├── backend/
│   ├── main.py           # FastAPI entry point
│   ├── economics.py      # Core logic (extracted)
│   ├── models.py         # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # UI Components
│   │   ├── store/        # Zustand state
│   │   └── App.tsx
│   ├── package.json
│   └── vite.config.ts
├── modernization_plan.md
└── README.md