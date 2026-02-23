(function () {
  const chatEl = document.getElementById("chat");
  const form = document.getElementById("form");
  const input = document.getElementById("input");
  const sendBtn = document.getElementById("send");

  const API_BASE = "";

  function appendBubble(role, content, opts = {}) {
    const div = document.createElement("div");
    div.className = "bubble " + role + (opts.typing ? " typing" : "");
    div.textContent = content || "";
    if (opts.id) div.dataset.id = opts.id;
    chatEl.appendChild(div);
    chatEl.scrollTop = chatEl.scrollHeight;
    return div;
  }

  function setBubbleContent(el, content) {
    if (el) {
      el.textContent = content;
      el.classList.remove("typing");
      chatEl.scrollTop = chatEl.scrollHeight;
    }
  }

  function collectHistory() {
    const bubbles = chatEl.querySelectorAll(".bubble.user, .bubble.assistant");
    const history = [];
    bubbles.forEach((b) => {
      const role = b.classList.contains("user") ? "user" : "assistant";
      history.push({ role, content: b.textContent.trim() });
    });
    return history;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = (input.value || "").trim();
    if (!text) return;

    input.value = "";
    appendBubble("user", text);

    const history = collectHistory();
    history.pop();
    const placeholder = appendBubble("assistant", "…", { typing: true });

    sendBtn.disabled = true;
    try {
      const res = await fetch(API_BASE + "/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          user_id: "default",
          history: history,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setBubbleContent(placeholder, "错误: " + (data.detail || res.statusText));
        return;
      }
      setBubbleContent(placeholder, data.reply || "");
    } catch (err) {
      setBubbleContent(placeholder, "请求失败: " + (err.message || "网络错误"));
    } finally {
      sendBtn.disabled = false;
    }
  });

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      form.requestSubmit();
    }
  });
})();
