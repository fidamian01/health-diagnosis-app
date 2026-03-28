import pickle
import numpy as np
import os

class HealthPredictor:
    def __init__(self, model_dir='models'):
        """Initialize the health predictor with trained models"""
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.features = {}
        
        # Load diabetes model
        self._load_model('diabetes')
        
        # Load malaria model
        self._load_model('malaria')
    
    def _load_model(self, disease):
        """Load a specific disease model"""
        try:
            model_path   = os.path.join(self.model_dir, f"{disease}_model.pkl")
            scaler_path  = os.path.join(self.model_dir, f"{disease}_scaler.pkl")
            features_path= os.path.join(self.model_dir, f"{disease}_features.pkl")
            with open(model_path,    'rb') as f: self.models[disease]   = pickle.load(f)
            with open(scaler_path,   'rb') as f: self.scalers[disease]  = pickle.load(f)
            with open(features_path, 'rb') as f: self.features[disease] = pickle.load(f)
            print(f"✅ {disease.capitalize()} model loaded successfully")
        except Exception as e:
            print(f"❌ Error loading {disease} model: {str(e)}")
    
    def predict_diabetes(self, symptoms):
        """
        Predict diabetes likelihood
        
        Expected symptoms dictionary:
        {
            'age': int,
            'bmi': float,
            'blood_pressure': int,
            'glucose': int,
            'insulin': float,
            'pregnancies': int,
            'skin_thickness': int,
            'diabetes_pedigree': float,
            'frequent_urination': int (0 or 1),
            'excessive_thirst': int (0 or 1),
            'unexplained_weight_loss': int (0 or 1),
            'fatigue': int (0 or 1),
            'blurred_vision': int (0 or 1),
            'slow_healing': int (0 or 1),
            'tingling_hands_feet': int (0 or 1)
        }
        """
        return self._predict('diabetes', symptoms)
    
    def predict_malaria(self, symptoms):
        """
        Predict malaria likelihood
        
        Expected symptoms dictionary:
        {
            'fever_days': int,
            'temperature': float,
            'chills': int (0 or 1),
            'sweating': int (0 or 1),
            'headache_severity': int (0-10),
            'nausea': int (0 or 1),
            'vomiting': int (0 or 1),
            'fatigue_level': int (0-10),
            'muscle_pain': int (0 or 1),
            'anemia_symptoms': int (0 or 1),
            'jaundice': int (0 or 1),
            'travel_to_endemic_area': int (0 or 1),
            'mosquito_exposure': int (0 or 1),
            'age': int,
            'cough': int (0 or 1)
        }
        """
        return self._predict('malaria', symptoms)
    
    def _predict(self, disease, symptoms):
        """Internal method to make predictions"""
        try:
            # Get the expected feature order
            expected_features = self.features[disease]
            
            # Create feature array in correct order
            feature_values = []
            for feature in expected_features:
                if feature not in symptoms:
                    raise ValueError(f"Missing feature: {feature}")
                feature_values.append(symptoms[feature])
            
            # Convert to numpy array and reshape
            X = np.array(feature_values).reshape(1, -1)
            
            # Scale the features
            X_scaled = self.scalers[disease].transform(X)
            
            # Make prediction
            prediction = self.models[disease].predict(X_scaled)[0]
            probability = self.models[disease].predict_proba(X_scaled)[0]
            
            # Get probability of positive class
            positive_probability = probability[1] * 100
            
            # Determine severity and recommendations
            severity, recommendations = self._get_recommendations(
                disease, positive_probability, symptoms
            )
            
            return {
                'disease': disease,
                'prediction': int(prediction),
                'probability': round(positive_probability, 2),
                'severity': severity,
                'recommendations': recommendations,
                'seek_medical_attention': severity in ['high', 'critical']
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'disease': disease
            }
    
    def _get_recommendations(self, disease, probability, symptoms):
        """Generate recommendations based on disease and probability"""
        
        if disease == 'diabetes':
            if probability < 30:
                severity = 'low'
                recommendations = [
                    "Your results look reassuring — keep up a healthy routine",
                    "Eat more vegetables, whole grains, and lean proteins, and cut back on sugary drinks and snacks",
                    "Aim for at least 30 minutes of walking or light exercise most days",
                    "Try to maintain a healthy body weight",
                    "Get a simple blood sugar check at your next routine doctor's visit",
                    "Avoid smoking, as it raises diabetes risk significantly"
                ]
            elif probability < 60:
                severity = 'moderate'
                recommendations = [
                    "Your results suggest some risk — it's worth seeing a doctor for a proper check-up",
                    "Ask your doctor for a blood sugar test (they will know which one to order)",
                    "Reduce sugary foods and drinks, white rice, white bread, and processed snacks",
                    "Try to be more active — even a 20-minute daily walk makes a real difference",
                    "If you are overweight, losing even 5–10% of your body weight can lower your risk significantly",
                    "A nutritionist or dietitian can help you build an eating plan that works for you"
                ]
            elif probability < 80:
                severity = 'high'
                recommendations = [
                    "Please see a doctor within the next day or two — don't put it off",
                    "Tell your doctor about this screening result and ask for a blood sugar test",
                    "Avoid sugary drinks, sweets, white bread, and fried foods until you've seen a doctor",
                    "Check your blood pressure if you can — high blood pressure often goes with high blood sugar",
                    "Write down any symptoms you have (e.g. unusual thirst, frequent trips to the toilet, tiredness) to share with your doctor",
                    "A doctor may recommend medication — take their advice seriously, it can prevent serious complications"
                ]
            else:
                severity = 'critical'
                recommendations = [
                    "🚨 Please go to a hospital or clinic today — do not wait",
                    "Show this result to the doctor and ask for an urgent blood sugar test",
                    "Warning signs to watch for right now: extreme thirst, confusion, rapid breathing, or fruity-smelling breath — if these occur, go to the emergency room immediately",
                    "Do not eat sugary or starchy foods until you have been seen",
                    "Bring someone with you to the appointment if possible",
                    "Diabetes is very treatable when caught — acting now protects your kidneys, eyes, and heart"
                ]
        
        elif disease == 'malaria':
            if probability < 30:
                severity = 'low'
                recommendations = [
                    "Monitor your symptoms for any changes",
                    "Stay hydrated and get adequate rest",
                    "Use mosquito repellent and bed nets",
                    "Maintain good hygiene",
                    "If fever persists for more than 2 days, consult a doctor",
                    "Take over-the-counter fever reducers if needed (consult pharmacist)"
                ]
            elif probability < 60:
                severity = 'moderate'
                recommendations = [
                    "Consult a healthcare provider for proper diagnosis",
                    "Request a malaria blood test (rapid diagnostic test or blood smear)",
                    "Stay well-hydrated",
                    "Get plenty of rest",
                    "Monitor your temperature regularly",
                    "Avoid mosquito exposure with nets and repellents",
                    "Keep track of symptom progression"
                ]
            elif probability < 80:
                severity = 'high'
                recommendations = [
                    "⚠️ Seek medical attention within 24 hours",
                    "Request immediate malaria testing",
                    "Get a complete blood count (CBC) test",
                    "Stay hydrated - drink plenty of fluids",
                    "Monitor for severe symptoms (confusion, difficulty breathing, seizures)",
                    "Antimalarial medication may be required - consult doctor",
                    "Inform doctor of any recent travel to malaria-endemic areas"
                ]
            else:
                severity = 'critical'
                recommendations = [
                    "🚨 SEEK EMERGENCY MEDICAL CARE IMMEDIATELY",
                    "Go to the nearest hospital emergency department",
                    "Severe malaria can be life-threatening",
                    "Request urgent malaria testing and treatment",
                    "Monitor for danger signs: severe headache, repeated vomiting, seizures, difficulty breathing",
                    "Intravenous antimalarial treatment may be needed",
                    "Do not delay - early treatment is crucial"
                ]
        
        return severity, recommendations

# Example usage
if __name__ == "__main__":
    predictor = HealthPredictor()
    
    # Test diabetes prediction
    print("\n" + "="*50)
    print("Testing Diabetes Prediction")
    print("="*50)
    
    diabetes_symptoms = {
        'age': 45,
        'bmi': 31.5,
        'blood_pressure': 130,
        'glucose': 150,
        'insulin': 120,
        'pregnancies': 2,
        'skin_thickness': 30,
        'diabetes_pedigree': 0.8,
        'frequent_urination': 1,
        'excessive_thirst': 1,
        'unexplained_weight_loss': 0,
        'fatigue': 1,
        'blurred_vision': 1,
        'slow_healing': 0,
        'tingling_hands_feet': 0
    }
    
    result = predictor.predict_diabetes(diabetes_symptoms)
    print(f"\nPrediction: {'Positive' if result['prediction'] == 1 else 'Negative'}")
    print(f"Probability: {result['probability']}%")
    print(f"Severity: {result['severity'].upper()}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")
    
    # Test malaria prediction
    print("\n" + "="*50)
    print("Testing Malaria Prediction")
    print("="*50)
    
    malaria_symptoms = {
        'fever_days': 3,
        'temperature': 39.5,
        'chills': 1,
        'sweating': 1,
        'headache_severity': 8,
        'nausea': 1,
        'vomiting': 0,
        'fatigue_level': 7,
        'muscle_pain': 1,
        'anemia_symptoms': 0,
        'jaundice': 0,
        'travel_to_endemic_area': 1,
        'mosquito_exposure': 1,
        'age': 35,
        'cough': 0
    }
    
    result = predictor.predict_malaria(malaria_symptoms)
    print(f"\nPrediction: {'Positive' if result['prediction'] == 1 else 'Negative'}")
    print(f"Probability: {result['probability']}%")
    print(f"Severity: {result['severity'].upper()}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"{i}. {rec}")
