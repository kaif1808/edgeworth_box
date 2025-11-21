from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import numpy as np

# Add current directory to sys.path to allow importing core
# This ensures that when running api/index.py, we can import from core/
sys.path.append(os.path.dirname(__file__))

try:
    from core.economics import solve_walrasian_equilibrium, solve_contract_curve, utility_func, calculate_mrs
except ImportError:
    # Fallback for Vercel environment where structure might differ
    from .core.economics import solve_walrasian_equilibrium, solve_contract_curve, utility_func, calculate_mrs

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

def sanitize_float(val):
    """Convert numpy floats and handle infinity for JSON serialization."""
    if val == float('inf') or val == np.inf:
        return "Infinity"
    if val == float('-inf') or val == -np.inf:
        return "-Infinity"
    if np.isnan(val):
        return None
    return float(val)

def calculate_handler():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Extract data
        dimensions = data.get('dimensions', {})
        total_x = float(dimensions.get('total_x', 10.0))
        total_y = float(dimensions.get('total_y', 10.0))
        
        agent_a = data.get('agent_a', {})
        type_a = agent_a.get('type', 'Cobb-Douglas')
        params_a = agent_a.get('params', {})
        endow_a_data = agent_a.get('endowment', {})
        endow_a = (float(endow_a_data.get('x', 5.0)), float(endow_a_data.get('y', 5.0)))
        
        agent_b = data.get('agent_b', {})
        type_b = agent_b.get('type', 'Cobb-Douglas')
        params_b = agent_b.get('params', {})
        # B's endowment is derived: Total - A
        endow_b = (total_x - endow_a[0], total_y - endow_a[1])
        
        # 1. Initial State
        # Utility
        u_a_init = utility_func(endow_a[0], endow_a[1], type_a, params_a)
        u_b_init = utility_func(endow_b[0], endow_b[1], type_b, params_b)
        
        # MRS
        mrs_a_init = calculate_mrs(endow_a[0], endow_a[1], type_a, params_a)
        mrs_b_init = calculate_mrs(endow_b[0], endow_b[1], type_b, params_b)
        
        initial_state = {
            "utility_a": sanitize_float(u_a_init),
            "utility_b": sanitize_float(u_b_init),
            "mrs_a": sanitize_float(mrs_a_init),
            "mrs_b": sanitize_float(mrs_b_init)
        }
        
        # 2. Walrasian Equilibrium
        px, alloc_a = solve_walrasian_equilibrium(
            total_x, total_y, 
            type_a, params_a, 
            type_b, params_b, 
            endow_a, endow_b
        )
        
        alloc_b = (total_x - alloc_a[0], total_y - alloc_a[1])
        trade_a_net_x = alloc_a[0] - endow_a[0]
        trade_a_net_y = alloc_a[1] - endow_a[1]
        
        walrasian_equilibrium = {
            "exists": True,
            "price_ratio_px_py": sanitize_float(px),
            "allocation_a": { "x": sanitize_float(alloc_a[0]), "y": sanitize_float(alloc_a[1]) },
            "allocation_b": { "x": sanitize_float(alloc_b[0]), "y": sanitize_float(alloc_b[1]) },
            "trade_a": { "net_x": sanitize_float(trade_a_net_x), "net_y": sanitize_float(trade_a_net_y) }
        }
        
        # 3. Contract Curve
        # Determine range for B's utility
        # Min: B has nothing (A has everything) -> utility at (0,0)
        z_b_min = utility_func(0, 0, type_b, params_b)
        # Max: B has everything (A has nothing) -> utility at (total_x, total_y)
        z_b_max = utility_func(total_x, total_y, type_b, params_b)
        
        pareto_x, pareto_y, core_x, core_y = solve_contract_curve(
            total_x, total_y,
            type_a, params_a,
            type_b, params_b,
            u_a_init, u_b_init,
            z_b_min, z_b_max
        )
        
        contract_curve = {
            "pareto_points": [{"x": sanitize_float(x), "y": sanitize_float(y)} for x, y in zip(pareto_x, pareto_y)],
            "core_points": [{"x": sanitize_float(x), "y": sanitize_float(y)} for x, y in zip(core_x, core_y)]
        }
        
        # 4. Grid Generation (if requested)
        include_grid = data.get('include_grid', True) 
        z_grid_a = []
        z_grid_b = []
        
        if include_grid:
            try:
                N = 50 # Grid density
                x_vec = np.linspace(0, total_x, N)
                y_vec = np.linspace(0, total_y, N)
                X, Y = np.meshgrid(x_vec, y_vec)
                
                # Calculate Utility A
                # utility_func handles numpy arrays if vectorized correctly. 
                # We'll assume it handles arrays or wrap if needed.
                Z_A = utility_func(X, Y, type_a, params_a)
                if isinstance(Z_A, (float, int)): Z_A = np.full_like(X, Z_A)
                
                # Calculate Utility B
                # B's utility depends on (total_x - x, total_y - y)
                Z_B = utility_func(total_x - X, total_y - Y, type_b, params_b)
                if isinstance(Z_B, (float, int)): Z_B = np.full_like(X, Z_B)
                
                # Convert to list for JSON (row-major)
                # We need to handle NaN/Inf in grids too
                z_grid_a = [[sanitize_float(val) for val in row] for row in Z_A]
                z_grid_b = [[sanitize_float(val) for val in row] for row in Z_B]
            except Exception as e:
                print(f"Grid generation error: {e}")
                # Fallback to empty grids if calculation fails
                z_grid_a = []
                z_grid_b = []

        # 5. Analysis
        mrs_a_val = mrs_a_init if not np.isinf(mrs_a_init) else 1e9
        mrs_b_val = mrs_b_init if not np.isinf(mrs_b_init) else 1e9
        
        mrs_diff = abs(mrs_a_val - mrs_b_val)
        # If either MRS is infinite, we might be at a corner solution or efficient boundary
        efficient = bool(mrs_diff < 0.05 or np.isinf(mrs_a_init) or np.isinf(mrs_b_init))
        
        trade_advice = ""
        if not efficient:
            if mrs_a_val > mrs_b_val:
                 # MRS_A > MRS_B => A values X more relative to Y than B does.
                 # A should buy X, sell Y.
                 trade_advice = "Agent A should buy X and sell Y."
            else:
                 trade_advice = "Agent B should buy X and sell Y."
        else:
            trade_advice = "Allocation is Pareto efficient."
            
        analysis = {
            "pareto_efficient": efficient,
            "mrs_difference": sanitize_float(mrs_diff),
            "trade_advice": trade_advice
        }

        response = {
            "initial_state": initial_state,
            "walrasian_equilibrium": walrasian_equilibrium,
            "contract_curve": contract_curve,
            "z_grid_a": z_grid_a,
            "z_grid_b": z_grid_b,
            "analysis": analysis
        }
        
        return jsonify(response)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# Register routes with multiple paths to handle Vercel rewrites defensively
@app.route('/api/calculate', methods=['POST', 'OPTIONS'])
def calculate_api():
    return calculate_handler()

@app.route('/calculate', methods=['POST', 'OPTIONS'])
def calculate_root():
    return calculate_handler()

@app.route('/api/health', methods=['GET'])
def health_api():
    return jsonify({"status": "ok", "path": request.path})

@app.route('/health', methods=['GET'])
def health_root():
    return jsonify({"status": "ok", "path": request.path})

# For local testing
# Catch-all for debugging routing issues
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print(f"Catch-all hit: {path}")
    return jsonify({
        "error": "Route not found",
        "path": path,
        "method": request.method
    }), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
