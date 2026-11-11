// Single source of truth for the site index. Edit NAV to change the sidebar.
// Each item: [file in /lessons, English title, French title]
const NAV = [
  { en: "Session 1", fr: "Séance 1", num: "1", items: [
    ["s1-pensee-economique.html", "History of economic thought", "Histoire de la pensée économique"],
    ["s1-principes.html", "The 7 principles of economics", "Les 7 principes de l'économie"],
    ["s1-echange.html", "Trade & comparative advantage", "Échange et avantage comparatif"],
  ]},
  { en: "Coming up", fr: "À venir", items: [
    ["offre-demande.html", "Supply, demand & equilibrium", "Offre, demande et équilibre"],
    ["concurrence-parfaite.html", "Perfect competition", "Concurrence parfaite"],
    ["monopole.html", "Monopoly", "Monopole"],
    ["oligopole-jeux.html", "Oligopoly & game theory", "Oligopole et théorie des jeux"],
  ]},
];
(function () {
  const t = (en, fr) => `<span class="en">${en}</span><span class="fr">${fr}</span>`;
  const inLessons = location.pathname.includes("/lessons/");
  const root = inLessons ? "../" : "";
  const here = location.pathname.split("/").pop() || "index.html";
  const link = (href, label, num) =>
    `<a href="${href}"${href.split("/").pop() === here ? ' class="active"' : ""}>${num ? `<span class="num">${num}</span>` : ""}<span>${label}</span></a>`;

  const aside = document.createElement("aside");
  aside.className = "sidebar";
  aside.innerHTML =
    `<a class="brand" href="${root}index.html">${t("Microeconomics", "Microéconomie")}<small>MSG 1 · SBS / ULB</small></a><nav>` +
    link(root + "index.html", t("Home", "Accueil")) +
    link(root + "syllabus.html", t("Syllabus", "Programme du cours")) +
    NAV.map((s) => `<div class="nav-section">${t(s.en, s.fr)}</div>` +
      s.items.map(([f, en, fr], i) => link(root + "lessons/" + f, t(en, fr), s.num ? `${s.num}.${i + 1}` : "·")).join("")).join("") +
    `</nav>`;
  document.querySelector(".layout").prepend(aside);

  const btn = document.createElement("button");
  btn.className = "menu-btn";
  btn.innerHTML = "☰ " + t("Index", "Index");
  btn.onclick = () => aside.classList.toggle("open");
  document.body.prepend(btn);

  // Prev/next pager across all lessons
  const all = NAV.flatMap((s) => s.items);
  const i = all.findIndex(([f]) => f === here);
  if (i >= 0) {
    const p = all[i - 1], n = all[i + 1];
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
