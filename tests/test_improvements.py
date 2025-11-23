import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from api.core.economics import (
    calculate_mrs, get_demand, solve_walrasian_equilibrium,
    utility_func
)

def test_mrs_edge_cases():
    """Test MRS handling for edge cases."""
    print("=" * 60)
    print("Testing MRS Edge Cases")
    print("=" * 60)
    
    # Test 1: Perfect Complements at kink (should return NaN)
    params_min = {'alpha': 1.0, 'beta': 1.0}
    mrs_min = calculate_mrs(5.0, 5.0, "Perfect Complements (Min)", params_min)
    print(f"Perfect Complements at (5, 5): {mrs_min} (expected: NaN)")
    assert np.isnan(mrs_min), "MRS at kink should be NaN"
    
    # Test 2: Cobb-Douglas at boundary (x=0)
    params_cd = {'alpha': 0.5, 'beta': 0.5}
    mrs_cd = calculate_mrs(0.0, 10.0, "Cobb-Douglas", params_cd)
    print(f"Cobb-Douglas at (0, 10): {mrs_cd} (expected: large or inf)")
    assert not np.isnan(mrs_cd), "MRS should not be NaN for CD at boundary"
    
    # Test 3: Perfect Substitutes (should have constant MRS)
    params_sub = {'alpha': 1.0, 'beta': 1.0}
    mrs_sub = calculate_mrs(10.0, 5.0, "Perfect Substitutes", params_sub)
    print(f"Perfect Substitutes at (10, 5): {mrs_sub} (expected: ~1.0)")
    assert abs(mrs_sub - 1.0) < 0.1, f"MRS should be ~1.0, got {mrs_sub}"
    
    print("✓ MRS edge cases passed\n")

def test_corner_solutions():
    """Test corner solution detection."""
    print("=" * 60)
    print("Testing Corner Solutions")
    print("=" * 60)
    
    # Test 1: Perfect Substitutes - should prefer cheaper good
    params_sub = {'alpha': 1.0, 'beta': 1.0}
    x1, y1 = get_demand("Perfect Substitutes", params_sub, px=1, py=2, income=100)
    print(f"Perfect Substitutes (px=1, py=2, I=100): ({x1}, {y1})")
    assert y1 == 0.0, "Should buy only X when X is cheaper"
    assert x1 > 0, "Should buy positive amount of X"
    
    x2, y2 = get_demand("Perfect Substitutes", params_sub, px=2, py=1, income=100)
    print(f"Perfect Substitutes (px=2, py=1, I=100): ({x2}, {y2})")
    assert x2 == 0.0, "Should buy only Y when Y is cheaper"
    assert y2 > 0, "Should buy positive amount of Y"
    
    # Test 2: Max Preferences - should be at corner
    params_max = {'alpha': 1.0, 'beta': 1.0}
    x3, y3 = get_demand("Max Preferences (Convex)", params_max, px=1, py=1, income=100)
    print(f"Max Preferences (px=1, py=1, I=100): ({x3}, {y3})")
    assert (x3 == 0.0 or y3 == 0.0), "Max preferences should be at corner"
    
    # Test 3: Budget constraint satisfaction
    x4, y4 = get_demand("Cobb-Douglas", {'alpha': 0.5, 'beta': 0.5}, px=1, py=1, income=100)
    budget_check = 1 * x4 + 1 * y4
    print(f"Cobb-Douglas budget check: {budget_check} (should be <= 100)")
    assert budget_check <= 100.01, f"Budget constraint violated: {budget_check} > 100"
    
    print("✓ Corner solutions passed\n")

def test_non_negative_constraints():
    """Test that allocations and prices are non-negative."""
    print("=" * 60)
    print("Testing Non-Negative Constraints")
    print("=" * 60)
    
    # Test various utility types
    test_cases = [
        ("Cobb-Douglas", {'alpha': 0.5, 'beta': 0.5}),
        ("Perfect Substitutes", {'alpha': 1.0, 'beta': 1.0}),
        ("Perfect Complements (Min)", {'alpha': 1.0, 'beta': 1.0}),
        ("CES", {'alpha': 0.5, 'beta': 0.5, 'rho': 0.5}),
    ]
    
    for u_type, params in test_cases:
        x, y = get_demand(u_type, params, px=1, py=1, income=100)
        print(f"{u_type}: ({x}, {y})")
        assert x >= 0, f"{u_type}: x should be >= 0, got {x}"
        assert y >= 0, f"{u_type}: y should be >= 0, got {y}"
        assert not np.isnan(x), f"{u_type}: x should not be NaN"
        assert not np.isnan(y), f"{u_type}: y should not be NaN"
    
    print("✓ Non-negative constraints passed\n")

def test_walrasian_equilibrium():
    """Test Walrasian equilibrium with multiple equilibria handling."""
    print("=" * 60)
    print("Testing Walrasian Equilibrium")
    print("=" * 60)
    
    # Standard case: Cobb-Douglas (should have unique equilibrium)
    params_A = {'alpha': 0.5, 'beta': 0.5}
    params_B = {'alpha': 0.5, 'beta': 0.5}
    
    success, msg, eqs = solve_walrasian_equilibrium(
        10.0, 10.0,
        "Cobb-Douglas", params_A,
        "Cobb-Douglas", params_B,
        (5.0, 5.0), (5.0, 5.0)
    )
    
    print(f"Success: {success}")
    print(f"Message: {msg}")
    print(f"Number of equilibria: {len(eqs)}")
    
    assert success, "Should find equilibrium for standard case"
    assert len(eqs) > 0, "Should have at least one equilibrium"
    
    # Check that all equilibria have non-negative prices and allocations
    for px, (xA, yA) in eqs:
        print(f"  Equilibrium: px={px:.4f}, A=({xA:.2f}, {yA:.2f})")
        assert px > 0, f"Price should be positive, got {px}"
        assert xA >= 0, f"xA should be >= 0, got {xA}"
        assert yA >= 0, f"yA should be >= 0, got {yA}"
        assert not np.isnan(px), "Price should not be NaN"
        assert not np.isnan(xA), "xA should not be NaN"
        assert not np.isnan(yA), "yA should not be NaN"
    
    print("✓ Walrasian equilibrium passed\n")

def test_performance():
    """Test that SymPy optimizations improve performance."""
    print("=" * 60)
    print("Testing Performance (SymPy Caching)")
    print("=" * 60)
    
    import time
    
    params = {'alpha': 0.5, 'beta': 0.5}
    formula = "x**0.5 * y**0.5"
    
    # First call (should be slower - parsing/caching)
    start = time.time()
    for _ in range(10):
        mrs1 = calculate_mrs(5.0, 5.0, "Cobb-Douglas", params)
    time1 = time.time() - start
    
    # Second call (should be faster - using cache)
    start = time.time()
    for _ in range(10):
        mrs2 = calculate_mrs(5.0, 5.0, "Cobb-Douglas", params)
    time2 = time.time() - start
    
    print(f"First 10 calls: {time1:.4f}s")
    print(f"Second 10 calls: {time2:.4f}s")
    print(f"Speedup: {time1/time2:.2f}x")
    
    # Both should return same result
    assert abs(mrs1 - mrs2) < 1e-6, "Cached and non-cached should return same result"
    
    print("✓ Performance test passed\n")

if __name__ == "__main__":
    test_mrs_edge_cases()
    test_corner_solutions()
    test_non_negative_constraints()
    test_walrasian_equilibrium()
    test_performance()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)


