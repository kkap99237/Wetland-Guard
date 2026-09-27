"""
src/model.py
Machine Learning pipeline for Wetland Guard:
Random Forest Classifier and Logistic Regression Baseline.
Strict chronological splitting, zero future leakage, and joblib serialization.
"""
import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_auc_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "NDVI", "MNDWI", "EVI", "SAR_change", "water_change", "soil_moisture",
    "NDVI_trend", "MNDWI_trend", "EVI_trend", "water_trend",
    "NDVI_anomaly", "MNDWI_anomaly", "SAR_anomaly",
    "persistence_of_decline", "multi_indicator_decline"
]


def prepare_features(df):
    """
    Extracts strictly numerical feature matrix X.
    Wetland IDs, names, dates, and labels are NEVER included as model features.
    """
    available_cols = [c for c in FEATURE_COLUMNS if c in df.columns]
    X = df[available_cols].copy()
    for c in available_cols:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    return X, available_cols


def chronological_split(df, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15):
    """
    Splits time-series observations strictly chronologically.
    """
    df_sorted = df.sort_values("date").reset_index(drop=True)
    n = len(df_sorted)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))
    
    train_df = df_sorted.iloc[:train_end].copy()
    val_df = df_sorted.iloc[train_end:val_end].copy()
    test_df = df_sorted.iloc[val_end:].copy()
    
    return train_df, val_df, test_df


def train_random_forest(X_train, y_train, n_estimators=200, random_state=42):
    """Trains Random Forest with balanced class weights."""
    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(X_train)
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=8,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_imp, y_train)
    return model, imputer


def train_logistic_baseline(X_train, y_train, random_state=42):
    """Trains Logistic Regression baseline with balanced class weights."""
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    X_imp = imputer.fit_transform(X_train)
    X_scale = scaler.fit_transform(X_imp)
    
    model = LogisticRegression(
        class_weight="balanced",
        max_iter=1000,
        random_state=random_state
    )
    model.fit(X_scale, y_train)
    return model, imputer, scaler


def evaluate_model(model, imputer, X_test, y_test, scaler=None):
    """Evaluates model and returns metrics dictionary."""
    X_imp = imputer.transform(X_test)
    if scaler is not None:
        X_eval = scaler.transform(X_imp)
    else:
        X_eval = X_imp
        
    y_pred = model.predict(X_eval)
    y_prob = model.predict_proba(X_eval)[:, 1] if hasattr(model, "predict_proba") else y_pred
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    cm = confusion_matrix(y_test, y_pred).tolist()
    
    try:
        auc = roc_auc_score(y_test, y_prob)
    except Exception:
        auc = 0.5
        
    return {
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1_score": float(f1),
        "roc_auc": float(auc),
        "confusion_matrix": cm
    }


def predict_risk(model, imputer, X, scaler=None):
    """Predicts risk probabilities [0.0 to 1.0]."""
    X_imp = imputer.transform(X)
    if scaler is not None:
        X_eval = scaler.transform(X_imp)
    else:
        X_eval = X_imp
    probs = model.predict_proba(X_eval)[:, 1]
    return probs
