from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import joblib
import numpy as np
import os

app = Flask(__name__)

# CONFIGURAÇÃO CORS MAIS PERMISSIVA
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Ou ainda mais simples - PERMITE TUDO
# CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"])

# Carregar modelo
modelo_path = os.path.join(os.path.dirname(__file__), "lr_top15.pkl")
modelo = joblib.load(modelo_path)

@app.route("/predict", methods=["POST", "OPTIONS"])
@cross_origin()  # Decorator adicional
def predict():
    # Se for OPTIONS (preflight), retorna OK
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200
    
    dados = request.get_json()
    print("Dados recebidos:", dados)  # Debug

    # SEU CÓDIGO DE PREDICTION AQUI
    sex_male = 1 if dados.get("Sex") == "Masculino" else 0
    obesity = 1 if float(dados.get("BMI", 0)) >= 30 else 0
    diet_healthy = 0

    X = np.array([[
        dados.get("Alcohol Consumption", 0),
        dados.get("Family History", 0),
        dados.get("Medication Use", 0),
        obesity,
        dados.get("Sleep Hours Per Day", 0),
        dados.get("Previous Heart Problems", 0),
        sex_male,
        diet_healthy,
        dados.get("Diabetes", 0),
        dados.get("Stress Level", 0),
        dados.get("Smoking", 0),
        dados.get("Diastolic", 0),
        dados.get("Physical Activity Days Per Week", 0),
        dados.get("BMI", 0),
        dados.get("Systolic", 0)
    ]])

    try:
        pred = modelo.predict(X)[0]
        risk = "ALTO" if pred == 1 else "BAIXO"
        return jsonify({"risk": risk})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)