// Single source of truth for the site index. Edit this list to change the sidebar.
// Each entry: [file, English title, French title]
const LESSONS = [
  ["01-introduction.html", "Introduction & Scarcity", "Introduction et rareté"],
  ["02-supply-demand.html", "Supply and Demand", "Offre et demande"],
  ["03-elasticity.html", "Elasticity", "Élasticité"],
  ["04-consumer-choice.html", "Consumer Choice & Utility", "Choix du consommateur et utilité"],
  ["05-production-costs.html", "Production and Costs", "Production et coûts"],
  ["06-perfect-competition.html", "Perfect Competition", "Concurrence parfaite"],
  ["07-monopoly.html", "Monopoly", "Monopole"],
  ["08-oligopoly-game-theory.html", "Oligopoly & Game Theory", "Oligopole et théorie des jeux"],
  ["09-factor-markets.html", "Factor Markets", "Marchés des facteurs"],
  ["10-market-failures.html", "Market Failures & Public Goods", "Défaillances du marché et biens publics"],
];
(function () {
  const t = (en, fr) => `<span class="en">${en}</span><span class="fr">${fr}</span>`;
  const inLessons = location.pathname.includes("/lessons/");
  const root = inLessons ? "../" : "";
  const here = location.pathname.split("/").pop() || "index.html";
  const link = (href, label, num) =>
    `<a href="${href}"${href.endsWith(here) ? ' class="active"' : ""}>${num ? `<span class="num">${num}</span>` : ""}<span>${label}</span></a>`;

  const aside = document.createElement("aside");
  aside.className = "sidebar";
  aside.innerHTML =
    `<a class="brand" href="${root}index.html">${t("Microeconomics", "Microéconomie")}<small>${t("Study notes", "Notes d'étude")}</small></a><nav>` +
    link(root + "index.html", t("Home", "Accueil")) +
    link(root + "syllabus.html", t("Syllabus", "Programme du cours")) +
    `<div class="nav-section">${t("Lessons", "Leçons")}</div>` +
    LESSONS.map(([f, en, fr], i) => link(root + "lessons/" + f, t(en, fr), String(i + 1).padStart(2, "0"))).join("") +
    `</nav>`;
  document.querySelector(".layout").prepend(aside);

  const btn = document.createElement("button");
  btn.className = "menu-btn";
  btn.innerHTML = "☰ " + t("Lessons", "Leçons");
  btn.onclick = () => aside.classList.toggle("open");
  document.body.prepend(btn);

  // Prev/next pager on lesson pages
  const i = LESSONS.findIndex(([f]) => f === here);
  if (i >= 0) {
    const p = LESSONS[i - 1], n = LESSONS[i + 1];
    const pager = document.createElement("div");
    pager.className = "pager";
    pager.innerHTML =
      (p ? `<a href="${p[0]}">← ${t(p[1], p[2])}</a>` : "<span></span>") +
      (n ? `<a href="${n[0]}">${t(n[1], n[2])} →</a>` : "<span></span>");
    document.querySelector("main").append(pager);
  }

  // EN / FR switch (choice remembered in this browser)
  const sw = document.createElement("div");
  sw.className = "lang-switch";
  sw.innerHTML = `<button data-lang="en">EN</button><button data-lang="fr">FR</button>`;
  document.body.append(sw);
  const setLang = (lang) => {
    document.documentElement.lang = lang;
    sw.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", b.dataset.lang === lang));
    const title = document.querySelector("title");
    if (title.dataset[lang]) document.title = title.dataset[lang];
    try { localStorage.setItem("lang", lang); } catch (e) {}
  };
  sw.onclick = (e) => { if (e.target.dataset.lang) setLang(e.target.dataset.lang); };
  setLang(document.documentElement.lang === "fr" ? "fr" : "en");
})();
