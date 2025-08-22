// Fallback data (minimal example, same structure as data.json)
const fallbackData = {
  "ranks": [
    {
      "name": "Rank A",
      "description": "Topics I know well",
      "topics": [
        {
          "name": "C++",
          "subtopics": [
            { "name": "Templates", "resources": ["https://cppreference.com"] },
            { "name": "STL", "resources": [] },
            { "name": "Memory Management", "resources": [] }
          ],
          "quizzes": [
            {
              "question": "What does RAII stand for?",
              "type": "text",
              "answers": ["Resource Acquisition Is Initialization"],
              "caseSensitive": false,
              "hint": "Think about resource management in C++."
            },
            {
              "question": "Which STL container provides O(1) lookup?",
              "type": "multiple-choice",
              "options": ["vector", "list", "unordered_map", "map"],
              "answers": ["unordered_map"],
              "hint": "Consider hash-based containers."
            }
          ]
        },
        {
          "name": "Python",
          "subtopics": [
            { "name": "OOP", "resources": [] },
            { "name": "Asyncio", "resources": [] },
            { "name": "Decorators", "resources": [] }
          ],
          "quizzes": [
            {
              "question": "What keyword is used to create a generator?",
              "type": "text",
              "answers": ["yield"],
              "caseSensitive": false,
              "hint": "It’s used in functions to return iterators."
            }
          ]
        }
      ]
    },
    {
      "name": "Rank B",
      "description": "Topics I want to learn",
      "topics": [
        {
          "name": "Quant",
          "subtopics": [
            { "name": "Stochastic Calculus", "resources": [] },
            { "name": "Portfolio Theory", "resources": [] }
          ],
          "quizzes": [
            {
              "question": "What is the CAPM formula?",
              "type": "text",
              "answers": ["E(Ri) = Rf + βi(E(Rm) - Rf)", "E(Ri) = Rf + βi * (E(Rm) - Rf)"],
              "caseSensitive": false,
              "hint": "Relates expected return to market risk."
            }
          ]
        }
      ]
    }
  ]
};

// Load data with fallback
async function loadData() {
  console.log("🔍 loadData() called...");

  try {
    const res = await fetch('data.json');
    console.log("➡️ Fetch response:", res);

    if (!res.ok) throw new Error(`HTTP error: ${res.status}`);

    const data = await res.json();
    console.log("✅ Parsed data:", data);

    initProgress(data);
    buildTree(data);
  } catch (error) {
    console.warn("⚠️ Falling back to inline data:", error);
    initProgress(fallbackData);
    buildTree(fallbackData);
  }
}

// Add progress info to topics
function initProgress(data) {
  const savedProgress = JSON.parse(localStorage.getItem('learningProgress')) || {};
  console.log("📦 Saved progress:", savedProgress);

  data.ranks.forEach(rank => {
    rank.topics.forEach(topic => {
      const key = `${rank.name}:${topic.name}`;
      topic.progress = savedProgress[key] ?? 0;
    });
  });
}

// Build topic tree
function buildTree(data) {
  const tree = document.getElementById('topicTree');
  tree.innerHTML = '';

  data.ranks.forEach(rank => {
    const rankDiv = document.createElement('div');
    rankDiv.className = 'rank';
    rankDiv.innerHTML = `<h2>${rank.name}</h2><p>${rank.description}</p>`;

    rank.topics.forEach(topic => {
      const topicDiv = document.createElement('div');
      topicDiv.className = 'topic';
      topicDiv.innerHTML = `${topic.name} <span class="progress">(${topic.progress}%)</span>`;
      topicDiv.setAttribute('aria-expanded', 'false');
      topicDiv.setAttribute('tabindex', '0');

      const subDiv = document.createElement('div');
      subDiv.className = 'subtopics';
      subDiv.setAttribute('aria-hidden', 'true');

      // Add subtopics
      topic.subtopics.forEach(st => {
        const stDiv = document.createElement('div');
        stDiv.textContent = `• ${st.name}`;
        if (st.resources.length) {
          const resLink = document.createElement('a');
          resLink.href = st.resources[0];
          resLink.textContent = ' [Learn More]';
          resLink.target = '_blank';
          stDiv.appendChild(resLink);
        }
        subDiv.appendChild(stDiv);
      });

      // Add quiz button
      const quizBtn = document.createElement('button');
      quizBtn.textContent = 'Take Quiz';
      quizBtn.onclick = () => showQuiz(topic, rank.name);
      subDiv.appendChild(quizBtn);

      // Toggle subtopics
      topicDiv.onclick = () => toggleSubtopics(topicDiv, subDiv);
      topicDiv.onkeydown = (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          toggleSubtopics(topicDiv, subDiv);
        }
      };

      rankDiv.appendChild(topicDiv);
      rankDiv.appendChild(subDiv);
    });

    tree.appendChild(rankDiv);
  });

  // Toggle all button
  document.getElementById('toggleAll').onclick = () => {
    const topics = document.querySelectorAll('.topic');
    const subtopics = document.querySelectorAll('.subtopics');
    const isExpanded = topics[0]?.getAttribute('aria-expanded') === 'true';
    topics.forEach((topic, i) => {
      topic.setAttribute('aria-expanded', !isExpanded);
      subtopics[i].setAttribute('aria-hidden', isExpanded);
      subtopics[i].style.display = isExpanded ? 'none' : 'block';
    });
    document.getElementById('toggleAll').textContent = isExpanded ? 'Expand All' : 'Collapse All';
  };
}

// Toggle subtopics
function toggleSubtopics(topicDiv, subDiv) {
  const isExpanded = topicDiv.getAttribute('aria-expanded') === 'true';
  topicDiv.setAttribute('aria-expanded', !isExpanded);
  subDiv.setAttribute('aria-hidden', isExpanded);
  subDiv.style.display = isExpanded ? 'none' : 'block';
}

// Show quiz
function showQuiz(topic, rankName) {
  const quizSection = document.getElementById('quizSection');
  quizSection.innerHTML = `<h3>Quiz: ${topic.name}</h3>`;
  quizSection.classList.remove('hidden');

  let correctAnswers = 0;

  topic.quizzes.forEach((item, index) => {
    const qDiv = document.createElement('div');
    qDiv.className = 'quiz-question';
    qDiv.innerHTML = `<p><b>${index + 1}. ${item.question}</b> <small>(Hint: ${item.hint})</small></p>`;

    let input;
    if (item.type === 'multiple-choice') {
      input = document.createElement('select');
      item.options.forEach(opt => {
        const option = document.createElement('option');
        option.value = opt;
        option.textContent = opt;
        input.appendChild(option);
      });
    } else {
      input = document.createElement('input');
      input.type = 'text';
      input.placeholder = 'Your answer...';
    }

    const checkBtn = document.createElement('button');
    checkBtn.textContent = 'Check';
    checkBtn.onclick = () => {
      const userAnswer = input.value.trim();
      const isCorrect = item.caseSensitive
        ? item.answers.includes(userAnswer)
        : item.answers.some(a => a.toLowerCase() === userAnswer.toLowerCase());

      if (isCorrect) {
        alert('✅ Correct!');
        correctAnswers++;
        updateProgress(rankName, topic.name, correctAnswers, topic.quizzes.length);
      } else {
        alert('❌ Try again.\nCorrect answer(s): ' + item.answers.join(', '));
      }
    };

    qDiv.appendChild(input);
    qDiv.appendChild(checkBtn);
    quizSection.appendChild(qDiv);
  });
}

// Update and save progress
function updateProgress(rankName, topicName, correct, total) {
  const percent = Math.round((correct / total) * 100);
  const key = `${rankName}:${topicName}`;

  // Save progress to localStorage
  const savedProgress = JSON.parse(localStorage.getItem('learningProgress')) || {};
  savedProgress[key] = percent;
  localStorage.setItem('learningProgress', JSON.stringify(savedProgress));

  // Update UI
  const topics = document.querySelectorAll('.topic');
  topics.forEach(t => {
    if (t.textContent.startsWith(topicName)) {
      t.querySelector('.progress').textContent = `(${percent}%)`;
    }
  });
}

loadData();
