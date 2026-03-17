import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import warnings
warnings.filterwarnings('ignore')

def load_and_preprocess_data(filepath):
    """Loads dataset and applies standard preprocessing steps for stroke prediction."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    print("Dropping 'id' column and handling missing values...")
    df = df.drop('id', axis=1)
    df['bmi'].fillna(df['bmi'].mean(), inplace=True)
    
    print("Encoding categorical variables...")
    label_encoders = {}
    categorical_cols = ['gender', 'ever_married', 'work_type', 'Residence_type', 'smoking_status']
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
        
    joblib.dump(label_encoders, '../models/label_encoders.pkl')
    
    X = df.drop('stroke', axis=1)
    y = df['stroke']
    
    return X, y, label_encoders

def train_model():
    """Trains a Random Forest model on the stroke dataset with SMOTE balancing."""
    X, y, _ = load_and_preprocess_data('../data/clinical_stroke_records_raw.csv')
    
    print("Applying SMOTE to balance the dataset...")
    smote = SMOTE(random_state=42)
    X_smote, y_smote = smote.fit_resample(X, y)
    
    print("Splitting dataset into training and testing sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X_smote, y_smote, test_size=0.2, random_state=42)
    
    print("Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    joblib.dump(scaler, '../models/scaler.pkl')
    
    print("Training Random Forest Classifier model...")
    rf_model = RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1)
    rf_model.fit(X_train_scaled, y_train)
    
    print("Saving the trained model pipeline...")
    joblib.dump(rf_model, '../models/stroke_model_v2.pkl')
    
    print("Evaluating initial performance...")
    predictions = rf_model.predict(X_test_scaled)
    print("\n--- Model Performance Report ---")
    print(f"Accuracy: {accuracy_score(y_test, predictions)*100:.2f}%")
    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, predictions))
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))
    
    print("\n✅ Training pipeline completed successfully.")

if __name__ == "__main__":
    train_model()
