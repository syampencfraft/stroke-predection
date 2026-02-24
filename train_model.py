import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, BaggingClassifier
from sklearn.metrics import accuracy_score, classification_report
from imblearn.over_sampling import SMOTE
import joblib
import os

# Create data directory if not exists
if not os.path.exists('data'):
    os.makedirs('data')

def generate_synthetic_data(n_samples=5000):
    print("Generating synthetic stroke dataset...")
    np.random.seed(42)
    
    data = {
        'id': np.arange(n_samples),
        'gender': np.random.choice(['Male', 'Female', 'Other'], n_samples),
        'age': np.random.uniform(1, 90, n_samples),
        'hypertension': np.random.choice([0, 1], n_samples, p=[0.9, 0.1]),
        'heart_disease': np.random.choice([0, 1], n_samples, p=[0.95, 0.05]),
        'ever_married': np.random.choice(['Yes', 'No'], n_samples),
        'work_type': np.random.choice(['Private', 'Self-employed', 'Govt_job', 'children', 'Never_worked'], n_samples),
        'Residence_type': np.random.choice(['Urban', 'Rural'], n_samples),
        'avg_glucose_level': np.random.uniform(50, 280, n_samples),
        'bmi': np.random.uniform(15, 60, n_samples),
        'smoking_status': np.random.choice(['formerly smoked', 'never smoked', 'smokes', 'Unknown'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Introduce correlation to target 'stroke'
    # Simplified logic: higher age, glucose, hypertension, heart_disease -> higher probability
    prob = (df['age'] / 100 * 0.4) + (df['avg_glucose_level'] / 300 * 0.3) + (df['hypertension'] * 0.2) + (df['heart_disease'] * 0.3)
    # Add some noise
    prob += np.random.normal(0, 0.1, n_samples)
    df['stroke'] = (prob > 0.6).astype(int)
    
    df.to_csv('data/stroke_data.csv', index=False)
    print("Dataset saved to data/stroke_data.csv")
    return df

def train_models():
    # Load data
    if not os.path.exists('data/stroke_data.csv'):
        df = generate_synthetic_data()
    else:
        df = pd.read_csv('data/stroke_data.csv')

    print("Preprocessing data...")
    # Handling missing values (though synthetic data doesn't have them, real data might)
    df['bmi'] = df['bmi'].fillna(df['bmi'].mean())

    # Encoding
    le_dict = {}
    categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        le_dict[col] = le

    # Features and Target
    X = df.drop(['id', 'stroke'], axis=1)
    y = df['stroke']

    # SMOTE for balancing
    print("Applying SMOTE for data balancing...")
    smote = SMOTE(random_state=42)
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 1. Random Forest
    print("Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train_scaled, y_train)
    rf_preds = rf_model.predict(X_test_scaled)
    print(f"Random Forest Accuracy: {accuracy_score(y_test, rf_preds):.4f}")

    # 2. Bagging Classifier
    print("Training Bagging Classifier...")
    bag_model = BaggingClassifier(random_state=42)
    bag_model.fit(X_train_scaled, y_train)
    bag_preds = bag_model.predict(X_test_scaled)
    print(f"Bagging Accuracy: {accuracy_score(y_test, bag_preds):.4f}")

    # Model Evaluation (for reporting)
    model_results = {
        'Random Forest': accuracy_score(y_test, rf_preds),
        'Bagging': accuracy_score(y_test, bag_preds)
    }
    
    # Save the best model
    best_model_name = max(model_results, key=model_results.get)
    print(f"Best Model: {best_model_name}")
    
    if best_model_name == 'Random Forest':
        best_model = rf_model
    else:
        best_model = bag_model

    # Save components for Django
    print("Saving models and preprocessing components...")
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'le_dict': le_dict,
        'feature_names': X.columns.tolist()
    }
    joblib.dump(model_data, 'data/best_stroke_model.pkl')
    print("All components saved to data/best_stroke_model.pkl")

if __name__ == "__main__":
    train_models()
