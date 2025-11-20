import sys
import os
import numpy as np
from simpleeval import simple_eval
import re

# Copying functions from api/core/economics.py to test them in isolation
def parse_latex_to_numpy(latex_str):
    if not latex_str: return "0"
    expr = latex_str.lower().replace("^", "**").replace(r"\cdot", "*")
    replacements = {
        r"\\ln": "np.log", r"\\log": "np.log", r"\\exp": "np.exp",
        r"\\sqrt": "np.sqrt", r"\\min": "np.minimum", r"\\max": "np.maximum",
        r"min": "np.minimum", r"max": "np.maximum",
    }
    for tex, py in replacements.items(): expr = re.sub(tex, py, expr)
    expr = expr.replace("{", "(").replace("}", ")")
    expr = re.sub(r'(\d)([xy])', r'\1*\2', expr)
    return expr

def evaluate_custom_utility(x, y, formula):
    try:
        parsed_formula = parse_latex_to_numpy(formula)
        print(f"Original: {formula}")
        print(f"Parsed:   {parsed_formula}")
        
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
        names = {'x': x, 'y': y}
        return simple_eval(parsed_formula, names=names, functions=functions)
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test Cases
print("--- Testing Custom Functions ---")
test_cases = [
    "x^0.5 * y^0.5",
    "\\ln(x) + \\ln(y)",
    "min(x, y)",
    "2x + 3y",  # Implicit multiplication
    "x^{0.5}y^{0.5}", # LaTeX style powers
    "\\sqrt{x*y}"
]

x_val = 10.0
y_val = 10.0

for case in test_cases:
    result = evaluate_custom_utility(x_val, y_val, case)
    print(f"Result ({x_val}, {y_val}): {result}\n")