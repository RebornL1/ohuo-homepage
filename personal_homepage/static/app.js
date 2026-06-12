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

function renderSelfDistillation() {
  const items = data.self_distillation || [];
  const hotwords = data.self_hotwords || [];
  const firstHotword = hotwords[0];
  document.querySelector("#selfConsole").innerHTML = `
    <div class="self-map">
      <div class="self-core">
        <span>SELF</span>
        <strong>哦呼0_0</strong>
        <small>猎奇 / 记录 / 复盘 / 共创</small>
      </div>
      ${items
        .map(
          (item, index) => `
            <article class="self-card self-card-${index + 1}">
              <div class="self-card-head">
                <span>${escapeHtml(item.signal)}</span>
                <strong>${escapeHtml(item.metric)}</strong>
              </div>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.summary)}</p>
              <div class="self-tags">
                ${(item.items || []).map((tag) => `<span>${escapeHtml(tag)}</span>`).join("")}
              </div>
              <small>${escapeHtml(item.source)} · ${escapeHtml(item.unit)}</small>
            </article>
          `
        )
        .join("")}
    </div>
    <div class="hotword-console">
      <div class="hotword-panel">
        <span class="hotword-panel-label">ENFP Curiosity Cloud</span>
        <h3>把生活拆成可点击的热词</h3>
        <p>吃饭、游戏、心理学、阅读、健身、城市漫游、影像创作、怪知识和关系体验都可以成为自我数据入口。</p>
        <div class="hotword-detail" aria-live="polite">
          <span>${escapeHtml(firstHotword?.domain || "领域")}</span>
          <strong>${escapeHtml(firstHotword?.label || "热词")}</strong>
          <p>${escapeHtml(firstHotword?.note || "点击任意热词查看它如何成为主页里的一个自我切片。")}</p>
        </div>
      </div>
      <div class="hotword-cloud" aria-label="可点击兴趣热词">
        ${hotwords
          .map(
            (word, index) => `
              <button class="hotword-chip ${index === 0 ? "active" : ""}" type="button" data-index="${index}">
                ${escapeHtml(word.label)}
              </button>
            `
          )
          .join("")}
      </div>
    </div>
  `;
}

function renderJournals() {
  const journals = [...data.journals].sort((a, b) => b.written_at.localeCompare(a.written_at));
  const selected = journals[0];
  const monthDate = new Date(`${selected.written_at}T00:00:00`);
  const year = monthDate.getFullYear();
  const month = monthDate.getMonth();
  const firstDay = new Date(year, month, 1);
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const entryByDate = new Map(journals.map((entry) => [entry.written_at, entry]));
  const blanks = Array.from({ length: firstDay.getDay() }, () => `<span class="calendar-blank"></span>`);
  const days = Array.from({ length: daysInMonth }, (_, index) => {
    const day = index + 1;
    const dateKey = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    const entry = entryByDate.get(dateKey);
    const isSelected = selected.written_at === dateKey;
    if (!entry) {
      return `<span class="calendar-day muted">${day}</span>`;
    }
    return `
      <button class="calendar-day has-entry ${isSelected ? "active" : ""}" type="button" data-date="${dateKey}">
        <span>${day}</span>
      </button>
    `;
  });

  document.querySelector("#journalList").innerHTML = `
    <div class="journal-console">
      <div class="journal-calendar" aria-label="生活随笔日历">
        <div class="calendar-head">
          <span>Life Calendar</span>
          <strong>${year}.${String(month + 1).padStart(2, "0")}</strong>
        </div>
        <div class="calendar-weekdays" aria-hidden="true">
          <span>日</span><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span>
        </div>
        <div class="calendar-grid">${[...blanks, ...days].join("")}</div>
      </div>
      <article class="journal-reader" aria-live="polite">
        <span class="journal-reader-label">Selected Note</span>
        <time>${selected.written_at}</time>
        <h3>${escapeHtml(selected.title)}</h3>
        <p>${escapeHtml(selected.body)}</p>
      </article>
    </div>
  `;
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

  document.querySelector("#journalList").addEventListener("click", (event) => {
    const button = event.target.closest(".calendar-day.has-entry");
    if (!button) return;
    const entry = data.journals.find((item) => item.written_at === button.dataset.date);
    if (!entry) return;
    document.querySelectorAll(".calendar-day.has-entry").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(".journal-reader").innerHTML = `
      <span class="journal-reader-label">Selected Note</span>
      <time>${entry.written_at}</time>
      <h3>${escapeHtml(entry.title)}</h3>
      <p>${escapeHtml(entry.body)}</p>
    `;
  });

  document.querySelector("#selfConsole").addEventListener("click", (event) => {
    const button = event.target.closest(".hotword-chip");
    if (!button) return;
    const word = (data.self_hotwords || [])[Number(button.dataset.index)];
    if (!word) return;
    document.querySelectorAll(".hotword-chip").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    document.querySelector(".hotword-detail").innerHTML = `
      <span>${escapeHtml(word.domain)}</span>
      <strong>${escapeHtml(word.label)}</strong>
      <p>${escapeHtml(word.note)}</p>
    `;
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
  renderSelfDistillation();
  renderJournals();
  renderTimeline();
  renderWorks();
  renderMetrics();
  bindEvents();
}

init();
