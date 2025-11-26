from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import os

app = Flask(__name__)
CORS(app)

# ORDEM DAS 7 FEATURES DO MODELO TREINADO
FEATURE_ORDER_7 = [
    "Cardio_Risk_Score",
    "Medical_Risk", 
    "Lifestyle_Risk",
    "Sex_Male",
    "Heart Rate",
    "BMI",
    "Diastolic"
]

# Carregar modelo
try:
    import joblib
    modelo_path = os.path.join(os.path.dirname(__file__), "heart_risk_predictor.pkl")
    
    if os.path.exists(modelo_path):
        modelo_original = joblib.load(modelo_path)
        print("✅ Modelo carregado com sucesso! (7 features)")
        print("🔧 APENAS CORREÇÃO DE INVERSÃO")
        
    else:
        raise FileNotFoundError("Arquivo do modelo não encontrado")
        
except Exception as e:
    print(f"❌ Erro ao carregar modelo: {e}")
    # Criar modelo dummy
    class DummyModel:
        def predict(self, X):
            return [0]
        def predict_proba(self, X):
            return np.array([[0.5, 0.5]])
    modelo_original = DummyModel()

# 🔥 APENAS CORREÇÃO DA INVERSÃO
class ModeloCorrigido:
    def __init__(self, modelo_original):
        self.modelo_original = modelo_original
        
    def predict(self, X):
        pred = self.modelo_original.predict(X)[0]
        # 🔥 APENAS CORRIGINDO A INVERSÃO: 1→0, 0→1
        return [1 - pred]
    
    def predict_proba(self, X):
        proba = self.modelo_original.predict_proba(X)[0]
        # 🔥 APENAS CORRIGINDO A INVERSÃO das probabilidades
        return np.array([[proba[1], proba[0]]])

# Instanciar modelo corrigido
modelo = ModeloCorrigido(modelo_original)

def prepare_features_for_model(dados):
    """Prepara as 7 features para o modelo a partir dos dados do frontend"""
    
    feature_values = []
    for feature in FEATURE_ORDER_7:
        if feature in dados:
            feature_values.append(float(dados[feature]))
        else:
            print(f"⚠️  Feature {feature} não encontrada, usando 0")
            feature_values.append(0.0)
    
    return feature_values

@app.route("/predict", methods=["POST"])
def predict():
    try:
        dados = request.get_json()
        print("📥 Dados recebidos:", dados)

        # Preparar as 7 features (já vem prontas do frontend)
        feature_values = prepare_features_for_model(dados)

        print(f"🎯 7 Features para o modelo:")
        for i, (feature, value) in enumerate(zip(FEATURE_ORDER_7, feature_values)):
            print(f"  {i+1:2d}. {feature}: {value:.6f}")

        X = np.array([feature_values])

        # 🔥 APENAS CORREÇÃO DA INVERSÃO
        pred = modelo.predict(X)[0]
        proba = modelo.predict_proba(X)[0]
        probability_high = float(proba[1])  # P(alto)
        probability_low = float(proba[0])   # P(baixo)

        print(f"🎯 Predição CORRIGIDA: {pred}")
        print(f"📈 Probabilidades CORRIGIDAS: Baixo={probability_low:.6f}, Alto={probability_high:.6f}")

        risk = "ALTO" if pred == 1 else "BAIXO"

        return jsonify({
            "risk": risk,
            "probability_high": probability_high,
            "probability_low": probability_low,
            "confidence": max(probability_high, probability_low)
        })

    except Exception as e:
        print("❌ ERRO NO BACKEND:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route("/model-info", methods=["GET"])
def model_info():
    """Endpoint para verificar informações do modelo"""
    return jsonify({
        "model_type": "XGBoost (7 features) - INVERSÃO CORRIGIDA",
        "features": FEATURE_ORDER_7,
        "features_count": len(FEATURE_ORDER_7),
        "correction_applied": "✅ APENAS correção de inversão",
        "status": "OPERACIONAL"
    })

@app.route("/teste-risco-alto", methods=["GET"])
def teste_risco_alto():
    """Endpoint de teste FIXO para risco alto usando as 7 features"""

    # Dados de paciente de ALTO risco (já nas 7 features)
    patient_data = {
        "Cardio_Risk_Score": 0.9,
        "Medical_Risk": 0.95,
        "Lifestyle_Risk": 0.85,
        "Sex_Male": 1,
        "Heart Rate": 0.9,
        "BMI": 0.92,
        "Diastolic": 0.9
    }

    # Preparar features
    feature_values = prepare_features_for_model(patient_data)

    print("🎯 TESTE RISCO ALTO - 7 Features:")
    for i, (feature, value) in enumerate(zip(FEATURE_ORDER_7, feature_values)):
        print(f"  {i+1:2d}. {feature}: {value:.6f}")

    X = np.array([feature_values])
    
    # 🔥 APENAS CORREÇÃO DA INVERSÃO
    pred = modelo.predict(X)[0]
    proba = modelo.predict_proba(X)[0]
    probability_high = float(proba[1])
    probability_low = float(proba[0])

    print("🎯 TESTE RISCO ALTO - Resultado CORRIGIDO:")
    print(f"Predição: {pred}")
    print(f"Probabilidade ALTO: {probability_high:.6f}")
    print(f"Probabilidade BAIXO: {probability_low:.6f}")

    risk_level = "ALTO" if pred == 1 else "BAIXO"

    return jsonify({
        "risk": risk_level,
        "probability_high": probability_high,
        "probability_low": probability_low,
        "message": f"TESTE FIXO - Resultado: {risk_level} risco",
        "expected": "ALTO",
        "features_used": {k: float(v) for k, v in zip(FEATURE_ORDER_7, feature_values)}
    })

@app.route("/teste-risco-baixo", methods=["GET"])
def teste_risco_baixo():
    """Endpoint de teste FIXO para risco baixo usando as 7 features"""

    # Dados de paciente de BAIXO risco (já nas 7 features)
    patient_data = {
        "Cardio_Risk_Score": 0.05,
        "Medical_Risk": 0.02,
        "Lifestyle_Risk": 0.08,
        "Sex_Male": 0,
        "Heart Rate": 0.3,
        "BMI": 0.28,
        "Diastolic": 0.2
    }

    # Preparar features
    feature_values = prepare_features_for_model(patient_data)

    print("🟢 TESTE RISCO BAIXO - 7 Features:")
    for i, (feature, value) in enumerate(zip(FEATURE_ORDER_7, feature_values)):
        print(f"  {i+1:2d}. {feature}: {value:.6f}")

    X = np.array([feature_values])
    
    # 🔥 APENAS CORREÇÃO DA INVERSÃO
    pred = modelo.predict(X)[0]
    proba = modelo.predict_proba(X)[0]
    probability_high = float(proba[1])
    probability_low = float(proba[0])

    print("🟢 TESTE RISCO BAIXO - Resultado CORRIGIDO:")
    print(f"Predição: {pred}")
    print(f"Probabilidade ALTO: {probability_high:.6f}")
    print(f"Probabilidade BAIXO: {probability_low:.6f}")

    risk_level = "ALTO" if pred == 1 else "BAIXO"

    return jsonify({
        "risk": risk_level,
        "probability_high": probability_high,
        "probability_low": probability_low,
        "message": f"TESTE FIXO - Resultado: {risk_level} risco",
        "expected": "BAIXO",
        "features_used": {k: float(v) for k, v in zip(FEATURE_ORDER_7, feature_values)}
    })

@app.route("/debug-predict", methods=["POST"])
def debug_predict():
    """Endpoint para debug detalhado"""
    try:
        dados = request.get_json()
        print("🔍 DEBUG - Dados recebidos:", dados)
        
        # Verificar se todas as 7 features estão presentes
        features_faltantes = [f for f in FEATURE_ORDER_7 if f not in dados]
        if features_faltantes:
            print(f"❌ Features faltantes: {features_faltantes}")
            return jsonify({"error": f"Features faltantes: {features_faltantes}"}), 400
        
        # Preparar dados para predição
        feature_values = [dados[f] for f in FEATURE_ORDER_7]
        X = np.array([feature_values])
        
        print("🎯 DEBUG - Features para modelo:")
        for i, (feature, value) in enumerate(zip(FEATURE_ORDER_7, feature_values)):
            print(f"  {i+1:2d}. {feature}: {value:.6f}")
        
        # 🔥 COMPARANDO AMBOS
        print("\n🔧 TESTANDO MODELO ORIGINAL:")
        pred_original = modelo_original.predict(X)[0]
        proba_original = modelo_original.predict_proba(X)[0]
        print(f"   Predição original: {pred_original}")
        print(f"   Probabilidade original: {proba_original}")
        
        print("\n🔧 TESTANDO MODELO CORRIGIDO:")
        pred_corrigido = modelo.predict(X)[0]
        proba_corrigido = modelo.predict_proba(X)[0]
        print(f"   Predição corrigida: {pred_corrigido}")
        print(f"   Probabilidade corrigida: {proba_corrigido}")
        
        # Usar modelo corrigido
        probability_high = float(proba_corrigido[1])
        probability_low = float(proba_corrigido[0])
        risk = "ALTO" if pred_corrigido == 1 else "BAIXO"
        
        print(f"\n🎯 RESULTADO FINAL: {risk}")
        print(f"   P(ALTO): {probability_high:.6f}")
        print(f"   P(BAIXO): {probability_low:.6f}")
        
        return jsonify({
            "risk": risk,
            "probability_high": probability_high,
            "probability_low": probability_low,
            "confidence": max(probability_high, probability_low),
            "debug": {
                "prediction_original": int(pred_original),
                "prediction_corrected": int(pred_corrigido),
                "features_used": {k: float(v) for k, v in zip(FEATURE_ORDER_7, feature_values)}
            }
        })
        
    except Exception as e:
        print("❌ ERRO NO DEBUG:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)