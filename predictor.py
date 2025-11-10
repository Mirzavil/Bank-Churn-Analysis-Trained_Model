import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
import time
import warnings
warnings.filterwarnings('ignore')

class ChurnPredictor:
    def __init__(self, model_path='churn_risk_model.pkl'):
        self.package = joblib.load(model_path)
        self.model = self.package['model']
        self.scaler = self.package['scaler']
        self.feature_names = self.package['feature_names']
        self.f1_threshold = self.package['f1_optimized_threshold']

    def get_customers(self):
        conn = sqlite3.connect('bank_sim.db')
        df = pd.read_sql_query("SELECT * FROM customers WHERE churned = 0", conn)
        conn.close()
        return df

    def engineer_features(self, df):
        df_fe = df.copy().drop(['id', 'name', 'churn_day', 'churned'], errors='ignore')
        df_fe['AgeGroup'] = pd.cut(df_fe['Age'], bins=[0, 30, 40, 50, 60, 100], labels=['18-30', '31-40', '41-50', '51-60', '60+'])
        df_fe['TenureGroup'] = pd.cut(df_fe['Tenure'], bins=[-1, 2, 5, 8, 11], labels=['0-2', '3-5', '6-8', '9-10'])
        df_fe['CreditScoreGroup'] = pd.cut(df_fe['CreditScore'], bins=[0, 600, 700, 850], labels=['Low', 'Medium', 'High'])
        df_fe['BalanceToSalaryRatio'] = df_fe['Balance'] / (df_fe['EstimatedSalary'] + 1)
        df_fe['ProductsPerYear'] = df_fe['NumOfProducts'] / (df_fe['Tenure'] + 1)
        df_fe['ActiveFewProducts'] = ((df_fe['IsActiveMember'] == 1) & (df_fe['NumOfProducts'] <= 1)).astype(int)
        balance_median = df_fe['Balance'].median()
        df_fe['HighBalanceInactive'] = ((df_fe['Balance'] > balance_median) & (df_fe['IsActiveMember'] == 0)).astype(int)
        return df_fe

    def preprocess_data(self, df_engineered):
        categorical_columns = ['Geography', 'Gender', 'AgeGroup', 'TenureGroup', 'CreditScoreGroup']
        X_encoded = pd.get_dummies(df_engineered, columns=categorical_columns, drop_first=True)
        for feature in self.feature_names:
            if feature not in X_encoded.columns:
                X_encoded[feature] = 0
        return X_encoded[self.feature_names]

    def predict_batch(self, customer_dataframe):
        X_batch = customer_dataframe[self.feature_names]
        X_batch_scaled = self.scaler.transform(X_batch.values)
        probabilities = self.model.predict_proba(X_batch_scaled)[:, 1]
        
        results = []
        for prob in probabilities:
            if prob < 0.3: risk_level, recommendation = "LOW RISK", "Monitor"
            elif prob < 0.6: risk_level, recommendation = "MEDIUM RISK", "Engage"  
            else: risk_level, recommendation = "HIGH RISK", "Immediate action"
            
            results.append({
                'churn_probability': round(prob, 4),
                'prediction': 1 if prob >= self.f1_threshold else 0,
                'risk_level': risk_level,
                'recommendation': recommendation
            })
        
        return pd.DataFrame(results)

    def predict_all_customers(self):
        df = self.get_customers()
        if df is None or len(df) == 0: return None
        
        df_engineered = self.engineer_features(df)
        X_processed = self.preprocess_data(df_engineered)
        batch_results = self.predict_batch(X_processed)
        
        return pd.concat([df.reset_index(drop=True), batch_results.reset_index(drop=True)], axis=1)

def real_time_monitoring():
    predictor = ChurnPredictor()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\nIteration {iteration} - {datetime.now().strftime('%H:%M:%S')}")
            
            results = predictor.predict_all_customers()
            if results is not None:
                risk_counts = results['risk_level'].value_counts()
                flagged_count = results['prediction'].sum()
                total = len(results)
                
                print(f"Customers: {total}, Churn predicted: {flagged_count} ({flagged_count/total*100:.1f}%)")
                print(f"Risk - High: {risk_counts.get('HIGH RISK', 0)}, Medium: {risk_counts.get('MEDIUM RISK', 0)}, Low: {risk_counts.get('LOW RISK', 0)}")
                
                high_risk = results[results['risk_level'] == 'HIGH RISK']
                if len(high_risk) > 0:
                    high_risk_sorted = high_risk.sort_values('churn_probability', ascending=False)
                    print("High risk:")
                    for _, customer in high_risk_sorted.iterrows():
                        print(f"  {customer['name']} - {customer['churn_probability']:.1%}")
            
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("Stopped")

def single_run():
    predictor = ChurnPredictor()
    results = predictor.predict_all_customers()
    
    if results is not None:
        risk_counts = results['risk_level'].value_counts()
        flagged_count = results['prediction'].sum()
        total = len(results)
        
        print(f"\nTotal customers: {total}")
        print(f"Predicted to churn: {flagged_count} ({flagged_count/total*100:.1f}%)")
        print(f"Risk - High: {risk_counts.get('HIGH RISK', 0)}, Medium: {risk_counts.get('MEDIUM RISK', 0)}, Low: {risk_counts.get('LOW RISK', 0)}")
        
        high_risk = results[results['risk_level'] == 'HIGH RISK']
        if len(high_risk) > 0:
            high_risk_sorted = high_risk.sort_values('churn_probability', ascending=False)
            print("\nHigh risk customers:")
            for _, customer in high_risk_sorted.iterrows():
                print(f"  {customer['name']} (ID: {customer['id']}) - {customer['churn_probability']:.1%}")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"churn_predictions_{timestamp}.csv"
        results.to_csv(output_file, index=False)
        print(f"\nSaved to: {output_file}")

if __name__ == "__main__":
    print("1. Real-time monitoring")
    print("2. Single run")
    choice = input("Choose (1 or 2): ").strip()
    
    if choice == "1":
        real_time_monitoring()
    else:
            single_run()