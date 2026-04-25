import os
import joblib
import pandas as pd
import numpy as np

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml', 'models'))

class MLService:
    def __init__(self):
        self.iso_model = None
        self.gb_model = None
        self.le = None
        self._load_models()

    def _load_models(self):
        try:
            self.iso_model = joblib.load(os.path.join(MODEL_DIR, "isolation_forest.joblib"))
            self.gb_model = joblib.load(os.path.join(MODEL_DIR, "gradient_boosting.joblib"))
            self.le = joblib.load(os.path.join(MODEL_DIR, "label_encoder.joblib"))
        except Exception as e:
            print(f"Warning: Models not loaded. Run ML pipeline first. Error: {e}")

    def score_event(self, features_dict: dict) -> float:
        if not self.iso_model or not self.gb_model:
            return features_dict.get('base_risk_score', 0.0) # Fallback

        # Convert to DataFrame
        df = pd.DataFrame([features_dict])
        
        # We need the exact features:
        # 'hour_of_day', 'is_weekend', 'event_type_encoded', 'resource_sensitivity_score',
        # 'session_file_count', 'failed_auth_count_last_1h', 'cross_dept_access_flag',
        # 'ip_changed_flag', 'cumulative_risk_last_24h', 'deviation_from_baseline'
        
        # Encode event type if not already
        if 'event_type' in df.columns and self.le:
            try:
                df['event_type_encoded'] = self.le.transform(df['event_type'])
            except:
                df['event_type_encoded'] = 0
                
        feature_cols = [
            'hour_of_day', 'is_weekend', 'event_type_encoded', 'resource_sensitivity_score',
            'session_file_count', 'failed_auth_count_last_1h', 'cross_dept_access_flag',
            'ip_changed_flag', 'cumulative_risk_last_24h', 'deviation_from_baseline'
        ]
        
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0.0
                
        X = df[feature_cols].values
        
        iso_scores = -self.iso_model.decision_function(X)
        # Normalize (rough estimate since we don't store min/max)
        iso_norm = np.clip((iso_scores + 0.15) / 0.3, 0, 1)[0]
        
        gb_prob = self.gb_model.predict_proba(X)[0][1]
        
        final_risk = 0.4 * iso_norm + 0.6 * gb_prob
        return float(final_risk * 100) # 0 to 100

ml_service = MLService()
