const chatWindow = document.getElementById("chat-window");
const chatLauncher = document.getElementById("chat-launcher");
const chatCard = document.getElementById("chat-card");
const closeChatButton = document.getElementById("close-chat");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const backButton = document.getElementById("back-button");
const quickReplies = document.getElementById("quick-replies");
const typingIndicator = document.getElementById("typing-indicator");
const template = document.getElementById("message-template");

let sessionId = null;
let chatInitialized = false;

const sentimentMeta = {
  positive: { icon: ":)", className: "sentiment-positive" },
  neutral: { icon: ":|", className: "sentiment-neutral" },
  negative: { icon: ":(", className: "sentiment-negative" },
};

function timestamp() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function addMessage({ text, sender, sentiment = "neutral" }) {
  const node = template.content.firstElementChild.cloneNode(true);
  node.classList.add(sender);
  node.querySelector(".bubble-text").textContent = text;
  node.querySelector(".timestamp").textContent = timestamp();

  const badge = node.querySelector(".sentiment-badge");
  const meta = sentimentMeta[sentiment] || sentimentMeta.neutral;
  badge.textContent = meta.icon;
  badge.className = "sentiment-badge";
  badge.classList.add(meta.className);

  chatWindow.appendChild(node);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

function setQuickReplies(items) {
  quickReplies.innerHTML = "";
  items.forEach((label) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", () => {
      messageInput.value = label;
      chatForm.requestSubmit();
    });
    quickReplies.appendChild(button);
  });
}

function openChat() {
  chatCard.classList.remove("hidden-chat");
  chatLauncher.classList.add("hidden");
  if (!chatInitialized) {
    addMessage({
      text: "Hello! Welcome to ShopAI. What is your name? I can help you track, cancel, or place orders.",
      sender: "bot",
      sentiment: "positive",
    });
    setQuickReplies(["Hello", "Track order", "Buy electronics", "Buy fashion items"]);
    chatInitialized = true;
  }
  messageInput.focus();
}

function closeChat() {
  chatCard.classList.add("hidden-chat");
  chatLauncher.classList.remove("hidden");
}

async function sendMessage(text) {
  addMessage({ text, sender: "user" });
  typingIndicator.classList.remove("hidden");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, session_id: sessionId }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Request failed");
    }

    sessionId = data.session_id;
    addMessage({ text: data.response, sender: "bot", sentiment: data.sentiment });
    setQuickReplies(data.quick_replies || []);
  } catch (error) {
    addMessage({
      text: `Something went wrong: ${error.message}. Please try again.`,
      sender: "bot",
      sentiment: "negative",
    });
  } finally {
    typingIndicator.classList.add("hidden");
  }
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = messageInput.value.trim();
  if (!text) {
    return;
  }
  messageInput.value = "";
  await sendMessage(text);
});

backButton.addEventListener("click", async () => {
  await sendMessage("Back");
});

chatLauncher.addEventListener("click", openChat);
closeChatButton.addEventListener("click", closeChat);
