// ========================
// Variáveis Globais
// ========================
let formData = {};
let currentStep = 1;
const totalSteps = 4;

const stepTitles = [
  "1. Seu Perfil e Histórico",
  "2. Suas Medidas de Saúde",
  "3. Seu Estilo de Vida",
  "4. Seus Hábitos Diários"
];

// ========================
// Inicialização
// ========================
document.addEventListener("DOMContentLoaded", () => {
  updateView(1);

  const stressSlider = document.getElementById("stress-level");
  if (stressSlider) {
    document.getElementById("stressValue").innerText = stressSlider.value;

    stressSlider.addEventListener("input", () => {
      document.getElementById("stressValue").innerText = stressSlider.value;
    });
  }
});

// ========================
// Alternar etapas do form
// ========================
function updateView(stepNumber) {
  document.querySelectorAll(".step").forEach((step) => {
    step.style.display = "none";
    step.classList.remove("active");
  });

  const nextStep = document.getElementById(`step-${stepNumber}`);

  if (!nextStep) {
    console.error(`Step ${stepNumber} não existe.`);
    return;
  }

  nextStep.style.display = "block";
  nextStep.classList.add("active");

  const percentage = ((stepNumber - 1) / totalSteps) * 100;
  document.querySelector(".progress-bar").style.width = percentage + "%";
  document.querySelector(".progress-text").innerText = stepTitles[stepNumber - 1];

  currentStep = stepNumber;

  const finalBtn = document.querySelector(".final-submit");
  finalBtn.style.display = stepNumber === totalSteps ? "inline-block" : "none";
}

// ========================
// Coleta dos dados por etapa
// ========================
function collectStepData(stepNumber) {
  const step = document.getElementById(`step-${stepNumber}`);
  const inputs = step.querySelectorAll("input, select");
  const data = {};

  inputs.forEach((input) => {
    const name = input.name;
    if (!name) return;

    if (input.type === "radio") {
      if (input.checked) data[name] = input.value;
      return;
    }

    if (input.type === "checkbox") {
      data[name] = input.checked ? 1 : 0;
      return;
    }

    if (!isNaN(input.value) && input.value.trim() !== "") {
      data[name] = parseFloat(input.value);
    } else {
      data[name] = input.value;
    }
  });

  return data;
}

// ========================
// Validação
// ========================
function validateStepData(data, stepNumber) {
  const step = document.getElementById(`step-${stepNumber}`);
  let valid = true;

  step.querySelectorAll("[required]").forEach((input) => {
    if (input.type === "radio") {
      const group = input.name;
      if (!step.querySelector(`input[name="${group}"]:checked`)) valid = false;
    } else if (input.type === "select-one") {
      if (input.value === "" || input.selectedIndex === 0) valid = false;
    } else if (input.value.trim() === "") {
      valid = false;
    }
  });

  if (!valid) alert("Por favor, preencha todos os campos obrigatórios.");
  return valid;
}

// ========================
// Controles: avançar / voltar
// ========================
function handleStepSubmission(stepNumber, proceed = true) {
  if (proceed) {
    const data = collectStepData(stepNumber);
    if (!validateStepData(data, stepNumber)) return;

    Object.assign(formData, data);
    updateView(stepNumber + 1);
  } else {
    if (stepNumber > 1) updateView(stepNumber - 1);
  }
}

// ========================
// 🔥 NORMALIZAÇÃO
// ========================
function normalizarValor(valor, min, max) {
  valor = parseFloat(valor);
  return Math.max(0, Math.min(1, (valor - min) / (max - min)));
}

function normalizarDadosFormulario(dados) {
  const normalizados = {};

  if (dados["Alcohol Consumption"] !== undefined)
    normalizados["Alcohol Consumption"] = normalizarValor(dados["Alcohol Consumption"], 0, 10);

  if (dados["BMI"] !== undefined)
    normalizados["BMI"] = normalizarValor(dados["BMI"], 15, 40);

  if (dados["Diabetes"] !== undefined)
    normalizados["Diabetes"] = parseInt(dados["Diabetes"]);

  if (dados["Diastolic"] !== undefined)
    normalizados["Diastolic"] = normalizarValor(dados["Diastolic"], 40, 120);

  if (dados["Heart Rate"] !== undefined)
    normalizados["Heart Rate"] = normalizarValor(dados["Heart Rate"], 40, 180);

  if (dados["Diet_Healthy"] !== undefined)
    normalizados["Diet_Healthy"] = parseFloat(dados["Diet_Healthy"]);

  if (dados["Family History"] !== undefined)
    normalizados["Family History"] = parseInt(dados["Family History"]);

  if (dados["Medication Use"] !== undefined)
    normalizados["Medication Use"] = parseInt(dados["Medication Use"]);

  if (dados["Obesity"] !== undefined)
    normalizados["Obesity"] = parseInt(dados["Obesity"]);

  if (dados["Physical Activity Days Per Week"] !== undefined)
    normalizados["Physical Activity Days Per Week"] = normalizarValor(dados["Physical Activity Days Per Week"], 0, 7);

  if (dados["Previous Heart Problems"] !== undefined)
    normalizados["Previous Heart Problems"] = parseInt(dados["Previous Heart Problems"]);

  if (dados["Sex_Male"] !== undefined)
    normalizados["Sex_Male"] = parseInt(dados["Sex_Male"]);

  if (dados["Sleep Hours Per Day"] !== undefined)
    normalizados["Sleep Hours Per Day"] = normalizarValor(dados["Sleep Hours Per Day"], 0, 24);

  if (dados["Smoking"] !== undefined)
    normalizados["Smoking"] = parseInt(dados["Smoking"]);

  if (dados["Stress Level"] !== undefined)
    normalizados["Stress Level"] = normalizarValor(dados["Stress Level"], 0, 10);

  return normalizados;
}

// ========================
// 🔥 CÁLCULO DAS 8 FEATURES (SEM SYSTOLIC)
// ========================
function calcularFeaturesCompostas(dados) {
  console.log("📊 Dados recebidos:", dados);

  const obesity = parseFloat(dados.Obesity) || 0;
  const smoking = parseFloat(dados.Smoking) || 0;
  const alcohol = parseFloat(dados["Alcohol Consumption"]) || 0;
  const diabetes = parseFloat(dados.Diabetes) || 0;
  const heartProblems = parseFloat(dados["Previous Heart Problems"]) || 0;
  const familyHistory = parseFloat(dados["Family History"]) || 0;
  const medicationUse = parseFloat(dados["Medication Use"]) || 0;
  const sexMale = parseFloat(dados.Sex_Male) || 0;
  const bmi = parseFloat(dados.BMI) || 0;
  const diastolic = parseFloat(dados.Diastolic) || 0;
  const heartRate = parseFloat(dados["Heart Rate"]) || 0;

  const cardioRisk =
    (obesity + smoking + alcohol + diabetes + heartProblems + familyHistory) / 6;

  const medicalRisk =
    (diabetes + heartProblems + familyHistory + medicationUse) / 4;

  const lifestyleRisk = (smoking + alcohol + obesity) / 3;

  const features = {
    Cardio_Risk_Score: cardioRisk,
    Medical_Risk: medicalRisk,
    Lifestyle_Risk: lifestyleRisk,
    Sex_Male: sexMale,
    BMI: bmi,
    Diastolic: diastolic,
    Heart_Rate: heartRate
  };

  console.log("🔥 Features finais enviadas:", features);
  return features;
}

// ========================
// 🔥 ENVIO FINAL
// ========================
async function handleFinalSubmission() {
  const data = collectStepData(totalSteps);
  if (!validateStepData(data, totalSteps)) return;

  Object.assign(formData, data);

  console.log("🔍 Dados brutos:", formData);

  // Converter Sex → Sex_Male
  if (formData["Sex"]) {
    formData["Sex_Male"] = formData["Sex"] === "Masculino" ? 1 : 0;
    delete formData["Sex"];
  }

  // Obesity baseado no BMI
  if (formData["BMI"]) {
    formData["Obesity"] = formData["BMI"] >= 30 ? 1 : 0;
  }

  // Normalizar tudo
  const dadosNormalizados = normalizarDadosFormulario(formData);

  console.log("📤 Normalizados:", dadosNormalizados);

  // Calcular features finais
  const featuresParaBackend = calcularFeaturesCompostas(dadosNormalizados);

  try {
    const resp = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(featuresParaBackend)
    });

    if (!resp.ok) throw new Error("Erro na requisição");

    const result = await resp.json();
    console.log("📥 Resposta:", result);

    document.getElementById(`step-${totalSteps}`).style.display = "none";
    const results = document.getElementById("results");
    results.style.display = "block";

    const riskColor = result.risk === "ALTO" ? "#e74c3c" : "#27ae60";

    document.getElementById("result-text").innerHTML = `
      <div style="text-align: center; padding: 20px;">
          <h3>Seu Resultado:</h3>
          <div style="font-size: 28px; font-weight: bold; color: ${riskColor}; margin: 20px 0;">
              RISCO ${result.risk}
          </div>
          <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 15px 0;">
              <p>Probabilidade de risco alto: <strong>${(result.probability_high * 100).toFixed(1)}%</strong></p>
              <p>Probabilidade de risco baixo: <strong>${(result.probability_low * 100).toFixed(1)}%</strong></p>
          </div>
          <p style="color: #666; font-size: 14px; margin-top: 20px;">
              💡 Este resultado tem <strong>${(result.confidence * 100).toFixed(1)}%</strong> de confiança
          </p>
      </div>
    `;

    document.querySelector(".progress-bar").style.width = "100%";
    document.querySelector(".progress-text").innerText = "Avaliação Concluída!";
    
  } catch (err) {
    alert("Erro: " + err.message);
    console.error(err);
  }
}
