
import numpy as np
from api.core.economics import calculate_mrs, get_demand, solve_walrasian_equilibrium

def test_mrs_undefined():
    print("Testing MRS Undefined/Infinite...")
    # Case 1: Vertical indifference curve (Perfect Complements or similar at kink?)
    # Actually, let's try Cobb-Douglas at x=0. U = x^0.5 * y^0.5. MUx = 0.5 x^-0.5 y^0.5 = inf. MUy = ...
    # At x=0, y>0: MUx is inf, MUy is finite. MRS = inf.
    params = {'alpha': 0.5, 'beta': 0.5}
    mrs = calculate_mrs(0.0, 10.0, "Cobb-Douglas", params)
    print(f"MRS at (0, 10) for CD: {mrs}")

    # Case 2: Horizontal indifference curve (MUx=0)
    # MRS = 0/MUy = 0.
    
    # Case 3: Perfect Complements (Min(x,y))
    # At x=y, not differentiable.
    params_min = {'alpha': 1.0, 'beta': 1.0}
    mrs_min = calculate_mrs(5.0, 5.0, "Perfect Complements (Min)", params_min)
    print(f"MRS at (5, 5) for Min: {mrs_min}")

def test_corner_demand():
    print("\nTesting Corner Demand...")
    # Utility: Linear U = x + y (Perfect Substitutes)
    # Prices: px=1, py=2. MRS = 1. Price ratio = 0.5.
    # MRS > px/py (1 > 0.5). Should buy all X.
    params = {'alpha': 1.0, 'beta': 1.0}
    x, y = get_demand("Perfect Substitutes", params, px=1, py=2, income=100)
    print(f"Demand PerfSub (px=1, py=2, I=100): ({x}, {y})")
    
    # Utility: Concave? Or something that prefers corners.
    # Max Preferences: U = max(x, y)
    # Prices: px=1, py=1, I=100.
    # Should buy (100, 0) or (0, 100).
    params_max = {'alpha': 1.0, 'beta': 1.0}
    x_max, y_max = get_demand("Max Preferences (Convex)", params_max, px=1, py=1, income=100)
    print(f"Demand MaxPref (px=1, py=1, I=100): ({x_max}, {y_max})")

def test_walrasian_multiple():
    print("\nTesting Walrasian Multiple Equilibria...")
    # This is harder to construct synthetically without specific parameters known to cause it.
    # Usually happens with non-homothetic preferences or strong income effects (Giffen goods).
    # For now, just run a standard one to ensure no regression.
    params_A = {'alpha': 0.5, 'beta': 0.5} # CD
    params_B = {'alpha': 0.5, 'beta': 0.5} # CD
    # CD always has unique equilibrium.
    
    success, msg, eqs = solve_walrasian_equilibrium(
        10, 10, 
        "Cobb-Douglas", params_A, 
        "Cobb-Douglas", params_B, 
        (5, 5), (5, 5)
    )
    print(f"Walrasian Result: {success}, {len(eqs)} equilibria")

if __name__ == "__main__":
    test_mrs_undefined()
    test_corner_demand()
    test_walrasian_multiple()

