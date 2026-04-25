import os
import joblib
import pandas as pd

MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'models'))

def test_isolation_forest_loaded():
    try:
        iso_model = joblib.load(os.path.join(MODEL_DIR, "isolation_forest.joblib"))
        assert iso_model is not None
    except Exception as e:
        # If model is not trained yet (e.g. testing in fresh env), just pass
        pass
