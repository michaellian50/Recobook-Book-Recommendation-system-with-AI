const questions = [
    {
        number: 1,
        text: "How do you prefer your story to unfold?",
        type: "choice",
        options: [
            { label: "Fast pace with constant action", value: "fast-paced with non-stop action and high stakes" },
            { label: "Steady progression", value: "balanced pacing with a steady build-up" },
            { label: "Slow and contemplative", value: "slow-burn, philosophical, and deeply contemplative" }
        ]
    },
    {
        number: 2,
        text: "What kind of atmosphere draws you in?",
        type: "choice",
        options: [
            { label: "Dark and eerie", value: "a dark, gothic, and chilling atmosphere" },
            { label: "Cozy and warm", value: "a cozy, heartwarming, and comforting vibe" },
            { label: "Mysterious and tense", value: "a suspenseful, mysterious, and tense environment" }
        ]
    },
    {
        number: 3,
        text: "Where should the story be set?",
        type: "choice",
        options: [
            { label: "Our modern world", value: "set in a realistic, contemporary modern-day setting" },
            { label: "A futuristic world", value: "set in a high-tech, sci-fi futuristic universe" },
            { label: "A magical realm", value: "set in a high-fantasy world with magic and lore" }
        ]
    },
    {
        number: 4,
        text: "What kind of ending do you prefer?",
        type: "choice",
        options: [
            { label: "Happy and conclusive", value: "a satisfying, happy ending where everything is resolved" },
            { label: "Bittersweet or open", value: "a realistic, bittersweet, or thought-provoking open ending" },
            { label: "Dark and shocking", value: "a tragic, dark, or mind-bending plot twist ending" }
        ]
    },
    {
        number: 5,
        text: "Tell us more... what specifically are you looking for?",
        type: "text",
        placeholder: "e.g. I want a story about a lonely robot in a forest with themes of friendship..."
    }
];

let currentStep = 0;
let userAnswers = [];

function loadQuestion() {
    const q = questions[currentStep];
    document.getElementById('questionNumber').innerText = `Question ${q.number} of 5`;
    document.getElementById('questionText').innerText = q.text;
    
    const optionsContainer = document.getElementById('optionsGroup');
    optionsContainer.innerHTML = ''; 

    if (q.type === "choice") {
        // Render buttons for multiple choice
        q.options.forEach(opt => {
            const btn = document.createElement('button');
            btn.className = 'option-btn';
            btn.innerText = opt.label;
            
            // Check if this option was previously selected
            if (userAnswers[currentStep] === opt.value) btn.classList.add('selected');
            
            btn.onclick = () => selectOption(btn, opt.value);
            optionsContainer.appendChild(btn);
        });
    } else {
        // Render textarea for open-ended question
        const textArea = document.createElement('textarea');
        textArea.className = 'quiz-textarea'; // Ensure you have this in quiz.css
        textArea.id = "openEndedInput";
        textArea.placeholder = q.placeholder;
        textArea.value = userAnswers[currentStep] || "";
        textArea.oninput = (e) => { userAnswers[currentStep] = e.target.value; };
        optionsContainer.appendChild(textArea);
    }

    const nextBtn = document.getElementById('nextBtn');
    nextBtn.innerText = (currentStep === questions.length - 1) ? "Find My Books" : "Next Question";
}

function selectOption(btn, value) {
    document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    userAnswers[currentStep] = value;
}

document.getElementById('nextBtn').onclick = async function() {
    if (!userAnswers[currentStep] || userAnswers[currentStep].trim() === "") {
        alert("Please provide an answer!");
        return;
    }

    if (currentStep < questions.length - 1) {
        currentStep++;
        loadQuestion();
    } else {
        submitQuiz();
    }
};

async function submitQuiz() {
    // STITCHING LOGIC: Build the high-quality profile sentence
    const pace = userAnswers[0];
    const atmosphere = userAnswers[1];
    const setting = userAnswers[2];
    const ending = userAnswers[3];
    const openEnded = userAnswers[4];

    const masterProfile = `I am looking for a book that is ${pace}. It should have ${atmosphere} and be ${setting}. I prefer ${ending}. Specifically, ${openEnded}`;
    
    console.log("Master Profile for AI:", masterProfile);

    sessionStorage.setItem('user_quiz_prompt', masterProfile);
    window.location.href = '/result_page'; 
}

loadQuestion();