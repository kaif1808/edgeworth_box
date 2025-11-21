import sys
import os
import numpy as np

# Add the root directory to sys.path so we can import api
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.economics import solve_contract_curve, utility_func

def test_example_1_quasi_linear():
    """
    Problem 1:
    UA = x1A(x2A + 3) -> Quasi-Linear a=0, b=3
    UB = x1B(x2B + 2) -> Quasi-Linear a=0, b=2
    Total: 5, 10
    """
    print("Testing Example 1: Quasi-Linear...")
    total_x, total_y = 5.0, 10.0
    
    type_A = "Quasi-Linear (Shifted Product)"
    params_A = {"a": 0.0, "b": 3.0}
    
    type_B = "Quasi-Linear (Shifted Product)"
    params_B = {"a": 0.0, "b": 2.0}
    
    # Dummy endowment utilities (we just want the curve, not the core necessarily, 
    # but solve_contract_curve filters for core if we pass real u_w. 
    # Passing -inf allows us to see the full pareto set).
    pareto_x, pareto_y, _, _ = solve_contract_curve(
        total_x, total_y, 
        type_A, params_A, 
        type_B, params_B, 
        uA_w=-float('inf'), uB_w=-float('inf'), 
        Z_B_min=0, Z_B_max=utility_func(total_x, total_y, type_B, params_B)
    )
    
    # Check if we have points
    if not pareto_x:
        print("FAIL: No points found")
        return

    # Verify analytical solution for interior: x2A = 3x1A - 3
    # Valid for x1A in [1, 13/3] -> [1, 4.33]
    error_sum = 0
    count = 0
    print("  Debug Points (x, y, expected):")
    for x, y in zip(pareto_x, pareto_y):
        # Check interior logic
        if 1.0 < x < 4.33:
            expected_y = 3 * x - 3
            error_sum += abs(y - expected_y)
            count += 1
            if count <= 5:
                print(f"    ({x:.2f}, {y:.2f}) -> {expected_y:.2f} (Diff: {abs(y - expected_y):.2f})")
            
    if count > 0:
        avg_error = error_sum / count
        print(f"  Interior fit error: {avg_error:.4f}")
        if avg_error > 0.1:
            print("  FAIL: Interior points do not match analytical solution")
        else:
            print("  PASS: Interior points match")
    else:
        print("  WARN: No interior points found in analytical range")

    # Check corners (P2 and P3 from text)
    # P2: x1A in [0, 1), x2A = 0
    has_p2 = any(x < 1.0 and abs(y) < 0.1 for x, y in zip(pareto_x, pareto_y))
    # P3: x1A in (4.33, 5], x2A = 10
    has_p3 = any(x > 4.33 and abs(y - 10) < 0.1 for x, y in zip(pareto_x, pareto_y))
    
    print(f"  Has P2 (Bottom Edge): {has_p2}")
    print(f"  Has P3 (Top Edge): {has_p3}")
    
    if has_p2 and has_p3:
        print("  PASS: Corner segments detected")
    else:
        print("  FAIL: Missing corner segments")

def test_example_2_mixed_linear():
    """
    Problem 2:
    UA = x1A * (x2A)^3 -> Mixed Cobb-Douglas alpha=3
    UB = x1B + x2B -> Perfect Substitutes alpha=1, beta=1
    Total: 12, 12
    """
    print("\nTesting Example 2: Mixed CD vs Perfect Substitutes...")
    total_x, total_y = 12.0, 12.0
    
    type_A = "Mixed Cobb-Douglas"
    params_A = {"alpha": 3.0}
    
    type_B = "Perfect Substitutes"
    params_B = {"alpha": 1.0, "beta": 1.0}
    
    pareto_x, pareto_y, _, _ = solve_contract_curve(
        total_x, total_y, 
        type_A, params_A, 
        type_B, params_B, 
        uA_w=-float('inf'), uB_w=-float('inf'), 
        Z_B_min=0, Z_B_max=utility_func(total_x, total_y, type_B, params_B)
    )

    # Analytical:
    # Interior: x2A = 3x1A for x1A in (0, 4)
    # Edge: x1A > 4, x2A = 12
    
    error_sum = 0
    count = 0
    interior_points = 0
    edge_points = 0
    
    for x, y in zip(pareto_x, pareto_y):
        if 0.1 < x < 3.9:
            expected_y = 3 * x
            error_sum += abs(y - expected_y)
            count += 1
            interior_points += 1
        elif x > 4.1:
            if abs(y - 12.0) < 0.1:
                edge_points += 1
                
    if count > 0:
        print(f"  Interior fit error: {error_sum/count:.4f}")
    
    print(f"  Interior points: {interior_points}")
    print(f"  Edge points (Top): {edge_points}")
    
    if interior_points > 0 and edge_points > 0:
         print("  PASS: Found both interior and edge solutions")
    else:
         print("  FAIL: Missing parts of the contract curve")

def test_example_3_min_max():
    """
    Problem 3:
    UA = min(x1, x2)
    UB = max(x1, x2)
    Total: 10, 10 (Assumed symmetric for simplicity or use 6,6 from text if needed, but let's use 10,10)
    Text says "Total omega". Let's use 10.
    """
    print("\nTesting Example 3: Min vs Max Preferences...")
    total_x, total_y = 10.0, 10.0
    
    type_A = "Perfect Complements (Min)"
    params_A = {"alpha": 1.0, "beta": 1.0}
    
    type_B = "Max Preferences (Convex)"
    params_B = {"alpha": 1.0, "beta": 1.0}
    
    pareto_x, pareto_y, _, _ = solve_contract_curve(
        total_x, total_y, 
        type_A, params_A, 
        type_B, params_B, 
        uA_w=-float('inf'), uB_w=-float('inf'), 
        Z_B_min=0, Z_B_max=utility_func(total_x, total_y, type_B, params_B)
    )
    
    # Analytical: All allocations are Pareto efficient?
    # Text says: "All such allocations give B utility w-k... all allocations are Pareto-efficient"
    # Actually, wait.
    # "Consider the set of non-wasteful allocations that lie on agent A's indifference curve...
    # show that all such allocations provide B with the same level of utility...
    # Therefore, all allocations are Pareto-efficient."
    
    # If ALL allocations are Pareto efficient, the solver might return a scatter or a grid?
    # Our solver iterates through B's utility levels.
    # For a fixed Ub, it maximizes Ua.
    # If all points are efficient, then for a fixed Ub, there is a Ua max?
    # Actually if Ub is fixed at level L, Ua is also fixed at level (Total - L).
    # So any point on the indifference curve is a solution.
    # The solver minimizes -Ua subject to Ub >= Level.
    # It might just pick one point per level.
    
    print(f"  Points found: {len(pareto_x)}")
    if len(pareto_x) > 10:
        print("  PASS: Found ample points (thick set approximation)")
    else:
        print("  WARN: Few points found (might be expected if solver collapses degenerate solutions)")

def test_example_6_satiation():
    """
    Problem 6:
    UA = -(x1 - 3)^2 - (x2 - 3)^2 (Bliss point at 3,3)
    UB = x1 * x2
    Total: 10, 10
    """
    print("\nTesting Example 6: Satiation...")
    total_x, total_y = 10.0, 10.0
    
    type_A = "Satiation (Bliss Point)"
    params_A = {"a": 3.0, "b": 3.0}
    
    type_B = "Cobb-Douglas"
    params_B = {"alpha": 1.0, "beta": 1.0}
    
    pareto_x, pareto_y, _, _ = solve_contract_curve(
        total_x, total_y, 
        type_A, params_A, 
        type_B, params_B, 
        uA_w=-float('inf'), uB_w=-float('inf'), 
        Z_B_min=0, Z_B_max=utility_func(total_x, total_y, type_B, params_B)
    )
    
    # Analytical: x1A = x2A for x1A in [0, 3].
    # Points where x1A > 3 or x2A > 3 should NOT be in Pareto set (A is satiated, can give to B).
    
    bad_points = 0
    good_points = 0
    for x, y in zip(pareto_x, pareto_y):
        if x > 3.1 or y > 3.1:
            bad_points += 1
        else:
            if abs(x - y) < 0.2:
                good_points += 1
                
    print(f"  Good points (on diagonal <= 3): {good_points}")
    print(f"  Bad points (beyond bliss point): {bad_points}")
    
    if bad_points == 0 and good_points > 0:
        print("  PASS: Correctly clipped at bliss point")
    else:
        print("  FAIL: Included points beyond bliss point or found none")

if __name__ == "__main__":
    test_example_1_quasi_linear()
    test_example_2_mixed_linear()
    test_example_3_min_max()
    test_example_6_satiation()

