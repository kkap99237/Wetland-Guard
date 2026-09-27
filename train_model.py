"""
train_model.py
Standalone, reproducible model training pipeline for Wetland Guard.
Executes:
1. Load processed real observations
2. Validate data
3. Engineer temporal features
4. Create retrospective weak labels
5. Chronological Train / Val / Test Split
6. Train Random Forest (200 trees, balanced weights)
7. Train Logistic Regression baseline
8. Evaluate both models and compute metrics
9. Save models, scaler, imputer, feature list, and metadata
10. Generate latest risk scores, reason codes, and priority rankings
11. Print concise report
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from src.preprocessing import load_observations, validate_observations
from src.temporal_features import engineer_all_temporal_features
from src.labels import create_retrospective_weak_labels, get_label_rationale_docs
from src.model import (
    prepare_features, chronological_split,
    train_random_forest, train_logistic_baseline,
    evaluate_model, predict_risk
)
from src.risk import compute_risk_score, categorize_risk, rank_wetlands_prioritization
from src.explanations import generate_reason_codes, compute_feature_importances
from src.utils import save_json


def main():
    print("=" * 60)
    print("WETLAND GUARD - MODEL TRAINING & EVALUATION PIPELINE")
    print("=" * 60)

    os.makedirs("models", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # 1. Load observations
    obs_path = "data/processed/wetland_observations.csv"
    print(f"Loading observations from: {obs_path}")
    df_raw = load_observations(obs_path)
    
    # 2. Validate data
    is_valid, warnings = validate_observations(df_raw)
    if warnings:
        for w in warnings:
            print(f"  [Validation Warning] {w}")

    # 3. Engineer temporal features
    print("Engineering temporal features (strictly backward-looking)...")
    df_feat = engineer_all_temporal_features(df_raw)

    # 4. Create retrospective weak labels
    print("Generating retrospective weak labels (multi-indicator decline)...")
    df_labeled = create_retrospective_weak_labels(df_feat)
    
    # 5. Chronological Split (70% train, 15% val, 15% test)
    print("Splitting datasets chronologically (70% Train / 15% Val / 15% Test)...")
    train_df, val_df, test_df = chronological_split(df_labeled, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)
    
    train_df.to_csv("outputs/training_data.csv", index=False)
    val_df.to_csv("outputs/validation_data.csv", index=False)
    test_df.to_csv("outputs/test_data.csv", index=False)
    print(f"  Train: {len(train_df)} rows ({train_df['date'].min().strftime('%Y-%m')} to {train_df['date'].max().strftime('%Y-%m')})")
    print(f"  Val:   {len(val_df)} rows ({val_df['date'].min().strftime('%Y-%m')} to {val_df['date'].max().strftime('%Y-%m')})")
    print(f"  Test:  {len(test_df)} rows ({test_df['date'].min().strftime('%Y-%m')} to {test_df['date'].max().strftime('%Y-%m')})")

    # Prepare features
    X_train, feature_cols = prepare_features(train_df)
    y_train = train_df["risk_event_label"].values
    
    X_val, _ = prepare_features(val_df)
    y_val = val_df["risk_event_label"].values
    
    X_test, _ = prepare_features(test_df)
    y_test = test_df["risk_event_label"].values

    # 6. Train Random Forest
    print("Training Random Forest Classifier (200 trees, class_weight='balanced')...")
    rf_model, imputer = train_random_forest(X_train, y_train, n_estimators=200, random_state=42)

    # 7. Train Logistic Regression baseline
    print("Training Logistic Regression Baseline...")
    lr_model, _, lr_scaler = train_logistic_baseline(X_train, y_train, random_state=42)

    # 8. Evaluate both
    print("Evaluating models on chronological test set...")
    rf_metrics = evaluate_model(rf_model, imputer, X_test, y_test)
    lr_metrics = evaluate_model(lr_model, imputer, X_test, y_test, scaler=lr_scaler)

    # 9. Save models and metadata
    joblib.dump({"model": rf_model, "imputer": imputer}, "models/wetland_model.pkl")
    joblib.dump({"model": lr_model, "imputer": imputer, "scaler": lr_scaler}, "models/logistic_baseline.pkl")
    
    with open("models/feature_columns.json", "w", encoding="utf-8") as f:
        json.dump(feature_cols, f, indent=2)

    # Feature importances
    imp_df = compute_feature_importances(rf_model, feature_cols)
    imp_df.to_csv("outputs/feature_importances.csv", index=False)

    metadata = {
        "model_name": "RandomForestClassifier",
        "n_estimators": 200,
        "class_weight": "balanced",
        "training_date": datetime.now().isoformat(),
        "n_features": len(feature_cols),
        "feature_columns": feature_cols,
        "n_wetlands": int(df_raw["wetland_id"].nunique()),
        "total_observations": len(df_labeled),
        "date_range": f"{df_raw['date'].min().strftime('%Y-%m-%d')} to {df_raw['date'].max().strftime('%Y-%m-%d')}",
        "train_samples": len(train_df),
        "val_samples": len(val_df),
        "test_samples": len(test_df),
        "random_forest_metrics": rf_metrics,
        "logistic_baseline_metrics": lr_metrics,
        "label_rationale": get_label_rationale_docs()
    }
    save_json(metadata, "models/model_metadata.json")
    save_json(metadata, "outputs/evaluation_report.json")

    # Save test predictions
    test_preds_df = test_df[["wetland_id", "wetland_name", "date", "risk_event_label"]].copy()
    test_preds_df["rf_risk_prob"] = predict_risk(rf_model, imputer, X_test)
    test_preds_df["rf_risk_score"] = compute_risk_score(test_preds_df["rf_risk_prob"])
    test_preds_df["rf_predicted_class"] = (test_preds_df["rf_risk_prob"] >= 0.5).astype(int)
    test_preds_df.to_csv("outputs/predictions.csv", index=False)

    # 10. Generate Latest Risk Scores, Reason Codes & Priority Ranking
    print("Generating latest priority rankings and evidence reason codes...")
    # Find latest observation per wetland
    latest_indices = df_labeled.groupby("wetland_id")["date"].idxmax()
    latest_df = df_labeled.loc[latest_indices].copy().reset_index(drop=True)
    
    X_latest, _ = prepare_features(latest_df)
    latest_probs = predict_risk(rf_model, imputer, X_latest)
    latest_df["risk_prob"] = latest_probs
    latest_df["risk_score"] = compute_risk_score(latest_probs)
    latest_df = rank_wetlands_prioritization(latest_df)

    # Generate reason codes
    all_reasons = []
    for idx, row in latest_df.iterrows():
        reasons = generate_reason_codes(row)
        all_reasons.append("; ".join(reasons))
    latest_df["evidence_reasons"] = all_reasons
    latest_df["top_reason"] = [r.split("; ")[0] if r else "Normal seasonal fluctuation" for r in all_reasons]

    export_cols = [
        "priority_rank", "wetland_id", "wetland_name", "latitude", "longitude",
        "area", "risk_score", "risk_category", "NDVI", "NDVI_trend",
        "MNDWI", "MNDWI_trend", "water_change", "SAR_change",
        "data_quality", "top_reason", "evidence_reasons", "date"
    ]
    latest_df[export_cols].to_csv("outputs/risk_scores.csv", index=False)
    print("Saved priority rankings to: outputs/risk_scores.csv")

    # 11. Print Concise Training Report
    print("\n" + "=" * 60)
    print("TRAINING REPORT")
    print("=" * 60)
    print("DATASET")
    print("-------")
    print(f"Wetlands:          {metadata['n_wetlands']}")
    print(f"Observations:      {metadata['total_observations']}")
    print(f"Date Range:        {metadata['date_range']}")
    print(f"Features:          {metadata['n_features']}")
    print()
    print("MODEL: Random Forest Classifier (n_estimators=200, class_weight='balanced')")
    print("-------------------------------------------------------------------------")
    print(f"Accuracy:          {rf_metrics['accuracy']:.4f}")
    print(f"Precision:         {rf_metrics['precision']:.4f}")
    print(f"Recall:            {rf_metrics['recall']:.4f}")
    print(f"F1-Score:          {rf_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:           {rf_metrics['roc_auc']:.4f}")
    print(f"Confusion Matrix:  {rf_metrics['confusion_matrix']}")
    print()
    print("BASELINE: Logistic Regression (class_weight='balanced')")
    print("-------------------------------------------------------")
    print(f"Accuracy:          {lr_metrics['accuracy']:.4f}")
    print(f"Precision:         {lr_metrics['precision']:.4f}")
    print(f"Recall:            {lr_metrics['recall']:.4f}")
    print(f"F1-Score:          {lr_metrics['f1_score']:.4f}")
    print(f"ROC-AUC:           {lr_metrics['roc_auc']:.4f}")
    print()
    print("TOP 5 PREDICTIVE FEATURES (Random Forest Importance):")
    for i, r in imp_df.head(5).iterrows():
        print(f"  {i+1}. {r['feature']:<24}: {r['importance']:.4f}")
    print()
    print("WARNING:")
    print("Labels are retrospective weak/derived labels based on multi-indicator heuristic rules.")
    print("Model evaluation reflects pattern recognition fidelity, NOT field-validated ground truth.")
    print("Wetland Guard is an early-warning screening tool for prioritising field investigation.")
    print("=" * 60)


if __name__ == '__main__':
    main()
