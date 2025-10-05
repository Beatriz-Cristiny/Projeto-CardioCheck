// Variáveis Globais de Controle
let formData = {};
let currentStep = 1;
const totalSteps = 4;
const stepTitles = [
    "1. Seu Perfil e Histórico",
    "2. Suas Medidas de Saúde",
    "3. Seu Estilo de Vida",
    "4. Sua Atividade Física"
];

// Funções de Utilidade na Inicialização
document.addEventListener('DOMContentLoaded', () => {
    updateView(1);
    // Atualiza o valor inicial do slider de estresse (Etapa 3)
    const stressSlider = document.getElementById('stress-level');
    if (stressSlider) {
        document.getElementById('stressValue').innerText = stressSlider.value;
    }
});

// Funções de Transição
function updateView(stepNumber) {
    // 1. Esconde todas as etapas
    document.querySelectorAll('.step').forEach(step => {
        step.style.display = 'none';
        step.classList.remove('active');
    });

    // 2. Mostra a etapa correta
    const nextStepElement = document.getElementById(`step-${stepNumber}`);
    if (nextStepElement) {
        nextStepElement.style.display = 'block';
        nextStepElement.classList.add('active');
    }

    // 3. Atualiza o indicador de progresso
    const percentage = ((stepNumber - 1) / totalSteps) * 100;
    document.querySelector('.progress-bar').style.width = percentage + '%';
    document.querySelector('.progress-text').innerText = stepTitles[stepNumber - 1] || 'Concluído!';
    
    currentStep = stepNumber;
}

// Funções Essenciais do Formulário

function collectStepData(stepNumber) {
    const stepElement = document.getElementById(`step-${stepNumber}`);
    const data = {};

    // Coleta todos os campos de entrada (input, select) dentro da etapa
    const inputs = stepElement.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        const name = input.name;
        let value;

        if (input.type === 'radio' && input.checked) {
            value = input.value;
            data[name] = value;
        } else if (input.type === 'checkbox') {
            // Para checkboxes (Toggle Switch), envia 1 para "Sim" e 0 para "Não"
            data[name] = input.checked ? 1 : 0;
        } else if (input.type !== 'radio') {
            value = input.value;
            // Converte números para tipo Number, se aplicável
            if (!isNaN(parseFloat(value)) && isFinite(value) && value.trim() !== '') {
                data[name] = parseFloat(value);
            } else {
                data[name] = value;
            }
        }
    });

    // TRATAMENTO ESPECIAL PARA PRESSÃO ARTERIAL (Etapa 2)
    if (stepNumber === 2) {
        const sys = document.getElementById('blood-pressure-sys').value;
        const dia = document.getElementById('blood-pressure-dia').value;
        if (sys && dia) {
            // Combina os dois em uma string para enviar (ex: "120/80")
            data['Blood Pressure'] = `${sys}/${dia}`; 
        }
    }

    return data;
}

function validateStepData(data, stepNumber) {
    // Lógica SIMPLIFICADA: Checa apenas se os campos obrigatórios têm algum valor
    let isValid = true;
    const stepElement = document.getElementById(`step-${stepNumber}`);
    
    stepElement.querySelectorAll('[required]').forEach(input => {
        if (input.type === 'radio') {
            // Verifica se pelo menos um rádio button no grupo está checado
            const groupName = input.name;
            if (!stepElement.querySelector(`input[name="${groupName}"]:checked`)) {
                isValid = false;
            }
        } else if (input.value.trim() === '') {
            isValid = false;
        }
    });

    // Adicione VALIDAÇÕES ESPECÍFICAS aqui (ex: Idade > 18, IMC em faixa razoável)

    return isValid;
}


function handleStepSubmission(stepNumber, proceed = true) {
    if (proceed) {
        // Lógica de PROSSEGUIR: Coleta, Valida e Armazena
        const stepData = collectStepData(stepNumber);
        
        if (!validateStepData(stepData, stepNumber)) {
            alert("Por favor, preencha todos os campos obrigatórios corretamente.");
            return;
        }
        
        Object.assign(formData, stepData);
        console.log(`Dados Etapa ${stepNumber} Coletados:`, formData);
        
        updateView(stepNumber + 1);
    } else {
        // Lógica de VOLTAR
        if (stepNumber > 1) {
            updateView(stepNumber - 1);
        }
    }
}

function handleFinalSubmission() {
    // 1. Coleta os dados finais da Etapa 4 e valida
    const step4Data = collectStepData(totalSteps);
    if (!validateStepData(step4Data, totalSteps)) {
        alert("Preencha a última seção para obter seu resultado.");
        return;
    }
    Object.assign(formData, step4Data);
    
    // 2. Envio Final e Simulação do Resultado
    console.log("DADOS FINAIS PRONTOS PARA ENVIO:", formData);
    
    // Aqui você enviaria 'formData' para o seu backend/modelo ML
    
    // 3. Exibe a tela de resultado
    document.getElementById(`step-${totalSteps}`).style.display = 'none';
    const resultsElement = document.getElementById('results');
    resultsElement.style.display = 'block';

    // SIMULAÇÃO DA CLASSIFICAÇÃO DE RISCO
    document.getElementById('result-text').innerHTML = `
        <p>Agradecemos por completar a avaliação. Seu coração está sendo analisado!</p>
        <p><strong>SIMULAÇÃO:</strong> Seu risco foi classificado como <span style="color: red; font-weight: bold;">ALTO</span>, baseado nos dados fornecidos.</p>
        <p><em>(Esta é uma simulação. No ambiente real, o resultado viria do seu modelo de Machine Learning.)</em></p>
    `;
    
    // Atualiza a barra de progresso para 100%
    document.querySelector('.progress-bar').style.width = '100%';
    document.querySelector('.progress-text').innerText = 'Avaliação Concluída!';
}