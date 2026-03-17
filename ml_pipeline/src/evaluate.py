import pandas as pd
import joblib
import numpy as np

def predict_single_record(age, gender, hypertension, heart_disease, ever_married, work_type, residence, avg_glucose, bmi, smoking):
    """
    Simulates a prediction using the trained ML model pipeline.
    """
    print("Loading models and scalers...")
    try:
        model = joblib.load('../models/stroke_model_v2.pkl')
        scaler = joblib.load('../models/scaler.pkl')
        encoders = joblib.load('../models/label_encoders.pkl')
    except FileNotFoundError:
        print("⚠️ Warning: Model files not found. Are you sure you ran train.py first?")
        return
        
    print("Processing input data...")
    input_data = pd.DataFrame([{
        'gender': gender,
        'age': age,
        'hypertension': hypertension,
        'heart_disease': heart_disease,
        'ever_married': ever_married,
        'work_type': work_type,
        'Residence_type': residence,
        'avg_glucose_level': avg_glucose,
        'bmi': bmi,
        'smoking_status': smoking
    }])
    
    print("Applying saved label encoders...")
    for col in input_data.columns:
        if col in encoders:
            try:
                input_data[col] = encoders[col].transform(input_data[col])
            except ValueError:
                # Handle unseen labels by setting to 0 (simplification for dummy script)
                input_data[col] = 0 
                
    print("Scaling features...")
    scaled_data = scaler.transform(input_data)
    
    print("Running AI Inference...")
    prediction = model.predict(scaled_data)[0]
    probabilities = model.predict_proba(scaled_data)[0]
    
    risk_level = "High Risk" if prediction == 1 else "Low Risk"
    confidence = probabilities[prediction] * 100
    
    print("\n===============================")
    print("    PREDICTION RESULTS")
    print("===============================")
    print(f"Risk Assessment : {risk_level}")
    print(f"Confidence      : {confidence:.2f}%")
    print(f"Prob. [0, 1]    : [{probabilities[0]:.4f}, {probabilities[1]:.4f}]")
    print("===============================\n")

if __name__ == "__main__":
    # Test with a high-risk dummy profile
    print("Testing with sample high-risk profile (Elderly, smokes, high glucose):")
    predict_single_record(age=78, gender='Male', hypertension=1, heart_disease=1, 
                          ever_married='Yes', work_type='Private', residence='Urban', 
                          avg_glucose=210.5, bmi=32.4, smoking='smokes')
                          
    # Test with a low-risk dummy profile
    print("Testing with sample low-risk profile (Young, healthy):")
    predict_single_record(age=25, gender='Female', hypertension=0, heart_disease=0, 
                          ever_married='No', work_type='Private', residence='Urban', 
                          avg_glucose=85.2, bmi=22.1, smoking='never smoked')
