import numpy as np
import re
from typing import Optional, Tuple, Union, List

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("Warning: sympy not found. Symbolic differentiation will be unavailable.")

def is_available() -> bool:
    """Check if SymPy is available."""
    return SYMPY_AVAILABLE

def clean_formula_for_sympy(formula: str) -> str:
    """
    Preprocesses a formula string to be compatible with SymPy.
    - Replaces numpy functions with standard math names.
    - Handles power operator replacement if necessary.
    """
    if not formula:
        return "0"
    
    # Basic replacements
    expr = formula.lower()
    replacements = {
        "np.log": "log", "np.exp": "exp", "np.sqrt": "sqrt",
        "np.minimum": "Min", "np.maximum": "Max",
        "log": "log",
        "ln": "log", # Handle ln as log
        "^": "**" # Ensure power syntax is correct for SymPy
    }
    for py, g in replacements.items():
        expr = expr.replace(py, g)
        
    return expr

def calculate_mrs(formula: str, x_val: float, y_val: float) -> Optional[float]:
    """
    Calculates the Marginal Rate of Substitution (MRS) using symbolic differentiation.
    MRS = (dU/dx) / (dU/dy)
    
    Args:
        formula (str): The utility function formula.
        x_val (float): Quantity of good X.
        y_val (float): Quantity of good Y.
        
    Returns:
        float: The MRS at (x_val, y_val). Returns np.inf or 0.0 appropriately.
               Returns None if symbolic calculation fails.
    """
    if not SYMPY_AVAILABLE:
        return None

    try:
        # 1. Setup variables
        x, y = sympy.symbols('x y')
        
        # 2. Parse formula
        cleaned_formula = clean_formula_for_sympy(formula)
        # parse_expr with transformations might be needed for implicit mult, 
        # but economics.py handles it. We use sympify for simplicity.
        u = sympy.sympify(cleaned_formula)
        
        # 3. Differentiate
        du_dx = sympy.diff(u, x)
        du_dy = sympy.diff(u, y)
        
        # 4. Evaluate
        # use subs and evalf
        val_du_dx = float(du_dx.subs({x: x_val, y: y_val}))
        val_du_dy = float(du_dy.subs({x: x_val, y: y_val}))
        
        # 5. Calculate Ratio
        if abs(val_du_dy) < 1e-9:
            if abs(val_du_dx) < 1e-9:
                return 0.0 # Indeterminate/Flat
            return np.inf * np.sign(val_du_dx)
            
        return val_du_dx / val_du_dy
        
    except Exception as e:
        # Fallback or logging could happen here
        # print(f"SymPy Error in calculate_mrs: {e}")
        return None

def get_gradient(formula: str, x_val: float, y_val: float) -> Optional[np.ndarray]:
    """
    Calculates the gradient vector [dU/dx, dU/dy] symbolically.
    
    Returns:
        np.ndarray: The gradient vector.
        None: If symbolic calculation fails.
    """
    if not SYMPY_AVAILABLE:
        return None

    try:
        x, y = sympy.symbols('x y')
        
        cleaned_formula = clean_formula_for_sympy(formula)
        u = sympy.sympify(cleaned_formula)
        
        du_dx = sympy.diff(u, x)
        du_dy = sympy.diff(u, y)
        
        val_du_dx = float(du_dx.subs({x: x_val, y: y_val}))
        val_du_dy = float(du_dy.subs({x: x_val, y: y_val}))
        
        return np.array([val_du_dx, val_du_dy])
        
    except Exception as e:
        # print(f"SymPy Error in get_gradient: {e}")
        return None
