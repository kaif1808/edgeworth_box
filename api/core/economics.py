import numpy as np
from scipy.optimize import minimize, brentq, minimize_scalar
import re
import ast
import operator
from typing import Dict, Any, Tuple, List, Union, Optional
from simpleeval import simple_eval, SimpleEval, NameNotDefined

def parse_latex_to_numpy(latex_str: str) -> str:
    """
    Parses a LaTeX string into a NumPy-compatible expression.

    Args:
        latex_str (str): The LaTeX string to parse.

    Returns:
        str: A string containing the NumPy-compatible expression.
    """
    if not latex_str: return "0"
    expr = latex_str.lower().replace("^", "**").replace(r"\cdot", "*")
    replacements = {
        r"\\ln": "np.log", r"\\log": "np.log", r"\\exp": "np.exp",
        r"\\sqrt": "np.sqrt", r"\\min": "np.minimum", r"\\max": "np.maximum",
        r"min": "np.minimum", r"max": "np.maximum",
    }
    for tex, py in replacements.items(): expr = re.sub(tex, py, expr)
    expr = expr.replace("{", "(").replace("}", ")")
    
    # Handle implicit multiplication
    expr = re.sub(r'\)\(', ')*(', expr)           # (a)(b) -> (a)*(b)
    expr = re.sub(r'\)([xy])', r')*\1', expr)     # (a)x -> (a)*x
    expr = re.sub(r'(\d)\(', r'\1*(', expr)       # 2(x) -> 2*(x)
    expr = re.sub(r'(\d)([xy])', r'\1*\2', expr)  # 2x -> 2*x
    
    return expr

def evaluate_custom_utility(x: Union[float, np.ndarray], y: Union[float, np.ndarray], formula: str) -> Union[float, np.ndarray]:
    """
    Evaluates a custom utility formula using simpleeval for safety.

    Args:
        x (Union[float, np.ndarray]): Quantity of good X.
        y (Union[float, np.ndarray]): Quantity of good Y.
        formula (str): The utility formula (LaTeX-like or Python expression).

    Returns:
        Union[float, np.ndarray]: The calculated utility.
    """
    try:
        # Parse LaTeX to numpy-compatible string first
        parsed_formula = parse_latex_to_numpy(formula)
        
        # Define safe functions
        functions = {
            'np': np,
            'abs': np.abs,
            'log': np.log,
            'exp': np.exp,
            'sqrt': np.sqrt,
            'minimum': np.minimum,
            'maximum': np.maximum,
            'min': np.minimum,
            'max': np.maximum
        }
        
        # Define names
        names = {'x': x, 'y': y}
        
        # Use SimpleEval with overridden Pow operator to support numpy arrays
        s = SimpleEval(names=names, functions=functions)
        s.operators[ast.Pow] = operator.pow
        
        return s.eval(parsed_formula)
    except (SyntaxError, NameNotDefined, TypeError, ZeroDivisionError, Exception):
        # Fallback for safety
        return np.zeros_like(x) if isinstance(x, np.ndarray) else 0.0

def utility_func(x: Union[float, np.ndarray], y: Union[float, np.ndarray], u_type: str, params: Dict[str, Any]) -> Union[float, np.ndarray]:
    """
    Calculates utility based on the specified utility function type and parameters.

    Args:
        x (Union[float, np.ndarray]): Quantity of good X.
        y (Union[float, np.ndarray]): Quantity of good Y.
        u_type (str): The type of utility function (e.g., "Cobb-Douglas").
        params (Dict[str, Any]): Dictionary of parameters for the utility function.

    Returns:
        Union[float, np.ndarray]: The calculated utility.
    """
    x = np.maximum(x, 1e-9)
    y = np.maximum(y, 1e-9)

    if u_type == "Custom (Enter Formula)":
        return evaluate_custom_utility(x, y, params.get('formula', 'x*y'))

    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    a = params.get('a', 0.0)
    b = params.get('b', 0.0)
    
    if u_type == "Cobb-Douglas":
        return (x ** alpha) * (y ** beta)
    elif u_type == "Perfect Substitutes":
        return alpha * x + beta * y
    elif u_type == "Perfect Complements (Min)": 
        return np.minimum(alpha * x, beta * y)
    elif u_type == "Max Preferences (Convex)": 
        return np.maximum(alpha * x, beta * y)
    elif u_type == "Quasi-Linear (Shifted Product)": 
        return (x + a) * (y + b) 
    elif u_type == "Satiation (Bliss Point)": 
        return -1 * ((x - a)**2 + (y - b)**2)
    elif u_type == "Mixed Cobb-Douglas": 
        return x * (y ** alpha)
    return 0.0

def is_convex_preference(u_type: str) -> bool:
    """
    Determines if the preference relation is convex (quasi-concave utility).
    Returns True for standard preferences (Cobb-Douglas, etc.).
    Returns False for non-convex preferences (e.g., Max Preferences).
    """
    if u_type == "Max Preferences (Convex)":
        return False
    # Assume others are convex (standard)
    return True

def verify_pareto_efficiency(x: float, y: float, total_x: float, total_y: float,
                           type_A: str, params_A: Dict[str, Any],
                           type_B: str, params_B: Dict[str, Any]) -> bool:
    """
    Verifies if a point (x, y) is Pareto efficient by checking for local improvements.
    Uses gradients to find potential improvement directions.
    """
    h = 1e-5
    
    # 1. Calculate Gradients locally
    def get_grad(u_func, type_u, params_u, px, py):
        u0 = u_func(px, py, type_u, params_u)
        ux = (u_func(px + h, py, type_u, params_u) - u0) / h
        uy = (u_func(px, py + h, type_u, params_u) - u0) / h
        return np.array([ux, uy]), u0

    gA, uA_curr = get_grad(utility_func, type_A, params_A, x, y)
    
    # For B, inputs are (total_x - x, total_y - y).
    # Gradient w.r.t x, y (A's coords) is -1 * Gradient w.r.t B's inputs
    # because d(TB - x)/dx = -1.
    gB_inputs, uB_curr = get_grad(utility_func, type_B, params_B, total_x - x, total_y - y)
    gB_wrt_A = -gB_inputs 
    
    # Normalize gradients to get directions (avoid division by zero)
    norm_A = np.linalg.norm(gA)
    norm_B = np.linalg.norm(gB_wrt_A)
    
    dirs = []
    if norm_A > 1e-9: dirs.append(gA / norm_A)
    if norm_B > 1e-9: dirs.append(gB_wrt_A / norm_B)
    
    # Bisector (compromise direction)
    if norm_A > 1e-9 and norm_B > 1e-9:
        bisect = (gA / norm_A) + (gB_wrt_A / norm_B)
        if np.linalg.norm(bisect) > 1e-9:
            dirs.append(bisect / np.linalg.norm(bisect))
            
    # Add standard 8 directions for robustness (especially at corners/non-smooth)
    eps = 1e-3
    # We scale directions by eps
    standard_dirs = [
        (1,0), (-1,0), (0,1), (0,-1),
        (1,1), (1,-1), (-1,1), (-1,-1)
    ]
    
    # Combine all test displacements
    test_displacements = [np.array(d) * eps for d in standard_dirs]
    for d in dirs:
        test_displacements.append(d * eps)
        
    # Check candidates
    tol = 1e-7
    
    for dvec in test_displacements:
        dx, dy = dvec[0], dvec[1]
        nx, ny = x + dx, y + dy
        
        # Feasibility check
        if nx < -1e-9 or ny < -1e-9 or nx > total_x + 1e-9 or ny > total_y + 1e-9:
            continue
            
        # Clamp
        nx = max(0, min(total_x, nx))
        ny = max(0, min(total_y, ny))
        
        # Re-eval
        uA_new = utility_func(nx, ny, type_A, params_A)
        uB_new = utility_func(total_x - nx, total_y - ny, type_B, params_B)
        
        # Check improvement
        # Strict for one, weak for other
        A_improved = uA_new > uA_curr + tol
        B_improved = uB_new > uB_curr + tol
        A_weak = uA_new >= uA_curr - tol
        B_weak = uB_new >= uB_curr - tol
        
        if (A_improved and B_weak) or (B_improved and A_weak):
             return False
             
    return True

def calculate_mrs(x: float, y: float, u_type: str, params: Dict[str, Any]) -> float:
    """
    Calculates the Marginal Rate of Substitution (MRS) at a given point.

    Args:
        x (float): Quantity of good X.
        y (float): Quantity of good Y.
        u_type (str): The type of utility function.
        params (Dict[str, Any]): Dictionary of parameters for the utility function.

    Returns:
        float: The MRS at the point (x, y). Returns np.inf if MRS is infinite.
    """
    h = 1e-5
    u0 = utility_func(x, y, u_type, params)
    ux = (utility_func(x + h, y, u_type, params) - u0) / h
    uy = (utility_func(x, y + h, u_type, params) - u0) / h
    
    if abs(uy) < 1e-9:
        if abs(ux) < 1e-9: return 0.0
        return np.inf
    return ux / uy

def get_demand(u_type: str, params: Dict[str, Any], px: float, py: float, income: float, total_x_limit: Optional[float] = None, total_y_limit: Optional[float] = None) -> Tuple[float, float]:
    """
    Calculates the optimal bundle (x, y) given prices and income.

    Args:
        u_type (str): The type of utility function.
        params (Dict[str, Any]): Dictionary of parameters for the utility function.
        px (float): Price of good X.
        py (float): Price of good Y.
        income (float): Total income.
        total_x_limit (Optional[float]): Maximum available quantity of good X.
        total_y_limit (Optional[float]): Maximum available quantity of good Y.

    Returns:
        Tuple[float, float]: The optimal quantity of X and Y.
    """
    # 1. Analytical Solutions for Standard Types
    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    
    if u_type in ["Cobb-Douglas", "Mixed Cobb-Douglas"]:
        # CD: x = (alpha/(alpha+beta)) * I / px
        # Mixed CD: U = x * y^alpha -> equivalent to alpha=1, beta=alpha
        if u_type == "Mixed Cobb-Douglas":
            eff_alpha, eff_beta = 1.0, alpha
        else:
            eff_alpha, eff_beta = alpha, beta
            
        x = (eff_alpha / (eff_alpha + eff_beta)) * income / px
        y = (eff_beta / (eff_alpha + eff_beta)) * income / py
        return x, y

    elif u_type == "Perfect Substitutes":
        # MRS = alpha/beta. If px/py < MRS, buy all X. If >, buy all Y.
        mrs = alpha / beta
        price_ratio = px / py
        
        if price_ratio < mrs - 1e-6:
            return income / px, 0.0
        elif price_ratio > mrs + 1e-6:
            return 0.0, income / py
        else:
            # Indifferent. Return a point on budget line. 
            return income / px, 0.0 

    elif u_type == "Perfect Complements (Min)":
        # Optimal path: alpha * x = beta * y => y = (alpha/beta) * x
        # Budget: px*x + py*(alpha/beta)*x = I
        # x * (px + py*alpha/beta) = I
        x = income / (px + py * (alpha / beta))
        y = (alpha / beta) * x
        return x, y

    elif u_type == "Quasi-Linear (Shifted Product)":
        # U = (x+a)(y+b). Let X=x+a, Y=y+b. U=XY.
        # Budget: px(X-a) + py(Y-b) = I => pxX + pyY = I + pxa + pyb = I_eff
        # Demand for X: I_eff / 2px. Demand for Y: I_eff / 2py.
        a = params.get('a', 0.0)
        b = params.get('b', 0.0)
        I_eff = income + px*a + py*b
        
        X = I_eff / (2 * px)
        # Y = I_eff / (2 * py) # Unused variable
        
        x = max(0, X - a)
        y = (income - px*x) / py
        return x, y

    # 2. Numerical Solution for Others (Satiation, Custom, Max Prefs)
    # For Max Prefs (convex U), solution is at corners.
    if u_type == "Max Preferences (Convex)":
        # Check corners
        x1, y1 = income / px, 0.0
        x2, y2 = 0.0, income / py
        u1 = utility_func(x1, y1, u_type, params)
        u2 = utility_func(x2, y2, u_type, params)
        return (x1, y1) if u1 >= u2 else (x2, y2)

    # General Numerical Solver
    def obj(v): return -utility_func(v[0], v[1], u_type, params)
    def con_budget(v): return income - (px*v[0] + py*v[1])
    
    # Bounds
    b_x = (0, total_x_limit) if total_x_limit else (0, None)
    b_y = (0, total_y_limit) if total_y_limit else (0, None)
    
    # Guess (Midpoint of budget)
    x0 = income / (2 * px)
    y0 = income / (2 * py)
    
    res = minimize(obj, [x0, y0], bounds=[b_x, b_y], constraints={'type':'ineq', 'fun':con_budget}, tol=1e-5)
    if res.success:
        return res.x[0], res.x[1]
    
    return x0, y0

def solve_walrasian_equilibrium(total_x: float, total_y: float, type_A: str, params_A: Dict[str, Any], type_B: str, params_B: Dict[str, Any], endow_A: Tuple[float, float], endow_B: Tuple[float, float]) -> Tuple[float, Tuple[float, float]]:
    """
    Solves for the Walrasian Equilibrium prices and allocation.

    Args:
        total_x (float): Total quantity of good X.
        total_y (float): Total quantity of good Y.
        type_A (str): Utility type for Agent A.
        params_A (Dict[str, Any]): Parameters for Agent A's utility.
        type_B (str): Utility type for Agent B.
        params_B (Dict[str, Any]): Parameters for Agent B's utility.
        endow_A (Tuple[float, float]): Endowment for Agent A (x, y).
        endow_B (Tuple[float, float]): Endowment for Agent B (x, y).

    Returns:
        Tuple[float, Tuple[float, float]]: Equilibrium price of X (px) and Agent A's allocation (xA, yA).
    """
    # Normalize py = 1. Solve for px.
    py = 1.0
    
    wAx, wAy = endow_A
    wBx, wBy = endow_B
    
    def excess_demand_x(px):
        if px <= 0: return 1e9 # Penalty for negative price
        
        # Income
        IA = px * wAx + py * wAy
        IB = px * wBx + py * wBy
        
        # Demand
        xA, yA = get_demand(type_A, params_A, px, py, IA, total_x, total_y)
        xB, yB = get_demand(type_B, params_B, px, py, IB, total_x, total_y)
        
        return (xA + xB) - total_x

    # Root Finding for px
    # Try to bracket the root
    low, high = 0.01, 100.0
    try:
        px_eq = brentq(excess_demand_x, low, high, xtol=1e-4)
    except ValueError:
        # brentq failed (no sign change). Try minimize absolute excess demand.
        res = minimize_scalar(lambda p: abs(excess_demand_x(p)), bounds=(0.01, 100.0), method='bounded')
        px_eq = res.x
    
    # Calculate Final Allocation
    IA = px_eq * wAx + py * wAy
    xA, yA = get_demand(type_A, params_A, px_eq, py, IA, total_x, total_y)
    
    return px_eq, (xA, yA)

def solve_contract_curve(total_x: float, total_y: float, type_A: str, params_A: Dict[str, Any], type_B: str, params_B: Dict[str, Any], uA_w: float, uB_w: float, Z_B_min: float, Z_B_max: float) -> Tuple[List[float], List[float], List[float], List[float]]:
    """
    Solves for the contract curve (Pareto set) and the Core.
    Includes checks for convexity and a fail-safe Pareto verification.
    """
    pareto_candidates = []
    
    # 1. Optimization Sweep (Good for Interior & Standard Convex Preferences)
    # We check if we should prioritize interior or boundary based on convexity
    convex_A = is_convex_preference(type_A)
    convex_B = is_convex_preference(type_B)
    
    steps = 100 
    if Z_B_max > Z_B_min and (convex_A and convex_B):
        levels_B = np.linspace(Z_B_min, Z_B_max, steps)
        last_x = [total_x / 2, total_y / 2] 
        
        for ub_val in levels_B:
            def obj(v): return -utility_func(v[0], v[1], type_A, params_A)
            def con(v): return utility_func(total_x - v[0], total_y - v[1], type_B, params_B) - ub_val
            
            bnds = ((0, total_x), (0, total_y))
            # Try to keep close to previous solution for continuity
            res = minimize(obj, last_x, bounds=bnds, constraints={'type':'ineq', 'fun':con}, tol=1e-5)
            
            best_p = None
            best_u = -np.inf
            
            if res.success:
                best_p = res.x
                last_x = res.x
            else:
                starts = [[0, 0], [total_x, total_y], [0, total_y], [total_x, 0], [total_x/2, total_y/2]]
                for s in starts:
                    res_retry = minimize(obj, s, bounds=bnds, constraints={'type':'ineq', 'fun':con}, tol=1e-5)
                    if res_retry.success:
                        ua = utility_func(res_retry.x[0], res_retry.x[1], type_A, params_A)
                        if ua > best_u:
                            best_u = ua
                            best_p = res_retry.x
                            last_x = res_retry.x

            if best_p is not None:
                ub_real = utility_func(total_x - best_p[0], total_y - best_p[1], type_B, params_B)
                if ub_real >= ub_val - 0.1: # Relaxed tolerance for constraint
                    pareto_candidates.append((best_p[0], best_p[1]))

    # 2. Boundary Check (Crucial for Non-Convex / Concave Preferences, and Corners)
    # Always check boundaries as fail-safe for corner solutions
    if True:
        num_edge = 100
        edge1 = [(x, 0.0) for x in np.linspace(0, total_x, num_edge)]
        edge2 = [(x, total_y) for x in np.linspace(0, total_x, num_edge)]
        edge3 = [(0.0, y) for y in np.linspace(0, total_y, num_edge)]
        edge4 = [(total_x, y) for y in np.linspace(0, total_y, num_edge)]
        pareto_candidates.extend(edge1 + edge2 + edge3 + edge4)
        
        # Also add exact corners
        pareto_candidates.extend([(0.0, 0.0), (total_x, total_y), (0.0, total_y), (total_x, 0.0)])

    # 3. Verification and Filtering
    valid_pareto = []
    seen_points = []
    
    # Use a simple grid hash for deduplication
    def get_grid_key(p):
        return (int(p[0] * 100), int(p[1] * 100))
    
    seen_keys = set()

    for px, py in pareto_candidates:
        # Quick bounds check
        px = max(0, min(total_x, px))
        py = max(0, min(total_y, py))
        
        key = get_grid_key((px, py))
        if key in seen_keys:
            continue
            
        # Fail-safe verification
        if verify_pareto_efficiency(px, py, total_x, total_y, type_A, params_A, type_B, params_B):
            valid_pareto.append((px, py))
            seen_keys.add(key)

    # 4. Sort and Extract Core
    pareto_x, pareto_y = [], []
    core_x, core_y = [], []
    
    if valid_pareto:
        # Sort by X, then Y
        valid_pareto.sort(key=lambda p: (p[0], p[1]))
        
        for px, py in valid_pareto:
            pareto_x.append(px)
            pareto_y.append(py)
            
            ua = utility_func(px, py, type_A, params_A)
            ub = utility_func(total_x - px, total_y - py, type_B, params_B)
            
            if ua >= uA_w - 1e-3 and ub >= uB_w - 1e-3:
                core_x.append(px)
                core_y.append(py)

    return pareto_x, pareto_y, core_x, core_y