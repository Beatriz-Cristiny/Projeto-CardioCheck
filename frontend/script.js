// Variáveis Globais
let formData = {};
let currentStep = 1;
const totalSteps = 4;

const stepTitles = [
  "1. Seu Perfil e Histórico",
  "2. Suas Medidas de Saúde",
  "3. Seu Estilo de Vida",
  "4. Sua Atividade Física"
];

// Inicialização
document.addEventListener("DOMContentLoaded", () => {
  updateView(1);
  const stressSlider = document.getElementById("stress-level");
  if (stressSlider) {
    document.getElementById("stressValue").innerText = stressSlider.value;
  }
});

// === TRANSIÇÃO ENTRE ETAPAS ===
function updateView(stepNumber) {
  document.querySelectorAll(".step").forEach((step) => {
    step.style.display = "none";
    step.classList.remove("active");
  });

  const nextStep = document.getElementById(`step-${stepNumber}`);
  nextStep.style.display = "block";
  nextStep.classList.add("active");

  const percentage = ((stepNumber - 1) / totalSteps) * 100;
  document.querySelector(".progress-bar").style.width = percentage + "%";
  document.querySelector(".progress-text").innerText =
    stepTitles[stepNumber - 1];

  currentStep = stepNumber;

  // === Mostrar botão final só no último passo ===
  const finalBtn = document.querySelector(".final-submit");
  if (stepNumber === totalSteps) {
    finalBtn.style.display = "inline-block";
  } else {
    finalBtn.style.display = "none";
  }
}

// === COLETA DAS ETAPAS ===
function collectStepData(stepNumber) {
  const step = document.getElementById(`step-${stepNumber}`);
  const inputs = step.querySelectorAll("input, select");
  const data = {};

  inputs.forEach((input) => {
    const name = input.name;

    if (input.type === "radio") {
      if (input.checked) data[name] = input.value;
      return;
    }

    if (input.type === "checkbox") {
      data[name] = input.checked ? 1 : 0;
      return;
    }

    // Números → float
    if (input.value.trim() !== "" && !isNaN(input.value)) {
      data[name] = parseFloat(input.value);
    } else {
      data[name] = input.value;
    }
  });

  return data;
}

// === VALIDAÇÃO ===
function validateStepData(data, stepNumber) {
  const step = document.getElementById(`step-${stepNumber}`);
  let valid = true;

  step.querySelectorAll("[required]").forEach((input) => {
    if (input.type === "radio") {
      const group = input.name;
      if (!step.querySelector(`input[name="${group}"]:checked`))
        valid = false;
    } else if (input.value.trim() === "") {
      valid = false;
    }
  });

  return valid;
}

// === BOTÕES DE AVANÇAR/VOLTAR ===
function handleStepSubmission(stepNumber, proceed = true) {
  if (proceed) {
    const data = collectStepData(stepNumber);
    if (!validateStepData(data, stepNumber)) {
      alert("Por favor, preencha todos os campos obrigatórios.");
      return;
    }

    Object.assign(formData, data);
    console.log("Dados coletados:", formData);

    updateView(stepNumber + 1);
  } else {
    if (stepNumber > 1) updateView(stepNumber - 1);
  }
}

// === ENVIO FINAL PARA O BACKEND ===
async function handleFinalSubmission() {
  const data = collectStepData(totalSteps);
  if (!validateStepData(data, totalSteps)) {
    alert("Preencha a última seção!");
    return;
  }

  Object.assign(formData, data);

  try {
    const resp = await fetch("http://127.0.0.1:5000/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });

    if (!resp.ok) {
      throw new Error("Erro na requisição");
    }

    const result = await resp.json();

    document.getElementById(`step-${totalSteps}`).style.display = "none";
    const results = document.getElementById("results");
    results.style.display = "block";

    document.getElementById("result-text").innerHTML = `
      <p>Resultado:</p>
      <p><strong style="font-size: 22px; color: ${
        result.risk === "ALTO" ? "red" : "green"
      }">${result.risk}</strong></p>
    `;

    document.querySelector(".progress-bar").style.width = "100%";
    document.querySelector(".progress-text").innerText =
      "Avaliação Concluída!";
  } catch (err) {
    alert("Erro ao conectar com o servidor.");
    console.error(err);
  }
}
