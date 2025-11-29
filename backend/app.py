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
    "BMI",           
    "Diastolic",
    "Heart Rate"       
]

# Carregar modelo
try:
    import joblib
    modelo_path = os.path.join(os.path.dirname(__file__), "modelo_cardiaco_otimizado.pkl")
    
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
        corrected_pred = 1 - pred
        print(f"🔧 Correção de inversão: {pred} → {corrected_pred}")
        return [corrected_pred]
    
    def predict_proba(self, X):
        proba = self.modelo_original.predict_proba(X)[0]
        # 🔥 APENAS CORRIGINDO A INVERSÃO das probabilidades
        corrected_proba = np.array([[proba[1], proba[0]]])
        print(f"🔧 Correção de probabilidades: [{proba[0]:.3f}, {proba[1]:.3f}] → [{corrected_proba[0][0]:.3f}, {corrected_proba[0][1]:.3f}]")
        return corrected_proba

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
        "BMI": 0.92,
        "Diastolic": 0.9,
        "Heart Rate": 0.9
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
        "BMI": 0.28,
        "Diastolic": 0.2,
        "Heart Rate": 0.2
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

@app.route("/model-debug", methods=["GET"])
def model_debug():
    """Debug completo do modelo"""
    try:
        # Verificar features do modelo
        if hasattr(modelo_original, 'feature_names_in_'):
            features_reais = modelo_original.feature_names_in_.tolist()
        else:
            features_reais = "Não disponível - verificar joblib"
        
        # Verificar número de features esperadas
        if hasattr(modelo_original, 'n_features_in_'):
            n_features = modelo_original.n_features_in_
        else:
            n_features = "Não disponível"
            
        return jsonify({
            "modelo_features_reais": features_reais,
            "numero_features_esperadas": n_features,
            "features_que_estamos_enviando": FEATURE_ORDER_7,
            "dataset_original_features": [
                "Alcohol Consumption", "Obesity", "Diet_Healthy", "Medication Use",
                "Previous Heart Problems", "Sleep Hours Per Day", "Sex_Male", 
                "Family History", "Diabetes", "Stress Level", "Heart Rate", 
                "Diastolic", "Physical Activity Days Per Week", "Smoking", "BMI"
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/teste-inversao", methods=["GET"])
def teste_inversao():
    """Testar se realmente precisa da inversão"""
    
    # Caso de ALTO risco (deve prever 1)
    dados_alto = {
        "Cardio_Risk_Score": 0.9,
        "Medical_Risk": 0.95, 
        "Lifestyle_Risk": 0.85,
        "Sex_Male": 1,
        "BMI": 0.92,
        "Diastolic": 0.9,
        "Heart Rate": 0.9
    }
    
    # Caso de BAIXO risco (deve prever 0)  
    dados_baixo = {
        "Cardio_Risk_Score": 0.05,
        "Medical_Risk": 0.02,
        "Lifestyle_Risk": 0.08,
        "Sex_Male": 0, 
        "BMI": 0.28,
        "Diastolic": 0.2,
        "Heart Rate": 0.2
    }
    
    # Testar modelo ORIGINAL
    X_alto = np.array([prepare_features_for_model(dados_alto)])
    X_baixo = np.array([prepare_features_for_model(dados_baixo)])
    
    pred_original_alto = int(modelo_original.predict(X_alto)[0])
    pred_original_baixo = int(modelo_original.predict(X_baixo)[0])
    
    pred_corrigido_alto = int(modelo.predict(X_alto)[0])
    pred_corrigido_baixo = int(modelo.predict(X_baixo)[0])
    
    # Converter numpy.bool_ para bool nativo do Python
    original_correto = bool(pred_original_alto == 1 and pred_original_baixo == 0)
    corrigido_correto = bool(pred_corrigido_alto == 1 and pred_corrigido_baixo == 0)
    
    return jsonify({
        "modelo_original": {
            "alto_risco_pred": pred_original_alto,
            "baixo_risco_pred": pred_original_baixo,
            "esta_correto": original_correto
        },
        "modelo_corrigido": {
            "alto_risco_pred": pred_corrigido_alto, 
            "baixo_risco_pred": pred_corrigido_baixo,
            "esta_correto": corrigido_correto
        },
        "conclusao": "Modelo original ESTÁ CORRETO" if original_correto else "Modelo original ESTÁ INVERTIDO"
    })
    
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)