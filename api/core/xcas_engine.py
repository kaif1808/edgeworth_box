import numpy as np
import re
from typing import Optional, Tuple, Union, List, Dict, Callable
from functools import lru_cache

try:
    import sympy
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("Warning: sympy not found. Symbolic differentiation will be unavailable.")

def is_available() -> bool:
    """Check if SymPy is available."""
    return SYMPY_AVAILABLE

# Cache for parsed expressions and lambdified functions
_expression_cache: Dict[str, sympy.Expr] = {}
_derivative_cache: Dict[str, Tuple[sympy.Expr, sympy.Expr]] = {}
_lambdified_cache: Dict[str, Callable] = {}
_gradient_lambdified_cache: Dict[str, Callable] = {}

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

def _get_or_parse_expression(formula: str) -> Optional[sympy.Expr]:
    """Get cached expression or parse and cache it."""
    if not SYMPY_AVAILABLE:
        return None
    
    if formula in _expression_cache:
        return _expression_cache[formula]
    
    try:
        cleaned_formula = clean_formula_for_sympy(formula)
        expr = sympy.sympify(cleaned_formula)
        _expression_cache[formula] = expr
        return expr
    except Exception:
        return None

def _get_or_compute_derivatives(formula: str) -> Optional[Tuple[sympy.Expr, sympy.Expr]]:
    """Get cached derivatives or compute and cache them."""
    if not SYMPY_AVAILABLE:
        return None
    
    if formula in _derivative_cache:
        return _derivative_cache[formula]
    
    expr = _get_or_parse_expression(formula)
    if expr is None:
        return None
    
    try:
        x, y = sympy.symbols('x y')
        du_dx = sympy.diff(expr, x)
        du_dy = sympy.diff(expr, y)
        _derivative_cache[formula] = (du_dx, du_dy)
        return (du_dx, du_dy)
    except Exception:
        return None

def _get_or_lambdify_mrs(formula: str) -> Optional[Callable]:
    """Get cached lambdified MRS function or create and cache it."""
    if not SYMPY_AVAILABLE:
        return None
    
    cache_key = f"mrs_{formula}"
    if cache_key in _lambdified_cache:
        return _lambdified_cache[cache_key]
    
    derivatives = _get_or_compute_derivatives(formula)
    if derivatives is None:
        return None
    
    du_dx, du_dy = derivatives
    
    try:
        x, y = sympy.symbols('x y')
        # Create MRS function: (du_dx) / (du_dy)
        # Use lambdify with numpy for fast evaluation
        mrs_func = sympy.lambdify([x, y], du_dx / du_dy, modules='numpy')
        _lambdified_cache[cache_key] = mrs_func
        return mrs_func
    except Exception:
        return None

def _get_or_lambdify_gradient(formula: str) -> Optional[Callable]:
    """Get cached lambdified gradient function or create and cache it."""
    if not SYMPY_AVAILABLE:
        return None
    
    cache_key = f"grad_{formula}"
    if cache_key in _gradient_lambdified_cache:
        return _gradient_lambdified_cache[cache_key]
    
    derivatives = _get_or_compute_derivatives(formula)
    if derivatives is None:
        return None
    
    du_dx, du_dy = derivatives
    
    try:
        x, y = sympy.symbols('x y')
        # Create gradient function: [du_dx, du_dy]
        grad_func = sympy.lambdify([x, y], [du_dx, du_dy], modules='numpy')
        _gradient_lambdified_cache[cache_key] = grad_func
        return grad_func
    except Exception:
        return None

def calculate_mrs(formula: str, x_val: float, y_val: float) -> Optional[float]:
    """
    Calculates the Marginal Rate of Substitution (MRS) using symbolic differentiation.
    MRS = (dU/dx) / (dU/dy)
    
    Uses cached lambdified functions for performance when available.
    
    Args:
        formula (str): The utility function formula.
        x_val (float): Quantity of good X.
        y_val (float): Quantity of good Y.
        
    Returns:
        float: The MRS at (x_val, y_val). Returns np.inf, -np.inf, np.nan, or 0.0 appropriately.
               Returns None if symbolic calculation fails.
    """
    if not SYMPY_AVAILABLE:
        return None

    # Try lambdified function first (fast path)
    mrs_func = _get_or_lambdify_mrs(formula)
    if mrs_func is not None:
        try:
            result = mrs_func(x_val, y_val)
            # Handle numpy array results
            if isinstance(result, np.ndarray):
                result = float(result.item())
            else:
                result = float(result)
            
            # Check for invalid values
            if np.isnan(result) or np.isinf(result):
                # Fall back to manual calculation for better error handling
                pass
            else:
                return result
        except (ZeroDivisionError, ValueError, TypeError):
            # Fall through to manual calculation
            pass

    # Fallback to manual calculation (more robust error handling)
    try:
        derivatives = _get_or_compute_derivatives(formula)
        if derivatives is None:
            return None
        
        du_dx, du_dy = derivatives
        x, y = sympy.symbols('x y')
        
        # Evaluate derivatives
        val_du_dx = float(du_dx.subs({x: x_val, y: y_val}))
        val_du_dy = float(du_dy.subs({x: x_val, y: y_val}))
        
        # Handle edge cases
        if abs(val_du_dy) < 1e-9:
            if abs(val_du_dx) < 1e-9:
                return 0.0  # Indeterminate/Flat
            return np.inf * np.sign(val_du_dx) if val_du_dx != 0 else np.nan
        
        result = val_du_dx / val_du_dy
        
        # Check for invalid results
        if np.isnan(result) or (np.isinf(result) and not np.isinf(val_du_dx)):
            return np.nan
            
        return result
        
    except Exception:
        return None

def get_gradient(formula: str, x_val: float, y_val: float) -> Optional[np.ndarray]:
    """
    Calculates the gradient vector [dU/dx, dU/dy] symbolically.
    
    Uses cached lambdified functions for performance when available.
    
    Returns:
        np.ndarray: The gradient vector.
        None: If symbolic calculation fails.
    """
    if not SYMPY_AVAILABLE:
        return None

    # Try lambdified function first (fast path)
    grad_func = _get_or_lambdify_gradient(formula)
    if grad_func is not None:
        try:
            result = grad_func(x_val, y_val)
            # Handle numpy array results
            if isinstance(result, (list, tuple)):
                result = np.array([float(r) for r in result])
            elif isinstance(result, np.ndarray):
                result = result.astype(float)
            else:
                result = np.array([float(result)])
            
            # Check for invalid values
            if np.any(np.isnan(result)) or np.any(np.isinf(result)):
                # Fall back to manual calculation
                pass
            else:
                return result
        except (ZeroDivisionError, ValueError, TypeError):
            # Fall through to manual calculation
            pass

    # Fallback to manual calculation
    try:
        derivatives = _get_or_compute_derivatives(formula)
        if derivatives is None:
            return None
        
        du_dx, du_dy = derivatives
        x, y = sympy.symbols('x y')
        
        val_du_dx = float(du_dx.subs({x: x_val, y: y_val}))
        val_du_dy = float(du_dy.subs({x: x_val, y: y_val}))
        
        result = np.array([val_du_dx, val_du_dy])
        
        # Check for invalid results
        if np.any(np.isnan(result)) or (np.any(np.isinf(result)) and not np.any(np.isinf([val_du_dx, val_du_dy]))):
            return None
            
        return result
        
    except Exception:
        return None
