import numpy as np
from scipy.optimize import minimize, brentq, minimize_scalar
import re
import ast
import operator
from typing import Dict, Any, Tuple, List, Union, Optional
from simpleeval import simple_eval, SimpleEval, NameNotDefined
try:
    from api.core import xcas_engine
except ImportError:
    xcas_engine = None # Fallback if import fails

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

def get_computational_formula(u_type: str, params: Dict[str, Any]) -> str:
    """
    Returns a clean mathematical string representing the utility function
    suitable for XCas parsing (no LaTeX).
    """
    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    a = params.get('a', 0.0)
    b = params.get('b', 0.0)
    
    if u_type == "Cobb-Douglas" or u_type == "Non-standard Cobb-Douglas":
        return f"(x^{alpha}) * (y^{beta})"
    elif u_type == "Perfect Substitutes":
        return f"{alpha}*x + {beta}*y"
    elif u_type == "Perfect Complements (Min)": 
        # Note: Min is often not differentiable at the kink
        return f"min({alpha}*x, {beta}*y)"
    elif u_type == "Max Preferences (Convex)": 
        return f"max({alpha}*x, {beta}*y)"
    elif u_type == "Quasi-Linear (Shifted Product)": 
        return f"(x + {a})*(y + {b})"
    elif u_type == "Satiation (Bliss Point)": 
        return f"-1*((x - {a})^2 + (y - {b})^2)"
    elif u_type == "Mixed Cobb-Douglas": 
        return f"x * (y^{alpha})"
    elif u_type == "CES":
        rho = params.get('rho', 0.5)
        if abs(rho) < 1e-3: return f"(x^{alpha}) * (y^{beta})"
        return f"({alpha}*x^{rho} + {beta}*y^{rho})^(1/{rho})"
    elif u_type == "Custom (Enter Formula)":
        return params.get('formula', 'x*y')
    return "0"

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
    
    if u_type == "Cobb-Douglas" or u_type == "Non-standard Cobb-Douglas":
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
    elif u_type == "CES":
        rho = params.get('rho', 0.5)
        if abs(rho) < 1e-3: # Approx Cobb-Douglas
             return (x ** alpha) * (y ** beta)
        # Handle negative bases safely if rho is integer, but generally x, y > 0
        # Add small epsilon to avoid div by zero in power if rho < 0
        return (alpha * (x**rho) + beta * (y**rho))**(1/rho)
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
    
    # Try Symbolic Gradient first
    gA, gB_wrt_A = None, None
    
    if xcas_engine and xcas_engine.is_available():
        form_A = get_computational_formula(type_A, params_A)
        form_B = get_computational_formula(type_B, params_B)
        
        # Skip symbolic for non-differentiable types like Min/Max
        if "min" not in form_A and "max" not in form_A:
            gA = xcas_engine.get_gradient(form_A, x, y)
            
        if "min" not in form_B and "max" not in form_B:
            # For B, evaluate at (total_x - x, total_y - y)
            # But we need gradient w.r.t (x,y). 
            # U_B(x_B, y_B) = U_B(Tx - x, Ty - y)
            # dU_B/dx = (dU_B/dx_B) * (-1)
            gB_raw = xcas_engine.get_gradient(form_B, total_x - x, total_y - y)
            if gB_raw is not None:
                gB_wrt_A = -gB_raw

    # Fallback to Numerical Gradient if symbolic failed or unavailable
    h = 1e-5
    def get_grad_num(u_func, type_u, params_u, px, py):
        u0 = u_func(px, py, type_u, params_u)
        ux = (u_func(px + h, py, type_u, params_u) - u0) / h
        uy = (u_func(px, py + h, type_u, params_u) - u0) / h
        return np.array([ux, uy]), u0

    if gA is None:
        gA, _ = get_grad_num(utility_func, type_A, params_A, x, y)
    
    if gB_wrt_A is None:
        gB_inputs, _ = get_grad_num(utility_func, type_B, params_B, total_x - x, total_y - y)
        gB_wrt_A = -gB_inputs 
    
    uA_curr = utility_func(x, y, type_A, params_A)
    uB_curr = utility_func(total_x - x, total_y - y, type_B, params_B)

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
    tol = 1e-6 # Relaxed from 1e-7 to account for optimizer noise
    
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
        float: The MRS at the point (x, y). Returns np.inf, -np.inf, or np.nan appropriately.
    """
    # Ensure non-negative inputs for utility calculation
    x = max(0.0, x)
    y = max(0.0, y)
    
    # Try Symbolic Calculation first
    if xcas_engine and xcas_engine.is_available():
        formula = get_computational_formula(u_type, params)
        # Skip Min/Max/Custom if complex
        if "min" not in formula.lower() and "max" not in formula.lower():
            mrs = xcas_engine.calculate_mrs(formula, x, y)
            if mrs is not None:
                # Validate result: only reject NaN as definitely invalid
                # Infinite MRS can be legitimate (e.g., when du/dy = 0), so accept it
                if np.isnan(mrs):
                    # Invalid result, fall through to numerical
                    pass
                else:
                    return mrs

    # Fallback to Numerical
    h = 1e-5
    # Use small epsilon to avoid division issues at boundaries
    x_safe = max(h, x)
    y_safe = max(h, y)
    
    u0 = utility_func(x_safe, y_safe, u_type, params)
    ux = (utility_func(x_safe + h, y_safe, u_type, params) - u0) / h
    uy = (utility_func(x_safe, y_safe + h, u_type, params) - u0) / h
    
    # Handle small gradients (flat regions or kinks)
    if abs(uy) < 1e-9:
        if abs(ux) < 1e-9: 
            # Check if it's a kink like Min(x,y) where forward difference yields 0
            # Try backward difference to see if it's 0 there too
            if x > h and y > h:
                ux_b = (u0 - utility_func(x_safe - h, y_safe, u_type, params)) / h
                uy_b = (u0 - utility_func(x_safe, y_safe - h, u_type, params)) / h
                if abs(ux_b) > 1e-9 or abs(uy_b) > 1e-9:
                    # Kink detected. MRS is undefined.
                    return np.nan
            return 0.0  # Truly flat?
        # uy is near zero, ux is not -> infinite MRS
        return np.inf * np.sign(ux) if ux != 0 else np.nan
    
    # Normal case: both derivatives are non-zero
    result = ux / uy
    
    # Validate result
    if np.isnan(result) or (np.isinf(result) and abs(uy) > 1e-9):
        return np.nan
        
    return result

def get_demand(u_type: str, params: Dict[str, Any], px: float, py: float, income: float, total_x_limit: Optional[float] = None, total_y_limit: Optional[float] = None) -> Tuple[float, float]:
    """
    Calculates the optimal bundle (x, y) given prices and income.

    Args:
        u_type (str): The type of utility function.
        params (Dict[str, Any]): Dictionary of parameters for the utility function.
        px (float): Price of good X (must be > 0).
        py (float): Price of good Y (must be > 0).
        income (float): Total income (must be >= 0).
        total_x_limit (Optional[float]): Maximum available quantity of good X.
        total_y_limit (Optional[float]): Maximum available quantity of good Y.

    Returns:
        Tuple[float, float]: The optimal quantity of X and Y (both >= 0).
    """
    # Validate inputs
    px = max(1e-9, px)  # Ensure positive price
    py = max(1e-9, py)  # Ensure positive price
    income = max(0.0, income)  # Ensure non-negative income
    
    # Helper to clamp results and ensure non-negative
    def clamp_res(cx, cy):
        cx = max(0.0, cx)
        cy = max(0.0, cy)
        # Ensure budget constraint is satisfied
        if px * cx + py * cy > income + 1e-6:  # Allow small numerical error
            # If over budget, scale down proportionally
            scale = income / (px * cx + py * cy) if (px * cx + py * cy) > 0 else 0
            cx = cx * scale
            cy = cy * scale
        # Ensure within limits if specified
        if total_x_limit is not None:
            cx = min(cx, total_x_limit)
        if total_y_limit is not None:
            cy = min(cy, total_y_limit)
        return cx, cy

    # 1. Analytical Solutions for Standard Types
    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    
    if u_type in ["Cobb-Douglas", "Mixed Cobb-Douglas", "Non-standard Cobb-Douglas"]:
        # CD: x = (alpha/(alpha+beta)) * I / px
        # Mixed CD: U = x * y^alpha -> equivalent to alpha=1, beta=alpha
        if u_type == "Mixed Cobb-Douglas":
            eff_alpha, eff_beta = 1.0, alpha
        else:
            eff_alpha, eff_beta = alpha, beta
            
        x = (eff_alpha / (eff_alpha + eff_beta)) * income / px
        y = (eff_beta / (eff_alpha + eff_beta)) * income / py
        return clamp_res(x, y)

    elif u_type == "CES":
        rho = params.get('rho', 0.5)
        # Edge case: Cobb-Douglas
        if abs(rho) < 1e-3:
             x = (alpha / (alpha + beta)) * income / px
             y = (beta / (alpha + beta)) * income / py
             return clamp_res(x, y)
        
        try:
            r = rho
            # Check for potential overflow in exponent
            exponent = 1 / (1 - r)
            if abs(exponent) > 100: 
                raise OverflowError("Exponent too large")
                
            # Formula derived: x = I / (px + py * ( (px*beta)/(py*alpha) )**(1/(1-r)) )
            term_base = (px * beta) / (py * alpha)
            term = term_base ** exponent
            
            x = income / (px + py * term)
            y = x * term
            return clamp_res(x, y)
        except (OverflowError, ZeroDivisionError, ValueError):
            # Fallback to numerical
            pass

    elif u_type == "Perfect Substitutes":
        # MRS = alpha/beta. If px/py < MRS, buy all X. If >, buy all Y.
        mrs = alpha / beta
        price_ratio = px / py
        
        if price_ratio < mrs - 1e-6:
            return clamp_res(income / px, 0.0)
        elif price_ratio > mrs + 1e-6:
            return clamp_res(0.0, income / py)
        else:
            # Indifferent. Return a point on budget line. 
            return clamp_res(income / px, 0.0)

    elif u_type == "Perfect Complements (Min)":
        # Optimal path: alpha * x = beta * y => y = (alpha/beta) * x
        # Budget: px*x + py*(alpha/beta)*x = I
        # x * (px + py*alpha/beta) = I
        x = income / (px + py * (alpha / beta))
        y = (alpha / beta) * x
        return clamp_res(x, y)

    elif u_type == "Quasi-Linear (Shifted Product)":
        # U = (x+a)(y+b). Let X=x+a, Y=y+b. U=XY.
        # Budget: px(X-a) + py(Y-b) = I => pxX + pyY = I + pxa + pyb = I_eff
        # Demand for X: I_eff / 2px. Demand for Y: I_eff / 2py.
        a = params.get('a', 0.0)
        b = params.get('b', 0.0)
        I_eff = income + px*a + py*b
        
        X = I_eff / (2 * px)
        
        x = max(0.0, X - a)
        y = (income - px * x) / py
        
        # Check if y became negative
        if y < 0:
            y = 0.0
            x = income / px
            
        return clamp_res(x, y)

    # 2. Numerical Solution for Others (Satiation, Custom, Max Prefs)
    # For Max Prefs (convex U), solution is at corners.
    if u_type == "Max Preferences (Convex)":
        # Check corners
        x1, y1 = income / px, 0.0
        x2, y2 = 0.0, income / py
        u1 = utility_func(x1, y1, u_type, params)
        u2 = utility_func(x2, y2, u_type, params)
        return clamp_res(x1, y1) if u1 >= u2 else clamp_res(x2, y2)

    # General Numerical Solver
    def obj(v): return -utility_func(v[0], v[1], u_type, params)
    def con_budget(v): return income - (px*v[0] + py*v[1])
    
    # Bounds
    b_x = (0, total_x_limit) if total_x_limit else (0, None)
    b_y = (0, total_y_limit) if total_y_limit else (0, None)
    
    # Guess (Midpoint of budget)
    x0 = income / (2 * px)
    y0 = income / (2 * py)
    
    # 1. Interior Optimization
    res = minimize(obj, [x0, y0], bounds=[b_x, b_y], constraints={'type':'ineq', 'fun':con_budget}, tol=1e-5)
    
    # 2. Corner Checks (Crucial for non-convex or edge cases)
    # Corner X (spend all on X)
    cx_x = income / px
    if total_x_limit: cx_x = min(cx_x, total_x_limit)
    cx_y = (income - px*cx_x) / py
    
    # Corner Y (spend all on Y)
    cy_y = income / py
    if total_y_limit: cy_y = min(cy_y, total_y_limit)
    cy_x = (income - py*cy_y) / px
    
    corners = [(cx_x, cx_y), (cy_x, cy_y)]
    best_res = None
    max_u = -np.inf
    
    # Evaluate Interior Result
    if res.success:
        ux = res.x[0]
        uy = res.x[1]
        u_val = utility_func(ux, uy, u_type, params)
        best_res = (ux, uy)
        max_u = u_val
        
    # Evaluate Corners
    for (cx, cy) in corners:
        if cx < 0 or cy < 0: continue # Should not happen with clamp but safe check
        u_val = utility_func(cx, cy, u_type, params)
        if u_val > max_u + 1e-5: # Strict improvement tolerance
            max_u = u_val
            best_res = (cx, cy)
            
    if best_res:
        return clamp_res(best_res[0], best_res[1])
    
    return clamp_res(x0, y0)

def solve_walrasian_equilibrium(total_x: float, total_y: float, type_A: str, params_A: Dict[str, Any], type_B: str, params_B: Dict[str, Any], endow_A: Tuple[float, float], endow_B: Tuple[float, float]) -> Tuple[bool, str, List[Tuple[float, Tuple[float, float]]]]:
    """
    Solves for all Walrasian Equilibrium prices and allocations.

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
        Tuple[bool, str, List[Tuple[float, Tuple[float, float]]]]: 
            - Success (bool)
            - Message (str)
            - List of Equilibria [(price, allocation_a), ...]
    """
    # Normalize py = 1. Solve for px.
    py = 1.0
    
    wAx, wAy = endow_A
    wBx, wBy = endow_B
    
    def excess_demand_x(px):
        if px <= 0: return 1e9  # Penalty for negative price
        
        # Income (ensure non-negative)
        IA = max(0.0, px * wAx + py * wAy)
        IB = max(0.0, px * wBx + py * wBy)
        
        # Demand (already clamped to non-negative in get_demand)
        xA, yA = get_demand(type_A, params_A, px, py, IA, total_x, total_y)
        xB, yB = get_demand(type_B, params_B, px, py, IB, total_x, total_y)
        
        # Ensure allocations are non-negative and within bounds
        xA = max(0.0, min(total_x, xA))
        yA = max(0.0, min(total_y, yA))
        xB = max(0.0, min(total_x, xB))
        yB = max(0.0, min(total_y, yB))
        
        return (xA + xB) - total_x

    # Root Finding for px
    # Scan logarithmic range for multiple roots
    low_exp, high_exp = -2.0, 2.0
    search_points = np.logspace(low_exp, high_exp, 200) # 200 points from 0.01 to 100
    
    roots = []
    
    for i in range(len(search_points) - 1):
        p1 = search_points[i]
        p2 = search_points[i+1]
        
        ed1 = excess_demand_x(p1)
        ed2 = excess_demand_x(p2)
        
        if ed1 * ed2 <= 0: # Sign change detected
            try:
                px_root = brentq(excess_demand_x, p1, p2, xtol=1e-4)
                
                # Check if unique (avoid duplicates from adjacent intervals)
                is_unique = True
                for r in roots:
                    if abs(r - px_root) < 1e-3:
                        is_unique = False
                        break
                
                if is_unique:
                    roots.append(px_root)
            except ValueError:
                continue

    equilibria = []
    success = False
    message = ""

    if roots:
        success = True
        message = f"Found {len(roots)} equilibrium price(s)."
        
        for px_eq in roots:
            # Ensure price is positive
            if px_eq <= 0:
                continue
                
            # Calculate Final Allocation for each price
            IA = max(0.0, px_eq * wAx + py * wAy)
            IB = max(0.0, px_eq * wBx + py * wBy)
            
            xA, yA = get_demand(type_A, params_A, px_eq, py, IA, total_x, total_y)
            xB, yB = get_demand(type_B, params_B, px_eq, py, IB, total_x, total_y)
            
            # Ensure allocations are non-negative and feasible
            xA = max(0.0, min(total_x, xA))
            yA = max(0.0, min(total_y, yA))
            xB = max(0.0, min(total_x, xB))
            yB = max(0.0, min(total_y, yB))
            
            # Verify feasibility: xA + xB <= total_x, yA + yB <= total_y
            # If not feasible, scale down proportionally
            if xA + xB > total_x + 1e-6:
                scale_x = total_x / (xA + xB) if (xA + xB) > 0 else 0
                xA = xA * scale_x
                xB = xB * scale_x
            if yA + yB > total_y + 1e-6:
                scale_y = total_y / (yA + yB) if (yA + yB) > 0 else 0
                yA = yA * scale_y
                yB = yB * scale_y
            
            equilibria.append((px_eq, (xA, yA)))
            
    else:
        # Fallback to minimization if no root found (scan failed)
        res = minimize_scalar(lambda p: abs(excess_demand_x(p)), bounds=(0.01, 100.0), method='bounded')
        px_eq = res.x
        
        final_excess = excess_demand_x(px_eq)
        if abs(final_excess) < 0.1 * total_x: 
             # Ensure price is positive before setting success
             if px_eq > 0:
                 IA = max(0.0, px_eq * wAx + py * wAy)
                 IB = max(0.0, px_eq * wBx + py * wBy)
                 
                 xA, yA = get_demand(type_A, params_A, px_eq, py, IA, total_x, total_y)
                 xB, yB = get_demand(type_B, params_B, px_eq, py, IB, total_x, total_y)
                 
                 # Ensure allocations are non-negative and feasible
                 xA = max(0.0, min(total_x, xA))
                 yA = max(0.0, min(total_y, yA))
                 xB = max(0.0, min(total_x, xB))
                 yB = max(0.0, min(total_y, yB))
                 
                 # Verify feasibility
                 if xA + xB > total_x + 1e-6:
                     scale_x = total_x / (xA + xB) if (xA + xB) > 0 else 0
                     xA = xA * scale_x
                     xB = xB * scale_x
                 if yA + yB > total_y + 1e-6:
                     scale_y = total_y / (yA + yB) if (yA + yB) > 0 else 0
                     yA = yA * scale_y
                     yB = yB * scale_y
                 
                 equilibria.append((px_eq, (xA, yA)))
                 # Only set success after confirming equilibrium was appended
                 success = True
                 message = "Approximate equilibrium found (minimized excess demand)."
        else:
             success = False
             message = f"Could not find market clearing price. Excess demand for X at best price (p={px_eq:.2f}) is {final_excess:.2f}."
             
             if not is_convex_preference(type_A) or not is_convex_preference(type_B):
                 message += " Non-convex preferences (e.g., Max Preferences) often lead to corner solutions that do not clear the market."

    return success, message, equilibria

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
    
    steps = 500 
    if Z_B_max > Z_B_min and (convex_A and convex_B):
        levels_B = np.linspace(Z_B_min, Z_B_max, steps)
        last_x = [total_x / 2, total_y / 2] 
        
        for ub_val in levels_B:
            def obj(v): return -utility_func(v[0], v[1], type_A, params_A)
            def con(v): return utility_func(total_x - v[0], total_y - v[1], type_B, params_B) - ub_val
            
            bnds = ((0, total_x), (0, total_y))
            # Try to keep close to previous solution for continuity
            res = minimize(obj, last_x, bounds=bnds, constraints={'type':'ineq', 'fun':con}, tol=1e-6)
            
            best_p = None
            best_u = -np.inf
            
            if res.success:
                best_p = res.x
                last_x = res.x
            else:
                starts = [[0, 0], [total_x, total_y], [0, total_y], [total_x, 0], [total_x/2, total_y/2]]
                for s in starts:
                    res_retry = minimize(obj, s, bounds=bnds, constraints={'type':'ineq', 'fun':con}, tol=1e-6)
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
        num_edge = 200
        edge1 = [(x, 0.0) for x in np.linspace(0, total_x, num_edge)]
        edge2 = [(x, total_y) for x in np.linspace(0, total_x, num_edge)]
        edge3 = [(0.0, y) for y in np.linspace(0, total_y, num_edge)]
        edge4 = [(total_x, y) for y in np.linspace(0, total_y, num_edge)]
        pareto_candidates.extend(edge1 + edge2 + edge3 + edge4)
        
        # Also add exact corners
        pareto_candidates.extend([(0.0, 0.0), (total_x, total_y), (0.0, total_y), (total_x, 0.0)])

    # 2.5 Analytical Expansion Paths for Min Functions (Hard Corners)
    # Numerical gradients fail at the kink of Min functions.
    # We explicitly add the expansion path (where alpha*x = beta*y) to candidates.
    if type_A == "Perfect Complements (Min)":
        alpha_a = params_A.get('alpha', 0.5)
        beta_a = params_A.get('beta', 0.5)
        if beta_a > 1e-9:
            ratio_a = alpha_a / beta_a
            # Generate points along y = ratio * x
            x_pts = np.linspace(0, total_x, 200)
            y_pts = ratio_a * x_pts
            for i in range(len(x_pts)):
                if 0 <= y_pts[i] <= total_y:
                    pareto_candidates.append((float(x_pts[i]), float(y_pts[i])))

    if type_B == "Perfect Complements (Min)":
        alpha_b = params_B.get('alpha', 0.5)
        beta_b = params_B.get('beta', 0.5)
        if beta_b > 1e-9:
            ratio_b = alpha_b / beta_b
            # B's expansion path: alpha_b * x_b = beta_b * y_b
            # x_b = total_x - x_a, y_b = total_y - y_a
            # alpha_b * (total_x - x_a) = beta_b * (total_y - y_a)
            # (alpha_b/beta_b) * (total_x - x_a) = total_y - y_a
            # y_a = total_y - ratio_b * (total_x - x_a)
            x_pts = np.linspace(0, total_x, 200)
            y_pts = total_y - ratio_b * (total_x - x_pts)
            for i in range(len(x_pts)):
                if 0 <= y_pts[i] <= total_y:
                    pareto_candidates.append((float(x_pts[i]), float(y_pts[i])))

    # 3. Verification and Filtering
    valid_pareto = []
    seen_points = []
    
    # Use a simple grid hash for deduplication
    def get_grid_key(p):
        return (int(p[0] * 500), int(p[1] * 500))
    
    seen_keys = set()

    for px, py in pareto_candidates:
        # Strict bounds check (allowing for tiny numerical error but clamping)
        # Also discard if significantly out of bounds (negative)
        if px < -1e-5 or py < -1e-5 or px > total_x + 1e-5 or py > total_y + 1e-5:
             continue
        
        # Clamp to exact bounds for safety
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

def get_utility_string(u_type: str, params: Dict[str, Any]) -> str:
    """Returns a LaTeX string representing the utility function."""
    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    a = params.get('a', 0.0)
    b = params.get('b', 0.0)
    
    if u_type == "Cobb-Douglas" or u_type == "Non-standard Cobb-Douglas":
        return f"x^{{{alpha}}} y^{{{beta}}}"
    elif u_type == "Perfect Substitutes":
        return f"{alpha}x + {beta}y"
    elif u_type == "Perfect Complements (Min)": 
        return f"\\min({alpha}x, {beta}y)"
    elif u_type == "Max Preferences (Convex)": 
        return f"\\max({alpha}x, {beta}y)"
    elif u_type == "Quasi-Linear (Shifted Product)": 
        return f"(x + {a})(y + {b})"
    elif u_type == "Satiation (Bliss Point)": 
        return f"-1((x - {a})^2 + (y - {b})^2)"
    elif u_type == "Mixed Cobb-Douglas": 
        return f"x y^{{{alpha}}}"
    elif u_type == "CES":
        rho = params.get('rho', 0.5)
        return f"({alpha}x^{{{rho}}} + {beta}y^{{{rho}}})^{{1/{rho}}}"
    elif u_type == "Custom (Enter Formula)":
        return params.get('formula', 'x*y')
    return "u(x,y)"

def generate_workings(total_x, total_y, type_a, params_a, type_b, params_b, endow_a, endow_b, equilibria, we_success=True, we_message="", pareto_found=True, core_found=True):
    workings = {}

    # 1. Primitives
    u_str_a = get_utility_string(type_a, params_a)
    u_str_b = get_utility_string(type_b, params_b)
    
    workings['1_primitives'] = {
        "title": "1. Model Primitives",
        "content": [
            "**Agents & Endowments**",
            f"Agent A: Utility {type_a}",
            f"$u^A(x^A, y^A) = {u_str_a}$",
            f"Endowment $\\omega^A = ({endow_a[0]:.2f}, {endow_a[1]:.2f})$",
            "",
            f"Agent B: Utility {type_b}",
            f"$u^B(x^B, y^B) = {u_str_b}$",
            f"Endowment $\\omega^B = ({endow_b[0]:.2f}, {endow_b[1]:.2f})$",
            "",
            "**Total Resources**",
            f"$\\bar{{X}} = {total_x}, \\bar{{Y}} = {total_y}$"
        ]
    }

    # 2. Demand Functions (Simplified)
    workings['2_demand'] = {
        "title": "2. Demand Functions",
        "content": [
            "Given prices $p_x, p_y=1$ and income $I$, agents maximize utility subject to budget constraints.",
            f"Income $I^A = p_x \\omega_x^A + \\omega_y^A$",
            f"Income $I^B = p_x \\omega_x^B + \\omega_y^B$",
            "Demand functions $x(p_x, I)$ derived from FOCs:",
            "For Cobb-Douglas: $x^* = \\frac{\\alpha}{\\alpha+\\beta} \\frac{I}{p_x}$",
            "For Perfect Substitutes: Corner solution depending on $p_x$ vs $MRS$",
            "For Perfect Complements: Expansion path $\\alpha x = \\beta y$ substituted into budget",
        ]
    }

    # 3. Market Clearing
    if we_success and equilibria:
        content = [
            "Equilibrium price $p_x^*$ is found where excess demand for X is zero.",
            f"$Z_x(p_x) = x^A(p_x) + x^B(p_x) - \\bar{{X}} = 0$",
            f"**Found {len(equilibria)} Equilibrium/Equilibria:**"
        ]
        
        for i, (px, _) in enumerate(equilibria):
            content.append(f"{i+1}. $p_x = {px:.4f}$")
            
        workings['3_market_clearing'] = {
            "title": "3. Market Clearing Condition",
            "content": content
        }
    else:
        workings['3_market_clearing'] = {
            "title": "3. Market Clearing Condition (Failed)",
            "content": [
                "**Walrasian Equilibrium Not Found**",
                f"The solver failed to find a price where excess demand is zero.",
                f"**Reason:** {we_message}"
            ]
        }

    # 4. Efficiency Condition (Pareto Set)
    def format_mrs(val):
        if np.isinf(val): return r"\infty"
        return f"{val:.4f}"

    if pareto_found:
        workings['4_efficiency'] = {
            "title": "4. Efficiency Condition (Pareto Set)",
            "content": [
                "An allocation is Pareto Efficient if $MRS^A = MRS^B$ (for interior solutions).",
                "The Contract Curve is the set of all points where these marginal rates of substitution are equal (tangency condition), bounded by feasibility."
            ]
        }
    else:
        workings['4_efficiency'] = {
            "title": "4. Efficiency Condition (Empty Set)",
            "content": [
                "**No Pareto Efficient Points Found**",
                "The system could not identify any points where neither agent can be made better off without harming the other.",
            ]
        }

    # 5. The Core
    u_a_w = utility_func(endow_a[0], endow_a[1], type_a, params_a)
    u_b_w = utility_func(endow_b[0], endow_b[1], type_b, params_b)

    if core_found:
        workings['5_core'] = {
            "title": "5. The Core",
            "content": [
                "The Core is the subset of the Pareto Set that satisfies Individual Rationality (IR).",
                "**Utility at Endowment (Reservation Utility):**",
                f"$u^A(\\omega^A) = {u_a_w:.2f}$",
                f"$u^B(\\omega^B) = {u_b_w:.2f}$",
                "**Core Condition:**",
                f"Any core allocation must satisfy $u^A(x^A) \\ge {u_a_w:.2f}$ and $u^B(x^B) \\ge {u_b_w:.2f}$."
            ]
        }
    else:
        workings['5_core'] = {
            "title": "5. The Core (Empty)",
            "content": [
                "**No Core Points Found**",
                "The Core is empty.",
                "**Reservation Utilities:**",
                f"$u^A(\\omega^A) = {u_a_w:.2f}$",
                f"$u^B(\\omega^B) = {u_b_w:.2f}$"
            ]
        }

    # 6. Final Allocation Summary
    if we_success and equilibria:
        content = ["**Equilibrium Summary:**"]
        for i, (px, (ax, ay)) in enumerate(equilibria):
             content.append(f"**Equilibrium {i+1}:**")
             content.append(f"$p_x^* = {px:.4f}, p_y^* = 1$")
             content.append(f"Allocation A: ({ax:.2f}, {ay:.2f})")
             content.append(f"Allocation B: ({total_x - ax:.2f}, {total_y - ay:.2f})")
             content.append("")

        workings['6_summary'] = {
            "title": "6. Final Allocation Summary",
            "content": content
        }
    else:
        workings['6_summary'] = {
            "title": "6. Final Allocation Summary (None)",
            "content": [
                "No valid equilibrium allocation could be determined.",
                "Please adjust preferences or endowments to find a solution."
            ]
        }

    return workings
