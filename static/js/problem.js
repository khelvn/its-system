// Global variables
let currentProblem = null;
let currentDifficulty = document.getElementById('current-level').textContent;

// DOM Elements
const problemText = document.getElementById('problem-text');
const problemSteps = document.getElementById('problem-steps');
const answerInput = document.getElementById('answer-input');
const unitInput = document.getElementById('unit-input');
const submitButton = document.getElementById('submit-answer');
const nextButton = document.getElementById('next-problem');
const feedbackDiv = document.getElementById('feedback');

// Load initial problem
window.addEventListener('load', () => {
    loadNewProblem();
});

// Load new problem from server
async function loadNewProblem() {
    try {
        const response = await fetch(`/get_problem/${TOPIC}/${currentDifficulty}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        currentProblem = await response.json();
        
        if (currentProblem.error) {
            problemText.innerHTML = currentProblem.error;
            return;
        }
        
        displayProblem(currentProblem);
        submitButton.style.display = 'inline-block';
        nextButton.style.display = 'none';
        feedbackDiv.innerHTML = '';
        answerInput.value = '';
        unitInput.value = '';
        
    } catch (error) {
        console.error('Error:', error);
        problemText.innerHTML = 'Error loading problem. Please try again.';
    }
}

// Display problem on page
function displayProblem(problem) {
    problemText.innerHTML = `<h3>${problem.description}</h3>`;
    problemSteps.innerHTML = '';
    
    if (problem.steps && problem.steps.length > 0) {
        const stepsHtml = problem.steps.map(step => `<li>${step}</li>`).join('');
        problemSteps.innerHTML += `<ol>${stepsHtml}</ol>`;
    }
    
    unitInput.placeholder = problem.unit || 'Unit';
}

// Submit answer
submitButton.addEventListener('click', async () => {
    if (!currentProblem) return;
    
    const studentAnswer = parseFloat(answerInput.value);
    const studentUnit = unitInput.value.trim();
    
    if (isNaN(studentAnswer)) {
        feedbackDiv.innerHTML = 'Please enter a valid number';
        feedbackDiv.className = 'feedback error';
        return;
    }
    
    if (!studentUnit) {
        feedbackDiv.innerHTML = 'Please enter the unit';
        feedbackDiv.className = 'feedback error';
        return;
    }
    
    try {
        const response = await fetch('/check_answer', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                topic: TOPIC,
                answer: studentAnswer,
                unit: studentUnit,
                correct_answer: currentProblem.answer,
                expected_unit: currentProblem.unit
            })
        });
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        feedbackDiv.innerHTML = result.correct ? 
            'Correct! Well done!' : 
            `Incorrect. The correct answer is ${currentProblem.answer} ${currentProblem.unit}`;
        feedbackDiv.className = `feedback ${result.correct ? 'success' : 'error'}`;
        
        // Update difficulty level if provided
        if (result.next_difficulty) {
            currentDifficulty = result.next_difficulty;
            document.getElementById('current-level').textContent = currentDifficulty;
        }
        
        // Show next button
        submitButton.style.display = 'none';
        nextButton.style.display = 'inline-block';
        
        // Update progress if provided
        if (result.progress) {
            document.getElementById('problems-solved').textContent = result.progress.problems_solved;
            document.getElementById('correct-answers').textContent = result.progress.correct_answers;
        }
        
    } catch (error) {
        console.error('Error:', error);
        feedbackDiv.innerHTML = 'Error checking answer. Please try again.';
        feedbackDiv.className = 'feedback error';
    }
});

// Load next problem
nextButton.addEventListener('click', () => {
    feedbackDiv.innerHTML = ''; // Clear feedback
    loadNewProblem();
});