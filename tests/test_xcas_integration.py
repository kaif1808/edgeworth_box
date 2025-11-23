import unittest
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api.core.xcas_engine import calculate_mrs, get_gradient, is_available
from api.core.economics import get_computational_formula, utility_func

class TestXCasIntegration(unittest.TestCase):

    def setUp(self):
        self.available = is_available()
        if not self.available:
            print("Skipping XCas tests: giacpy not installed.")

    def test_availability(self):
        """Check if XCas is detected (informative only)."""
        if self.available:
            print("XCas/Giac is available.")
        else:
            print("XCas/Giac is NOT available.")

    def test_cobb_douglas_mrs(self):
        """Test Symbolic MRS for Cobb-Douglas u = x^0.5 * y^0.5"""
        if not self.available: return

        formula = "(x^0.5) * (y^0.5)"
        
        # Analytical MRS = (0.5/0.5) * (y/x) = y/x
        x, y = 2.0, 4.0
        expected_mrs = y / x # 2.0
        
        calculated = calculate_mrs(formula, x, y)
        self.assertAlmostEqual(calculated, expected_mrs, places=5)

    def test_cobb_douglas_gradient(self):
        """Test Symbolic Gradient for u = x^0.5 * y^0.5"""
        if not self.available: return

        formula = "(x^0.5) * (y^0.5)"
        x, y = 4.0, 9.0 # u = 2 * 3 = 6
        
        # du/dx = 0.5 * x^-0.5 * y^0.5 = 0.5 * (1/2) * 3 = 0.75
        # du/dy = 0.5 * x^0.5 * y^-0.5 = 0.5 * 2 * (1/3) = 0.3333...
        
        grad = get_gradient(formula, x, y)
        self.assertIsNotNone(grad)
        self.assertAlmostEqual(grad[0], 0.75, places=5)
        self.assertAlmostEqual(grad[1], 1.0/3.0, places=5)

    def test_perfect_substitutes_mrs(self):
        """Test Perfect Substitutes u = 2x + y"""
        if not self.available: return
        
        formula = "2*x + 1*y"
        # MRS = 2/1 = 2
        
        calculated = calculate_mrs(formula, 10, 10)
        self.assertAlmostEqual(calculated, 2.0, places=5)

    def test_formula_generator(self):
        """Test that get_computational_formula produces valid strings."""
        params = {'alpha': 0.3, 'beta': 0.7}
        f_cd = get_computational_formula("Cobb-Douglas", params)
        self.assertEqual(f_cd, "(x^0.3) * (y^0.7)")
        
        params_lin = {'alpha': 2, 'beta': 1}
        f_lin = get_computational_formula("Perfect Substitutes", params_lin)
        self.assertEqual(f_lin, "2*x + 1*y")

if __name__ == '__main__':
    unittest.main()

