import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import api.core.xcas_engine

class TestXCasMRSSignedInf(unittest.TestCase):

    def setUp(self):
        # Ensure giac exists in the module so we can patch it
        if not hasattr(api.core.xcas_engine, 'giac'):
            api.core.xcas_engine.giac = None

    @patch('api.core.xcas_engine.GIAC_AVAILABLE', True)
    @patch('api.core.xcas_engine.giac')
    def test_mrs_negative_numerator_zero_denominator(self, mock_giac):
        from api.core.xcas_engine import calculate_mrs

        # Setup mock behavior to simulate dU/dx < 0 and dU/dy ~ 0
        
        mock_x = MagicMock()
        mock_y = MagicMock()
        mock_u = MagicMock()
        mock_du_dx = MagicMock()
        mock_du_dy = MagicMock()
        
        # giac('x'), giac('y'), giac(formula) calls
        mock_giac.side_effect = [mock_x, mock_y, mock_u]
        
        # u.diff(x) -> mock_du_dx
        # u.diff(y) -> mock_du_dy
        mock_u.diff.side_effect = [mock_du_dx, mock_du_dy]
        
        # subs return values
        mock_du_dx.subs.return_value = -5.0
        mock_du_dy.subs.return_value = 0.0
        
        # Call calculate_mrs
        mrs = calculate_mrs("some_formula", 1.0, 1.0)
        
        # We expect -np.inf because numerator is negative and denominator is zero
        self.assertEqual(mrs, -np.inf, f"Expected -inf but got {mrs}")

if __name__ == '__main__':
    unittest.main()
