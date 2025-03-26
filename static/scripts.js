let mediaRecorder;
let audioChunks = [];
let audio = null; // Store the AI speech audio instance globally

// Scenario-based AI greeting messages
let scenarioMessages = {
  casual: "Hi! Let's have a friendly chat. What’s on your mind today?",
  interview:
    "Hello! What job role are you preparing for? Let's do a mock interview!",
  debate:
    "Let's have a debate! Here are some topics: 1) AI in Education, 2) Climate Change, 3) Social Media Influence. Choose one!",
  storytelling: "Tell me a short story idea, and I’ll help you develop it!",
};

// Update AI's initial message based on the selected scenario
function updateScenario() {
  let scenario = document.getElementById("scenario").value;
  document.getElementById("chat-box").innerHTML =
    `<div class="chat-message ai-message"><strong>AI:</strong> ${scenarioMessages[scenario]}</div>`;
}

// Function to send chat messages
function sendMessage() {
  let userInput = document.getElementById("user_input").value.trim();
  let scenario = document.getElementById("scenario").value;

  if (!userInput) return;

  document.getElementById("chat-box").innerHTML +=
    `<div class="chat-message user-message"><strong>You:</strong> ${userInput}</div>`;
  document.getElementById("user_input").value = "";
  document.getElementById("loading").style.display = "block";

  fetch("/chat", {
    method: "POST",
    body: new URLSearchParams({ user_input: userInput, scenario: scenario }),
  })
    .then((response) => response.json())
    .then((data) => {
      document.getElementById("loading").style.display = "none";
      displayAIResponse(data);
    })
    .catch((error) => {
      document.getElementById("loading").style.display = "none";
      alert("Error processing chat response.");
    });
}

function displayAIResponse(data) {
  let aiResponse = data.feedback || "**AI did not return feedback.**";

  // ✅ Convert Markdown to HTML using `marked.js`
  let formattedResponse = marked.parse(aiResponse);

  // ✅ Create a new div and set its innerHTML to prevent escaping
  let aiMessageDiv = document.createElement("div");
  aiMessageDiv.className = "chat-message ai-message";
  aiMessageDiv.innerHTML = `<strong>AI:</strong> ${formattedResponse}`;

  // ✅ Append properly formatted response to chat box
  document.getElementById("chat-box").appendChild(aiMessageDiv);
  document.getElementById("chat-box").scrollTop =
    document.getElementById("chat-box").scrollHeight;
}

// Function to play/pause AI speech with speed control
function toggleAudio(button) {
  let audioUrl = button.getAttribute("data-audio-url");
  if (!audioUrl) return;

  let speedSelector = button.nextElementSibling;
  let speed = parseFloat(speedSelector.value);

  if (audio && !audio.paused) {
    audio.pause();
    audio.currentTime = 0;
    button.innerText = "🔊 Hear AI";
  } else {
    audio = new Audio(audioUrl);
    audio.playbackRate = speed; // Apply speed setting
    audio.play();
    button.innerText = "⏹ Stop AI";

    audio.onended = function () {
      button.innerText = "🔊 Hear AI";
    };
  }
}

// Function to update audio speed dynamically
function updateAudioSpeed(select) {
  if (audio) {
    audio.playbackRate = parseFloat(select.value);
  }
}

/* ======================== Voice Recording for Chat Input ======================== */

// Start recording when mic button is clicked
async function startRecording() {
  try {
    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      let audioBlob = new Blob(audioChunks, { type: "audio/wav" });
      sendVoiceInput(audioBlob);
    };

    mediaRecorder.start();
    document.getElementById("recordButton").classList.add("recording");
  } catch (error) {
    alert("Microphone access denied. Please allow microphone permissions.");
  }
}

// Stop recording when mic button is clicked again
function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === "recording") {
    mediaRecorder.stop();
    document.getElementById("recordButton").classList.remove("recording");
  }
}

// Function to send recorded voice input
async function sendVoiceInput(audioBlob) {
  let formData = new FormData();
  formData.append("audio", audioBlob, "recorded_audio.wav");

  document.getElementById("loading").style.display = "block";

  let response = await fetch("/voice", {
    method: "POST",
    body: formData,
  });

  let data = await response.json();
  document.getElementById("loading").style.display = "none";

  if (data.transcript) {
    document.getElementById("chat-box").innerHTML +=
      `<div class="chat-message user-message"><strong>You:</strong> ${data.transcript}</div>`;
  }

  displayAIResponse(data);
}

async function uploadAudio() {
  let fileInput = document.getElementById("audio");
  let file = fileInput.files[0];

  if (!file) {
    alert("Please select an audio file.");
    return;
  }

  let formData = new FormData();
  formData.append("audio", file);

  document.getElementById("loading").style.display = "block";

  try {
    let response = await fetch("/assessment_audio", {
      method: "POST",
      body: formData,
    });

    let data = await response.json();
    document.getElementById("loading").style.display = "none";

    if (data.error) {
      alert("Error: " + data.error);
      return;
    }

    // ✅ Display transcript and AI feedback
    document.getElementById("result").style.display = "block";
    document.getElementById("transcript").innerText =
      data.transcript || "No transcription available.";
    document.getElementById("ai_response").innerText =
      data.feedback || "AI did not return feedback.";
  } catch (error) {
    document.getElementById("loading").style.display = "none";
    console.error("Error:", error);
    alert("Error processing the audio.");
  }
}
