import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest, GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, recall_score, f1_score, classification_report, confusion_matrix
import joblib

# Ensure we can import from backend app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.database import SessionLocal
from app.models import ActivityLog, MLModel, UserBaseline

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def extract_features(df, baselines=None):
    if df.empty:
        return df

    # Basic time features
    df['hour_of_day'] = df['timestamp'].dt.hour
    df['is_weekend'] = df['timestamp'].dt.dayofweek >= 5

    # Event type encoding
    le = LabelEncoder()
    df['event_type_encoded'] = le.fit_transform(df['event_type'])

    # Resource sensitivity
    def score_resource(r):
        if not isinstance(r, str): return 0.0
        r = r.lower()
        if 'payroll' in r or 'sensitive' in r or 'admin' in r: return 1.0
        return 0.1
    df['resource_sensitivity_score'] = df['resource_accessed'].apply(score_resource)

    # Simple session counts (using hour window)
    df['hour_window'] = df['timestamp'].dt.floor('h')
    session_counts = df.groupby(['user_id', 'hour_window']).size().reset_index(name='session_file_count')
    df = pd.merge(df, session_counts, on=['user_id', 'hour_window'], how='left')

    # Failed auth counts
    failed_df = df[df['event_type'] == 'FAILED_AUTH']
    failed_counts = failed_df.groupby(['user_id', 'hour_window']).size().reset_index(name='failed_auth_count_last_1h')
    df = pd.merge(df, failed_counts, on=['user_id', 'hour_window'], how='left')
    df['failed_auth_count_last_1h'] = df['failed_auth_count_last_1h'].fillna(0)

    # Cross dept
    df['cross_dept_access_flag'] = df.apply(lambda x: 1 if ('/' in str(x['resource_accessed']) and str(x['resource_accessed']).split('/')[0] not in str(x['department']).lower()) else 0, axis=1)

    # IP Changed (simplified logic: count unique IPs per user in day)
    df['date'] = df['timestamp'].dt.date
    ip_counts = df.groupby(['user_id', 'date'])['ip_address'].nunique().reset_index(name='unique_ips_day')
    df = pd.merge(df, ip_counts, on=['user_id', 'date'], how='left')
    df['ip_changed_flag'] = (df['unique_ips_day'] > 1).astype(int)

    # Cumulative risk
    df['cumulative_risk_last_24h'] = df.groupby(['user_id', 'date'])['risk_score'].cumsum().fillna(0)

    # Deviation from baseline
    df['deviation_from_baseline'] = 0.0  # Placeholder, a real one would use the baselines dictionary

    # Fill NA
    df = df.fillna(0)

    feature_cols = [
        'hour_of_day', 'is_weekend', 'event_type_encoded', 'resource_sensitivity_score',
        'session_file_count', 'failed_auth_count_last_1h', 'cross_dept_access_flag',
        'ip_changed_flag', 'cumulative_risk_last_24h', 'deviation_from_baseline'
    ]

    return df, feature_cols, le

def train_models():
    db = SessionLocal()
    try:
        print("Fetching data from DB...")
        logs = db.query(
            ActivityLog.id,
            ActivityLog.user_id,
            ActivityLog.event_type,
            ActivityLog.resource_accessed,
            ActivityLog.ip_address,
            ActivityLog.timestamp,
            ActivityLog.risk_score,
            ActivityLog.is_anomalous
        ).all()

        if not logs:
            print("No logs found. Run seeder first.")
            return

        # Also get user departments to help with cross_dept feature
        users_query = db.query(ActivityLog.user_id, ActivityLog.user.has().label("has_user")) # Wait, just join Users
        sql = """
            SELECT a.id, a.user_id, a.event_type, a.resource_accessed, a.ip_address, a.timestamp, a.risk_score, a.is_anomalous, u.department
            FROM activity_logs a
            JOIN users u ON a.user_id = u.id
        """
        df = pd.read_sql(sql, db.bind)
        
        print(f"Loaded {len(df)} logs.")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        print("Extracting features...")
        df, feature_cols, le = extract_features(df)
        X = df[feature_cols].values
        y = df['is_anomalous'].astype(int).values

        print("Training IsolationForest...")
        iso_model = IsolationForest(contamination=0.02, n_estimators=200, random_state=42)
        iso_model.fit(X)
        iso_preds = iso_model.predict(X)
        # Convert 1 (normal), -1 (anomaly) to 0, 1
        iso_preds_binary = np.where(iso_preds == -1, 1, 0)
        iso_scores = -iso_model.decision_function(X) # higher is more anomalous
        # normalize
        iso_scores_norm = (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min())

        print("Training GradientBoostingClassifier...")
        # Supervised
        gb_model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, max_depth=4, random_state=42)
        gb_model.fit(X, y)
        gb_preds = gb_model.predict(X)
        gb_probs = gb_model.predict_proba(X)[:, 1]

        print("Evaluating final ensemble...")
        final_risk_scores = 0.4 * iso_scores_norm + 0.6 * gb_probs
        final_preds = (final_risk_scores > 0.5).astype(int)

        print("\nClassification Report (Ensemble):")
        print(classification_report(y, final_preds))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y, final_preds))
        
        acc = accuracy_score(y, final_preds)
        rec = recall_score(y, final_preds)
        f1 = f1_score(y, final_preds)
        print(f"Accuracy: {acc:.4f}, Recall: {rec:.4f}")

        print("Saving models...")
        joblib.dump(iso_model, os.path.join(MODEL_DIR, "isolation_forest.joblib"))
        joblib.dump(gb_model, os.path.join(MODEL_DIR, "gradient_boosting.joblib"))
        joblib.dump(le, os.path.join(MODEL_DIR, "label_encoder.joblib"))

        print("Saving metrics to DB...")
        # Clear old metrics
        db.query(MLModel).update({"is_active": False})
        
        model_record = MLModel(
            model_name="ensemble_if_gb",
            model_type="Ensemble",
            accuracy=acc,
            f1_score=f1,
            feature_columns=feature_cols,
            is_active=True,
            file_path=MODEL_DIR
        )
        db.add(model_record)
        db.commit()
        print("ML Models trained and saved successfully.")

    finally:
        db.close()

if __name__ == "__main__":
    train_models()
