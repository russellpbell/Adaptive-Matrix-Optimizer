import pytest
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

def test_timeseriessplit_no_lookahead():
    """
    Verifies that TimeSeriesSplit ensures training indices are always less than test indices.
    """
    X = np.arange(100)
    tscv = TimeSeriesSplit(n_splits=5)
    
    for train_index, test_index in tscv.split(X):
        max_train = np.max(train_index)
        min_test = np.min(test_index)
        
        # Critical Check: Max Train Index must be < Min Test Index
        assert max_train < min_test, f"Look-ahead bias detected! Max Train: {max_train}, Min Test: {min_test}"
        
        # Also ensure no overlap
        intersection = np.intersect1d(train_index, test_index)
        assert len(intersection) == 0, f"Overlap detected between train and test: {intersection}"

if __name__ == "__main__":
    test_timeseriessplit_no_lookahead()
    print("Test Validated: No look-ahead bias found in TimeSeriesSplit.")
