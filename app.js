async function loadToday() {
  const card = document.getElementById("card");
  try {
    const res = await fetch("./data/today.json", { cache: "no-store" });
    if (!res.ok) throw new Error("today.json not found");
    const data = await res.json();

    const psychologistTag = data.psychologist
      ? `<p class="psychologist">🧠 ${escapeHtml(data.psychologist)} 的研究</p>`
      : "";

    card.innerHTML = `
      <p class="eyebrow">每日心理學知識</p>
      <p class="date">${data.date}</p>
      ${psychologistTag}
      <h1>${escapeHtml(data.title)}</h1>
      <p class="extract">${escapeHtml(data.extract)}</p>
      <a class="source" href="${data.url}" target="_blank" rel="noopener">查看原文 →</a>
    `;
  } catch (err) {
    card.innerHTML = `<p class="error">目前還沒有今日內容,請稍後再試。</p>`;
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

loadToday();
