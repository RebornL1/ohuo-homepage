const visibilityLabels = {
  public: "公开",
  member: "会员",
  private: "私密"
};

const commentPolicyLabels = {
  visitor: "游客可评论",
  member: "会员共创",
  closed: "不开放"
};

const data = window.__HOME_DATA__;
const articleGrid = document.querySelector("#articleGrid");
const searchInput = document.querySelector("#searchInput");
const filterButtons = document.querySelectorAll("[data-filter]");
let activeFilter = "all";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderPrinciples() {
  document.querySelector("#principles").innerHTML = data.principles
    .map(
      (item) => `
        <article class="principle">
          <span>${item.label}</span>
          <h3>${escapeHtml(item.title)}</h3>
          <p>${escapeHtml(item.body)}</p>
        </article>
      `
    )
    .join("");
}

function renderArticles() {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = data.articles.filter((article) => {
    const matchesFilter = activeFilter === "all" || article.visibility === activeFilter;
    const haystack = [article.title, article.summary, (article.tags || []).join(" ")]
      .join(" ")
      .toLowerCase();
    return matchesFilter && haystack.includes(query);
  });

  articleGrid.innerHTML = filtered
    .map(
      (article) => `
        <article class="article-card">
          <div class="card-topline">
            <span class="badge ${article.visibility}">${visibilityLabels[article.visibility]}</span>
            <time class="card-date">${article.published_at}</time>
          </div>
          <h3>${escapeHtml(article.title)}</h3>
          <p>${escapeHtml(article.summary)}</p>
          <div class="link-row">
            <span class="link-chip">${commentPolicyLabels[article.comment_policy]}</span>
            <span class="link-chip">${escapeHtml(article.kind)}</span>
          </div>
          <div class="tag-row">
            ${(article.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderTools() {
  document.querySelector("#toolGrid").innerHTML = `
      <aside class="tool-rail" aria-label="工具状态索引">
        <span class="tool-rail-label">Tool Stack</span>
        ${data.tools
          .map(
            (tool, index) => `
              <a class="tool-rail-item" href="#tool-${index + 1}">
                <span>${String(index + 1).padStart(2, "0")}</span>
                <strong>${escapeHtml(tool.name)}</strong>
                <small>${escapeHtml(tool.status)}</small>
              </a>
            `
          )
          .join("")}
      </aside>
      <div class="tool-stage">
        ${data.tools
    .map(
      (tool, index) => `
        <article class="tool-card ${index === 0 ? "featured" : ""}" id="tool-${index + 1}">
          <div class="card-topline">
            <span class="badge public">${escapeHtml(tool.status)}</span>
            <span class="tool-index">${String(index + 1).padStart(2, "0")}</span>
          </div>
          <h3>${escapeHtml(tool.name)}</h3>
          <p>${escapeHtml(tool.description)}</p>
          <div class="tag-row">
            ${(tool.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}
          </div>
        </article>
      `
    )
    .join("")}
      </div>
    `;
}

function renderJournals() {
  document.querySelector("#journalList").innerHTML = data.journals
    .map(
      (entry) => `
        <article class="journal-item">
          <time>${entry.written_at}</time>
          <div>
            <h3>${escapeHtml(entry.title)}</h3>
            <p>${escapeHtml(entry.body)}</p>
          </div>
        </article>
      `
    )
    .join("");
}

function renderTimeline() {
  document.querySelector("#timelineList").innerHTML = data.timeline
    .map(
      (event) => `
        <article class="timeline-item">
          <div>
            <time class="timeline-date">${event.happened_at}</time>
            <div class="tag">${escapeHtml(event.event_type)}</div>
          </div>
          <div>
            <h3>${escapeHtml(event.title)}</h3>
            <p>${escapeHtml(event.note)}</p>
          </div>
        </article>
      `
    )
    .join("");
}

function renderWorks() {
  document.querySelector("#workGrid").innerHTML = data.works
    .map(
      (work) => `
        <article class="work-card">
          <div class="card-topline">
            <span class="badge member">${escapeHtml(work.year)}</span>
            <span class="card-date">${escapeHtml(work.role)}</span>
          </div>
          <h3>${escapeHtml(work.title)}</h3>
          <p>${escapeHtml(work.summary)}</p>
          <div class="link-row">
            ${(work.references || [])
              .map((reference) => `<span class="link-chip">${escapeHtml(reference)}</span>`)
              .join("")}
          </div>
        </article>
      `
    )
    .join("");
}

function renderMetrics() {
  document.querySelector("#metricArticles").textContent = data.articles.length;
  document.querySelector("#metricTools").textContent = data.tools.length;
  document.querySelector("#metricEvents").textContent = data.timeline.length;
  document.querySelector("#metricWorks").textContent = data.works.length;
}

async function createTimelineEvent(payload) {
  const response = await fetch("/api/timeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) {
    throw new Error("保存失败");
  }
  return response.json();
}

function bindEvents() {
  searchInput.addEventListener("input", renderArticles);
  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      filterButtons.forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      activeFilter = button.dataset.filter;
      renderArticles();
    });
  });

  document.querySelector("#captureForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const formData = new FormData(form);
    const saved = await createTimelineEvent({
      title: formData.get("title"),
      date: formData.get("date"),
      type: formData.get("type"),
      note: formData.get("note") || "无备注",
      visibility: formData.get("visibility")
    });
    data.timeline.unshift(saved);
    data.timeline.sort((a, b) => b.happened_at.localeCompare(a.happened_at));
    form.reset();
    setDefaultDate();
    renderTimeline();
    renderMetrics();
    document.querySelector("#timeline").scrollIntoView({ behavior: "smooth" });
  });
}

function setDefaultDate() {
  document.querySelector('input[name="date"]').value = new Date().toISOString().slice(0, 10);
}

function init() {
  document.querySelector("#year").textContent = new Date().getFullYear();
  setDefaultDate();
  renderPrinciples();
  renderArticles();
  renderTools();
  renderJournals();
  renderTimeline();
  renderWorks();
  renderMetrics();
  bindEvents();
}

init();
