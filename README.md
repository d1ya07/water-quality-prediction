# 💧 Smart Water Quality Prediction
A machine learning project that predicts whether drinking water is safe or unsafe using 20 chemical and biological parameters.

## 🏆 Results
- **Best Model:** XGBoost
- **Accuracy:** 96.81%
- **AUC-ROC:** 0.9819

## 🔬 Features
- Trained 4 ML models (Logistic Regression, Random Forest, Gradient Boosting, XGBoost)
- Interactive Streamlit web app with dark mode
- Visual analytics: bar chart, radar chart
- Downloadable PDF report
- Chemical vs WHO safe limit comparison

## 🛠️ Tech Stack
Python · pandas · scikit-learn · XGBoost · Streamlit · Matplotlib · Seaborn

## 📊 Dataset
Water Quality Dataset — 7,999 samples, 20 features
Source: Kaggle (mssmartypants/water-quality)

## 🚀 How to Run
pip install -r requirements.txt
streamlit run streamlit_app.py
