import numpy as np
import re
from typing import Optional, Tuple, Union, List

try:
    import giacpy
    from giacpy import giac
    GIAC_AVAILABLE = True
except ImportError:
    GIAC_AVAILABLE = False
    print("Warning: giacpy not found. Symbolic differentiation will be unavailable.")

def is_available() -> bool:
    """Check if XCas/Giac is available."""
    return GIAC_AVAILABLE

def clean_formula_for_giac(formula: str) -> str:
    """
    Preprocesses a formula string to be compatible with Giac.
    - Replaces numpy functions with standard math names.
    - Handles power operator replacement if necessary (Giac uses ^, Python uses **).
    - Ensures explicit multiplication where needed (though Giac is generally good at implicit).
    """
    if not formula:
        return "0"
    
    # Basic replacements
    expr = formula.lower()
    replacements = {
        "np.log": "ln", "np.exp": "exp", "np.sqrt": "sqrt",
        "np.minimum": "min", "np.maximum": "max",
        "log": "ln",
        "**": "^" # Ensure power syntax is correct for Giac
    }
    for py, g in replacements.items():
        expr = expr.replace(py, g)
        
    return expr

def calculate_mrs(formula: str, x_val: float, y_val: float) -> float:
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
    if not GIAC_AVAILABLE:
        return None

    try:
        # 1. Setup variables
        x = giac('x')
        y = giac('y')
        
        # 2. Parse formula
        cleaned_formula = clean_formula_for_giac(formula)
        u = giac(cleaned_formula)
        
        # 3. Differentiate
        du_dx = u.diff(x)
        du_dy = u.diff(y)
        
        # 4. Evaluate
        # subs syntax: expression.subs([var1, var2], [val1, val2])
        # Note: inputs to subs should be lists
        val_du_dx = float(du_dx.subs([x, y], [x_val, y_val]))
        val_du_dy = float(du_dy.subs([x, y], [x_val, y_val]))
        
        # 5. Calculate Ratio
        if abs(val_du_dy) < 1e-9:
            if abs(val_du_dx) < 1e-9:
                return 0.0 # Indeterminate/Flat
            return np.inf * np.sign(val_du_dx)
            
        return val_du_dx / val_du_dy
        
    except Exception as e:
        # Fallback or logging could happen here
        # print(f"XCas Error in calculate_mrs: {e}")
        return None

def get_gradient(formula: str, x_val: float, y_val: float) -> Optional[np.ndarray]:
    """
    Calculates the gradient vector [dU/dx, dU/dy] symbolically.
    
    Returns:
        np.ndarray: The gradient vector.
        None: If symbolic calculation fails.
    """
    if not GIAC_AVAILABLE:
        return None

    try:
        x = giac('x')
        y = giac('y')
        
        cleaned_formula = clean_formula_for_giac(formula)
        u = giac(cleaned_formula)
        
        du_dx = u.diff(x)
        du_dy = u.diff(y)
        
        val_du_dx = float(du_dx.subs([x, y], [x_val, y_val]))
        val_du_dy = float(du_dy.subs([x, y], [x_val, y_val]))
        
        return np.array([val_du_dx, val_du_dy])
        
    except Exception as e:
        # print(f"XCas Error in get_gradient: {e}")
        return None

