import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

class DriftDetector:
    def __init__(self, alpha=0.05):
        """
        Initializes DriftDetector.
        Args:
            alpha (float): Significance level for KS test.
        """
        self.alpha = alpha

    def detect_drift(self, reference_data, current_data):
        """
        Detects data drift between reference (training) and current (inference) data using KS test.
        
        Args:
            reference_data (pd.DataFrame): Training data baseline.
            current_data (pd.DataFrame): New data to check.
            
        Returns:
            pd.DataFrame: Drift report containing p-values and status.
        """
        report = []
        
        # Identify common numeric columns
        ref_numeric = reference_data.select_dtypes(include=[np.number])
        cur_numeric = current_data.select_dtypes(include=[np.number])
        
        common_cols = [c for c in ref_numeric.columns if c in cur_numeric.columns]
        
        for col in common_cols:
            ref_series = ref_numeric[col].dropna()
            cur_series = cur_numeric[col].dropna()
            
            if len(ref_series) == 0 or len(cur_series) == 0:
                continue
                
            # KS Test
            stat, p_value = ks_2samp(ref_series, cur_series)
            
            drift_detected = p_value < self.alpha
            
            report.append({
                'Feature': col,
                'KS_Statistic': stat,
                'P_Value': p_value,
                'Drift_Detected': drift_detected
            })
            
        return pd.DataFrame(report)

if __name__ == "__main__":
    # Simple test
    print("Testing DriftDetector...")
    np.random.seed(42)
    df_ref = pd.DataFrame({'val': np.random.normal(0, 1, 1000)})
    df_cur_ok = pd.DataFrame({'val': np.random.normal(0, 1, 1000)})
    df_cur_drift = pd.DataFrame({'val': np.random.normal(1, 1, 1000)}) # Shifted mean
    
    detector = DriftDetector()
    print("\n--- No Drift Case ---")
    print(detector.detect_drift(df_ref, df_cur_ok))
    
    print("\n--- Drift Case ---")
    print(detector.detect_drift(df_ref, df_cur_drift))
