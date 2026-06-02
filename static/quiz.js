// Check for existing results before starting the quiz
function checkExistingProfile() {
    const savedProfile = sessionStorage.getItem('user_quiz_prompt');
    if (savedProfile) {
        // If profile exists, skip the quiz and go to results
        window.location.href = '/result_page';
    }
}

// Execute the check immediately
checkExistingProfile();

// ... existing code (questions array, currentStep, etc.) ...
const questions = [
    { number: 1, text: "What is your age?", type: "choice", options: [
        { label: "Below 18", features: [{ tag: "ya", weight: 1 }] },
        { label: "18 and above", features: [{ tag: "adult", weight: 1 }] }
    ]},
    { number: 2, text: "How do you typically spend your free time?", type: "choice", options: [
        { label: "Watching movies/series", features: [{ tag: "fast_paced", weight: 1 }] },
        { label: "Reading or relaxing quietly", features: [{ tag: "slow_paced", weight: 1 }, { tag: "philosophical", weight: 1 }] },
        { label: "Playing games", features: [{ tag: "fantasy", weight: 1 }, { tag: "adventure", weight: 1 }] },
        { label: "Outdoor activities / exploring", features: [{ tag: "adventure", weight: 1 }] }
    ]},
    { number: 3, text: "When starting a new project, how do you handle the details?", type: "choice", options: [
        { label: "Plan everything carefully", features: [{ tag: "mystery", weight: 1 }, { tag: "slow_paced", weight: 1 }] },
        { label: "Go with the flow", features: [{ tag: "adventure", weight: 1 }, { tag: "fast_paced", weight: 1 }] },
        { label: "Mix of both", features: [] }
    ]},
    { number: 4, text: "How do you usually feel when facing a major challenge?", type: "choice", options: [
        { label: "Excited", features: [{ tag: "adventure", weight: 1 }, { tag: "fast_paced", weight: 1 }] },
        { label: "Nervous", features: [{ tag: "thriller", weight: 1 }, { tag: "dark", weight: 1 }] },
        { label: "Calm and thoughtful", features: [{ tag: "philosophical", weight: 1 }, { tag: "slow_paced", weight: 1 }] }
    ]},
    { number: 5, text: "When reading, what matters more to you?", type: "choice", options: [
        { label: "Atmosphere / vibe", features: [{ tag: "romance", weight: 1 }, { tag: "slow_paced", weight: 1 }] },
        { label: "Action / excitement", features: [{ tag: "thriller", weight: 1 }, { tag: "fast_paced", weight: 1 }] }
    ]},
    { number: 6, text: "Do you believe people are generally...", type: "choice", options: [
        { label: "Good", features: [{ tag: "light", weight: 1 }, { tag: "romance", weight: 1 }] },
        { label: "Selfish", features: [{ tag: "dark", weight: 1 }, { tag: "thriller", weight: 1 }] }
    ]},
    { number: 7, text: "When you look at a starry sky, what do you think about?", type: "choice", options: [
        { label: "Space and universe", features: [{ tag: "sci_fi", weight: 2 }] },
        { label: "Magic and unknown worlds", features: [{ tag: "fantasy", weight: 2 }] },
        { label: "Meaning of life", features: [{ tag: "philosophical", weight: 2 }] },
        { label: "Nothing special", features: [{ tag: "contemporary", weight: 1 }] }
    ]},
    { number: 8, text: "Pick a place to live for a month:", type: "choice", options: [
        { label: "Modern city", features: [{ tag: "contemporary", weight: 2 }] },
        { label: "Forest / magical land", features: [{ tag: "fantasy", weight: 2 }] },
        { label: "Space station", features: [{ tag: "sci_fi", weight: 2 }] },
        { label: "Historical town", features: [{ tag: "historical", weight: 2 }] }
    ]},
    { number: 9, text: "Which secret would you rather discover?", type: "choice", options: [
        { label: "Hidden crime", features: [{ tag: "mystery", weight: 2 }] },
        { label: "Ancient magic", features: [{ tag: "fantasy", weight: 2 }] },
        { label: "Government conspiracy", features: [{ tag: "thriller", weight: 2 }] },
        { label: "Personal story", features: [{ tag: "romance", weight: 1 }, { tag: "philosophical", weight: 1 }] }
    ]},
    { number: 10, text: "It's Friday night! Where are you?", type: "choice", options: [
        { label: "Party / social", features: [{ tag: "romance", weight: 1 }, { tag: "light", weight: 1 }] },
        { label: "At home alone", features: [{ tag: "philosophical", weight: 1 }, { tag: "slow_paced", weight: 1 }] },
        { label: "Exploring outside", features: [{ tag: "adventure", weight: 1 }, { tag: "fast_paced", weight: 1 }] },
        { label: "Watching intense shows", features: [{ tag: "thriller", weight: 1 }, { tag: "dark", weight: 1 }] }
    ]},
    { number: 11, text: "Which job sounds most fun?", type: "choice", options: [
        { label: "Detective", features: [{ tag: "mystery", weight: 3 }] },
        { label: "Scientist", features: [{ tag: "sci_fi", weight: 3 }] },
        { label: "Warrior / Knight", features: [{ tag: "fantasy", weight: 3 }, { tag: "adventure", weight: 2 }] },
        { label: "Writer / Artist", features: [{ tag: "philosophical", weight: 2 }, { tag: "slow_paced", weight: 1 }] }
    ]},
    { number: 12, text: "How do you prefer your story to unfold?", type: "choice", options: [
        { label: "Slow and deep", features: [{ tag: "slow_paced", weight: 4 }] },
        { label: "Fast and exciting", features: [{ tag: "fast_paced", weight: 4 }] }
    ]},
    { number: 13, text: "What kind of atmosphere draws you in?", type: "choice", options: [
        { label: "Dark and intense", features: [{ tag: "dark", weight: 4 }, { tag: "thriller", weight: 2 }] },
        { label: "Light and happy", features: [{ tag: "light", weight: 4 }, { tag: "romance", weight: 2 }] },
        { label: "Mysterious", features: [{ tag: "mystery", weight: 4 }, { tag: "thriller", weight: 2 }] }
    ]},
    { number: 14, text: "Where should the story be set?", type: "choice", options: [
        { label: "Fantasy world", features: [{ tag: "fantasy", weight: 5 }] },
        { label: "Futuristic world", features: [{ tag: "sci_fi", weight: 5 }] },
        { label: "Modern real world", features: [{ tag: "contemporary", weight: 5 }] },
        { label: "Historical setting", features: [{ tag: "historical", weight: 5 }] }
    ]},
    { number: 15, text: "What kind of ending do you prefer?", type: "choice", options: [
        { label: "Happy ending", features: [{ tag: "romance", weight: 4 }, { tag: "light", weight: 2 }] },
        { label: "Tragic ending", features: [{ tag: "dark", weight: 4 }] },
        { label: "Plot twist", features: [{ tag: "thriller", weight: 4 }] },
        { label: "Open ending", features: [{ tag: "philosophical", weight: 4 }] }
    ]}
];

let currentStep = 0;
let userAnswers = [];

function shuffleArray(array) {
    let shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// Function to update progress bar and counter
function updateUIProgress() {
    const total = questions.length;
    const progress = ((currentStep + 1) / total) * 100;
    
    // Update the bar width
    const bar = document.getElementById('progressBar');
    if (bar) bar.style.width = `${progress}%`;
    
    // Update the counter text
    const counter = document.getElementById('questionNumber');
    if (counter) counter.innerText = `Question ${currentStep + 1} of ${total}`;
}

function loadQuestion() {
    updateUIProgress(); //
    
    const q = questions[currentStep]; //
    document.getElementById('questionText').innerText = q.text; //[cite: 11]
    
    const optionsContainer = document.getElementById('optionsGroup'); //[cite: 11]
    optionsContainer.innerHTML = ''; 

    // TOGGLE PREVIOUS BUTTON VISIBILITY
    const prevBtn = document.getElementById('prevBtn');
    if (currentStep === 0) {
        prevBtn.style.display = 'none'; // Hide on the first question
    } else {
        prevBtn.style.display = 'inline-block'; // Show on all other questions
    }

    let displayOptions = q.number === 1 ? q.options : shuffleArray(q.options); //[cite: 11]

    displayOptions.forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = opt.label; //[cite: 11]
        
        // HIGHLIGHT PREVIOUSLY SELECTED ANSWER
        // This checks if the current option features match what is stored in userAnswers[cite: 11]
        if (userAnswers[currentStep] && 
            JSON.stringify(userAnswers[currentStep]) === JSON.stringify(opt.features)) {
            btn.classList.add('selected');
        }
        
        btn.onclick = () => selectOption(btn, opt.features); //[cite: 11]
        optionsContainer.appendChild(btn);
    });

    const nextBtn = document.getElementById('nextBtn'); //[cite: 11]
    nextBtn.innerText = (currentStep === questions.length - 1) ? "Generate My Profile" : "Next Question"; //[cite: 11]
}

function selectOption(btn, features) {
    document.querySelectorAll('.option-btn').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    userAnswers[currentStep] = features;
}

document.getElementById('nextBtn').onclick = function() {
    if (userAnswers[currentStep] === undefined) {
        alert("Please select an option before proceeding!");
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
    // Show 100% progress during processing
    const bar = document.getElementById('progressBar');
    if (bar) bar.style.width = '100%';
    
    let featureCounts = {};

    userAnswers.forEach(answer => {
        answer.forEach(f => {
            const tagName = typeof f === 'object' ? f.tag : f;
            const weight = typeof f === 'object' ? f.weight : 1;
            featureCounts[tagName] = (featureCounts[tagName] || 0) + weight;
        });
    });

    const technicalTags = ['ya', 'adult', 'fast_paced', 'slow_paced', 'dark', 'light', 'philosophical'];
    
    const pacingMap = { "slow_paced": "slow-paced and deep", "fast_paced": "fast-paced and exciting" };
    const vibeMap = { "dark": "dark and intense", "light": "light and happy", "mystery": "mysterious and suspenseful" };
    const settingMap = { "fantasy": "magical fantasy world", "sci_fi": "futuristic sci-fi universe", "contemporary": "modern real-world setting", "historical": "rich historical period" };
    const endingMap = { "romance": "happy and satisfying ending", "dark": "tragic and emotional ending", "thriller": "shocking plot twist", "philosophical": "philosophical and open ending" };

    let sortedGenres = Object.entries(featureCounts)
        .filter(([tag]) => !technicalTags.includes(tag))
        .sort((a, b) => b[1] - a[1]);
    
    let topTwo = sortedGenres.slice(0, 2).map(item => item[0]);

    const findTagInHistory = (map) => {
        for (let answer of userAnswers) {
            const found = answer.find(f => map[f.tag || f]);
            if (found) return map[found.tag || found];
        }
        return null;
    };

    const paceDesc = findTagInHistory(pacingMap) || "balanced";
    const vibeDesc = findTagInHistory(vibeMap) || "engaging";
    const settingDesc = findTagInHistory(settingMap) || "interesting";
    const endingDesc = findTagInHistory(endingMap) || "thought-provoking";

    const genreString = topTwo.length > 0 ? topTwo.join(" and ") : "compelling";

    const masterProfile = `I am looking for a ${genreString} book. ` +
                        `It should be a ${paceDesc} story with a ${vibeDesc} atmosphere. ` +
                        `The story should be set in a ${settingDesc} and feature a ${endingDesc}.`;

    const ageCategory = userAnswers[0].some(f => (f.tag || f) === 'ya') ? 'ya' : 'adult';

    try {
        // --- FIX: Send data to backend API instead of just hiding it in sessionStorage ---
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                quiz_text: masterProfile, 
                age: ageCategory 
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || "Failed to fetch recommendations");
        }

        const recommendedBooks = await response.json();

        // Store everything so your result_page JavaScript can easily read and display them
        sessionStorage.setItem('user_quiz_prompt', masterProfile);
        sessionStorage.setItem('user_age', ageCategory);
        sessionStorage.setItem('recommended_books', JSON.stringify(recommendedBooks));
        
        window.location.href = '/result_page'; 
    } catch (error) {
        console.error("Error submitting quiz:", error);
        alert(error.message || "Something went wrong. Please try again.");
    }
}

document.getElementById('prevBtn').onclick = function() {
    if (currentStep > 0) {
        currentStep--;
        loadQuestion();
    }
};
// Start the quiz
loadQuestion();