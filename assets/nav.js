// Single source of truth for the site index. Edit this list to change the sidebar.
const LESSONS = [
  ["01-introduction.html", "Introduction & Scarcity"],
  ["02-supply-demand.html", "Supply and Demand"],
  ["03-elasticity.html", "Elasticity"],
  ["04-consumer-choice.html", "Consumer Choice & Utility"],
  ["05-production-costs.html", "Production and Costs"],
  ["06-perfect-competition.html", "Perfect Competition"],
  ["07-monopoly.html", "Monopoly"],
  ["08-oligopoly-game-theory.html", "Oligopoly & Game Theory"],
  ["09-factor-markets.html", "Factor Markets"],
  ["10-market-failures.html", "Market Failures & Public Goods"],
];
(function () {
  const inLessons = location.pathname.includes("/lessons/");
  const root = inLessons ? "../" : "";
  const here = location.pathname.split("/").pop() || "index.html";
  const link = (href, label, num) =>
    `<a href="${href}"${href.endsWith(here) ? ' class="active"' : ""}>${num ? `<span class="num">${num}</span>` : ""}<span>${label}</span></a>`;
  const aside = document.createElement("aside");
  aside.className = "sidebar";
  aside.innerHTML =
    `<a class="brand" href="${root}index.html">Microeconomics<small>Study notes</small></a><nav>` +
    link(root + "index.html", "Home") + link(root + "syllabus.html", "Syllabus") +
    `<div class="nav-section">Lessons</div>` +
    LESSONS.map(([f, t], i) => link(root + "lessons/" + f, t, String(i + 1).padStart(2, "0"))).join("") +
    `</nav>`;
  const layout = document.querySelector(".layout");
  layout.prepend(aside);
  const btn = document.createElement("button");
  btn.className = "menu-btn"; btn.textContent = "☰ Lessons";
  btn.onclick = () => aside.classList.toggle("open");
  document.body.prepend(btn);
  // Prev/next pager on lesson pages
  const i = LESSONS.findIndex(([f]) => f === here);
  if (i >= 0) {
    const p = LESSONS[i - 1], n = LESSONS[i + 1];
    const pager = document.createElement("div"); pager.className = "pager";
    pager.innerHTML = (p ? `<a href="${p[0]}">← ${p[1]}</a>` : "<span></span>") + (n ? `<a href="${n[0]}">${n[1]} →</a>` : "<span></span>");
    document.querySelector("main").append(pager);
  }
})();
