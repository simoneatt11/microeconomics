"""Generates the bilingual study pages. Run: python3 -I build.py <site_dir>"""
import os, sys, math

SITE = sys.argv[1]
V = "5"  # bump to bust browser cache when CSS/JS change


def head(title_en, title_fr, root):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title data-en="{title_en} · Microeconomics" data-fr="{title_fr} · Microéconomie">{title_en} · Microeconomics</title>
<script>try{{if(localStorage.getItem("lang")==="fr")document.documentElement.lang="fr"}}catch(e){{}}</script>
<link rel="stylesheet" href="{root}assets/style.css?v={V}">
</head>
<body>
<div class="layout">
<main>
'''


def foot(root, extra=""):
    return f'''
</main>
</div>
<script src="{root}assets/nav.js?v={V}"></script>
{extra}
</body>
</html>
'''


def write(path, title, blocks, root="../", extra=""):
    """blocks: list of str (shared) or (en, fr) tuples."""
    out = [head(title[0], title[1], root)]
    for b in blocks:
        if isinstance(b, tuple):
            out.append(f'<div class="en">\n{b[0]}\n</div>\n<div class="fr">\n{b[1]}\n</div>\n')
        else:
            out.append(b)
    out.append(foot(root, extra))
    with open(os.path.join(SITE, path), "w") as f:
        f.write("".join(out))


def L(en, fr):
    return (en, fr)


def marker(mid):
    return f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" style="fill:var(--muted)"/></marker></defs>'


def vbar(x, top, w, base, cls):
    r = min(4, (base - top) / 2)
    return (f'<path class="{cls}" d="M{x},{base} V{top + r:.1f} Q{x},{top:.1f} {x + r},{top:.1f} '
            f'H{x + w - r} Q{x + w},{top:.1f} {x + w},{top + r:.1f} V{base} Z"/>')


def hbar(x0, x1, y, h, cls, rounded=True):
    r = min(4, (x1 - x0) / 2) if rounded else 0
    return (f'<path class="{cls}" d="M{x0},{y} H{x1 - r:.1f} Q{x1:.1f},{y} {x1:.1f},{y + r} '
            f'V{y + h - r} Q{x1:.1f},{y + h} {x1 - r:.1f},{y + h} H{x0} Z"/>')


# ------------------------------------------------------------------ diagrams

def svg_mc_mr(lang):
    q = "Quantity" if lang == "en" else "Quantité"
    mc, mr = ("MC", "MR") if lang == "en" else ("Cm", "Rm")
    more = "MC < MR: produce more →" if lang == "en" else "Cm < Rm : produire plus →"
    less = "← MC > MR: produce less" if lang == "en" else "← Cm > Rm : produire moins"
    opt = "Optimum: MC = MR" if lang == "en" else "Optimum : Cm = Rm"
    # MC line from (60,205) to (460,35); MR at y=110 -> x=283.5
    return f'''<svg viewBox="0 0 520 250" role="img" aria-label="{opt}">
<line class="axis" x1="50" y1="220" x2="490" y2="220"/><line class="axis" x1="50" y1="220" x2="50" y2="15"/>
<text x="490" y="238" text-anchor="end" class="muted small">{q}</text>
<text x="44" y="22" text-anchor="end" class="muted small">€</text>
<line class="line2" x1="60" y1="110" x2="470" y2="110"/><text x="474" y="114">{mr}</text>
<line class="line1" x1="60" y1="205" x2="460" y2="35"/><text x="464" y="34">{mc}</text>
<line class="axis" x1="283.5" y1="110" x2="283.5" y2="220" stroke-dasharray="4 4"/>
<text x="283.5" y="236" text-anchor="middle" class="bold">q*</text>
<circle cx="283.5" cy="110" r="5" class="c1 ring"/>
<text x="292" y="98" class="bold">{opt}</text>
<text x="70" y="160" class="muted small">{more}</text>
<text x="470" y="160" text-anchor="end" class="muted small">{less}</text>
</svg>'''


def svg_multiplier(lang):
    m = f"mul{lang}"
    nodes = {
        "en": ["Government spending", "Jobs created", "Income &amp; consumption ↑", "More jobs", "Economic growth ↑"],
        "fr": ["Dépenses de l'État", "Emplois créés", "Revenus et consommation ↑", "Emplois supplémentaires", "Croissance économique ↑"],
    }[lang]
    sub = {"en": "(public works)", "fr": "(grands travaux)"}[lang]
    centre = {"en": "Keynesian multiplier", "fr": "Multiplicateur keynésien"}[lang]
    pos = [(270, 40), (450, 120), (390, 245), (150, 245), (90, 120)]
    out = [f'<svg viewBox="0 0 540 290" role="img" aria-label="{centre}">', marker(m)]
    for i, (x, y) in enumerate(pos):
        nx, ny = pos[(i + 1) % 5]
        if i == 4:
            continue
        # shorten arrow ends
        dx, dy = nx - x, ny - y
        d = math.hypot(dx, dy)
        sx, sy = x + dx / d * 62, y + dy / d * 26
        ex, ey = nx - dx / d * 70, ny - dy / d * 28
        out.append(f'<line class="arrow" x1="{sx:.0f}" y1="{sy:.0f}" x2="{ex:.0f}" y2="{ey:.0f}" marker-end="url(#{m})"/>')
    # loop back from "More jobs" to "Income & consumption" is implied by the cycle; growth comes out of More jobs
    out.append(f'<path class="arrow" d="M130,222 Q100,190 92,146" marker-end="url(#{m})"/>')
    for i, (x, y) in enumerate(pos):
        cls = "boxa" if i in (0, 4) else "box"
        out.append(f'<rect class="{cls}" x="{x - 80}" y="{y - 22}" width="160" height="44" rx="8"/>')
        if i == 0:
            out.append(f'<text x="{x}" y="{y - 3}" text-anchor="middle" class="bold">{nodes[i]}</text><text x="{x}" y="{y + 13}" text-anchor="middle" class="muted small">{sub}</text>')
        else:
            out.append(f'<text x="{x}" y="{y + 4}" text-anchor="middle">{nodes[i]}</text>')
    out.append(f'<text x="270" y="150" text-anchor="middle" class="muted small">{centre}</text>')
    out.append(f'<path class="arrow" d="M330,252 Q270,285 210,252" stroke-dasharray="3 3" marker-end="url(#{m})"/>')
    out.append(f'<text x="270" y="284" text-anchor="middle" class="muted small">{"spending is re-spent…" if lang == "en" else "les dépenses sont re-dépensées…"}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_circular(lang):
    m = f"circ{lang}"
    lab = {
        "en": ["Design &amp; produce", "Use", "Repair &amp; reuse", "Recycle"],
        "fr": ["Concevoir et produire", "Utiliser", "Réparer et réutiliser", "Recycler"],
    }[lang]
    inn = {"en": "Fewer raw materials in", "fr": "Moins de matières premières"}[lang]
    out_ = {"en": "Less waste out", "fr": "Moins de déchets"}[lang]
    pos = [(270, 45), (440, 135), (270, 225), (100, 135)]
    s = [f'<svg viewBox="0 0 540 270" role="img" aria-label="circular economy">', marker(m)]
    s.append('<ellipse cx="270" cy="135" rx="170" ry="90" fill="none" style="stroke:var(--c1)" stroke-width="2" stroke-dasharray="2 6"/>')
    arcs = ["M345,52 Q420,70 440,108", "M440,162 Q420,205 345,220", "M195,220 Q120,205 100,162", "M100,108 Q120,70 195,52"]
    for a in arcs:
        s.append(f'<path class="arrow" d="{a}" marker-end="url(#{m})"/>')
    for i, (x, y) in enumerate(pos):
        s.append(f'<rect class="{"boxa" if i == 0 else "box"}" x="{x - 75}" y="{y - 18}" width="150" height="36" rx="8"/><text x="{x}" y="{y + 4}" text-anchor="middle">{lab[i]}</text>')
    s.append(f'<text x="270" y="131" text-anchor="middle" class="muted small">↓ {inn}</text>')
    s.append(f'<text x="270" y="149" text-anchor="middle" class="muted small">↓ {out_}</text>')
    s.append("</svg>")
    return "".join(s)


def svg_depletion(lang):
    groups = {
        "en": [("Energy", [("Natural gas", 2074), ("Oil", 2078), ("Uranium", 2115), ("Coal", 2165)]),
               ("Metals for low-carbon tech", [("Antimony", 2045), ("Lead", 2045), ("Rare earths", 2255)]),
               ("Other industrial metals", [("Zinc", 2044), ("Gold", 2044), ("Silver", 2051), ("Copper", 2068)])],
        "fr": [("Énergie", [("Gaz naturel", 2074), ("Pétrole", 2078), ("Uranium", 2115), ("Charbon", 2165)]),
               ("Métaux des technologies bas carbone", [("Antimoine", 2045), ("Plomb", 2045), ("Terres rares", 2255)]),
               ("Autres métaux industriels", [("Zinc", 2044), ("Or", 2044), ("Argent", 2051), ("Cuivre", 2068)])],
    }[lang]
    x0, x1, y0, y1 = 130, 560, 2025, 2260
    X = lambda yr: x0 + (yr - y0) * (x1 - x0) / (y1 - y0)
    rows = sum(1 + len(g[1]) for g in groups)
    H = rows * 22 + 40
    s = [f'<svg viewBox="0 0 600 {H}" role="img" aria-label="depletion horizons">']
    for yr in (2050, 2100, 2150, 2200, 2250):
        s.append(f'<line class="gridline" x1="{X(yr):.1f}" y1="8" x2="{X(yr):.1f}" y2="{H - 28}"/><text x="{X(yr):.1f}" y="{H - 12}" text-anchor="middle" class="muted small">{yr}</text>')
    s.append(f'<line class="axis" x1="{x0}" y1="8" x2="{x0}" y2="{H - 28}"/><text x="{x0}" y="{H - 12}" text-anchor="middle" class="muted small">2025</text>')
    y = 14
    for g, items in groups:
        s.append(f'<text x="0" y="{y + 10}" class="muted small bold">{g.upper()}</text>')
        y += 22
        for name, yr in items:
            yrs = yr - 2025
            tip = f"{name}: ~{yr} ({yrs} {'years' if lang == 'en' else 'ans'})"
            s.append(f'<g><title>{tip}</title><text x="{x0 - 8}" y="{y + 10}" text-anchor="end">{name}</text>{hbar(x0, X(yr), y, 14, "fill1")}<text x="{X(yr) + 6:.1f}" y="{y + 11}" class="small">{yr}</text></g>')
            y += 22
    s.append("</svg>")
    return "".join(s)


def svg_kalundborg(lang):
    E, W, M = "energy", "water", "mat"
    hub = {"en": ("Ørsted power station", "(Asnæs, hub)"), "fr": ("Centrale Ørsted", "(Asnæs, pivot)")}[lang]
    n = {
        "en": [("Refinery", "steam ⇄ cooling water", E), ("Town of Kalundborg", "waste heat → 3,500 homes", E),
               ("Novo Nordisk", "steam (insulin plant)", E), ("Novonesis", "steam (enzymes)", E),
               ("ARGO", "waste → energy", M), ("Avista Green", "used oils regenerated", M),
               ("Saint-Gobain Gyproc", "gypsum (historic, stopped)", M), ("Kalundborg Utility", "lake Tissø water", W),
               ("Kalundborg Bioenergi", "biogas / biomethane", E)],
        "fr": [("Raffinerie", "vapeur ⇄ eau de refroidissement", E), ("Ville de Kalundborg", "chaleur résiduelle → 3 500 logements", E),
               ("Novo Nordisk", "vapeur (insuline)", E), ("Novonesis", "vapeur (enzymes)", E),
               ("ARGO", "déchets → énergie", M), ("Avista Green", "huiles usagées régénérées", M),
               ("Saint-Gobain Gyproc", "gypse (historique, arrêté)", M), ("Kalundborg Utility", "eau du lac Tissø", W),
               ("Kalundborg Bioenergi", "biogaz / biométhane", E)],
    }[lang]
    cx, cy, rx, ry = 320, 215, 245, 165
    s = [f'<svg viewBox="0 0 640 430" role="img" aria-label="Kalundborg">']
    pts = []
    for k in range(9):
        a = math.radians(-90 + k * 40)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    style = {E: 'style="stroke:var(--c1)" stroke-width="2"', W: 'style="stroke:var(--c1)" stroke-width="2" stroke-dasharray="7 5"',
             M: 'style="stroke:var(--c2)" stroke-width="2" stroke-dasharray="2 4"'}
    for (x, y), (_, lab, kind) in zip(pts, n):
        s.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" {style[kind]}/>')
    for (x, y), (name, _, _) in zip(pts, n):
        w = max(110, len(name) * 7 + 16)
        s.append(f'<rect class="box" x="{x - w / 2:.0f}" y="{y - 15:.0f}" width="{w}" height="30" rx="7"/><text x="{x:.0f}" y="{y + 4:.0f}" text-anchor="middle">{name}</text>')
    for k, ((x, y), (_, lab, kind)) in enumerate(zip(pts, n)):
        fr = {4: 0.42, 5: 0.78, 2: 0.56, 7: 0.56}.get(k, 0.6)
        mx, my = cx + (x - cx) * fr, cy + (y - cy) * fr
        s.append(f'<text x="{mx:.0f}" y="{my - 5:.0f}" text-anchor="middle" class="small" style="paint-order:stroke;stroke:var(--panel);stroke-width:5px">{lab}</text>')
    s.append(f'<rect class="boxa" x="{cx - 85}" y="{cy - 24}" width="170" height="48" rx="9"/><text x="{cx}" y="{cy - 3}" text-anchor="middle" class="bold">{hub[0]}</text><text x="{cx}" y="{cy + 14}" text-anchor="middle" class="muted small">{hub[1]}</text>')
    s.append("</svg>")
    legend = {"en": ("Energy (steam, heat, gas)", "Water", "Materials &amp; waste"),
              "fr": ("Énergie (vapeur, chaleur, gaz)", "Eau", "Matières et déchets")}[lang]
    lg = (f'<div class="row" style="display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.85rem;margin-top:8px">'
          f'<span><svg width="30" height="8" style="display:inline;width:30px"><line x1="0" y1="4" x2="30" y2="4" {style[E]}/></svg> {legend[0]}</span>'
          f'<span><svg width="30" height="8" style="display:inline;width:30px"><line x1="0" y1="4" x2="30" y2="4" {style[W]}/></svg> {legend[1]}</span>'
          f'<span><svg width="30" height="8" style="display:inline;width:30px"><line x1="0" y1="4" x2="30" y2="4" {style[M]}/></svg> {legend[2]}</span></div>')
    return "".join(s) + lg


def svg_sneakers(lang):
    base, top = 210, 20
    sc = (base - top) / 320
    vals = [300, 150, 60]
    labs = {"en": ["1st pair", "2nd pair", "3rd pair"], "fr": ["1re paire", "2e paire", "3e paire"]}[lang]
    price = {"en": "Price: €120", "fr": "Prix : 120 €"}[lang]
    buy = {"en": ["buy ✓", "buy ✓", "don't buy ✗"], "fr": ["acheter ✓", "acheter ✓", "ne pas acheter ✗"]}[lang]
    yl = {"en": "Extra benefit (€)", "fr": "Bénéfice supplémentaire (€)"}[lang]
    s = [f'<svg viewBox="0 0 520 250" role="img" aria-label="marginal benefit vs price">']
    for v in (100, 200, 300):
        y = base - v * sc
        s.append(f'<line class="gridline" x1="60" y1="{y:.1f}" x2="500" y2="{y:.1f}"/><text x="54" y="{y + 4:.1f}" text-anchor="end" class="muted small">{v}</text>')
    s.append(f'<text x="0" y="12" class="muted small">{yl}</text>')
    s.append(f'<line class="axis" x1="60" y1="{base}" x2="500" y2="{base}"/>')
    for i, v in enumerate(vals):
        x = 100 + i * 135
        cls = "fill1" if v > 120 else "fill2"
        s.append(f'<g><title>{labs[i]}: {v} €</title>{vbar(x, base - v * sc, 70, base, cls)}</g>')
        s.append(f'<text x="{x + 35}" y="{base - v * sc - 6:.1f}" text-anchor="middle" class="bold">{v} €</text>')
        s.append(f'<text x="{x + 35}" y="{base + 16}" text-anchor="middle">{labs[i]}</text>')
        s.append(f'<text x="{x + 35}" y="{base + 32}" text-anchor="middle" class="muted small">{buy[i]}</text>')
    py = base - 120 * sc
    s.append(f'<line x1="60" y1="{py:.1f}" x2="500" y2="{py:.1f}" style="stroke:var(--text)" stroke-width="1.5" stroke-dasharray="6 4"/>')
    s.append(f'<text x="500" y="{py - 6:.1f}" text-anchor="end" class="bold">{price}</text>')
    s.append("</svg>")
    return "".join(s)


def svg_oppcost(lang):
    sc = 400 / 9000
    x0 = 170
    t = {"en": dict(a="A — SME shares (chosen)", b="B — Rental property", c="C — Government bonds",
                    oc="opportunity cost 6,000 €", g="real gain 3,000 €", bb="best alternative given up", cc="discarded"),
         "fr": dict(a="A — Parts de PME (retenu)", b="B — Immobilier locatif", c="C — Obligations d'État",
                    oc="coût d'opportunité 6 000 €", g="gain réel 3 000 €", bb="meilleure option sacrifiée", cc="écartée")}[lang]
    s = [f'<svg viewBox="0 0 600 160" role="img" aria-label="opportunity cost">']
    s.append(f'<text x="{x0 - 8}" y="30" text-anchor="end" class="bold">{t["a"]}</text>')
    s.append(hbar(x0, x0 + 6000 * sc - 1, 18, 18, "fill2", rounded=False))
    s.append(hbar(x0 + 6000 * sc + 1, x0 + 9000 * sc, 18, 18, "fill1"))
    s.append(f'<text x="{x0 + 3000 * sc}" y="52" text-anchor="middle" class="small">{t["oc"]}</text>')
    s.append(f'<text x="{x0 + 7500 * sc}" y="52" text-anchor="middle" class="small bold">{t["g"]}</text>')
    s.append(f'<text x="{x0 + 9000 * sc + 6}" y="31" class="small">9 000 €</text>')
    s.append(f'<text x="{x0 - 8}" y="92" text-anchor="end">{t["b"]}</text>{hbar(x0, x0 + 6000 * sc, 80, 18, "fillm")}<text x="{x0 + 6000 * sc + 6}" y="93" class="small">6 000 € · {t["bb"]}</text>')
    s.append(f'<text x="{x0 - 8}" y="132" text-anchor="end">{t["c"]}</text>{hbar(x0, x0 + 3000 * sc, 120, 18, "fillm")}<text x="{x0 + 3000 * sc + 6}" y="133" class="small">3 000 € · {t["cc"]}</text>')
    s.append(f'<line x1="{x0 + 6000 * sc}" y1="12" x2="{x0 + 6000 * sc}" y2="104" style="stroke:var(--text)" stroke-dasharray="3 3"/>')
    s.append("</svg>")
    return "".join(s)


def svg_ppf(lang, who):
    if who == "farmer":
        ymax, yticks, front = 4, [0, 1, 2, 3, 4], ((0, 2), (4, 0))
        aut, spec, trade = (2, 1), (4, 0), (3, 3)
        name = {"en": "Farmer", "fr": "Cultivateur"}[lang]
    else:
        ymax, yticks, front = 40, [0, 10, 20, 30, 40], ((0, 40), (5, 0))
        aut, spec, trade = (2.5, 20), (2, 24), (3, 21)
        name = {"en": "Rancher", "fr": "Éleveur"}[lang]
    X = lambda v: 45 + v * 47
    Y = lambda v: 200 - v * 180 / ymax
    xl = {"en": "Potatoes (kg)", "fr": "Pommes de terre (kg)"}[lang]
    yl = {"en": "Meat (kg)", "fr": "Viande (kg)"}[lang]
    s = [f'<svg viewBox="0 0 300 240" role="img" aria-label="{name}">']
    s.append(f'<text x="45" y="10" class="bold">{name}</text>')
    for v in yticks:
        s.append(f'<line class="gridline" x1="45" y1="{Y(v):.1f}" x2="285" y2="{Y(v):.1f}"/><text x="39" y="{Y(v) + 4:.1f}" text-anchor="end" class="muted small">{v}</text>')
    for v in range(6):
        s.append(f'<text x="{X(v)}" y="216" text-anchor="middle" class="muted small">{v}</text>')
    s.append(f'<line class="axis" x1="45" y1="200" x2="285" y2="200"/><line class="axis" x1="45" y1="200" x2="45" y2="18"/>')
    s.append(f'<text x="285" y="234" text-anchor="end" class="muted small">{xl}</text>')
    s.append(f'<text x="50" y="26" class="muted small">{yl}</text>')
    s.append(f'<line class="line1" x1="{X(front[0][0])}" y1="{Y(front[0][1])}" x2="{X(front[1][0])}" y2="{Y(front[1][1])}"/>')
    ax, ay = X(aut[0]), Y(aut[1])
    sx, sy = X(spec[0]), Y(spec[1])
    tx, ty = X(trade[0]), Y(trade[1])
    s.append(f'<line x1="{sx}" y1="{sy}" x2="{tx}" y2="{ty}" style="stroke:var(--muted)" stroke-dasharray="3 3"/>')
    s.append(f'<g><title>{"Autarky" if lang == "en" else "Autarcie"}: {aut}</title><circle cx="{ax}" cy="{ay}" r="5" style="fill:var(--panel);stroke:var(--text)" stroke-width="2"/></g>')
    s.append(f'<g><title>{"Specialisation" if lang == "en" else "Spécialisation"}: {spec}</title><rect x="{sx - 5}" y="{sy - 5}" width="10" height="10" class="c1 ring"/></g>')
    star = " ".join(f"{tx + (8 if i % 2 == 0 else 3.5) * math.cos(math.radians(-90 + i * 36)):.1f},{ty + (8 if i % 2 == 0 else 3.5) * math.sin(math.radians(-90 + i * 36)):.1f}" for i in range(10))
    s.append(f'<g><title>{"After trade" if lang == "en" else "Après échange"}: {trade}</title><polygon points="{star}" class="c2 ring"/></g>')
    fmt = lambda p: f"({str(p[0]).replace('.', ',') if lang == 'fr' else p[0]} ; {p[1]})" if lang == "fr" else f"({p[0]}, {p[1]})"
    s.append(f'<text x="{tx + 11}" y="{ty + 4}" class="small bold">{fmt(trade)}</text>')
    s.append(f'<text x="{ax + (-9 if who == "rancher" else 9)}" y="{ay + (16 if who == "rancher" else 4)}" text-anchor="{"end" if who == "rancher" else "start"}" class="small">{fmt(aut)}</text>')
    s.append("</svg>")
    return "".join(s)


def ppf_legend(lang):
    t = {"en": ("Production possibilities frontier", "Autarky (consume what you produce)", "Specialised production", "Consumption after trade"),
         "fr": ("Frontière des possibilités de production", "Autarcie (on consomme ce qu'on produit)", "Production spécialisée", "Consommation après échange")}[lang]
    return (f'<div style="display:flex;flex-wrap:wrap;gap:6px 18px;font-size:.85rem;margin-top:6px">'
            f'<span><svg width="22" height="10" style="display:inline;width:22px"><line x1="0" y1="5" x2="22" y2="5" class="line1"/></svg> {t[0]}</span>'
            f'<span><svg width="12" height="12" style="display:inline;width:12px"><circle cx="6" cy="6" r="4" style="fill:var(--panel);stroke:var(--text)" stroke-width="2"/></svg> {t[1]}</span>'
            f'<span><svg width="12" height="12" style="display:inline;width:12px"><rect x="1" y="1" width="10" height="10" class="c1"/></svg> {t[2]}</span>'
            f'<span><svg width="14" height="14" style="display:inline;width:14px"><polygon points="7,0 8.8,5 14,5 9.8,8.2 11.4,13.5 7,10.3 2.6,13.5 4.2,8.2 0,5 5.2,5" class="c2"/></svg> {t[3]}</span></div>')


# ------------------------------------------------------------------ page: history of economic thought

def page_pensee():
    b = []
    b.append(L(
        '<p class="kicker">Session 1 · Part A</p><h1>History of economic thought</h1><p class="lead">A quick tour of the four great schools — Classical, Neoclassical, Marxist, Keynesian — and of today\'s sustainable alternatives.</p>',
        '<p class="kicker">Séance 1 · Partie A</p><h1>Histoire de la pensée économique</h1><p class="lead">Survol des quatre grands courants — classique, néoclassique, marxiste, keynésien — et des alternatives durables d\'aujourd\'hui.</p>'))
    b.append(L(
        '''<div class="callout"><strong>Why start here?</strong>This course sits in the <b>liberal</b> tradition — the one closest to today's Western capitalist economies. Knowing where it comes from, and what its critics say, helps explain its limits: the financial crisis of 2008, the health crisis of 2020, and today's climate, energy and social crises.</div>
<h2>Four schools on one timeline</h2>
<div class="timeline">
<div class="ev"><div class="when">Late 18th century · 1st industrial revolution</div><b>Classical school</b> — Smith, Malthus, Ricardo. The market as a self-regulating order.</div>
<div class="ev"><div class="when">19th century · 2nd industrial revolution</div><b>Neoclassical school</b> — Walras, Pareto, Marshall. Optimisation, margins, equilibrium.<br><b>Marxist school</b> — Marx &amp; Engels. A radical critique of capitalism.</div>
<div class="ev"><div class="when">1930s · Great Depression</div><b>Keynesian school</b> — Keynes. The State steps in to correct crises.</div>
<div class="ev"><div class="when">Today</div><b>Sustainable alternatives</b> — circular economy, functional economy, industrial symbiosis.</div>
</div>
<div class="grid">
<div class="card"><span class="tag">Liberal current</span><h4>Classical + Neoclassical</h4><p>Closest to the current Western economic system. Two branches: Classical (Smith, Ricardo, 18th c.) and Neoclassical (Walras, Pareto, 19th c.).</p></div>
<div class="card"><span class="tag">Marxist current</span><h4>Radical critique</h4><p>Capitalism exploits the proletariat for the benefit of the bourgeoisie. Ideal: a society without classes or State.</p></div>
<div class="card"><span class="tag">Keynesian current</span><h4>Answer to market failures</h4><p>The State must intervene to correct crises (unemployment, depression). Keynes, 1930s.</p></div>
</div>''',
        '''<div class="callout"><strong>Pourquoi commencer ici ?</strong>Ce cours s'inscrit dans le courant <b>libéral</b> — le plus proche des économies capitalistes occidentales actuelles. Connaître ses origines et ses critiques aide à comprendre ses limites : crise financière de 2008, crise sanitaire de 2020, crises climatiques, énergétiques et sociales.</div>
<h2>Quatre courants sur une frise</h2>
<div class="timeline">
<div class="ev"><div class="when">Fin du 18ᵉ siècle · 1ʳᵉ révolution industrielle</div><b>Courant classique</b> — Smith, Malthus, Ricardo. Le marché, un ordre auto-régulé.</div>
<div class="ev"><div class="when">19ᵉ siècle · 2ᵉ révolution industrielle</div><b>Courant néoclassique</b> — Walras, Pareto, Marshall. Optimisation, raisonnement à la marge, équilibre.<br><b>Courant marxiste</b> — Marx et Engels. Une critique radicale du capitalisme.</div>
<div class="ev"><div class="when">Années 1930 · Grande Dépression</div><b>Courant keynésien</b> — Keynes. L'État intervient pour corriger les crises.</div>
<div class="ev"><div class="when">Aujourd'hui</div><b>Alternatives durables</b> — économie circulaire, économie de la fonctionnalité, symbiose industrielle.</div>
</div>
<div class="grid">
<div class="card"><span class="tag">Courant libéral</span><h4>Classique + néoclassique</h4><p>Le plus proche du système économique occidental actuel. Deux branches : classique (Smith, Ricardo, 18ᵉ s.) et néoclassique (Walras, Pareto, 19ᵉ s.).</p></div>
<div class="card"><span class="tag">Courant marxiste</span><h4>Critique radicale</h4><p>L'organisation capitaliste exploite le prolétariat au profit de la bourgeoisie. Idéal : une société sans classes ni État.</p></div>
<div class="card"><span class="tag">Courant keynésien</span><h4>Réponse aux défaillances du marché</h4><p>L'État doit intervenir pour corriger les crises (chômage, dépression). Keynes, années 1930.</p></div>
</div>'''))
    # Classical
    b.append(L(
        '''<h2><span class="badge">1</span>The Classical school</h2>
<p><b>Late 18th century</b>, first industrial revolution — <b>Adam Smith</b>, <b>Thomas Malthus</b>, <b>David Ricardo</b>.</p>
<div class="grid">
<div class="card"><h4>Homo œconomicus</h4><p>Every individual is a rational being who maximises well-being and minimises effort. Only they know what is good for them.</p></div>
<div class="card"><h4>Private property</h4><p>Economic freedom can only be guaranteed by private ownership of goods and of the means of production.</p></div>
<div class="card"><h4>The invisible hand</h4><p>Pursuing one's own interest serves the general interest, through the market. Adam Smith, <i>The Wealth of Nations</i> (1776).</p></div>
<div class="card"><h4>Anti-interventionism</h4><p>Any State intervention, even well-meant, can only have perverse consequences.</p></div>
</div>
<div class="callout"><strong>The invisible hand</strong>The mechanism by which individual actions driven by self-interest contribute — without intending to — to collective well-being and overall economic efficiency. By pursuing their own interest, each person benefits society more effectively than by trying to promote the common good directly.</div>
<p><b>Foundation of liberal capitalism:</b> individual self-interest, the self-regulating market and private property.</p>''',
        '''<h2><span class="badge">1</span>Le courant classique</h2>
<p><b>Fin du 18ᵉ siècle</b>, 1ʳᵉ révolution industrielle — <b>Adam Smith</b>, <b>Thomas Malthus</b>, <b>David Ricardo</b>.</p>
<div class="grid">
<div class="card"><h4>Homo œconomicus</h4><p>Tout individu est un être rationnel qui maximise son bien-être et minimise ses efforts. Seul lui sait ce qui est bon pour lui.</p></div>
<div class="card"><h4>Propriété privée</h4><p>La liberté économique ne peut être assurée que par la détention privée des biens et des moyens de production.</p></div>
<div class="card"><h4>La main invisible</h4><p>La recherche de l'intérêt particulier réalise l'intérêt général, via le marché. Adam Smith, <i>La Richesse des nations</i> (1776).</p></div>
<div class="card"><h4>Anti-interventionnisme</h4><p>Toute intervention de l'État, même à but louable, ne peut être que perverse dans ses conséquences.</p></div>
</div>
<div class="callout"><strong>La main invisible</strong>Mécanisme par lequel les actions individuelles guidées par l'intérêt personnel contribuent, sans que ce soit intentionnel, au bien-être collectif et à l'efficacité économique globale. En cherchant son propre intérêt, chacun bénéficie à la société plus efficacement qu'en cherchant à favoriser directement le bien commun.</div>
<p><b>Socle du capitalisme libéral :</b> l'intérêt individuel, le marché auto-régulateur et la propriété privée.</p>'''))
    # Neoclassical
    mu_rows = [(1, 10, 10), (2, 7, 17), (3, 4, 21), (4, 2, 23), (5, 0, 23)]
    tr = "".join(f'<tr><td class="num">{a}</td><td class="num">{b_}</td><td class="num">{c}</td></tr>' for a, b_, c in mu_rows)
    b.append(L(
        f'''<h2><span class="badge">2</span>The Neoclassical school</h2>
<p><b>Second half of the 19th century</b>, second industrial revolution — <b>Léon Walras</b>, <b>Vilfredo Pareto</b>, <b>Alfred Marshall</b>. Mathematics becomes central to economic analysis.</p>
<h3>Rationality &amp; calculation</h3>
<p>Every economic behaviour is the result of an explicit or implicit calculation. Individuals constantly optimise, given their constraints.</p>
<h3>Diminishing marginal utility</h3>
<p>Consumers maximise their utility subject to their income. <b>Marginal</b> utility (the satisfaction from one <i>extra</i> unit) is positive but falls with each unit. <b>Total</b> utility keeps rising — just more and more slowly.</p>
<div class="table-wrap"><table><thead><tr><th class="num">Slices of pizza</th><th class="num">Marginal utility</th><th class="num">Total utility</th></tr></thead><tbody>{tr}</tbody></table></div>
<p style="font-size:.85rem;color:var(--muted)">Illustrative numbers: marginal utility ≠ total utility.</p>
<h3>Market equilibrium: MC = MR</h3>
<p>Producers maximise profit subject to their costs. The optimum is reached where <b>marginal cost = marginal revenue</b>.</p>
<figure>{svg_mc_mr("en")}<figcaption>While an extra unit brings in more than it costs (MC &lt; MR), produce more; once it costs more than it brings in (MC &gt; MR), cut back. The optimum is where the two meet.</figcaption></figure>''',
        f'''<h2><span class="badge">2</span>Le courant néoclassique</h2>
<p><b>2ᵉ moitié du 19ᵉ siècle</b>, 2ᵉ révolution industrielle — <b>Léon Walras</b>, <b>Vilfredo Pareto</b>, <b>Alfred Marshall</b>. Les mathématiques deviennent centrales dans l'analyse économique.</p>
<h3>Rationalité et calcul</h3>
<p>Tout comportement économique relève d'un calcul explicite ou implicite. Les individus optimisent en permanence, compte tenu de leurs contraintes.</p>
<h3>Utilité marginale décroissante</h3>
<p>Les consommateurs maximisent leur utilité sous contrainte de revenu. L'utilité <b>marginale</b> (la satisfaction d'une unité <i>supplémentaire</i>) est positive mais décroissante. L'utilité <b>totale</b> continue d'augmenter — mais de plus en plus lentement.</p>
<div class="table-wrap"><table><thead><tr><th class="num">Parts de pizza</th><th class="num">Utilité marginale</th><th class="num">Utilité totale</th></tr></thead><tbody>{tr}</tbody></table></div>
<p style="font-size:.85rem;color:var(--muted)">Chiffres illustratifs : utilité marginale ≠ utilité totale.</p>
<h3>Équilibre de marché : Cm = Rm</h3>
<p>Les producteurs maximisent leur profit sous contrainte de coûts. L'optimum est atteint quand <b>coût marginal = recette marginale</b>.</p>
<figure>{svg_mc_mr("fr")}<figcaption>Tant qu'une unité supplémentaire rapporte plus qu'elle ne coûte (Cm &lt; Rm), on produit davantage ; dès qu'elle coûte plus qu'elle ne rapporte (Cm &gt; Rm), on réduit. L'optimum est à l'intersection.</figcaption></figure>'''))
    # Marxist
    b.append(L(
        '''<h2><span class="badge">3</span>The Marxist school</h2>
<p><b>19th century</b>, a critique of capitalism — <b>Karl Marx</b> &amp; <b>Friedrich Engels</b>, <i>Das Kapital</i> (1867).</p>
<div class="grid">
<div class="card"><span class="tag">The liberal promise</span><ul><li>Homo œconomicus maximises their interest</li><li>The invisible hand → common good</li><li>Private property = freedom</li><li>The State should not intervene</li></ul></div>
<div class="card"><span class="tag">The Marxist critique</span><ul><li>Capitalist organisation leads to the exploitation of the proletariat</li><li>Two classes: proletariat (labour) vs bourgeoisie (capital)</li><li>Rising inequality and internal contradictions of the system</li></ul></div>
</div>
<div class="grid">
<div class="card"><h4>The diagnosis</h4><p>Capitalist society exploits the majority for the profit of a minority that owns the means of production.</p></div>
<div class="card"><h4>The ideal</h4><p>A classless, Stateless society with collective management of the means of production: “from each according to their ability, to each according to their needs”.</p></div>
</div>''',
        '''<h2><span class="badge">3</span>Le courant marxiste</h2>
<p><b>19ᵉ siècle</b>, critique du capitalisme — <b>Karl Marx</b> et <b>Friedrich Engels</b>, <i>Le Capital</i> (1867).</p>
<div class="grid">
<div class="card"><span class="tag">La promesse libérale</span><ul><li>L'homo œconomicus maximise son intérêt</li><li>La main invisible → bien commun</li><li>Propriété privée = liberté</li><li>L'État ne doit pas intervenir</li></ul></div>
<div class="card"><span class="tag">La critique marxiste</span><ul><li>L'organisation capitaliste aboutit à l'exploitation du prolétariat</li><li>Deux classes : prolétariat (travail) vs bourgeoisie (capital)</li><li>Accroissement des inégalités et contradictions internes du système</li></ul></div>
</div>
<div class="grid">
<div class="card"><h4>Le constat</h4><p>La société capitaliste exploite la majorité pour le profit d'une minorité détenant les moyens de production.</p></div>
<div class="card"><h4>L'idéal</h4><p>Une société sans classes, sans État, avec gestion collective des moyens de production : « chacun contribue selon ses capacités, reçoit selon ses besoins ».</p></div>
</div>'''))
    # Keynesian
    b.append(L(
        f'''<h2><span class="badge">4</span>The Keynesian school</h2>
<p><b>1930s</b>, Great Depression — <b>John Maynard Keynes</b>, <i>The General Theory</i> (1936). Economic crises are <b>market failures</b>; the solution is State intervention (public spending substituting for private).</p>
<div class="grid">
<div class="card"><h4>① Consumption</h4><p>People fulfil themselves through consumption. <b>Demand is the engine of the economy.</b></p></div>
<div class="card"><h4>② Money is not neutral</h4><p>Economic agents prefer to hold liquidity. They only turn to saving if it is very well remunerated.</p></div>
<div class="card"><h4>③ The State can boost output</h4><p>By financing public works the State creates jobs and supports consumption… which creates further jobs.</p></div>
</div>
<figure>{svg_multiplier("en")}<figcaption>The Keynesian multiplier: an initial round of public spending is spent again and again, so total income rises by more than the initial outlay.</figcaption></figure>
<div class="callout"><strong>Barro's critique</strong>The multiplier may be an illusion: households anticipate the future tax rises needed to pay for the spending and save the extra income — the stimulus is neutralised.</div>''',
        f'''<h2><span class="badge">4</span>Le courant keynésien</h2>
<p><b>Années 1930</b>, Grande Dépression — <b>John Maynard Keynes</b>, <i>Théorie générale</i> (1936). Les crises économiques sont des <b>défaillances du marché</b> ; la solution est l'intervention de l'État (substitution du public au privé).</p>
<div class="grid">
<div class="card"><h4>① La consommation</h4><p>L'homme se réalise par la consommation. <b>La demande est le moteur de l'économie.</b></p></div>
<div class="card"><h4>② La monnaie n'est pas neutre</h4><p>Les agents préfèrent détenir des liquidités. Ils ne se tournent vers l'épargne que si elle est très bien rémunérée.</p></div>
<div class="card"><h4>③ L'État peut agir sur la production</h4><p>En finançant de grands travaux, l'État crée des emplois et favorise la consommation… ce qui crée de nouveaux emplois.</p></div>
</div>
<figure>{svg_multiplier("fr")}<figcaption>Le multiplicateur keynésien : une dépense publique initiale est dépensée à nouveau, encore et encore, si bien que le revenu total augmente davantage que la dépense de départ.</figcaption></figure>
<div class="callout"><strong>La critique de Barro</strong>L'effet multiplicateur serait un leurre : les ménages anticipent les hausses d'impôts futures nécessaires pour financer la dépense et épargnent le revenu supplémentaire — la relance est stérilisée.</div>'''))
    # Limits
    b.append(L(
        f'''<h2>Limits of the liberal model</h2>
<div class="grid">
<div class="card"><h4>The irrational ignored</h4><p>No room for emotions or intuition. Mathematical modelling takes priority over how people actually behave.</p></div>
<div class="card"><h4>Nature as an instrument</h4><p>Nature is a stock of resources that humans see themselves as masters of — with little concern for depleting scarce resources or the consequences of over-exploitation.</p></div>
<div class="card"><h4>Desires ≠ needs</h4><p>“Unlimited needs” are equated with material desires. Needs for esteem, affection and friendship are reduced to material things.</p></div>
</div>
<h3>Is the model sustainable?</h3>
<figure>{svg_depletion("en")}<figcaption>Year in which known reserves (2025) would run out at the current production rate. A reserve is not a fixed physical stock: it depends on price, technology and exploration. Sources: USGS, <i>Mineral Commodity Summaries 2025</i>; Energy Institute, <i>Statistical Review of World Energy</i>; NEA-IAEA, <i>Uranium 2024</i>.</figcaption></figure>''',
        f'''<h2>Limites du modèle libéral</h2>
<div class="grid">
<div class="card"><h4>L'irrationnel ignoré</h4><p>Aucune place pour les émotions ni l'intuition. La modélisation mathématique prime sur la réalité comportementale des agents.</p></div>
<div class="card"><h4>La nature instrumentalisée</h4><p>La nature est un stock de ressources dont l'être humain se considère comme maître — sans (ou avec trop peu d') inquiétude sur l'épuisement des ressources rares et les conséquences d'une surexploitation.</p></div>
<div class="card"><h4>Désirs ≠ besoins</h4><p>Les « besoins illimités » sont assimilés aux désirs matériels. Les besoins d'estime, d'affection, d'amitié sont réduits à des éléments matériels.</p></div>
</div>
<h3>Le modèle est-il soutenable ?</h3>
<figure>{svg_depletion("fr")}<figcaption>Année d'épuisement des réserves connues (2025) au rythme de production actuel. Une réserve n'est pas un stock physique fixe : elle dépend du prix, de la technologie et de l'exploration. Sources : USGS, <i>Mineral Commodity Summaries 2025</i> ; Energy Institute, <i>Statistical Review of World Energy</i> ; AEN-AIEA, <i>Uranium 2024</i>.</figcaption></figure>'''))
    # Alternatives
    b.append(L(
        f'''<h2>Alternatives</h2>
<h3>From a linear to a circular economy</h3>
<div class="flow"><span class="step">Extract</span><span class="arr">→</span><span class="step">Produce</span><span class="arr">→</span><span class="step">Use</span><span class="arr">→</span><span class="step">Throw away</span></div>
<figure>{svg_circular("en")}<figcaption><b>Circular economy</b>: produce goods and services sustainably by limiting resource use and waste — Reduce · Reuse · Recycle. Moving from a throw-away society to a more circular model.</figcaption></figure>
<div class="grid">
<div class="card"><h4>Functional economy</h4><p>Sell a <b>service</b> that fulfils the same function instead of selling the good itself. The product stays the producer's property; the <i>use</i> is billed.</p><p><b>Example:</b> Michelin billing truck fleets per kilometre driven instead of selling tyres.</p></div>
<div class="card"><h4>Industrial symbiosis</h4><p>One company's waste becomes another's resource. Pioneer: Kalundborg, Denmark, since 1972.</p></div>
</div>
<h3>Industrial symbiosis: Kalundborg (Denmark)</h3>
<figure>{svg_kalundborg("en")}<figcaption>Simplified view of the world's first industrial symbiosis network: 16 partners and 30+ flows of materials, water and energy (2025). The power station (biomass since 2019) was the historic hub. Watch the ARTE report: <a href="https://www.youtube.com/watch?v=ZryUzaJvKZg" target="_blank" rel="noopener">youtube.com/watch?v=ZryUzaJvKZg</a>.</figcaption></figure>''',
        f'''<h2>Alternatives</h2>
<h3>D'une économie linéaire à une économie circulaire</h3>
<div class="flow"><span class="step">Extraire</span><span class="arr">→</span><span class="step">Produire</span><span class="arr">→</span><span class="step">Consommer</span><span class="arr">→</span><span class="step">Jeter</span></div>
<figure>{svg_circular("fr")}<figcaption><b>Économie circulaire</b> : produire des biens et services durablement en limitant la consommation de ressources et les déchets — Réduire · Réutiliser · Recycler. Passer de la société du tout-jetable à un modèle plus circulaire.</figcaption></figure>
<div class="grid">
<div class="card"><h4>Économie de la fonctionnalité</h4><p>Remplacer la vente d'un bien par la vente d'un <b>service</b> remplissant les mêmes fonctions. Le produit reste propriété du producteur ; l'<i>usage</i> est facturé.</p><p><b>Exemple :</b> Michelin facture des flottes de camions au kilomètre parcouru plutôt que de vendre des pneus.</p></div>
<div class="card"><h4>Symbiose industrielle</h4><p>Les déchets d'une entreprise sont les ressources d'une autre. Pionnier : Kalundborg, Danemark, depuis 1972.</p></div>
</div>
<h3>Symbiose industrielle : Kalundborg (Danemark)</h3>
<figure>{svg_kalundborg("fr")}<figcaption>Vue simplifiée du premier réseau mondial de symbiose industrielle : 16 partenaires et plus de 30 flux de matières, d'eau et d'énergie (2025). La centrale (biomasse depuis 2019) en est le pivot historique. Reportage ARTE : <a href="https://www.youtube.com/watch?v=ZryUzaJvKZg" target="_blank" rel="noopener">youtube.com/watch?v=ZryUzaJvKZg</a>.</figcaption></figure>'''))
    # Quiz
    b.append(L(
        '''<h2>Check yourself</h2>
<details class="q"><summary>Which two branches make up the liberal current, and who are their key authors?</summary>Classical (Smith, Malthus, Ricardo — 18th c.) and Neoclassical (Walras, Pareto, Marshall — 19th c.).</details>
<details class="q"><summary>What does the “invisible hand” mean?</summary>Individuals pursuing their own interest end up, without intending it, serving the general interest through the market.</details>
<details class="q"><summary>A firm's marginal cost is €40 and its marginal revenue is €55. What should it do?</summary>Produce more: MC &lt; MR, so each extra unit adds €15 to profit. It stops increasing output when MC = MR.</details>
<details class="q"><summary>Explain the Keynesian multiplier and Barro's objection in two sentences.</summary>Public spending creates jobs and income that are spent again, so total income rises by more than the initial spending. Barro argues households expect higher future taxes and save the extra income, cancelling the effect.</details>
<details class="q"><summary>What is the difference between a circular economy and a functional economy?</summary>The circular economy reduces resource use and waste by reusing and recycling; the functional economy sells the use of a good (a service) rather than the good itself, e.g. tyres billed per kilometre.</details>''',
        '''<h2>Testez-vous</h2>
<details class="q"><summary>Quelles sont les deux branches du courant libéral et leurs principaux auteurs ?</summary>Classique (Smith, Malthus, Ricardo — 18ᵉ s.) et néoclassique (Walras, Pareto, Marshall — 19ᵉ s.).</details>
<details class="q"><summary>Que signifie la « main invisible » ?</summary>En poursuivant leur intérêt propre, les individus servent, sans le vouloir, l'intérêt général via le marché.</details>
<details class="q"><summary>Le coût marginal d'une entreprise est de 40 € et sa recette marginale de 55 €. Que doit-elle faire ?</summary>Produire davantage : Cm &lt; Rm, chaque unité supplémentaire ajoute 15 € au profit. Elle s'arrête quand Cm = Rm.</details>
<details class="q"><summary>Expliquez en deux phrases le multiplicateur keynésien et l'objection de Barro.</summary>La dépense publique crée des emplois et des revenus qui sont à leur tour dépensés : le revenu total augmente plus que la dépense initiale. Pour Barro, les ménages anticipent des hausses d'impôts et épargnent le revenu supplémentaire, ce qui annule l'effet.</details>
<details class="q"><summary>Quelle différence entre économie circulaire et économie de la fonctionnalité ?</summary>L'économie circulaire réduit la consommation de ressources et les déchets (réutiliser, recycler) ; l'économie de la fonctionnalité vend l'usage d'un bien (un service) plutôt que le bien lui-même, ex. pneus facturés au kilomètre.</details>'''))
    write("lessons/s1-pensee-economique.html", ("History of economic thought", "Histoire de la pensée économique"), b)


# ------------------------------------------------------------------ page: principles

def page_principes():
    b = []
    b.append(L(
        '<p class="kicker">Session 1 · Part B</p><h1>The 7 principles of economics</h1><p class="lead">The foundations of liberal economic reasoning: how people make decisions, and how they interact.</p>',
        '<p class="kicker">Séance 1 · Partie B</p><h1>Les 7 principes de l\'économie</h1><p class="lead">Les fondements du raisonnement économique libéral : comment les individus décident, et comment ils interagissent.</p>'))
    b.append(L(
        '''<div class="callout"><strong>Definition</strong>(Micro)economics studies the choices human beings make in society to satisfy <b>unlimited desires</b> with <b>scarce resources</b>.</div>
<div class="grid">
<div class="card"><span class="tag">How do people decide?</span><ul><li><b>1</b> People face trade-offs</li><li><b>2</b> The cost of something is what you give up (opportunity cost)</li><li><b>3</b> Rational people think at the margin</li><li><b>4</b> People respond to incentives</li></ul></div>
<div class="card"><span class="tag">How do people interact?</span><ul><li><b>5</b> Trade can make everyone better off</li><li><b>6</b> Markets usually organise economic activity efficiently</li><li><b>7</b> Governments can sometimes improve market outcomes</li></ul></div>
</div>
<p style="font-size:.9rem;color:var(--muted)">These principles come from neoclassical theory (19th century — Walras, Pigou…), where mathematics plays a central role.</p>''',
        '''<div class="callout"><strong>Définition</strong>La science (micro)économique étudie les choix que les êtres humains effectuent en société pour satisfaire leurs <b>désirs illimités</b> au moyen de <b>ressources rares</b>.</div>
<div class="grid">
<div class="card"><span class="tag">Comment les individus décident ?</span><ul><li><b>1</b> Les gens font des choix</li><li><b>2</b> Coût du renoncement (coût d'opportunité)</li><li><b>3</b> Raisonnement à la marge</li><li><b>4</b> Le rôle des incitations</li></ul></div>
<div class="card"><span class="tag">Comment ils interagissent ?</span><ul><li><b>5</b> L'échange peut être profitable à tous</li><li><b>6</b> Les marchés organisent efficacement l'économie</li><li><b>7</b> L'intervention publique peut améliorer les situations de marché</li></ul></div>
</div>
<p style="font-size:.9rem;color:var(--muted)">Ces principes viennent de la théorie néoclassique (19ᵉ siècle — Walras, Pigou…), où les mathématiques jouent un rôle central.</p>'''))
    b.append(L(
        '''<h2><span class="badge">1</span>People face trade-offs</h2>
<p>With scarce resources, every choice means giving something up. This is the founding principle of economic reasoning.</p>
<p class="quote">“There is no free lunch.” — Milton Friedman</p>
<div class="grid">
<div class="card"><h4>Consumer</h4><p>Choices under an income constraint:</p><ul><li>Leisure vs work</li><li>Saving vs consuming now</li><li>Basket A vs basket B</li></ul></div>
<div class="card"><h4>Producer</h4><p>Choices under a cost constraint:</p><ul><li>Machines vs labour</li><li>R&amp;D vs producing now</li><li>Good X vs good Y</li></ul></div>
</div>''',
        '''<h2><span class="badge">1</span>Les gens font des choix</h2>
<p>Face à des ressources rares, tout choix implique un renoncement. C'est le principe fondateur du raisonnement économique : pour obtenir une chose, il faut renoncer à une autre.</p>
<p class="quote">« There is no free lunch. » — Milton Friedman</p>
<div class="grid">
<div class="card"><h4>Consommateur</h4><p>Choix sous contrainte de revenu :</p><ul><li>Loisir vs travail</li><li>Épargne vs consommation immédiate</li><li>Panier A vs panier B</li></ul></div>
<div class="card"><h4>Producteur</h4><p>Choix sous contrainte de coûts :</p><ul><li>Machines vs main-d'œuvre</li><li>R&amp;D vs production immédiate</li><li>Bien X vs bien Y</li></ul></div>
</div>'''))
    b.append(L(
        f'''<h2><span class="badge">2</span>Opportunity cost</h2>
<p>Decisions require comparing the costs and benefits of each option. <b>Opportunity cost = what you give up by making a choice</b> — the value of the <i>best</i> alternative sacrificed.</p>
<h3>Worked example — €100,000 to invest for 5 years</h3>
<p>Three investments with comparable risk, horizon and liquidity. You choose A. What does that choice really cost?</p>
<div class="table-wrap"><table><thead><tr><th>Option</th><th class="num">Return</th><th class="num">Annual gain</th><th>Status</th></tr></thead><tbody>
<tr class="hl"><td>A — SME shares</td><td class="num">9 % / yr</td><td class="num">€9,000</td><td>Chosen ✓</td></tr>
<tr><td>B — Rental property</td><td class="num">6 % / yr</td><td class="num">€6,000</td><td>Best alternative given up</td></tr>
<tr><td>C — Government bonds</td><td class="num">3 % / yr</td><td class="num">€3,000</td><td>Discarded</td></tr></tbody></table></div>
<figure>{svg_oppcost("en")}<figcaption>The opportunity cost of A is €6,000/yr — the return of B, the best alternative given up (never B + C). A's real economic gain is 9,000 − 6,000 = <b>€3,000/yr</b>. The accounting trap: comparing A with “doing nothing” (+€9,000). The money always had another use.</figcaption></figure>
<div class="callout"><strong>Key point</strong>Opportunity cost is a way of reasoning, not a formula. It tells you <i>what</i> to compare — the best alternative given up. It does not tell you how to measure it: finance provides those tools (risk premium, NPV, illiquidity premium). Microeconomics asks the question; finance calibrates the numbers.</div>''',
        f'''<h2><span class="badge">2</span>Coût du renoncement (coût d'opportunité)</h2>
<p>Les décisions impliquent de comparer les coûts et bénéfices de chaque option. <b>Coût d'opportunité = ce à quoi on renonce en faisant un choix</b> — la valeur de la <i>meilleure</i> option sacrifiée.</p>
<h3>Exemple appliqué — 100 000 € à placer, horizon 5 ans</h3>
<p>Trois placements à risque, horizon et liquidité comparables. Vous retenez A. Quel est le vrai coût de ce choix ?</p>
<div class="table-wrap"><table><thead><tr><th>Option</th><th class="num">Rendement</th><th class="num">Gain annuel</th><th>Statut</th></tr></thead><tbody>
<tr class="hl"><td>A — Parts de PME</td><td class="num">9 % / an</td><td class="num">9 000 €</td><td>Retenu ✓</td></tr>
<tr><td>B — Immobilier locatif</td><td class="num">6 % / an</td><td class="num">6 000 €</td><td>Meilleure option sacrifiée</td></tr>
<tr><td>C — Obligations d'État</td><td class="num">3 % / an</td><td class="num">3 000 €</td><td>Écartée</td></tr></tbody></table></div>
<figure>{svg_oppcost("fr")}<figcaption>Coût d'opportunité du choix A = 6 000 €/an — le rendement de B, la meilleure option sacrifiée (jamais B + C). Gain économique réel de A = 9 000 − 6 000 = <b>3 000 €/an</b>. Le piège comptable : comparer A à « ne rien faire » (+9 000 €). L'argent avait toujours un autre emploi.</figcaption></figure>
<div class="callout"><strong>À retenir</strong>Le coût d'opportunité est un principe de raisonnement, pas une formule de calcul. Il dit <i>ce qu'il faut comparer</i> — la meilleure alternative sacrifiée. Il ne dit pas comment mesurer : c'est le rôle de la finance (prime de risque, VAN, prime d'illiquidité). La microéconomie pose la question, la finance calibre les chiffres.</div>'''))
    b.append(L(
        f'''<h2><span class="badge">3</span>Thinking at the margin</h2>
<p>Every decision is judged at its margin: compare the <b>extra benefit</b> with the <b>extra cost</b> it brings. <b>Keep going as long as marginal benefit exceeds marginal cost.</b> What matters is the effect of the decision, not what came before it.</p>
<h3>Consumer — how many identical pairs of sneakers at €120?</h3>
<figure>{svg_sneakers("en")}<figcaption>Buy while the next pair is worth more than €120: <b>2 pairs</b>. The 3rd pair brings €60 and costs €120 — it would destroy €60 of value.</figcaption></figure>
<h3>Firm — should it produce 1,000 more units?</h3>
<div class="stats"><div class="stat"><div class="v">€50</div><div class="l">Selling price / unit</div></div><div class="stat"><div class="v">€55</div><div class="l">Marginal cost / unit</div></div><div class="stat"><div class="v">€42</div><div class="l">Average cost / unit</div></div></div>
<p>Each extra unit brings in €50 and costs €55: −€5, i.e. <b>−€5,000</b>. Don't expand. The average cost being below the price says the business is profitable overall — <i>not</i> that it should produce more.</p>
<h3>Sunk costs never enter the decision</h3>
<div class="flow"><span class="step" style="opacity:.6">Already committed<br><small>(spent, invested, incurred)</small></span><span class="arr">⟶ ✗</span><span class="step key">DECISION now</span><span class="arr">→</span><span class="step">+ extra benefit<br>− extra cost</span></div>
<div class="callout"><strong>Key point</strong>The question is not “how much have I already spent?” but “what does this extra unit add to my goal?”. The past cannot be changed by any present choice. Marginal reasoning looks forward: compare changes, not totals.</div>''',
        f'''<h2><span class="badge">3</span>Raisonnement à la marge</h2>
<p>Toute décision se juge à sa marge : on compare le <b>bénéfice supplémentaire</b> et le <b>coût supplémentaire</b> qu'elle entraîne. <b>On agit tant que le bénéfice marginal dépasse le coût marginal.</b> Ce qui compte, c'est l'effet de la décision, pas ce qui l'a précédée.</p>
<h3>Consommateur — combien de paires de baskets identiques à 120 € ?</h3>
<figure>{svg_sneakers("fr")}<figcaption>J'achète tant que la paire suivante vaut plus de 120 € : <b>2 paires</b>. La 3e paire me rapporte 60 € et m'en coûte 120 € : je détruirais 60 € de valeur.</figcaption></figure>
<h3>Entreprise — faut-il produire 1 000 unités de plus ?</h3>
<div class="stats"><div class="stat"><div class="v">50 €</div><div class="l">Prix de vente / unité</div></div><div class="stat"><div class="v">55 €</div><div class="l">Coût marginal / unité</div></div><div class="stat"><div class="v">42 €</div><div class="l">Coût moyen / unité</div></div></div>
<p>Chaque unité en plus rapporte 50 € et coûte 55 € : −5 €, soit <b>−5 000 €</b>. Il ne faut pas produire plus. Le coût moyen sous le prix dit que l'activité est rentable — <i>pas</i> qu'il faut produire davantage.</p>
<h3>Ce qui est déjà dépensé n'entre jamais dans la décision</h3>
<div class="flow"><span class="step" style="opacity:.6">Déjà engagé<br><small>(dépensé, investi, subi)</small></span><span class="arr">⟶ ✗</span><span class="step key">DÉCISION maintenant</span><span class="arr">→</span><span class="step">+ bénéfice supplémentaire<br>− coût supplémentaire</span></div>
<div class="callout"><strong>À retenir</strong>La question n'est pas « combien ai-je déjà engagé ? » mais « qu'est-ce que cette unité supplémentaire ajoute à mon objectif ? ». Le passé est irrécupérable : aucun choix présent ne peut le modifier. Le raisonnement à la marge est tourné vers l'avant : on compare des variations, pas des totaux.</div>'''))
    b.append(L(
        '''<h2><span class="badge">4</span>People respond to incentives</h2>
<p>Changes in costs or benefits lead people to change their behaviour.</p>
<div class="flow"><span class="step">Stimulus: ↓ taxes on R&amp;D</span><span class="arr">→</span><span class="step key">Reaction: ↑ business innovation</span></div>''',
        '''<h2><span class="badge">4</span>Le rôle des incitations</h2>
<p>Les changements dans les coûts ou les bénéfices incitent les gens à modifier leur comportement.</p>
<div class="flow"><span class="step">Stimulus : ↓ impôts sur la R&amp;D</span><span class="arr">→</span><span class="step key">Réaction : ↑ innovation des entreprises</span></div>'''))
    b.append(L(
        '''<h2><span class="badge">5</span>Trade can make everyone better off</h2>
<p>Trade lets each party specialise in what they do best (see <a href="s1-echange.html">Trade &amp; comparative advantage</a>).</p>
<ul><li><b>Condition:</b> both parties must be free to refuse the exchange.</li><li><b>Nuance:</b> mutually beneficial ≠ necessarily fair.</li></ul>
<h2><span class="badge">6</span>Markets usually organise economic activity efficiently</h2>
<p>The decisions of producers and consumers are coordinated through prices. <b>The price is the central signal</b> sent to everyone.</p>
<div class="flow"><span class="step">Buyers</span><span class="arr">⇄</span><span class="step key">Price</span><span class="arr">⇄</span><span class="step">Sellers</span></div>
<p>A <b>market</b> is a group of buyers and sellers exchanging a good or service — possibly dematerialised (e-commerce, financial markets).</p>
<div class="callout"><strong>Market efficiency</strong>A market is efficient when no reallocation of resources could make someone better off without making someone else worse off (Pareto efficiency). Every resource is used where it is most valuable: no waste is possible. The market maximises the <b>size of the pie</b> — it says nothing about how the slices are shared: <b>efficiency ≠ equity</b>.</div>''',
        '''<h2><span class="badge">5</span>L'échange peut être profitable à tous</h2>
<p>L'échange permet à chacun de se spécialiser dans son domaine d'excellence (voir <a href="s1-echange.html">Échange et avantage comparatif</a>).</p>
<ul><li><b>Condition :</b> l'échange doit pouvoir être refusé par les deux parties.</li><li><b>Nuance :</b> mutuellement profitable ≠ nécessairement équitable.</li></ul>
<h2><span class="badge">6</span>Les marchés organisent efficacement l'économie</h2>
<p>Les décisions des producteurs et des consommateurs sont coordonnées via la fixation des prix. <b>Le prix est le signal central</b> transmis à tous les acteurs.</p>
<div class="flow"><span class="step">Acheteurs</span><span class="arr">⇄</span><span class="step key">Prix</span><span class="arr">⇄</span><span class="step">Vendeurs</span></div>
<p>Un <b>marché</b> est un groupe d'acheteurs et de vendeurs échangeant un bien ou un service — éventuellement dématérialisé (e-commerce, marchés financiers).</p>
<div class="callout"><strong>Efficacité d'un marché</strong>Un marché est efficace quand aucune réallocation des ressources ne pourrait améliorer la situation de quelqu'un sans dégrader celle d'un autre (efficacité de Pareto). Toutes les ressources sont employées là où elles rendent le plus de services : aucun gaspillage possible. Le marché maximise la <b>taille du gâteau</b> — il ne dit rien du partage des parts : <b>efficacité ≠ équité</b>.</div>'''))
    b.append(L(
        '''<h2><span class="badge">7</span>Governments can sometimes improve market outcomes</h2>
<div class="grid">
<div class="card"><h4>Externality</h4><p>Costs or benefits imposed on third parties who are not part of the transaction.</p><p><b>Positive:</b> a beekeeper's bees pollinate neighbouring fields for free.<br><b>Negative:</b> neonicotinoid insecticides wipe out bee colonies.</p></div>
<div class="card"><h4>Market power</h4><p>The ability of one actor to influence market conditions to its own advantage, at others' expense.</p><p><b>Example — monopoly:</b> a single seller sets a price above the competitive price and sells less.<br>Other forms: cartels, monopsony (single buyer), barriers to entry.</p></div>
</div>
<div class="flow"><span class="step">Market failure</span><span class="arr">→</span><span class="step">Economic inefficiency</span><span class="arr">→</span><span class="step key">Possible public intervention</span></div>
<p style="font-size:.9rem;color:var(--muted)">The bee case: neither the pollination service nor the damage goes through a price — that is the very definition of an externality.</p>''',
        '''<h2><span class="badge">7</span>L'intervention publique peut améliorer les situations de marché</h2>
<div class="grid">
<div class="card"><h4>Externalité</h4><p>Coûts ou bénéfices imposés à des tiers qui ne participent pas à la transaction.</p><p><b>Positive :</b> la pollinisation gratuite des champs voisins par les abeilles d'un apiculteur.<br><b>Négative :</b> les insecticides néonicotinoïdes déciment les colonies d'abeilles.</p></div>
<div class="card"><h4>Pouvoir de marché</h4><p>Capacité d'un acteur à influencer les conditions du marché à son avantage, au détriment des autres.</p><p><b>Exemple — le monopole :</b> un vendeur unique fixe un prix supérieur au prix concurrentiel et vend moins.<br>Autres formes : cartel, monopsone (acheteur unique), barrières à l'entrée.</p></div>
</div>
<div class="flow"><span class="step">Défaillance de marché</span><span class="arr">→</span><span class="step">Inefficacité économique</span><span class="arr">→</span><span class="step key">Intervention publique possible</span></div>
<p style="font-size:.9rem;color:var(--muted)">Le cas des abeilles : ni le service rendu ni le dommage causé ne passent par un prix — c'est toute la définition de l'externalité.</p>'''))
    b.append(L(
        '''<h2>Check yourself</h2>
<details class="q"><summary>You have 3 offers: a job paying €2,000, an internship paying €800 and a freelance gig paying €1,500. You take the job. What is the opportunity cost?</summary>€1,500 — the value of the best alternative given up (the freelance gig), not €800 + €1,500.</details>
<details class="q"><summary>You have paid €50 for a non-refundable concert ticket; on the day you would rather stay home. Should the €50 influence your decision?</summary>No. It is a sunk cost — it is spent whatever you do. Only compare the extra benefit of going with the extra cost (time, transport…).</details>
<details class="q"><summary>Price €50, marginal cost €55, average cost €42. Expand output?</summary>No. Each extra unit loses €5. A low average cost shows overall profitability, not that the next unit is worth producing.</details>
<details class="q"><summary>Why is “efficient” not the same as “fair”?</summary>Efficiency concerns the size of the pie (no waste, no possible Pareto improvement); fairness concerns how the pie is shared.</details>
<details class="q"><summary>Give one example of a positive externality and one of market power.</summary>Positive externality: bees pollinating neighbouring fields. Market power: a monopoly charging above the competitive price (also cartels, monopsony, entry barriers).</details>''',
        '''<h2>Testez-vous</h2>
<details class="q"><summary>Vous avez 3 offres : un emploi à 2 000 €, un stage à 800 € et une mission freelance à 1 500 €. Vous prenez l'emploi. Quel est le coût d'opportunité ?</summary>1 500 € — la valeur de la meilleure option sacrifiée (le freelance), et non 800 € + 1 500 €.</details>
<details class="q"><summary>Vous avez payé 50 € un billet de concert non remboursable ; le jour J, vous préféreriez rester chez vous. Les 50 € doivent-ils influencer votre décision ?</summary>Non. C'est un coût irrécupérable : il est dépensé quoi que vous fassiez. Comparez seulement le bénéfice supplémentaire d'y aller au coût supplémentaire (temps, transport…).</details>
<details class="q"><summary>Prix 50 €, coût marginal 55 €, coût moyen 42 €. Faut-il augmenter la production ?</summary>Non. Chaque unité supplémentaire fait perdre 5 €. Un coût moyen bas montre la rentabilité globale, pas l'intérêt de produire l'unité suivante.</details>
<details class="q"><summary>Pourquoi « efficace » ne veut-il pas dire « équitable » ?</summary>L'efficacité concerne la taille du gâteau (pas de gaspillage, aucune amélioration de Pareto possible) ; l'équité concerne le partage des parts.</details>
<details class="q"><summary>Donnez un exemple d'externalité positive et un de pouvoir de marché.</summary>Externalité positive : les abeilles qui pollinisent les champs voisins. Pouvoir de marché : un monopole qui fixe un prix supérieur au prix concurrentiel (aussi cartel, monopsone, barrières à l'entrée).</details>'''))
    write("lessons/s1-principes.html", ("The 7 principles of economics", "Les 7 principes de l'économie"), b)


# ------------------------------------------------------------------ page: trade & comparative advantage

TOT_WIDGET = '''<div class="tot" id="tot">
<b><span class="en">Try it: terms of trade</span><span class="fr">À vous : les termes de l'échange</span></b>
<p style="margin:6px 0 10px;font-size:.92rem"><span class="en">Move the slider to set the price of 1 kg of potatoes, in kg of meat. Who accepts?</span><span class="fr">Déplacez le curseur pour fixer le prix d'1 kg de pommes de terre, en kg de viande. Qui accepte ?</span></p>
<div style="font-size:1.4rem;font-weight:700">1 kg <span class="en">potatoes</span><span class="fr">PDT</span> = <span id="totp">3</span> kg <span class="en">meat</span><span class="fr">viande</span></div>
<input type="range" id="tots" min="0" max="1000" aria-label="price">
<svg viewBox="0 0 600 46" id="totsvg" aria-hidden="true"></svg>
<div class="row">
<span id="totr"></span><span id="totf"></span>
</div>
<div class="verdict" id="totv"></div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px">
<button type="button" data-p="0.3333">1/3</button><button type="button" data-p="3">3</button><button type="button" data-p="9">9</button>
</div>
</div>'''

TOT_JS = '''<script>
(function(){
  var MIN=0.2, MAX=12, s=document.getElementById("tots"), out=document.getElementById("totp"),
      svg=document.getElementById("totsvg"), r=document.getElementById("totr"), f=document.getElementById("totf"), v=document.getElementById("totv");
  var toP=function(x){return Math.exp(Math.log(MIN)+x/1000*(Math.log(MAX)-Math.log(MIN)));};
  var toX=function(p){return 1000*(Math.log(p)-Math.log(MIN))/(Math.log(MAX)-Math.log(MIN));};
  var px=function(p){return 20+toX(p)/1000*560;};
  var fmt=function(p){var fr=document.documentElement.lang==="fr";var n=p<1?p.toFixed(2):p.toFixed(1);return fr?n.replace(".",","):n;};
  var T=function(en,fr){return '<span class="en">'+en+'</span><span class="fr">'+fr+'</span>';};
  function axis(){
    var h='<rect x="'+px(0.5)+'" y="14" width="'+(px(8)-px(0.5))+'" height="10" rx="3" class="fill1" opacity=".35"/>'+
      '<line x1="20" y1="19" x2="580" y2="19" class="axis"/>';
    [0.25,0.5,1,2,3,5,8,12].forEach(function(t){h+='<line x1="'+px(t)+'" y1="14" x2="'+px(t)+'" y2="24" class="axis"/><text x="'+px(t)+'" y="40" text-anchor="middle" class="muted small">'+(t===0.25?"¼":t===0.5?"½":t)+'</text>';});
    return h;
  }
  function render(){
    var p=toP(+s.value); out.textContent=fmt(p);
    var rOk=p<8, fOk=p>0.5;
    svg.innerHTML=axis()+'<circle cx="'+px(p)+'" cy="19" r="7" class="c2 ring"/>';
    r.innerHTML=(rOk?'<span class="ok">✓</span> ':'<span class="no">✗</span> ')+T("Rancher pays "+fmt(p)+" kg meat for a potato that would cost him 8 to make","L'Éleveur paie "+fmt(p)+" kg de viande une PDT qui lui coûterait 8");
    f.innerHTML=(fOk?'<span class="ok">✓</span> ':'<span class="no">✗</span> ')+T("Farmer pays "+fmt(1/p)+" kg potatoes for meat that would cost him 2","Le Cultivateur paie "+fmt(1/p)+" kg de PDT une viande qui lui coûterait 2");
    v.innerHTML=(rOk&&fOk)?'<span class="ok">'+T("Deal: both pay less than their own production cost.","Accord : les deux paient moins que leur propre coût de production.")+'</span>':
      '<span class="no">'+T("No deal: outside the ½ – 8 range, one side refuses.","Pas d\\'accord : hors de la fourchette ½ – 8, l\\'un des deux refuse.")+'</span>';
  }
  s.addEventListener("input",render);
  document.querySelectorAll("#tot button").forEach(function(b){b.addEventListener("click",function(){s.value=toX(+b.dataset.p);render();});});
  s.value=toX(3); render();
})();
</script>'''


def page_echange():
    b = []
    b.append(L(
        '<p class="kicker">Session 1 · Part C</p><h1>Trade &amp; comparative advantage</h1><p class="lead">Why trading is mutually beneficial, and how specialisation according to comparative advantage creates a surplus.</p>',
        '<p class="kicker">Séance 1 · Partie C</p><h1>Interdépendance et avantage comparatif</h1><p class="lead">Pourquoi l\'échange est mutuellement profitable, et comment la spécialisation selon l\'avantage comparatif crée un surplus.</p>'))
    b.append(L(
        '''<h2>Why trade?</h2>
<div class="grid">
<div class="card"><span class="tag">Autarky</span><h4>Production = consumption</h4><p>Each agent produces everything they need. Consumption possibilities = production possibilities (PPF = CPF).</p><p>➜ Limited economic gains.</p></div>
<div class="card"><span class="tag">Multilateral exchange</span><h4>Generalised interdependence</h4><p>Specialisation according to comparative advantage; open markets.</p><p>➜ Mutual gains — but more complexity.</p></div>
</div>
<p><b>What holds world trade back today:</b> protectionism, dependence on fossil fuels, geopolitical tensions, climate change, inequality. Globalisation is being gradually questioned: interdependence creates gains, but also vulnerabilities.</p>
<div class="callout"><strong>Why is trade mutually beneficial?</strong>Allowing trade cannot make the initial situation worse… <b>as long as either side can refuse</b>. Trade is organised on the basis that best allocates scarce resources: <b>comparative advantage</b> (Ricardo's principle).</div>''',
        '''<h2>Pourquoi échanger ?</h2>
<div class="grid">
<div class="card"><span class="tag">Autarcie</span><h4>Production = consommation</h4><p>Chaque agent produit tout ce dont il a besoin. Frontière des possibilités de consommation = frontière de production (FPP = FPC).</p><p>➜ Gains économiques limités.</p></div>
<div class="card"><span class="tag">Échange multilatéral</span><h4>Interdépendance généralisée</h4><p>Spécialisation selon les avantages comparatifs ; ouverture des marchés.</p><p>➜ Gains mutuels — mais complexité accrue.</p></div>
</div>
<p><b>Ce qui freine aujourd'hui l'échange mondial :</b> protectionnisme, énergies fossiles, tensions géopolitiques, changement climatique, inégalités. La globalisation est progressivement remise en cause : l'interdépendance crée des gains, mais aussi des vulnérabilités.</p>
<div class="callout"><strong>Pourquoi l'échange est-il mutuellement profitable ?</strong>Parce que permettre l'échange ne peut pas détériorer la situation initiale… <b>si la possibilité de refus reste ouverte</b>. L'échange s'organise sur la base qui optimise l'allocation des ressources rares : l'<b>avantage comparatif</b> (principe de Ricardo).</div>'''))
    b.append(L(
        '''<h2>The model</h2>
<div class="grid">
<div class="card"><span class="tag">2 goods</span><h4>Potatoes &amp; meat</h4></div>
<div class="card"><span class="tag">2 people</span><h4>Farmer &amp; rancher</h4></div>
<div class="card"><span class="tag">Mixed tastes</span><h4>Both want both goods</h4></div>
<div class="card"><span class="tag">Time constraint</span><h4>40 hours a week max</h4></div>
</div>
<p>A <b>productivity table</b> gives the hours needed to produce one unit of each good (or the units produced per hour).</p>
<div class="table-wrap"><table><thead><tr><th>Hours to produce 1 kg</th><th class="num">Meat</th><th class="num">Potatoes</th></tr></thead><tbody>
<tr><td>Farmer</td><td class="num">20 h</td><td class="num">10 h</td></tr>
<tr><td>Rancher</td><td class="num">1 h</td><td class="num">8 h</td></tr></tbody></table></div>
<p>With 40 hours, the farmer can make at most <b>4 kg of potatoes</b> or <b>2 kg of meat</b>; the rancher at most <b>5 kg of potatoes</b> or <b>40 kg of meat</b>. In autarky each splits their time 20 h / 20 h.</p>''',
        '''<h2>Le modèle</h2>
<div class="grid">
<div class="card"><span class="tag">2 biens</span><h4>Pommes de terre et viande</h4></div>
<div class="card"><span class="tag">2 personnes</span><h4>Cultivateur et éleveur</h4></div>
<div class="card"><span class="tag">Goûts mixtes</span><h4>Chacun veut les deux biens</h4></div>
<div class="card"><span class="tag">Contrainte de temps</span><h4>40 h max par semaine</h4></div>
</div>
<p>Un <b>tableau de productivité</b> donne les heures nécessaires pour produire une unité de chaque bien (ou le nombre d'unités produites par heure).</p>
<div class="table-wrap"><table><thead><tr><th>Heures pour produire 1 kg</th><th class="num">Viande</th><th class="num">Pommes de terre</th></tr></thead><tbody>
<tr><td>Cultivateur</td><td class="num">20 h</td><td class="num">10 h</td></tr>
<tr><td>Éleveur</td><td class="num">1 h</td><td class="num">8 h</td></tr></tbody></table></div>
<p>Avec 40 heures, le cultivateur peut produire au maximum <b>4 kg de PDT</b> ou <b>2 kg de viande</b> ; l'éleveur au maximum <b>5 kg de PDT</b> ou <b>40 kg de viande</b>. En autarcie, chacun partage son temps 20 h / 20 h.</p>'''))
    b.append(L(
        '''<h2>Absolute or comparative advantage?</h2>
<div class="grid">
<div class="card"><span class="tag">Adam Smith · 18th c.</span><h4>Absolute advantage</h4><p>Compares <b>productivity</b>: who needs fewer inputs to make one unit?</p><p>Meat: rancher 1 h vs farmer 20 h. Potatoes: rancher 8 h vs farmer 10 h.<br>➜ The rancher has the absolute advantage in <b>both</b> goods. This criterion does not say who should specialise in what.</p></div>
<div class="card"><span class="tag">David Ricardo · 19th c.</span><h4>Comparative advantage</h4><p>Compares <b>opportunity costs</b>: what does each give up to make one unit?</p><p>1 kg of potatoes costs the farmer ½ kg of meat, the rancher 8 kg.<br>➜ The farmer has the comparative advantage in potatoes. <b>This is what drives specialisation and trade.</b></p></div>
</div>
<h3>Opportunity costs, good by good</h3>
<div class="table-wrap"><table><thead><tr><th>Opportunity cost of 1 kg of…</th><th class="num">Meat</th><th class="num">Potatoes</th></tr></thead><tbody>
<tr><td>Farmer</td><td class="num">20 h → 2 kg potatoes</td><td class="num">★ 10 h → ½ kg meat</td></tr>
<tr><td>Rancher</td><td class="num">★ 1 h → ⅛ kg potatoes</td><td class="num">8 h → 8 kg meat</td></tr></tbody></table></div>
<p>★ = lowest opportunity cost → comparative advantage. The rancher gives up 16× less to make meat (⅛ &lt; 2); the farmer gives up 16× less to make potatoes (½ &lt; 8).</p>
<div class="callout"><strong>The rule</strong>Whoever has the lower opportunity cost has the comparative advantage in that good. The two advantages necessarily fall on opposite sides — nobody can give up less in both goods at once. So there is always room for specialisation, and therefore always a gain from trade. Being better at everything does not remove the gains from trading.</div>''',
        '''<h2>Avantage absolu ou avantage comparatif ?</h2>
<div class="grid">
<div class="card"><span class="tag">Adam Smith · 18ᵉ s.</span><h4>Avantage absolu</h4><p>Compare la <b>productivité</b> : qui a besoin du moins d'inputs pour produire 1 unité ?</p><p>Viande : éleveur 1 h vs cultivateur 20 h. PDT : éleveur 8 h vs cultivateur 10 h.<br>➜ L'éleveur a l'avantage absolu dans les <b>deux</b> biens. Ce critère ne dit pas qui doit se spécialiser dans quoi.</p></div>
<div class="card"><span class="tag">David Ricardo · 19ᵉ s.</span><h4>Avantage comparatif</h4><p>Compare les <b>coûts d'opportunité</b> : à quoi chacun renonce-t-il pour produire 1 unité ?</p><p>1 kg de PDT coûte ½ kg de viande au cultivateur, 8 kg à l'éleveur.<br>➜ Le cultivateur a l'avantage comparatif en PDT. <b>C'est ce critère qui fonde la spécialisation et l'échange.</b></p></div>
</div>
<h3>Coûts d'opportunité, bien par bien</h3>
<div class="table-wrap"><table><thead><tr><th>Coût d'opportunité d'1 kg de…</th><th class="num">Viande</th><th class="num">Pommes de terre</th></tr></thead><tbody>
<tr><td>Cultivateur</td><td class="num">20 h → 2 kg de PDT</td><td class="num">★ 10 h → ½ kg de viande</td></tr>
<tr><td>Éleveur</td><td class="num">★ 1 h → ⅛ kg de PDT</td><td class="num">8 h → 8 kg de viande</td></tr></tbody></table></div>
<p>★ = coût d'opportunité le plus faible → avantage comparatif. L'éleveur renonce à 16× moins pour produire de la viande (⅛ &lt; 2) ; le cultivateur renonce à 16× moins pour produire des PDT (½ &lt; 8).</p>
<div class="callout"><strong>La règle</strong>Celui dont le coût d'opportunité est le plus faible détient l'avantage comparatif dans ce bien. Les deux avantages tombent nécessairement dans des camps opposés : personne ne peut renoncer à moins dans les deux biens à la fois. Il y a donc toujours une spécialisation possible — et toujours un gain à l'échange. Être meilleur en tout n'empêche pas d'avoir intérêt à échanger.</div>'''))
    b.append(L(
        '''<h2>Specialise, then trade: before / after</h2>
<div class="flow"><span class="step"><b>Step 1 — specialise</b><br>Farmer: 40 h → 4 kg potatoes<br>Rancher: 24 h → 24 kg meat, 16 h → 2 kg potatoes</span><span class="arr">→</span><span class="step"><b>Step 2 — trade</b><br>Farmer gives 1 kg potatoes<br>Rancher gives 3 kg meat</span></div>
<div class="table-wrap"><table><thead><tr><th></th><th class="num">Autarky</th><th class="num">Produces (specialised)</th><th class="num">After trade</th><th class="num">Gain</th></tr></thead><tbody>
<tr><td><b>Farmer</b> — potatoes</td><td class="num">2 kg</td><td class="num">4 kg</td><td class="num">3 kg</td><td class="num ok">+1 kg</td></tr>
<tr><td><b>Farmer</b> — meat</td><td class="num">1 kg</td><td class="num">0 kg</td><td class="num">3 kg</td><td class="num ok">+2 kg</td></tr>
<tr><td><b>Rancher</b> — potatoes</td><td class="num">2.5 kg</td><td class="num">2 kg</td><td class="num">3 kg</td><td class="num ok">+0.5 kg</td></tr>
<tr><td><b>Rancher</b> — meat</td><td class="num">20 kg</td><td class="num">24 kg</td><td class="num">21 kg</td><td class="num ok">+1 kg</td></tr></tbody></table></div>
<div class="stats"><div class="stat"><div class="v">25.5 → 30</div><div class="l">total units produced, same 80 hours</div></div><div class="stat"><div class="v">+18 %</div><div class="l">surplus created by specialisation</div></div></div>
<p>Same 40 hours each, same technology. The only change is moving labour towards the good with the lower opportunity cost. <b>Specialisation creates the surplus; trade shares it.</b></p>''',
        '''<h2>Se spécialiser, puis échanger : avant / après</h2>
<div class="flow"><span class="step"><b>Étape 1 — spécialisation</b><br>Cultivateur : 40 h → 4 kg de PDT<br>Éleveur : 24 h → 24 kg de viande, 16 h → 2 kg de PDT</span><span class="arr">→</span><span class="step"><b>Étape 2 — échange</b><br>Le cultivateur cède 1 kg de PDT<br>L'éleveur cède 3 kg de viande</span></div>
<div class="table-wrap"><table><thead><tr><th></th><th class="num">Autarcie</th><th class="num">Produit (spéc.)</th><th class="num">Après échange</th><th class="num">Gain</th></tr></thead><tbody>
<tr><td><b>Cultivateur</b> — PDT</td><td class="num">2 kg</td><td class="num">4 kg</td><td class="num">3 kg</td><td class="num ok">+1 kg</td></tr>
<tr><td><b>Cultivateur</b> — viande</td><td class="num">1 kg</td><td class="num">0 kg</td><td class="num">3 kg</td><td class="num ok">+2 kg</td></tr>
<tr><td><b>Éleveur</b> — PDT</td><td class="num">2,5 kg</td><td class="num">2 kg</td><td class="num">3 kg</td><td class="num ok">+0,5 kg</td></tr>
<tr><td><b>Éleveur</b> — viande</td><td class="num">20 kg</td><td class="num">24 kg</td><td class="num">21 kg</td><td class="num ok">+1 kg</td></tr></tbody></table></div>
<div class="stats"><div class="stat"><div class="v">25,5 → 30</div><div class="l">unités produites au total, mêmes 80 heures</div></div><div class="stat"><div class="v">+18 %</div><div class="l">surplus créé par la spécialisation</div></div></div>
<p>Les 40 h de chacun sont inchangées, la technologie aussi. Le seul changement est la réallocation du travail vers le bien au coût d'opportunité le plus faible. <b>La spécialisation crée le surplus ; l'échange le partage.</b></p>'''))
    b.append(L(
        f'''<h2>Trade takes you beyond the production frontier</h2>
<figure><div class="grid" style="margin:0">{svg_ppf("en", "farmer")}{svg_ppf("en", "rancher")}</div>{ppf_legend("en")}<figcaption>Both stars lie <b>above</b> the production possibilities frontier: neither producer could reach that basket alone, however they split their 40 hours. Specialisation moves the point <i>along</i> the frontier; trade takes it <i>beyond</i>. Each consumes more of both goods than in autarky — without working an extra hour.</figcaption></figure>''',
        f'''<h2>L'échange fait sortir de la frontière de production</h2>
<figure><div class="grid" style="margin:0">{svg_ppf("fr", "farmer")}{svg_ppf("fr", "rancher")}</div>{ppf_legend("fr")}<figcaption>Les deux étoiles sont <b>au-dessus</b> de la frontière des possibilités de production : aucun des deux ne pouvait atteindre ce panier seul, quelle que soit la répartition de ses 40 heures. La spécialisation déplace le point <i>le long</i> de la courbe ; c'est l'échange qui le fait <i>franchir</i>. Chacun consomme davantage des deux biens qu'en autarcie — sans travailler une heure de plus.</figcaption></figure>'''))
    b.append(L(
        '''<h2>Terms of trade: at what price?</h2>
<p><b>Rule:</b> each side agrees to “buy” the good it produces badly only if it pays less than it would cost to make it themselves.</p>
<ul><li>The rancher would never pay more than <b>8 kg of meat</b> for 1 kg of potatoes (his own cost).</li><li>The farmer would never accept less than <b>½ kg of meat</b> for 1 kg of potatoes (his own cost).</li></ul>
<p>➜ <b>Range of agreement: between ½ and 8 kg of meat per kg of potatoes.</b></p>''',
        '''<h2>Termes de l'échange : à quel prix ?</h2>
<p><b>Règle :</b> chacun accepte d'« acheter » le bien qu'il produit mal à condition de le payer moins cher que ce qu'il lui coûterait de le produire lui-même.</p>
<ul><li>L'éleveur ne paiera jamais plus de <b>8 kg de viande</b> pour 1 kg de PDT (son propre coût).</li><li>Le cultivateur n'acceptera jamais moins de <b>½ kg de viande</b> pour 1 kg de PDT (son propre coût).</li></ul>
<p>➜ <b>Fourchette d'accord : entre ½ et 8 kg de viande par kg de PDT.</b></p>'''))
    b.append(TOT_WIDGET)
    b.append(L(
        '''<p style="font-size:.9rem;color:var(--muted)">Try the presets: <b>3</b> (accepted, the price used in the course), <b>9</b> (the rancher refuses: 9 &gt; 8) and <b>1/3</b> (the farmer refuses: he would pay 3 kg of potatoes for meat that costs him 2).</p>
<h2>Three lessons from comparative advantage</h2>
<div class="grid">
<div class="card"><h4>1 · Specialisation is almost always possible</h4><p>Unless both producers have exactly the same opportunity cost, one of them always has the comparative advantage in one good.</p></div>
<div class="card"><h4>2 · It raises total output</h4><p>If everyone focuses on the good they give up least to produce, total output rises — with unchanged resources (25.5 → 30 units, +18 %).</p></div>
<div class="card"><h4>3 · Trade only pays at certain prices</h4><p>Opportunity costs bound the acceptable price: here, between ½ and 8 kg of meat per kg of potatoes.</p></div>
</div>
<h2>Globalisation in question</h2>
<p>Three economists who favour free trade have qualified the result — and the facts have followed.</p>
<div class="grid">
<div class="card"><span class="tag">Samuelson · 2005</span><h4>Rich countries can lose out</h4><p>A partner's technological catch-up can worsen the advanced country's terms of trade.</p></div>
<div class="card"><span class="tag">Krugman · 2007</span><h4>Inequality between sectors</h4><p>Gains are aggregate; losses are concentrated on certain jobs and regions.</p></div>
<div class="card"><span class="tag">Summers · 2016</span><h4>Redistribution matters</h4><p>Without a way to share the gains, political support for openness erodes.</p></div>
</div>
<div class="stats"><div class="stat"><div class="v">7.1 %</div><div class="l">annual growth of world trade volume, 1987–2007</div></div><div class="stat"><div class="v">3.0 %</div><div class="l">since 2012 — “slowbalisation” (World Bank, IMF 2016)</div></div></div>
<p>Shocks along the way: the 2008 financial crisis, Covid, geopolitical tensions. <b>Takeaway:</b> globalisation produces aggregate gains but potentially individual losers — how the gains are distributed remains central.</p>''',
        '''<p style="font-size:.9rem;color:var(--muted)">Essayez les préréglages : <b>3</b> (accepté, le prix retenu dans le cours), <b>9</b> (l'éleveur refuse : 9 &gt; 8) et <b>1/3</b> (le cultivateur refuse : il paierait 3 kg de PDT une viande qui lui coûte 2).</p>
<h2>Trois enseignements de l'avantage comparatif</h2>
<div class="grid">
<div class="card"><h4>1 · La spécialisation est quasi systématique</h4><p>À moins que les deux producteurs aient exactement le même coût d'opportunité, l'un d'eux détient toujours l'avantage comparatif dans l'un des biens.</p></div>
<div class="card"><h4>2 · Elle augmente la production totale</h4><p>Si chacun se consacre au bien pour lequel il renonce au moins, le volume total s'élève — à ressources inchangées (25,5 → 30 unités, +18 %).</p></div>
<div class="card"><h4>3 · L'échange n'est profitable qu'à certains prix</h4><p>Les coûts d'opportunité bornent le prix acceptable : ici, entre ½ et 8 kg de viande par kg de PDT.</p></div>
</div>
<h2>La mondialisation en question</h2>
<p>Trois économistes favorables au libre-échange ont nuancé le résultat — et les faits ont suivi.</p>
<div class="grid">
<div class="card"><span class="tag">Samuelson · 2005</span><h4>Les pays riches peuvent s'appauvrir</h4><p>Le rattrapage technologique d'un partenaire peut dégrader les termes de l'échange du pays avancé.</p></div>
<div class="card"><span class="tag">Krugman · 2007</span><h4>Inégalités entre secteurs</h4><p>Les gains sont agrégés ; les pertes sont concentrées sur certains métiers et territoires.</p></div>
<div class="card"><span class="tag">Summers · 2016</span><h4>La redistribution compte</h4><p>Sans mécanisme de partage des gains, le soutien politique à l'ouverture s'érode.</p></div>
</div>
<div class="stats"><div class="stat"><div class="v">7,1 %</div><div class="l">croissance annuelle du volume des échanges mondiaux, 1987-2007</div></div><div class="stat"><div class="v">3,0 %</div><div class="l">depuis 2012 — « slowbalisation » (Banque mondiale, FMI 2016)</div></div></div>
<p>Chocs en chemin : crise financière de 2008, Covid, tensions géopolitiques. <b>À retenir :</b> la mondialisation génère des gains agrégés mais potentiellement des perdants individuels — la question de la distribution des gains reste centrale.</p>'''))
    b.append(L(
        '''<h2>Check yourself</h2>
<details class="q"><summary>Ana makes a cake in 2 h or a shirt in 4 h. Ben makes a cake in 3 h or a shirt in 3 h. Who has the comparative advantage in cakes?</summary>Ana. Her opportunity cost of 1 cake is ½ shirt (2 h / 4 h); Ben's is 1 shirt. Ben has the comparative advantage in shirts (1 cake vs Ana's 2 cakes).</details>
<details class="q"><summary>In the course example, why does the rancher trade even though he is more productive at everything?</summary>Because what matters is opportunity cost. Making potatoes costs him 8 kg of meat each; buying them from the farmer at 3 kg of meat is cheaper.</details>
<details class="q"><summary>Would “1 kg of potatoes for 10 kg of meat” work?</summary>No. 10 &gt; 8: the rancher would pay more than his own cost of making potatoes, so he refuses.</details>
<details class="q"><summary>Where does the surplus come from: specialisation or trade?</summary>Specialisation creates it (25.5 → 30 units); trade lets both share it and consume beyond their own frontier.</details>
<details class="q"><summary>Absolute vs comparative advantage in one sentence each.</summary>Absolute: who needs fewer inputs to make a good (productivity). Comparative: who gives up less of other goods to make it (opportunity cost) — the one that drives specialisation.</details>''',
        '''<h2>Testez-vous</h2>
<details class="q"><summary>Ana fait un gâteau en 2 h ou une chemise en 4 h. Ben fait un gâteau en 3 h ou une chemise en 3 h. Qui a l'avantage comparatif en gâteaux ?</summary>Ana. Son coût d'opportunité d'1 gâteau est ½ chemise (2 h / 4 h) ; celui de Ben, 1 chemise. Ben a l'avantage comparatif en chemises (1 gâteau contre 2 pour Ana).</details>
<details class="q"><summary>Dans l'exemple du cours, pourquoi l'éleveur échange-t-il alors qu'il est plus productif en tout ?</summary>Parce que c'est le coût d'opportunité qui compte. Produire une PDT lui coûte 8 kg de viande ; l'acheter au cultivateur pour 3 kg est moins cher.</details>
<details class="q"><summary>« 1 kg de PDT contre 10 kg de viande » : accord possible ?</summary>Non. 10 &gt; 8 : l'éleveur paierait plus que son propre coût de production des PDT, il refuse.</details>
<details class="q"><summary>D'où vient le surplus : de la spécialisation ou de l'échange ?</summary>La spécialisation le crée (25,5 → 30 unités) ; l'échange permet de le partager et de consommer au-delà de sa propre frontière.</details>
<details class="q"><summary>Avantage absolu vs comparatif, une phrase chacun.</summary>Absolu : qui a besoin du moins d'inputs pour produire un bien (productivité). Comparatif : qui renonce au moins aux autres biens pour le produire (coût d'opportunité) — c'est lui qui guide la spécialisation.</details>'''))
    write("lessons/s1-echange.html", ("Trade & comparative advantage", "Échange et avantage comparatif"), b, extra=TOT_JS)


# ------------------------------------------------------------------ syllabus, home, upcoming

def page_syllabus():
    b = [L(
        '''<p class="kicker">MSG · 1st year · Solvay Brussels School (ULB)</p><h1>Syllabus</h1><p class="lead">Microeconomics — Thierry Lallemand, PhD in Economics (ULB, 2006), lecturer at SBS since 2008.</p>
<h2>Practical organisation</h2>
<div class="grid">
<div class="card"><h4>Sessions</h4><p>6 to 7 in-person, interactive sessions, 18:15 – 21:00.</p></div>
<div class="card"><h4>Course material</h4><p>PDF slides on the course page, available before each session.</p></div>
<div class="card"><h4>Wooclap</h4><p>Live polls, Q&amp;A and exercises — on your phone or laptop.</p></div>
</div>
<h2>Course objectives</h2>
<ul><li><b>Understand</b> — tools to understand the behaviour of economic agents and their interactions in a free system of exchange of goods and services.</li>
<li><b>Analyse &amp; critique</b> — understand, then critique, the principles put forward by “liberal” economists on key microeconomic questions: agents' behaviour, the roles and structures of markets, how equilibrium forms.</li></ul>
<div class="grid">
<div class="card"><span class="tag">Demand for goods &amp; services</span><h4>Consumers</h4><p>Individual choices · income constraints · trade-offs</p></div>
<div class="card"><span class="tag">Supply &amp; production</span><h4>Firms &amp; institutions</h4><p>Role in markets · costs · production structures</p></div>
<div class="card"><span class="tag">Exchange</span><h4>Markets</h4><p>Structures · equilibrium · price formation</p></div>
</div>
<h2>Course structure</h2>
<div class="flow"><span class="step key">1 · Schools of thought</span><span class="arr">→</span><span class="step key">2 · Liberal foundations</span><span class="arr">→</span><span class="step">3 · Market economy<br><small>supply &amp; demand → equilibrium</small></span><span class="arr">→</span><span class="step">4 · Market structures<br><small>perfect competition · monopoly · oligopoly</small></span><span class="arr">→</span><span class="step">5 · Game theory<br><small>strategy &amp; oligopoly</small></span></div>
<p><b>Microeconomics</b> studies individual behaviour and interactions between agents in markets (consumers, firms, markets). <b>Macroeconomics</b> analyses the economy as a whole and its performance (growth, employment, unemployment, inflation…).</p>
<h2>Sessions</h2>
<div class="table-wrap"><table><thead><tr><th>Session</th><th>Topics</th></tr></thead><tbody>
<tr><td><b>1</b></td><td><a href="lessons/s1-pensee-economique.html">History of economic thought</a> · <a href="lessons/s1-principes.html">The 7 principles</a> · <a href="lessons/s1-echange.html">Trade &amp; comparative advantage</a></td></tr>
<tr><td><b>2</b></td><td><a href="lessons/s2-offre-demande.html">Supply, demand &amp; equilibrium</a> · <a href="lessons/s2-elasticite.html">Elasticity</a></td></tr><tr><td><b>3</b></td><td><a href="lessons/s3-consommateur.html">Consumer choice</a></td></tr><tr><td><b>4</b></td><td><a href="lessons/s4-couts.html">Production costs</a> · <a href="lessons/s4-concurrence-parfaite.html">The firm in perfect competition</a></td></tr><tr><td>5 →</td><td style="color:var(--muted)">To be added as the course progresses</td></tr></tbody></table></div>
<h2>Reference books</h2>
<ul><li>Mankiw, N. G. — <i>Principes de l'économie</i>, Economica</li><li>Jurion, B. — <i>Économie politique</i>, De Boeck</li><li>Pindyck, R. &amp; Rubinfeld, D. — <i>Microéconomie</i>, Pearson</li><li>Krugman, P. &amp; Wells, R. — <i>Microéconomie</i>, De Boeck</li></ul>''',
        '''<p class="kicker">MSG · 1ʳᵉ année · Solvay Brussels School (ULB)</p><h1>Programme du cours</h1><p class="lead">Microéconomie — Thierry Lallemand, docteur en économie (ULB, 2006), maître de conférences à la SBS depuis 2008.</p>
<h2>Organisation pratique</h2>
<div class="grid">
<div class="card"><h4>Séances</h4><p>6 à 7 séances interactives en présentiel, 18h15 – 21h00.</p></div>
<div class="card"><h4>Supports de cours</h4><p>Slides PDF sur la page de l'UV, disponibles avant chaque séance.</p></div>
<div class="card"><h4>Wooclap</h4><p>Sondages, Q&amp;R et exercices en direct — sur smartphone ou PC.</p></div>
</div>
<h2>Objectifs du cours</h2>
<ul><li><b>Comprendre</b> — des outils pour comprendre le comportement des agents économiques et leurs interactions au sein d'un système libre d'échange de biens et services.</li>
<li><b>Analyser / critiquer</b> — comprendre, puis critiquer, les principes avancés par les économistes « libéraux » sur quelques problématiques microéconomiques : comportement des agents, rôles et structures des marchés, formation d'un équilibre.</li></ul>
<div class="grid">
<div class="card"><span class="tag">Demande de biens et services</span><h4>Consommateurs</h4><p>Choix individuels · contraintes de revenu · arbitrages</p></div>
<div class="card"><span class="tag">Offre et production</span><h4>Entreprises et institutions</h4><p>Rôle sur les marchés · coûts · structures de production</p></div>
<div class="card"><span class="tag">Échanges</span><h4>Marchés</h4><p>Structures · équilibre · formation des prix</p></div>
</div>
<h2>Structure du cours</h2>
<div class="flow"><span class="step key">1 · Courants de pensée</span><span class="arr">→</span><span class="step key">2 · Fondements libéraux</span><span class="arr">→</span><span class="step">3 · Économie de marché<br><small>offre et demande → équilibre</small></span><span class="arr">→</span><span class="step">4 · Structures de marché<br><small>CPP · monopole · oligopole</small></span><span class="arr">→</span><span class="step">5 · Théorie des jeux<br><small>stratégie et oligopole</small></span></div>
<p>La <b>microéconomie</b> étudie les comportements individuels et les interactions entre agents sur les marchés (consommateurs, entreprises, marchés). La <b>macroéconomie</b> analyse le fonctionnement d'un système économique dans sa globalité et sa performance (croissance, emploi, chômage, inflation…).</p>
<h2>Séances</h2>
<div class="table-wrap"><table><thead><tr><th>Séance</th><th>Thèmes</th></tr></thead><tbody>
<tr><td><b>1</b></td><td><a href="lessons/s1-pensee-economique.html">Histoire de la pensée économique</a> · <a href="lessons/s1-principes.html">Les 7 principes</a> · <a href="lessons/s1-echange.html">Échange et avantage comparatif</a></td></tr>
<tr><td><b>2</b></td><td><a href="lessons/s2-offre-demande.html">Offre, demande et équilibre</a> · <a href="lessons/s2-elasticite.html">L'élasticité</a></td></tr><tr><td><b>3</b></td><td><a href="lessons/s3-consommateur.html">Le choix du consommateur</a></td></tr><tr><td><b>4</b></td><td><a href="lessons/s4-couts.html">Les coûts de production</a> · <a href="lessons/s4-concurrence-parfaite.html">La firme en concurrence parfaite</a></td></tr><tr><td>5 →</td><td style="color:var(--muted)">À compléter au fil du cours</td></tr></tbody></table></div>
<h2>Ouvrages de référence</h2>
<ul><li>Mankiw, N. G. — <i>Principes de l'économie</i>, Economica</li><li>Jurion, B. — <i>Économie politique</i>, De Boeck</li><li>Pindyck, R. et Rubinfeld, D. — <i>Microéconomie</i>, Pearson</li><li>Krugman, P. et Wells, R. — <i>Microéconomie</i>, De Boeck</li></ul>''')]
    write("syllabus.html", ("Syllabus", "Programme du cours"), b, root="")


def page_home():
    b = [L(
        '''<p class="kicker">MSG · 1st year · SBS / ULB</p><h1>Microeconomics</h1><p class="lead">A study companion for the course: notes, diagrams and self-check questions for each session.</p>
<h2>Session 1 — Introduction</h2>
<div class="grid">
<a class="card" href="lessons/s1-pensee-economique.html" style="text-decoration:none;color:inherit"><span class="tag">1.1</span><h4>History of economic thought</h4><p>Classical, Neoclassical, Marxist, Keynesian — and sustainable alternatives.</p></a>
<a class="card" href="lessons/s1-principes.html" style="text-decoration:none;color:inherit"><span class="tag">1.2</span><h4>The 7 principles</h4><p>Trade-offs, opportunity cost, marginal thinking, incentives, trade, markets, government.</p></a>
<a class="card" href="lessons/s1-echange.html" style="text-decoration:none;color:inherit"><span class="tag">1.3</span><h4>Trade &amp; comparative advantage</h4><p>Ricardo's model, production frontiers and terms of trade — with an interactive.</p></a>
</div>
<h2>Session 2 — Markets</h2>
<div class="grid">
<a class="card" href="lessons/s2-offre-demande.html" style="text-decoration:none;color:inherit"><span class="tag">2.1</span><h4>Supply, demand &amp; equilibrium</h4><p>Determinants, market demand, shifts vs movements, equilibrium and comparative statics — with a price slider.</p></a>
<a class="card" href="lessons/s2-elasticite.html" style="text-decoration:none;color:inherit"><span class="tag">2.2</span><h4>Elasticity</h4><p>Price, cross, income and supply elasticities; measurement; pricing and revenue — with an interactive.</p></a>
</div>
<h2>Session 3 — The consumer</h2>
<div class="grid">
<a class="card" href="lessons/s3-consommateur.html" style="text-decoration:none;color:inherit"><span class="tag">3.1</span><h4>Consumer choice</h4><p>Preferences, indifference curves, MRS, budget line, optimum and behavioural critiques — with an interactive.</p></a>
</div>
<h2>Session 4 — The firm</h2>
<div class="grid">
<a class="card" href="lessons/s4-couts.html" style="text-decoration:none;color:inherit"><span class="tag">4.1</span><h4>Production costs</h4><p>Factor combinations, cost curves, isoquants, returns and economies of scale.</p></a>
<a class="card" href="lessons/s4-concurrence-parfaite.html" style="text-decoration:none;color:inherit"><span class="tag">4.2</span><h4>The firm in perfect competition</h4><p>p = MC, shutdown rule, long-run equilibrium, electricity merit order — with an interactive.</p></a>
</div>
<p>See the <a href="syllabus.html">Syllabus</a> for the course organisation and reading list. Use the <b>EN / FR</b> switch at the top right to change language.</p>''',
        '''<p class="kicker">MSG · 1ʳᵉ année · SBS / ULB</p><h1>Microéconomie</h1><p class="lead">Un compagnon d'étude pour le cours : notes, schémas et questions d'auto-évaluation pour chaque séance.</p>
<h2>Séance 1 — Introduction</h2>
<div class="grid">
<a class="card" href="lessons/s1-pensee-economique.html" style="text-decoration:none;color:inherit"><span class="tag">1.1</span><h4>Histoire de la pensée économique</h4><p>Classiques, néoclassiques, marxistes, keynésiens — et alternatives durables.</p></a>
<a class="card" href="lessons/s1-principes.html" style="text-decoration:none;color:inherit"><span class="tag">1.2</span><h4>Les 7 principes</h4><p>Choix, coût d'opportunité, raisonnement à la marge, incitations, échange, marchés, État.</p></a>
<a class="card" href="lessons/s1-echange.html" style="text-decoration:none;color:inherit"><span class="tag">1.3</span><h4>Échange et avantage comparatif</h4><p>Le modèle de Ricardo, les frontières de production et les termes de l'échange — avec un module interactif.</p></a>
</div>
<h2>Séance 2 — Les marchés</h2>
<div class="grid">
<a class="card" href="lessons/s2-offre-demande.html" style="text-decoration:none;color:inherit"><span class="tag">2.1</span><h4>Offre, demande et équilibre</h4><p>Déterminants, demande de marché, mouvements vs déplacements, équilibre et statique comparative — avec un curseur de prix.</p></a>
<a class="card" href="lessons/s2-elasticite.html" style="text-decoration:none;color:inherit"><span class="tag">2.2</span><h4>L'élasticité</h4><p>Élasticités prix, croisée, revenu et de l'offre ; mesure ; prix et chiffre d'affaires — avec un module interactif.</p></a>
</div>
<h2>Séance 3 — Le consommateur</h2>
<div class="grid">
<a class="card" href="lessons/s3-consommateur.html" style="text-decoration:none;color:inherit"><span class="tag">3.1</span><h4>Le choix du consommateur</h4><p>Préférences, courbes d'indifférence, TMS, droite de budget, optimum et critiques comportementales — avec un module interactif.</p></a>
</div>
<h2>Séance 4 — La firme</h2>
<div class="grid">
<a class="card" href="lessons/s4-couts.html" style="text-decoration:none;color:inherit"><span class="tag">4.1</span><h4>Les coûts de production</h4><p>Combinaison des facteurs, courbes de coûts, isoquantes, rendements et économies d'échelle.</p></a>
<a class="card" href="lessons/s4-concurrence-parfaite.html" style="text-decoration:none;color:inherit"><span class="tag">4.2</span><h4>La firme en concurrence parfaite</h4><p>p = Cm, seuil de fermeture, équilibre de long terme, merit order de l'électricité — avec un module interactif.</p></a>
</div>
<p>Consultez le <a href="syllabus.html">Programme du cours</a> pour l'organisation et la bibliographie. Utilisez le bouton <b>EN / FR</b> en haut à droite pour changer de langue.</p>''')]
    write("index.html", ("Home", "Accueil"), b, root="")


def page_upcoming(f, en, fr, topics_en, topics_fr):
    b = [L(
        f'<p class="kicker">Coming up</p><h1>{en}</h1><p class="lead">This session has not been covered yet.</p><h2>Expected topics</h2><ul>{"".join(f"<li>{t}</li>" for t in topics_en)}</ul><div class="placeholder">Notes will be added after the session.</div>',
        f'<p class="kicker">À venir</p><h1>{fr}</h1><p class="lead">Cette séance n\'a pas encore eu lieu.</p><h2>Thèmes prévus</h2><ul>{"".join(f"<li>{t}</li>" for t in topics_fr)}</ul><div class="placeholder">Les notes seront ajoutées après la séance.</div>')]
    write("lessons/" + f, (en, fr), b)


# ================================================================== SESSION 2

def num(x, lang, d=2):
    s = f"{x:.{d}f}".rstrip("0").rstrip(".") if d else f"{x:.0f}"
    return s.replace(".", ",") if lang == "fr" else s


def chart(lang, xmax, ymax, xticks, yticks, series=(), marks=(), xl=None, yl=None, title=None,
          W=320, H=250, extra=None, aria="chart"):
    """Economics convention: Q on the horizontal axis, P on the vertical axis."""
    Lm, Rm, Tm, Bm = 42, W - 14, 26 if title else 14, H - 34
    X = lambda q: Lm + q / xmax * (Rm - Lm)
    Y = lambda p: Bm - p / ymax * (Bm - Tm)
    xl = xl or ("Quantity" if lang == "en" else "Quantité")
    yl = yl or ("Price (€)" if lang == "en" else "Prix (€)")
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{aria}">']
    if title:
        s.append(f'<text x="{Lm}" y="12" class="bold">{title}</text>')
    for v in yticks:
        s.append(f'<line class="gridline" x1="{Lm}" y1="{Y(v):.1f}" x2="{Rm}" y2="{Y(v):.1f}"/><text x="{Lm - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" class="muted small">{num(v, lang)}</text>')
    for v in xticks:
        s.append(f'<text x="{X(v):.1f}" y="{Bm + 15}" text-anchor="middle" class="muted small">{num(v, lang)}</text>')
    s.append(f'<line class="axis" x1="{Lm}" y1="{Bm}" x2="{Rm}" y2="{Bm}"/><line class="axis" x1="{Lm}" y1="{Bm}" x2="{Lm}" y2="{Tm - 4}"/>')
    s.append(f'<text x="{Rm}" y="{H - 4}" text-anchor="end" class="muted small">{xl}</text>')
    s.append(f'<text x="{Lm + 5}" y="{Tm + 6}" class="muted small">{yl}</text>')
    if extra:
        s.append(extra(X, Y))
    for se in series:
        pts = " ".join(f"{X(q):.1f},{Y(p):.1f}" for q, p in se["pts"])
        dash = ' stroke-dasharray="6 4"' if se.get("dash") else ""
        s.append(f'<polyline points="{pts}" class="{se.get("cls", "line1")}"{dash}/>')
        if se.get("label"):
            q, p = se.get("lpos", se["pts"][-1])
            s.append(f'<text x="{X(q) + se.get("dx", 5):.1f}" y="{Y(p) + se.get("dy", 4):.1f}" text-anchor="{se.get("anchor", "start")}" class="bold small">{se["label"]}</text>')
    for m in marks:
        x, y = X(m["q"]), Y(m["p"])
        if m.get("guides"):
            s.append(f'<line x1="{Lm}" y1="{y:.1f}" x2="{x:.1f}" y2="{y:.1f}" class="axis" stroke-dasharray="3 3"/><line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{Bm}" class="axis" stroke-dasharray="3 3"/>')
        if m.get("kind") == "open":
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" style="fill:var(--panel);stroke:var(--text)" stroke-width="2"/>')
        else:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" class="{m.get("cls", "c1")} ring"/>')
        if m.get("label"):
            s.append(f'<text x="{x + m.get("dx", 8):.1f}" y="{y + m.get("dy", -6):.1f}" text-anchor="{m.get("anchor", "start")}" class="small bold">{m["label"]}</text>')
    s.append("</svg>")
    return "".join(s)


def arrow_between(X, Y, q1, p1, q2, p2, mid):
    return f'<line x1="{X(q1):.1f}" y1="{Y(p1):.1f}" x2="{X(q2):.1f}" y2="{Y(p2):.1f}" class="arrow" marker-end="url(#{mid})"/>'


def svg_fred(lang):
    pts = [(12 - 4 * p, p) for p in (0, 0.5, 1, 1.5, 2, 2.5, 3)]
    marks = [dict(q=q, p=p, cls="c1") for q, p in pts]
    marks[-1].update(label=("reservation price 3 €" if lang == "en" else "prix de réserve 3 €"), dx=8, dy=4)
    marks[0].update(label="a = 12", dx=-4, dy=-10, anchor="end")
    return chart(lang, 13, 3.5, range(0, 13, 2), [0, 1, 2, 3],
                 [dict(pts=[(12, 0), (0, 3)], cls="line1", label=("D: P = 3 − Q/4"), lpos=(6, 1.5), dx=6, dy=-8)],
                 marks, title=("Fred's demand for ice-cream cones" if lang == "en" else "Demande de cornets de Fred"), aria="Fred")


def svg_aggregate(lang):
    mid = f"agg{lang}"
    mkt = "Market" if lang == "en" else "Marché"

    def ex(X, Y):
        return (marker(mid) + f'<line x1="{X(0):.1f}" y1="{Y(2):.1f}" x2="{X(7):.1f}" y2="{Y(2):.1f}" class="axis" stroke-dasharray="3 3"/>'
                f'<text x="{X(7) + 6:.1f}" y="{Y(2) - 6:.1f}" class="small">4 + 3 = 7</text>')
    return chart(lang, 20, 4, range(0, 21, 4), [0, 1, 2, 3, 4], [
        dict(pts=[(12, 0), (0, 3)], cls="line2", label="Fred", lpos=(2, 2.5), dx=6, dy=0),
        dict(pts=[(7, 0), (0, 3.5)], cls="line1", label="Nico", lpos=(0.6, 3.3), dx=8, dy=-2),
        dict(pts=[(19, 0), (1, 3), (0, 3.5)], cls="lineT", label=mkt, lpos=(13, 1), dx=6, dy=-6),
    ], [dict(q=4, p=2, cls="c2"), dict(q=3, p=2, cls="c1"), dict(q=7, p=2, cls="c1")],
        extra=ex, W=560, H=280, aria="aggregation").replace('class="line1" points', 'class="line1" points')


def svg_move_vs_shift(lang):
    a = chart(lang, 18, 4, [0, 4, 8, 12, 16], [0, 1, 2, 3, 4],
              [dict(pts=[(12, 0), (0, 3)], cls="line1", label="D", lpos=(10, 0.5), dx=6, dy=-6)],
              [dict(q=4, p=2, label="A", dx=8, dy=-4, guides=True), dict(q=0, p=3, label="B", dx=8, dy=-2, cls="c2")],
              title=("1 · Movement along D (price changes)" if lang == "en" else "1 · Mouvement le long de D (le prix varie)"), aria="movement")
    b = chart(lang, 18, 4, [0, 4, 8, 12, 16], [0, 1, 2, 3, 4],
              [dict(pts=[(12, 0), (0, 3)], cls="line1", label="D1", lpos=(12, 0), dx=-4, dy=-8, anchor="end"),
               dict(pts=[(16, 0), (0, 4)], cls="line2", label="D2", lpos=(16, 0), dx=4, dy=-8)],
              [dict(q=4, p=2, label="", cls="c1"), dict(q=8, p=2, label="", cls="c2")],
              title=("2 · Shift of D (heatwave)" if lang == "en" else "2 · Déplacement de D (canicule)"),
              extra=lambda X, Y: marker(f"sh{lang}") + arrow_between(X, Y, 4.6, 2, 7.3, 2, f"sh{lang}"), aria="shift")
    return f'<div class="grid" style="margin:0">{a}{b}</div>'


def svg_tobacco(lang):
    a = chart(lang, 24, 8, [0, 6, 12, 18, 24], [0, 2, 4, 6, 8],
              [dict(pts=[(21, 0), (0, 7)], cls="line1", label="D1", lpos=(21, 0), dx=-2, dy=-8, anchor="end"),
               dict(pts=[(16, 0), (0, 16 / 3)], cls="line2", label="D2", lpos=(16, 0), dx=-2, dy=-8, anchor="end")],
              [dict(q=12, p=3, label="A (12)", dx=8, dy=-6), dict(q=7, p=3, label="B (7)", dx=-8, dy=-8, anchor="end", cls="c2")],
              title=("Awareness campaign → shift" if lang == "en" else "Sensibilisation → déplacement"),
              extra=lambda X, Y: f'<line x1="{X(0)}" y1="{Y(3):.1f}" x2="{X(24)}" y2="{Y(3):.1f}" class="axis" stroke-dasharray="3 3"/>', aria="tobacco awareness")
    b = chart(lang, 24, 8, [0, 6, 12, 18, 24], [0, 2, 4, 6, 8],
              [dict(pts=[(21, 0), (0, 7)], cls="line1", label="D", lpos=(21, 0), dx=-2, dy=-8, anchor="end")],
              [dict(q=12, p=3, label="A (3 €; 12)", dx=8, dy=-4, guides=True), dict(q=3, p=6, label="B (6 €; 3)", dx=8, dy=-4, guides=True, cls="c2")],
              title=("Higher excise tax → movement" if lang == "en" else "Hausse des accises → mouvement"), aria="tobacco tax")
    return f'<div class="grid" style="margin:0">{a}{b}</div>'


def svg_supply(lang):
    pts = [(2 * p - 1, p) for p in (0.5, 1, 1.5, 2, 2.5, 3)]
    marks = [dict(q=q, p=p, cls="c2") for q, p in pts]
    marks[0].update(label=("floor price 0.50 €" if lang == "en" else "prix plancher 0,50 €"), dx=8, dy=4)
    return chart(lang, 6, 3.5, range(0, 7), [0, 1, 2, 3],
                 [dict(pts=[(0, 0.5), (6, 3.5)], cls="line2", label="O: P = 0,5 + Q/2" if lang == "fr" else "S: P = 0.5 + Q/2", lpos=(5, 3), dx=-6, dy=-10, anchor="end")],
                 marks, title=("Supply of ice cream" if lang == "en" else "Offre de glace"), aria="supply")


def svg_statics(lang, case):
    D1, D2 = [(19, 0), (0, 19 / 6)], [(24, 0), (0, 4)]
    O1, O2 = [(0, 0.25), (15, 4)], [(0, 1.5), (10, 4)]
    S = "S" if lang == "en" else "O"
    if case == 1:
        ser = [dict(pts=D1, cls="line1", label="D1", lpos=(19, 0), dx=-2, dy=-8, anchor="end"), dict(pts=D2, cls="line1", dash=True, label="D2", lpos=(24, 0), dx=-2, dy=-8, anchor="end"),
               dict(pts=O1, cls="line2", label=f"{S}1", lpos=(15, 4), dx=4, dy=4)]
        mk = [dict(q=7, p=2, label="E1", dx=-8, dy=-6, anchor="end", kind="open"), dict(q=9, p=2.5, label="E2", dx=8, dy=-4, guides=True)]
        t = "Heatwave: demand ↑" if lang == "en" else "Canicule : demande ↑"
    elif case == 2:
        ser = [dict(pts=D1, cls="line1", label="D1", lpos=(19, 0), dx=-2, dy=-8, anchor="end"),
               dict(pts=O1, cls="line2", label=f"{S}1", lpos=(15, 4), dx=4, dy=4), dict(pts=O2, cls="line2", dash=True, label=f"{S}2", lpos=(10, 4), dx=4, dy=4)]
        mk = [dict(q=7, p=2, label="E1", dx=8, dy=10, kind="open"), dict(q=4, p=2.5, label="E2", dx=-8, dy=-6, anchor="end", guides=True)]
        t = "Covid closures: supply ↓" if lang == "en" else "Fermetures Covid : offre ↓"
    else:
        ser = [dict(pts=D1, cls="line1", label="D1", lpos=(19, 0), dx=-2, dy=-8, anchor="end"), dict(pts=D2, cls="line1", dash=True, label="D2", lpos=(24, 0), dx=-2, dy=-8, anchor="end"),
               dict(pts=O1, cls="line2", label=f"{S}1", lpos=(15, 4), dx=4, dy=4), dict(pts=O2, cls="line2", dash=True, label=f"{S}2", lpos=(10, 4), dx=4, dy=4)]
        mk = [dict(q=7, p=2, label="E1", dx=8, dy=10, kind="open"), dict(q=6, p=3, label="E2", dx=-8, dy=-6, anchor="end", guides=True)]
        t = "Both shocks" if lang == "en" else "Double choc"
    return chart(lang, 25, 4.2, [0, 5, 10, 15, 20, 25], [0, 1, 2, 3, 4], ser, mk, title=t, W=300, H=250, aria=t)


def case_panel(lang, kind, case):
    """Small multiple for the four elasticity cases."""
    W, H = 170, 130
    L_, R_, T_, B_ = 24, W - 8, 10, H - 22
    cls = "line1" if kind == "d" else "line2"
    line = {
        "inf": (L_ + 8, (T_ + B_) / 2, R_ - 6, (T_ + B_) / 2),
        "el": ((L_ + 6, T_ + 30, R_ - 8, B_ - 22) if kind == "d" else (L_ + 6, B_ - 30, R_ - 8, T_ + 26)),
        "inel": ((L_ + 50, T_ + 4, L_ + 82, B_ - 4) if kind == "d" else (L_ + 50, B_ - 4, L_ + 82, T_ + 4)),
        "zero": (L_ + 70, T_ + 4, L_ + 70, B_ - 4),
    }[case]
    s = [f'<svg viewBox="0 0 {W} {H}" aria-hidden="true">',
         f'<line class="axis" x1="{L_}" y1="{B_}" x2="{R_}" y2="{B_}"/><line class="axis" x1="{L_}" y1="{B_}" x2="{L_}" y2="{T_}"/>',
         f'<text x="{L_ - 6}" y="{T_ + 8}" text-anchor="end" class="muted small">P</text><text x="{R_}" y="{H - 6}" text-anchor="end" class="muted small">Q</text>',
         f'<line x1="{line[0]}" y1="{line[1]}" x2="{line[2]}" y2="{line[3]}" class="{cls}"/>', "</svg>"]
    return "".join(s)


def cases_grid(lang, kind):
    if kind == "d":
        items = {"en": [("inf", "a · Perfectly elastic", "|ε| → ∞", "Horizontal at P*. One cent above, sales fall to zero.", "Wheat on the world market: the producer takes the daily price; the only lever is cost."),
                        ("el", "b · Elastic", "|ε| > 1", "Volume changes proportionally more than price. ε = −2.5 at (Q = 2; P = 2): −10 % price, +25 % sales.", "An insulated water bottle sold online, compared across twenty retailers in one click."),
                        ("inel", "c · Inelastic", "|ε| < 1", "Steep curve: a big price rise is needed to reduce quantity a little.", "Household electricity: short-run ε ≈ −0.2 to −0.4."),
                        ("zero", "d · Perfectly inelastic", "ε = 0", "Vertical: quantity does not move, whatever the price.", "A vital dose of insulin; drinking water during a shortage.")],
                 "fr": [("inf", "a · Parfaitement élastique", "|ε| → ∞", "Horizontale au prix P*. Un centime au-dessus, la demande tombe à zéro.", "Le blé sur le marché mondial : le producteur accepte le cours du jour ; son seul levier est le coût."),
                        ("el", "b · À tendance élastique", "|ε| > 1", "Le volume varie proportionnellement plus que le prix. ε = −2,5 en (Q = 2 ; P = 2) : −10 % de prix, +25 % de ventes.", "Une gourde isotherme vendue en ligne, comparée en un clic chez vingt marchands."),
                        ("inel", "c · À tendance inélastique", "|ε| < 1", "Courbe pentue : il faut une forte hausse de prix pour réduire un peu les quantités.", "L'électricité du foyer : à court terme, ε ≈ −0,2 à −0,4."),
                        ("zero", "d · Parfaitement inélastique", "ε = 0", "Verticale : la quantité ne bouge pas, quel que soit le prix.", "Une dose vitale d'insuline ; l'eau potable en situation de pénurie.")]}[lang]
    else:
        items = {"en": [("inf", "a · Perfectly elastic", "εₛ → ∞", "Horizontal at the market price: each producer sells what it wants at that price, nothing above it.", "A perfectly competitive market: the producer is a price-taker; only cost makes the margin."),
                        ("el", "b · Elastic", "εₛ > 1", "Quantity supplied changes proportionally more than price. εₛ = +1.7 at (Q = 6; P = 2): flexible capacity.", "Standard garment making: workshops and staff mobilise within weeks."),
                        ("inel", "c · Inelastic", "εₛ < 1", "Very steep: capacity is rigid or constrained. εₛ = +0.2 at (Q = 2.5; P = 2).", "Oil in the short run: a new field takes years — price absorbs the shock, not volume."),
                        ("zero", "d · Perfectly inelastic", "εₛ = 0", "Vertical: quantity supplied is fixed; only price adjusts.", "Seats in a concert hall; unique works of art; scarce land.")],
                 "fr": [("inf", "a · Parfaitement élastique", "εₒ → ∞", "Horizontale au prix de marché : chaque producteur écoule ce qu'il veut à ce prix, rien au-dessus.", "Un marché parfaitement concurrentiel : le producteur est preneur de prix ; seul le coût fait la marge."),
                        ("el", "b · À tendance élastique", "εₒ > 1", "La quantité offerte varie proportionnellement plus que le prix. εₒ = +1,7 en (Q = 6 ; P = 2) : capacité flexible.", "La confection textile standard : ateliers et main-d'œuvre se mobilisent en quelques semaines."),
                        ("inel", "c · À tendance inélastique", "εₒ < 1", "Très pentue : capacité rigide ou contrainte. εₒ = +0,2 en (Q = 2,5 ; P = 2).", "Le pétrole à court terme : ouvrir un gisement prend des années — le prix absorbe le choc, pas les volumes."),
                        ("zero", "d · Parfaitement inélastique", "εₒ = 0", "Verticale : la quantité offerte est fixe ; seul le prix s'ajuste.", "Les billets d'une salle de concert ; les œuvres d'art uniques ; les terrains rares.")]}[lang]
    ex = "Example" if lang == "en" else "Exemple"
    return '<div class="grid g4">' + "".join(
        f'<div class="card">{case_panel(lang, kind, c)}<span class="tag">{v}</span><h4>{t}</h4><p>{d}</p><p><b>{ex} :</b> {e}</p></div>'.replace(" :</b>", ":</b>" if lang == "en" else " :</b>")
        for c, t, v, d, e in items) + "</div>"


def svg_linear_zones(lang):
    # Q = 8 - 4P : P from 0 to 2, midpoint (Q=4, P=1)
    el = "elastic |ε| > 1" if lang == "en" else "élastique |ε| > 1"
    inel = "inelastic |ε| < 1" if lang == "en" else "inélastique |ε| < 1"
    unit = "|ε| = 1"
    return chart(lang, 8.5, 2.2, range(0, 9, 2), [0, 0.5, 1, 1.5, 2], [
        dict(pts=[(0, 2), (4, 1)], cls="line1", label=el, lpos=(1.6, 1.6), dx=8, dy=-6),
        dict(pts=[(4, 1), (8, 0)], cls="line2", label=inel, lpos=(6, 0.5), dx=8, dy=-6)],
        [dict(q=4, p=1, label=unit, dx=8, dy=-8, cls="c1", guides=True)],
        title="Q = 8 − 4P", W=420, H=250, aria="elasticity zones")


# ---------------- interactive widgets

EQ_WIDGET = '''<div class="tot" id="eq">
<b><span class="en">Try it: move the price</span><span class="fr">À vous : faites varier le prix</span></b>
<p style="margin:6px 0 10px;font-size:.92rem"><span class="en">Ice-cream market — demand Q = 19 − 6P, supply Q = 2P − 1.</span><span class="fr">Marché de la glace — demande Q = 19 − 6P, offre Q = 2P − 1.</span></p>
<div style="font-size:1.4rem;font-weight:700">P = <span id="eqp"></span> €</div>
<input type="range" id="eqs" min="80" max="310" step="5" aria-label="price">
<svg viewBox="0 0 420 260" id="eqsvg" aria-hidden="true"></svg>
<div class="row"><span id="eqd"></span><span id="eqo"></span></div>
<div class="verdict" id="eqv"></div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><button type="button" data-p="300"><span class="en">€3.00</span><span class="fr">3,00 €</span></button><button type="button" data-p="250">P* = <span class="en">€2.50</span><span class="fr">2,50 €</span></button><button type="button" data-p="200"><span class="en">€2.00</span><span class="fr">2,00 €</span></button></div>
</div>'''

EQ_JS = '''<script>
(function(){
  var s=document.getElementById("eqs"),svg=document.getElementById("eqsvg");
  var L=42,R=406,T=14,B=226,QM=14,PM=3.5;
  var X=function(q){return L+q/QM*(R-L)}, Y=function(p){return B-p/PM*(B-T)};
  var fr=function(){return document.documentElement.lang==="fr"};
  var f=function(x,d){var t=x.toFixed(d);return fr()?t.replace(".",","):t};
  var T_=function(en,frs){return '<span class="en">'+en+'</span><span class="fr">'+frs+'</span>'};
  function base(){
    var h="";
    [0,1,2,3].forEach(function(p){h+='<line class="gridline" x1="'+L+'" y1="'+Y(p)+'" x2="'+R+'" y2="'+Y(p)+'"/><text x="'+(L-6)+'" y="'+(Y(p)+4)+'" text-anchor="end" class="muted small">'+p+'</text>'});
    [0,2,4,6,8,10,12,14].forEach(function(q){h+='<text x="'+X(q)+'" y="'+(B+15)+'" text-anchor="middle" class="muted small">'+q+'</text>'});
    h+='<line class="axis" x1="'+L+'" y1="'+B+'" x2="'+R+'" y2="'+B+'"/><line class="axis" x1="'+L+'" y1="'+B+'" x2="'+L+'" y2="'+(T-4)+'"/>';
    h+='<polyline class="line1" points="'+X(0)+','+Y(19/6)+' '+X(14)+','+Y(5/6)+'"/><text x="'+(X(14)-4)+'" y="'+(Y(5/6)-8)+'" text-anchor="end" class="bold small">D</text>';
    h+='<polyline class="line2" points="'+X(0)+','+Y(0.5)+' '+X(6)+','+Y(3.5)+'"/><text x="'+(X(6)+6)+'" y="'+(Y(3.5)+10)+'" class="bold small">'+(fr()?"O":"S")+'</text>';
    h+='<circle cx="'+X(4)+'" cy="'+Y(2.5)+'" r="4" style="fill:var(--panel);stroke:var(--text)" stroke-width="1.5"/><text x="'+(X(4)+8)+'" y="'+(Y(2.5)-8)+'" class="small bold">E</text>';
    return h;
  }
  function render(){
    var p=s.value/100, qd=Math.max(0,19-6*p), qo=Math.max(0,2*p-1), gap=qo-qd;
    document.getElementById("eqp").textContent=f(p,2);
    var y=Y(p), h=base();
    if(Math.abs(gap)>0.01){h+='<rect x="'+X(Math.min(qd,qo))+'" y="'+(y-5)+'" width="'+(X(Math.max(qd,qo))-X(Math.min(qd,qo)))+'" height="10" rx="3" class="'+(gap>0?"fill2":"fill1")+'" opacity=".35"/>';}
    h+='<line x1="'+L+'" y1="'+y+'" x2="'+R+'" y2="'+y+'" style="stroke:var(--text)" stroke-dasharray="5 4"/>';
    h+='<circle cx="'+X(qd)+'" cy="'+y+'" r="5" class="c1 ring"/><circle cx="'+X(qo)+'" cy="'+y+'" r="5" class="c2 ring"/>';
    svg.innerHTML=h;
    document.getElementById("eqd").innerHTML=T_("Quantity demanded Qd = ","Quantité demandée Qd = ")+"<b>"+f(qd,1)+"</b>";
    document.getElementById("eqo").innerHTML=T_("Quantity supplied Qs = ","Quantité offerte Qo = ")+"<b>"+f(qo,1)+"</b>";
    var v=document.getElementById("eqv");
    if(gap>0.01) v.innerHTML='<span class="no">'+T_("Surplus of "+f(gap,1)+" units → sellers cut prices ↓","Surplus de "+f(gap,1)+" unités → les vendeurs baissent les prix ↓")+'</span>';
    else if(gap<-0.01) v.innerHTML='<span class="no">'+T_("Shortage of "+f(-gap,1)+" units → buyers bid prices up ↑","Pénurie de "+f(-gap,1)+" unités → les acheteurs surenchérissent ↑")+'</span>';
    else v.innerHTML='<span class="ok">'+T_("Equilibrium: Qd = Qs = 4 — no pressure on the price.","Équilibre : Qd = Qo = 4 — aucune pression sur le prix.")+'</span>';
  }
  s.addEventListener("input",render);
  document.querySelectorAll("#eq button").forEach(function(b){b.addEventListener("click",function(){s.value=b.dataset.p;render()})});
  document.querySelectorAll(".lang-switch button").forEach(function(b){b.addEventListener("click",function(){setTimeout(render,0)})});
  s.value=300; render();
})();
</script>'''

EL_WIDGET = '''<div class="tot" id="el">
<b><span class="en">Try it: raise or cut the price?</span><span class="fr">À vous : monter ou baisser le prix ?</span></b>
<p style="margin:6px 0 10px;font-size:.92rem"><span class="en">Demand Q = 120 − 20P. The shaded rectangle is revenue (P × Q).</span><span class="fr">Demande Q = 120 − 20P. Le rectangle grisé est le chiffre d'affaires (P × Q).</span></p>
<div style="font-size:1.3rem;font-weight:700">P = <span id="elp"></span> € · Q = <span id="elq"></span> · ε = <span id="ele"></span></div>
<input type="range" id="els" min="25" max="575" step="5" aria-label="price">
<svg viewBox="0 0 420 260" id="elsvg" aria-hidden="true"></svg>
<div class="row"><span id="elr"></span><span id="elup"></span><span id="eldn"></span></div>
<div class="verdict" id="elv"></div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><button type="button" data-p="100">P = 1</button><button type="button" data-p="300">P = 3</button><button type="button" data-p="400">P = 4</button></div>
</div>'''

EL_JS = '''<script>
(function(){
  var s=document.getElementById("els"),svg=document.getElementById("elsvg");
  var L=42,R=406,T=14,B=226,QM=125,PM=6.2;
  var X=function(q){return L+q/QM*(R-L)}, Y=function(p){return B-p/PM*(B-T)};
  var fr=function(){return document.documentElement.lang==="fr"};
  var f=function(x,d){var t=x.toFixed(d);return fr()?t.replace(".",","):t};
  var T_=function(en,frs){return '<span class="en">'+en+'</span><span class="fr">'+frs+'</span>'};
  var rev=function(p){return p*(120-20*p)};
  function render(){
    var p=s.value/100,q=120-20*p,e=-20*p/q,r=rev(p),up=rev(p*1.1),dn=rev(p*0.9);
    document.getElementById("elp").textContent=f(p,2);document.getElementById("elq").textContent=f(q,0);document.getElementById("ele").textContent=f(e,2);
    var h="";
    [0,2,4,6].forEach(function(v){h+='<line class="gridline" x1="'+L+'" y1="'+Y(v)+'" x2="'+R+'" y2="'+Y(v)+'"/><text x="'+(L-6)+'" y="'+(Y(v)+4)+'" text-anchor="end" class="muted small">'+v+'</text>'});
    [0,20,40,60,80,100,120].forEach(function(v){h+='<text x="'+X(v)+'" y="'+(B+15)+'" text-anchor="middle" class="muted small">'+v+'</text>'});
    h+='<rect x="'+L+'" y="'+Y(p)+'" width="'+(X(q)-L)+'" height="'+(B-Y(p))+'" class="fillm" opacity=".9"/>';
    h+='<text x="'+((L+X(q))/2)+'" y="'+((Y(p)+B)/2+4)+'" text-anchor="middle" class="small bold">'+(fr()?"CA = ":"Revenue = ")+f(r,1)+'</text>';
    h+='<line class="axis" x1="'+L+'" y1="'+B+'" x2="'+R+'" y2="'+B+'"/><line class="axis" x1="'+L+'" y1="'+B+'" x2="'+L+'" y2="'+(T-4)+'"/>';
    h+='<polyline class="line1" points="'+X(0)+','+Y(6)+' '+X(60)+','+Y(3)+'"/><polyline class="line2" points="'+X(60)+','+Y(3)+' '+X(120)+','+Y(0)+'"/>';
    h+='<text x="'+(X(15)+8)+'" y="'+(Y(5.25)-6)+'" class="small bold">|ε| &gt; 1</text><text x="'+X(88)+'" y="'+Y(2.4)+'" class="small bold">|ε| &lt; 1</text>';
    h+='<circle cx="'+X(q)+'" cy="'+Y(p)+'" r="6" class="c2 ring"/>';
    svg.innerHTML=h;
    var pc=function(a){var x=(a/r-1)*100;return (x>=0?"+":"")+f(x,1)+" %"};
    document.getElementById("elr").innerHTML=T_("Revenue ","CA ")+"<b>"+f(r,1)+"</b>";
    document.getElementById("elup").innerHTML=T_("Price +10 % → revenue ","Prix +10 % → CA ")+"<b>"+pc(up)+"</b>";
    document.getElementById("eldn").innerHTML=T_("Price −10 % → revenue ","Prix −10 % → CA ")+"<b>"+pc(dn)+"</b>";
    var a=Math.abs(e),v=document.getElementById("elv");
    if(Math.abs(a-1)<0.02) v.innerHTML='<span class="ok">'+T_("|ε| = 1: revenue is at its maximum (P = 3, Q = 60, revenue = 180). Don't move.","|ε| = 1 : le CA est maximal (P = 3, Q = 60, CA = 180). Ne pas bouger.")+'</span>';
    else if(a<1) v.innerHTML='<span class="ok">'+T_("Inelastic (|ε| < 1): RAISE the price to increase revenue.","Inélastique (|ε| < 1) : MONTER le prix pour augmenter le CA.")+'</span>';
    else v.innerHTML='<span class="ok">'+T_("Elastic (|ε| > 1): LOWER the price to increase revenue.","Élastique (|ε| > 1) : BAISSER le prix pour augmenter le CA.")+'</span>';
  }
  s.addEventListener("input",render);
  document.querySelectorAll("#el button").forEach(function(b){b.addEventListener("click",function(){s.value=b.dataset.p;render()})});
  document.querySelectorAll(".lang-switch button").forEach(function(b){b.addEventListener("click",function(){setTimeout(render,0)})});
  s.value=100; render();
})();
</script>'''


def frac(top, bot):
    return f'<span class="frac"><span>{top}</span><span>{bot}</span></span>'


# ---------------- page 2.1 supply & demand

def page_s2_od():
    b = []
    b.append(L(
        '<p class="kicker">Session 2 · Part A</p><h1>Supply, demand &amp; equilibrium</h1><p class="lead">The market forces: in a free market, exchanges follow the law of supply and demand.</p>'
        '<div class="toc"><b>In this lesson</b><ol><li>Demand — definition, determinants, graphs, shifts</li><li>Supply — definition, determinants, supply curve, shifts</li><li>Equilibrium — market mechanism, comparative statics, examples</li></ol></div>',
        '<p class="kicker">Séance 2 · Partie A</p><h1>Offre, demande et équilibre</h1><p class="lead">Les forces du marché : sur un marché libre, les échanges s\'organisent selon la loi de l\'offre et de la demande.</p>'
        '<div class="toc"><b>Au programme</b><ol><li>La demande — définition, déterminants, analyse graphique, déplacements</li><li>L\'offre — définition, déterminants, courbe d\'offre, déplacements</li><li>L\'équilibre — mécanisme de marché, statique comparative, exemples</li></ol></div>'))
    fred_rows = "".join(f'<tr><td class="num">{p:.2f}</td><td class="num">{12 - 4 * p:g}</td></tr>' for p in (0, 0.5, 1, 1.5, 2, 2.5, 3))
    agg = [(0, 12, 7, 19), (0.5, 10, 6, 16), (1, 8, 5, 13), (1.5, 6, 4, 10), (2, 4, 3, 7), (2.5, 2, 2, 4), (3, 0, 1, 1), (3.5, "—", 0, 0)]
    agg_rows = lambda lang: "".join(f'<tr{" class=hl" if p == 2 else ""}><td class="num">{num(p, lang, 2) if p else "0"}</td><td class="num">{f}</td><td class="num">{n}</td><td class="num"><b>{m}</b></td></tr>' for p, f, n, m in agg)
    b.append(L(
        f'''<h2><span class="badge">1</span>Demand</h2>
<div class="callout"><strong>Definition</strong>The quantity of a good that buyers are <b>willing and able</b> to buy, under a given set of conditions and over a given period.</div>
<h3>Four determinants of demand</h3>
<div class="grid">
<div class="card"><span class="tag">01 · Price</span><h4>Law of demand</h4><p>Ceteris paribus, when the price of a good rises, the quantity demanded falls.</p><p><b>Exceptions:</b> <i>Giffen goods</i> — a higher price cuts purchasing power for substitutes, so consumption of the basic good rises. <i>Veblen goods</i> — luxury goods where a higher price signals rarity and status, so demand rises.</p></div>
<div class="card"><span class="tag">02 · Income</span><h4>Normal vs inferior goods</h4><p><b>Normal good:</b> income ↑ → demand ↑.<br><b>Inferior good:</b> income ↑ → demand ↓ (e.g. low-end products).</p></div>
<div class="card"><span class="tag">03 · Prices of related goods</span><h4>Substitutes &amp; complements</h4><p><b>Substitutes:</b> price of X ↑ → demand for Y ↑.<br><b>Complements:</b> price of X ↑ → demand for Y ↓.</p></div>
<div class="card"><span class="tag">04 · Tastes &amp; expectations</span><h4>Preferences, expectations</h4><p>Stronger preference → demand ↑. If consumers expect a future price rise, demand rises <i>today</i>.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">Positive cross relation · ΔQy/ΔPx &gt; 0</span><h4>Substitutes</h4><p>The two goods compete: one replaces the other. Price of X ↓ → demand for Y ↓.</p><p>Ice cream ⇄ sorbet · train ⇄ car · butter ⇄ margarine · Coca-Cola ⇄ Pepsi</p></div>
<div class="card"><span class="tag">Negative cross relation · ΔQy/ΔPx &lt; 0</span><h4>Complements</h4><p>The two goods are used together. Price of X ↓ → demand for Y ↑.</p><p>Smartphone + mobile plan · console + video games · electric car + electricity · coffee machine + capsules</p></div>
</div>
<h3>Individual demand: Fred's ice-cream cones</h3>
<div class="grid" style="align-items:start">
<div class="table-wrap"><table><thead><tr><th class="num">Price (€)</th><th class="num">Quantity demanded</th></tr></thead><tbody>{fred_rows}</tbody></table></div>
<figure style="margin:14px 0">{svg_fred("en")}</figure>
</div>
<p>General form <b>Q = a + b·P</b> (b &lt; 0). For Fred: direct form <b>Q = 12 − 4P</b>, inverse form <b>P = 3 − Q/4</b>.</p>
<div class="grid">
<div class="card"><span class="tag">a = 12</span><h4>Intercept on the Q axis</h4><p>Maximum quantity demanded if the good were free (P = 0).</p></div>
<div class="card"><span class="tag">b = −4</span><h4>Slope</h4><p>b = ΔQ/ΔP = −4: if the price rises by €0.50, quantity falls by 2. Constant along the line.</p></div>
<div class="card"><span class="tag">3.00 €</span><h4>Reservation price</h4><p>a / (−b) = 12 / 4 = €3: the price at which demand falls to zero.</p></div>
</div>
<p>The <b>direct</b> form Q = f(P) gives the quantity for any price; the <b>inverse</b> form P = f(Q) gives the marginal willingness to pay for the Q-th unit (slope ΔP/ΔQ = −0.25 € per unit).</p>
<div class="callout"><strong>Why is price on the vertical axis?</strong>Price is the explanatory variable, so it “should” be on the horizontal axis. The inversion is inherited from Marshall (1890), who reasoned with the inverse form P = f(Q). It was kept because it lets us draw supply and demand on the same graph to find the equilibrium price, and read surpluses as areas under the curves.</div>
<h3>From individual to market demand</h3>
<p><b>Market demand</b> = the sum of individual demands, at each price: Q<sub>market</sub> = (12 − 4P) + (7 − 2P) = <b>19 − 6P</b> (while both buy, i.e. P ≤ 3).</p>
<div>
<div class="table-wrap"><table><thead><tr><th class="num">P (€)</th><th class="num">Q Fred</th><th class="num">Q Nico</th><th class="num">Q market</th></tr></thead><tbody>{agg_rows("en")}</tbody></table></div>
<figure style="margin:14px 0">{svg_aggregate("en")}<figcaption><b>Horizontal summation:</b> at each price, add up the quantities. At P = €2: 4 + 3 = 7. Above €3 only Nico buys, which creates a kink.</figcaption></figure>
</div>
<p>Nico is less price-sensitive (b = −2 vs −4 for Fred) and has a higher reservation price (7/2 = €3.50).</p>
<h3>Movement along the curve vs shift of the curve</h3>
<figure>{svg_move_vs_shift("en")}<figcaption><b>Left:</b> the cone price goes from €2 to €3, so Fred's quantity goes from 4 to 0 — same curve, A → B. <b>Right:</b> a heatwave raises the preference for ice cream, so the whole curve shifts right (D1 → D2).</figcaption></figure>
<div class="callout"><strong>Golden rule</strong><b>Price</b> changes = movement <b>along</b> the curve. <b>Another factor</b> changes (income, related goods' prices, tastes, expectations) = <b>shift</b> of the curve.</div>
<h3>Application: cutting tobacco consumption</h3>
<p>A government can (1) run awareness campaigns or (2) raise excise taxes. Both reduce consumption — through different mechanisms.</p>
<figure>{svg_tobacco("en")}<figcaption><b>Awareness</b> changes preferences: D1 (Q = 21 − 3P) shifts left to D2 (Q = 16 − 3P); at €3, quantity falls from 12 to 7 (−5). <b>Taxes</b> change the price: we move along D from A (€3; 12) to B (€6; 3), −9 units (−75 %). Real tobacco demand is not strictly linear.</figcaption></figure>''',
        f'''<h2><span class="badge">1</span>La demande</h2>
<div class="callout"><strong>Définition</strong>Quantité d'un bien que les acheteurs sont <b>prêts et capables</b> d'acheter, pour un ensemble de conditions donné et au cours d'une période donnée.</div>
<h3>Quatre déterminants de la demande</h3>
<div class="grid">
<div class="card"><span class="tag">01 · Le prix</span><h4>Loi de la demande</h4><p>Ceteris paribus, quand le prix d'un bien augmente, la quantité demandée diminue.</p><p><b>Exceptions :</b> <i>biens Giffen</i> — la hausse du prix réduit le pouvoir d'achat sur les substituts, la consommation du bien de base augmente. <i>Biens Veblen</i> — biens de luxe : la hausse du prix signale la rareté (effet de statut), la demande augmente.</p></div>
<div class="card"><span class="tag">02 · Le revenu</span><h4>Bien normal vs inférieur</h4><p><b>Bien normal :</b> revenu ↑ → demande ↑.<br><b>Bien inférieur :</b> revenu ↑ → demande ↓ (ex. produits bas de gamme).</p></div>
<div class="card"><span class="tag">03 · Prix des biens comparables</span><h4>Substituables et complémentaires</h4><p><b>Substituables :</b> prix de X ↑ → demande de Y ↑.<br><b>Complémentaires :</b> prix de X ↑ → demande de Y ↓.</p></div>
<div class="card"><span class="tag">04 · Goûts et anticipations</span><h4>Préférences, anticipations</h4><p>Préférence accrue → demande ↑. Si les consommateurs anticipent une hausse future des prix, la demande augmente <i>aujourd'hui</i>.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">Relation croisée positive · ΔQy/ΔPx &gt; 0</span><h4>Biens substituables</h4><p>Les deux biens se font concurrence : l'un remplace l'autre. Prix de X ↓ → demande de Y ↓.</p><p>Glace ⇄ sorbet · train ⇄ voiture · beurre ⇄ margarine · Coca-Cola ⇄ Pepsi</p></div>
<div class="card"><span class="tag">Relation croisée négative · ΔQy/ΔPx &lt; 0</span><h4>Biens complémentaires</h4><p>Les deux biens sont utilisés conjointement. Prix de X ↓ → demande de Y ↑.</p><p>Smartphone + forfait mobile · console + jeux vidéo · voiture électrique + électricité · machine à café + capsules</p></div>
</div>
<h3>Demande individuelle : les cornets de glace de Fred</h3>
<div class="grid" style="align-items:start">
<div class="table-wrap"><table><thead><tr><th class="num">Prix (€)</th><th class="num">Quantité demandée</th></tr></thead><tbody>{fred_rows.replace(".", ",")}</tbody></table></div>
<figure style="margin:14px 0">{svg_fred("fr")}</figure>
</div>
<p>Forme générale <b>Q = a + b·P</b> (b &lt; 0). Pour Fred : forme directe <b>Q = 12 − 4P</b>, forme inverse <b>P = 3 − Q/4</b>.</p>
<div class="grid">
<div class="card"><span class="tag">a = 12</span><h4>Intercept de l'axe Q</h4><p>Quantité maximale demandée si le bien était gratuit (P = 0).</p></div>
<div class="card"><span class="tag">b = −4</span><h4>Pente</h4><p>b = ΔQ/ΔP = −4 : si le prix augmente de 0,50 €, la quantité baisse de 2. Constante sur toute la droite.</p></div>
<div class="card"><span class="tag">3,00 €</span><h4>Prix de réserve</h4><p>a / (−b) = 12 / 4 = 3 € : le prix qui annule la demande.</p></div>
</div>
<p>La forme <b>directe</b> Q = f(P) donne la quantité pour tout prix ; la forme <b>inverse</b> P = f(Q) donne le consentement à payer marginal pour la Q-ième unité (pente ΔP/ΔQ = −0,25 € par unité).</p>
<div class="callout"><strong>Pourquoi le prix en ordonnée ?</strong>Le prix est la variable explicative : il « devrait » figurer en abscisse. L'inversion est un héritage de Marshall (1890), qui raisonnait sur la forme inverse P = f(Q). On l'a gardée car elle permet de superposer offre et demande dans un même repère pour trouver le prix d'équilibre, et de lire les surplus comme des aires sous les courbes.</div>
<h3>De la demande individuelle à la demande de marché</h3>
<p><b>Demande de marché</b> = somme des demandes individuelles, à chaque prix : Q<sub>marché</sub> = (12 − 4P) + (7 − 2P) = <b>19 − 6P</b> (tant que les deux achètent, soit P ≤ 3).</p>
<div>
<div class="table-wrap"><table><thead><tr><th class="num">P (€)</th><th class="num">Q Fred</th><th class="num">Q Nico</th><th class="num">Q marché</th></tr></thead><tbody>{agg_rows("fr")}</tbody></table></div>
<figure style="margin:14px 0">{svg_aggregate("fr")}<figcaption><b>Somme horizontale :</b> à chaque prix, on additionne les quantités. À P = 2 € : 4 + 3 = 7. Au-delà de 3 €, seul Nico achète, d'où un coude.</figcaption></figure>
</div>
<p>Nico est moins sensible au prix (b = −2 contre −4 pour Fred) et a un prix de réserve plus élevé (7/2 = 3,50 €).</p>
<h3>Mouvement le long de la courbe vs déplacement de la courbe</h3>
<figure>{svg_move_vs_shift("fr")}<figcaption><b>À gauche :</b> le prix du cornet passe de 2 € à 3 €, la quantité de Fred de 4 à 0 — même courbe, A → B. <b>À droite :</b> une canicule renforce la préférence pour la glace, toute la courbe se déplace vers la droite (D1 → D2).</figcaption></figure>
<div class="callout"><strong>Règle d'or</strong>Le <b>prix</b> varie = mouvement <b>le long</b> de la courbe. Un <b>autre facteur</b> varie (revenu, prix des biens comparables, goûts, anticipations) = <b>déplacement</b> de la courbe.</div>
<h3>Application : réduire la consommation de tabac</h3>
<p>Un gouvernement peut (1) mener des campagnes de sensibilisation ou (2) augmenter les accises. Les deux réduisent la consommation — par des mécanismes différents.</p>
<figure>{svg_tobacco("fr")}<figcaption>La <b>sensibilisation</b> modifie les préférences : D1 (Q = 21 − 3P) se déplace vers la gauche en D2 (Q = 16 − 3P) ; à 3 €, la quantité passe de 12 à 7 (−5). Les <b>taxes</b> modifient le prix : on monte le long de D de A (3 € ; 12) à B (6 € ; 3), −9 unités (−75 %). La vraie demande de tabac n'est pas strictement linéaire.</figcaption></figure>'''))
    sup_rows = lambda lang: "".join(f'<tr><td class="num">{num(p, lang, 2)}</td><td class="num">{2 * p - 1:g}</td></tr>' for p in (0.5, 1, 1.5, 2, 2.5, 3))
    b.append(L(
        f'''<h2><span class="badge">2</span>Supply</h2>
<div class="callout"><strong>Definition</strong>The quantity of a good that sellers are <b>able and willing</b> to sell, under a given set of conditions and over a given period.</div>
<h3>Four determinants of supply</h3>
<div class="grid">
<div class="card"><span class="tag">Price</span><h4>Law of supply</h4><p>Ceteris paribus, when the price rises, the quantity supplied rises: a higher price makes production more profitable.</p></div>
<div class="card"><span class="tag">Inputs</span><h4>Factors of production</h4><p>Labour, capital, energy, raw materials. Their price is a cost: if it rises, production is less profitable and supply falls. E.g. +30 % on energy → less steel and cement supplied.</p></div>
<div class="card"><span class="tag">Technology</span><h4>How inputs are combined</h4><p>Technical progress produces more with the same inputs → unit cost ↓ → supply ↑. E.g. welding robots; the cost of solar kWh fell by about 90 % in ten years.</p></div>
<div class="card"><span class="tag">Expectations &amp; sellers</span><h4>Future prices, number of sellers</h4><p>If sellers expect higher future prices, they may stock up and supply less today. More sellers → more market supply.</p></div>
</div>
<h3>The supply curve</h3>
<div class="grid" style="align-items:start">
<div class="table-wrap"><table><thead><tr><th class="num">P (€)</th><th class="num">Quantity supplied</th></tr></thead><tbody>{sup_rows("en")}</tbody></table></div>
<figure style="margin:14px 0">{svg_supply("en")}</figure>
</div>
<p>Supply equation <b>Q = 2P − 1</b>; inverse form <b>P = 0.5 + Q/2</b> (slope +€0.50 per unit). Floor price: below <b>€0.50</b> no seller offers ice cream.</p>
<div class="grid">
<div class="card"><span class="tag">Movement along S</span><h4>The price changes</h4><p>Cone price €1 → €2: quantity supplied 1 → 3 (A → B on the same curve).</p></div>
<div class="card"><span class="tag">Shift to the right (supply ↑)</span><h4>Another factor changes</h4><p>Better technology · cheaper inputs · more sellers.</p></div>
<div class="card"><span class="tag">Shift to the left (supply ↓)</span><h4>Another factor changes</h4><p>Higher input costs (e.g. sugar) · negative expectations about future prices.</p></div>
</div>''',
        f'''<h2><span class="badge">2</span>L'offre</h2>
<div class="callout"><strong>Définition</strong>Quantité d'un bien que les vendeurs sont <b>capables et prêts</b> à vendre, pour un ensemble de conditions donné et au cours d'une période donnée.</div>
<h3>Quatre déterminants de l'offre</h3>
<div class="grid">
<div class="card"><span class="tag">Le prix</span><h4>Loi de l'offre</h4><p>Ceteris paribus, quand le prix augmente, la quantité offerte augmente : un prix plus élevé rend la production plus rentable.</p></div>
<div class="card"><span class="tag">Les intrants</span><h4>Facteurs de production</h4><p>Travail, capital, énergie, matières premières. Leur prix est un coût : s'il augmente, la production est moins rentable et l'offre diminue. Ex. : +30 % sur l'énergie → l'offre d'acier et de ciment recule.</p></div>
<div class="card"><span class="tag">La technologie</span><h4>La façon de combiner les intrants</h4><p>Un progrès technique produit plus avec les mêmes intrants → coût unitaire ↓ → offre ↑. Ex. : robots de soudure ; le coût du kWh solaire a chuté d'environ 90 % en dix ans.</p></div>
<div class="card"><span class="tag">Anticipations et vendeurs</span><h4>Prix futurs, nombre de vendeurs</h4><p>Si les vendeurs anticipent une hausse des prix, ils peuvent stocker et réduire l'offre aujourd'hui. Plus de vendeurs → offre de marché ↑.</p></div>
</div>
<h3>La courbe d'offre</h3>
<div class="grid" style="align-items:start">
<div class="table-wrap"><table><thead><tr><th class="num">P (€)</th><th class="num">Quantité offerte</th></tr></thead><tbody>{sup_rows("fr")}</tbody></table></div>
<figure style="margin:14px 0">{svg_supply("fr")}</figure>
</div>
<p>Équation de l'offre <b>Q = 2P − 1</b> ; forme inverse <b>P = 0,5 + Q/2</b> (pente +0,50 € par unité). Seuil plancher : en dessous de <b>0,50 €</b>, aucun vendeur n'offre de glace.</p>
<div class="grid">
<div class="card"><span class="tag">Mouvement le long de O</span><h4>Le prix varie</h4><p>Prix du cornet 1 € → 2 € : quantité offerte 1 → 3 (A → B sur la même courbe).</p></div>
<div class="card"><span class="tag">Déplacement à droite (offre ↑)</span><h4>Un autre facteur varie</h4><p>Meilleure technologie · intrants moins chers · davantage de vendeurs.</p></div>
<div class="card"><span class="tag">Déplacement à gauche (offre ↓)</span><h4>Un autre facteur varie</h4><p>Hausse du coût des intrants (ex. sucre) · anticipations négatives sur les prix futurs.</p></div>
</div>'''))
    b.append(L(
        '''<h2><span class="badge">3</span>Market equilibrium</h2>
<p><b>Equilibrium</b> is the price at which quantity demanded <b>equals</b> quantity supplied: no surplus, no shortage.</p>
<div class="grid">
<div class="card"><span class="tag">Algebra</span><h4>Qd = Qs</h4><p>19 − 6P = 2P − 1<br>20 = 8P → <b>P* = €2.50</b><br>Q* = 2 × 2.5 − 1 = <b>4 units</b><br>(check: 19 − 6 × 2.5 = 4 ✓)</p></div>
<div class="card"><span class="tag">Notable values</span><h4>Where the curves hit the axis</h4><p>Reservation price (demand, Q = 0): 19/6 ≈ €3.17<br>Floor price (supply, Q = 0): 1/2 = €0.50</p></div>
</div>''',
        '''<h2><span class="badge">3</span>L'équilibre de marché</h2>
<p>L'<b>équilibre</b> est le prix auquel la quantité demandée est <b>égale</b> à la quantité offerte : ni surplus, ni pénurie.</p>
<div class="grid">
<div class="card"><span class="tag">Dérivation algébrique</span><h4>Qd = Qo</h4><p>19 − 6P = 2P − 1<br>20 = 8P → <b>P* = 2,50 €</b><br>Q* = 2 × 2,5 − 1 = <b>4 unités</b><br>(vérification : 19 − 6 × 2,5 = 4 ✓)</p></div>
<div class="card"><span class="tag">Valeurs remarquables</span><h4>Où les courbes touchent l'axe</h4><p>Prix de réserve (demande, Q = 0) : 19/6 ≈ 3,17 €<br>Seuil plancher (offre, Q = 0) : 1/2 = 0,50 €</p></div>
</div>'''))
    b.append(EQ_WIDGET)
    b.append(L(
        f'''<div class="grid">
<div class="card"><span class="tag">P &gt; P*</span><h4>Excess supply (surplus)</h4><p>At €3: Qs = 5 &gt; Qd = 1 → surplus of 4. Sellers cut prices; as P falls, Qd rises and Qs falls, back to E.</p></div>
<div class="card"><span class="tag">P &lt; P*</span><h4>Excess demand (shortage)</h4><p>At €2: Qd = 7 &gt; Qs = 3 → shortage of 4, queues. Buyers bid up; as P rises, Qd falls and Qs rises, back to E.</p></div>
</div>
<div class="callout"><strong>The market mechanism</strong>The tendency of prices in a free market to adjust until Qd = Qs. It is <b>self-regulating</b>: it coordinates buyers' and sellers' decisions with no central intervention. At equilibrium nobody wants to change their behaviour, there is no pressure on prices, and resources are allocated efficiently (under perfect competition).<br><b>Conditions:</b> competition (no monopoly/oligopoly) · no distortions (externalities, public goods) · <b>flexible prices</b> — the neoclassical assumption that prices are not rigid.</div>
<h2>Comparative statics</h2>
<p>How does an outside event change the equilibrium? Three steps:</p>
<div class="flow"><span class="step"><b>1 · Which curve(s)?</b><br><small>Demand (preferences, income, related prices, buyers' expectations), supply (input costs, technology, sellers' expectations, number of sellers), or both</small></span><span class="arr">→</span><span class="step"><b>2 · Which direction?</b><br><small>Increase → shift right · decrease → shift left</small></span><span class="arr">→</span><span class="step key"><b>3 · New equilibrium?</b><br><small>Read the new P* and Q* (E2)</small></span></div>
<figure><div class="grid" style="margin:0">{svg_statics("en", 1)}{svg_statics("en", 2)}{svg_statics("en", 3)}</div><figcaption>Starting market: D1 Q = 19 − 6P, S1 Q = 4P − 1 → E1 (€2; 7). Shocks shift a curve by 5 units: D2 Q = 24 − 6P, S2 Q = 4P − 6.</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>Example</th><th>Shock</th><th class="num">E1</th><th class="num">E2</th><th>Result</th></tr></thead><tbody>
<tr><td>1 · Heatwave</td><td>Demand ↑ (D1 → D2). At €2: Qd = 12 &gt; Qs = 7 → shortage</td><td class="num">€2.00; 7</td><td class="num">€2.50; 9</td><td>P* ↑ (+€0.50), Q* ↑ (+2)</td></tr>
<tr><td>2 · Covid closures</td><td>Fewer sellers: supply ↓ (S1 → S2). At €2: Qs = 2 &lt; Qd = 7 → shortage</td><td class="num">€2.00; 7</td><td class="num">€2.50; 4</td><td>P* ↑ (+25 %), Q* ↓ (−3, −43 %)</td></tr>
<tr><td>3 · Both</td><td>Demand ↑ and supply ↓</td><td class="num">€2.00; 7</td><td class="num">€3.00; 6</td><td>P* ↑ for sure; Q* depends on the relative size of the shocks</td></tr></tbody></table></div>
<div class="callout"><strong>Two simultaneous shocks</strong>The effect on one variable is unambiguous (here P* rises); the effect on the other (here Q*) depends on which shock is larger. With these curves Q* falls slightly (7 → 6); a bigger heatwave would have raised it.</div>
<h2>Conclusions</h2>
<div class="grid">
<div class="card"><h4>1 · Essential forces</h4><p>Supply and demand are the fundamental forces behind how markets work.</p></div>
<div class="card"><h4>2 · Equilibrium</h4><p>Together they determine the equilibrium price P* and the quantity traded Q*.</p></div>
<div class="card"><h4>3 · Price as a signal</h4><p>Prices guide agents' decisions and allocate scarce resources.</p></div>
<div class="card"><h4>4 · Flexible prices</h4><p>Neoclassical assumption: prices adjust automatically — they are not rigid.</p></div>
</div>
<h2>Check yourself</h2>
<details class="q"><summary>The price of Pepsi falls. What happens to the demand curve for Coca-Cola?</summary>It shifts left: they are substitutes, so a cheaper Pepsi reduces demand for Coca-Cola at every price.</details>
<details class="q"><summary>Is a higher cigarette tax a movement along, or a shift of, the demand curve?</summary>A movement along the curve: the tax acts through the price. Awareness campaigns, by contrast, shift the curve.</details>
<details class="q"><summary>Demand Q = 30 − 2P, supply Q = 3P − 10. Find the equilibrium.</summary>30 − 2P = 3P − 10 → 40 = 5P → P* = 8, Q* = 14.</details>
<details class="q"><summary>Sum the demands Q = 10 − P and Q = 6 − 2P. Careful!</summary>For P ≤ 3 both buy: Q = 16 − 3P. For 3 &lt; P ≤ 10 only the first buys: Q = 10 − P. The market curve has a kink at P = 3.</details>
<details class="q"><summary>Sugar becomes more expensive and, at the same time, a new study says ice cream is healthy. Effect on the ice-cream market?</summary>Supply ↓ (costlier input) and demand ↑ (preferences): P* rises for sure; the effect on Q* is ambiguous.</details>''',
        f'''<div class="grid">
<div class="card"><span class="tag">P &gt; P*</span><h4>Offre excédentaire (surplus)</h4><p>À 3 € : Qo = 5 &gt; Qd = 1 → surplus de 4. Les producteurs baissent leur prix ; P baisse, Qd augmente et Qo diminue, retour vers E.</p></div>
<div class="card"><span class="tag">P &lt; P*</span><h4>Demande excédentaire (pénurie)</h4><p>À 2 € : Qd = 7 &gt; Qo = 3 → pénurie de 4, files d'attente. Les acheteurs surenchérissent ; P monte, Qd diminue et Qo augmente, retour vers E.</p></div>
</div>
<div class="callout"><strong>Le mécanisme de marché</strong>La tendance qu'ont les prix, dans un marché libre, à se modifier jusqu'à l'équilibre (Qd = Qo). C'est un <b>système auto-régulateur</b> : il coordonne les décisions des acheteurs et des vendeurs sans intervention centrale. À l'équilibre, aucun agent n'a intérêt à changer son comportement, aucune pression ne s'exerce sur les prix, et les ressources sont allouées efficacement (si concurrence parfaite).<br><b>Conditions :</b> concurrence (pas de monopole/oligopole) · pas de distorsions (externalités, biens publics) · <b>prix flexibles</b> — hypothèse néoclassique : les prix ne sont pas rigides.</div>
<h2>Statique comparative</h2>
<p>Comment un événement extérieur modifie-t-il l'équilibre ? Trois étapes :</p>
<div class="flow"><span class="step"><b>1 · Quelle(s) courbe(s) ?</b><br><small>Demande (préférences, revenus, prix des biens comparables, anticipations des acheteurs), offre (coûts des intrants, technologie, anticipations des vendeurs, nombre de vendeurs), ou les deux</small></span><span class="arr">→</span><span class="step"><b>2 · Quelle direction ?</b><br><small>Hausse → déplacement à droite · baisse → à gauche</small></span><span class="arr">→</span><span class="step key"><b>3 · Nouvel équilibre ?</b><br><small>Lire les nouveaux P* et Q* (E2)</small></span></div>
<figure><div class="grid" style="margin:0">{svg_statics("fr", 1)}{svg_statics("fr", 2)}{svg_statics("fr", 3)}</div><figcaption>Marché de départ : D1 Q = 19 − 6P, O1 Q = 4P − 1 → E1 (2 € ; 7). Chaque choc déplace une courbe de 5 unités : D2 Q = 24 − 6P, O2 Q = 4P − 6.</figcaption></figure>
<div class="table-wrap"><table><thead><tr><th>Exemple</th><th>Choc</th><th class="num">E1</th><th class="num">E2</th><th>Résultat</th></tr></thead><tbody>
<tr><td>1 · Été caniculaire</td><td>Demande ↑ (D1 → D2). À 2 € : Qd = 12 &gt; Qo = 7 → pénurie</td><td class="num">2,00 € ; 7</td><td class="num">2,50 € ; 9</td><td>P* ↑ (+0,50 €), Q* ↑ (+2)</td></tr>
<tr><td>2 · Mesures Covid</td><td>Moins de vendeurs : offre ↓ (O1 → O2). À 2 € : Qo = 2 &lt; Qd = 7 → pénurie</td><td class="num">2,00 € ; 7</td><td class="num">2,50 € ; 4</td><td>P* ↑ (+25 %), Q* ↓ (−3, −43 %)</td></tr>
<tr><td>3 · Double choc</td><td>Demande ↑ et offre ↓</td><td class="num">2,00 € ; 7</td><td class="num">3,00 € ; 6</td><td>P* ↑ sans ambiguïté ; Q* dépend de l'amplitude relative des chocs</td></tr></tbody></table></div>
<div class="callout"><strong>Deux chocs simultanés</strong>L'effet sur une variable est sans ambiguïté (ici P* monte) ; l'effet sur l'autre (ici Q*) dépend du choc le plus fort. Avec ces courbes, Q* baisse légèrement (7 → 6) ; une canicule plus forte l'aurait fait monter.</div>
<h2>Conclusions</h2>
<div class="grid">
<div class="card"><h4>1 · Forces essentielles</h4><p>L'offre et la demande sont les forces fondamentales du fonctionnement des marchés.</p></div>
<div class="card"><h4>2 · L'équilibre</h4><p>Ensemble, elles déterminent le prix d'équilibre P* et la quantité échangée Q*.</p></div>
<div class="card"><h4>3 · Le prix comme signal</h4><p>Les prix guident les décisions des agents et assurent l'allocation des ressources rares.</p></div>
<div class="card"><h4>4 · Flexibilité des prix</h4><p>Hypothèse néoclassique : les prix s'adaptent automatiquement — ils ne sont pas rigides.</p></div>
</div>
<h2>Testez-vous</h2>
<details class="q"><summary>Le prix du Pepsi baisse. Que devient la courbe de demande de Coca-Cola ?</summary>Elle se déplace vers la gauche : ce sont des substituts, un Pepsi moins cher réduit la demande de Coca-Cola à tout prix.</details>
<details class="q"><summary>Une hausse des taxes sur les cigarettes : mouvement le long de la courbe ou déplacement ?</summary>Mouvement le long de la courbe : la taxe agit via le prix. Les campagnes de sensibilisation, elles, déplacent la courbe.</details>
<details class="q"><summary>Demande Q = 30 − 2P, offre Q = 3P − 10. Trouvez l'équilibre.</summary>30 − 2P = 3P − 10 → 40 = 5P → P* = 8, Q* = 14.</details>
<details class="q"><summary>Additionnez les demandes Q = 10 − P et Q = 6 − 2P. Attention !</summary>Pour P ≤ 3, les deux achètent : Q = 16 − 3P. Pour 3 &lt; P ≤ 10, seul le premier achète : Q = 10 − P. La courbe de marché a un coude en P = 3.</details>
<details class="q"><summary>Le sucre devient plus cher et, en même temps, une étude affirme que la glace est bonne pour la santé. Effet sur le marché de la glace ?</summary>Offre ↓ (intrant plus cher) et demande ↑ (préférences) : P* monte à coup sûr ; l'effet sur Q* est ambigu.</details>'''))
    write("lessons/s2-offre-demande.html", ("Supply, demand & equilibrium", "Offre, demande et équilibre"), b, extra=EQ_JS)


# ---------------- page 2.2 elasticity

def page_s2_elasticite():
    b = []
    f_pd = frac("ΔQd / Qd", "ΔP / P")
    f_inc = frac("ΔQd / Qd", "ΔY / Y")
    f_x = frac("ΔQᵢ / Qᵢ", "ΔPⱼ / Pⱼ")
    f_s = frac("ΔQₛ / Qₛ", "ΔP / P")
    f_o = frac("ΔQₒ / Qₒ", "ΔP / P")
    b.append(L(
        f'''<p class="kicker">Session 2 · Part B</p><h1>Elasticity</h1><p class="lead">From qualitative to quantitative analysis: measuring precisely how sensitive buyers and sellers are.</p>
<div class="toc"><b>In this lesson</b><ol><li>Definition, formula and types of elasticity</li><li>Price elasticity of demand: determinants, measurement, extreme cases</li><li>Price, revenue and pricing decisions</li><li>Cross-price and income elasticities</li><li>Price elasticity of supply</li></ol></div>
<h2>From “price up, demand down” to “demand falls by X %”</h2>
<p>Supply and demand analysis tells us the <i>direction</i> of a change. <b>Elasticity</b> measures how strongly buyers and sellers react to a change in market conditions — by how many %, how much, in which direction.</p>
<div class="callout"><strong>Elasticity</strong>The % change in one variable following a <b>1 %</b> change in another.</div>
<div class="grid">
<div class="card"><p>Apple prices ↓ 1 % → by how many % does demand for apples rise?</p></div>
<div class="card"><p>Household income ↑ 1 % → by how many % does demand for organic food rise?</p></div>
<div class="card"><p>Electric-car prices −10 % → impact on demand for petrol cars?</p></div>
<div class="card"><p>Wheat price ↑ 1 % → by how many % does wheat supply rise?</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">1</span><h4>Price elasticity of demand</h4><p class="formula">ε = {f_pd}</p></div>
<div class="card"><span class="tag">2</span><h4>Income elasticity of demand</h4><p class="formula">Eʸ = {f_inc}</p></div>
<div class="card"><span class="tag">3</span><h4>Cross-price elasticity</h4><p class="formula">εᵢⱼ = {f_x}</p></div>
<div class="card"><span class="tag">4</span><h4>Price elasticity of supply</h4><p class="formula">εₛ = {f_s}</p></div>
</div>''',
        f'''<p class="kicker">Séance 2 · Partie B</p><h1>L'élasticité</h1><p class="lead">De l'analyse qualitative à la mesure précise de la sensibilité des acheteurs et des vendeurs.</p>
<div class="toc"><b>Au programme</b><ol><li>Définition, formule et types d'élasticité</li><li>Élasticité-prix de la demande : déterminants, mesure, cas extrêmes</li><li>Prix, chiffre d'affaires et décision</li><li>Élasticités croisée et revenu de la demande</li><li>Élasticité-prix de l'offre</li></ol></div>
<h2>De « le prix monte, la demande baisse » à « elle baisse de X % »</h2>
<p>L'analyse de l'offre et de la demande donne le <i>sens</i> d'une variation. L'<b>élasticité</b> mesure la sensibilité des acheteurs et des vendeurs à une variation des conditions du marché — de combien de %, quelle ampleur, quelle direction.</p>
<div class="callout"><strong>Élasticité</strong>Variation en % d'une chose suite à une variation de <b>1 %</b> d'une autre chose.</div>
<div class="grid">
<div class="card"><p>Prix des pommes ↓ 1 % → de combien de % la demande de pommes augmente-t-elle ?</p></div>
<div class="card"><p>Revenu des ménages ↑ 1 % → de combien de % la demande de bio augmente-t-elle ?</p></div>
<div class="card"><p>Prix des véhicules électriques −10 % → quel impact sur la demande de véhicules thermiques ?</p></div>
<div class="card"><p>Prix du blé ↑ 1 % → de combien de % l'offre de blé augmente-t-elle ?</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">1</span><h4>Élasticité-prix de la demande</h4><p class="formula">ε = {f_pd}</p></div>
<div class="card"><span class="tag">2</span><h4>Élasticité-revenu de la demande</h4><p class="formula">Eʸ = {f_inc}</p></div>
<div class="card"><span class="tag">3</span><h4>Élasticité-prix croisée</h4><p class="formula">εᵢⱼ = {f_x}</p></div>
<div class="card"><span class="tag">4</span><h4>Élasticité-prix de l'offre</h4><p class="formula">εₒ = {f_o}</p></div>
</div>'''))
    b.append(L(
        f'''<h2><span class="badge">1</span>Price elasticity of demand</h2>
<div class="grid">
<div class="card"><h4>Definition</h4><p>The % change in quantity demanded following a 1 % change in the market price.</p><p class="formula">ε = {f_pd}</p></div>
<div class="card"><h4>Key properties</h4><ul><li>ε &lt; 0 always (P ↑ ⇒ Qd ↓); we often quote |ε|</li><li>|ε| &gt; 1 → <b>elastic</b> demand</li><li>|ε| &lt; 1 → <b>inelastic</b> (rigid) demand</li><li>|ε| = 1 → <b>unit</b> elasticity</li></ul></div>
</div>
<h3>What makes demand more or less elastic?</h3>
<div class="grid">
<div class="card"><span class="tag">1 · Nature of the good</span><h4>Essential vs luxury</h4><p><b>Essentials</b> — rigid demand, hard to cut back: water, gas, electricity, medicines.<br><b>Luxuries</b> — elastic: the purchase can be postponed or dropped: jewellery, haute couture, leisure travel.</p></div>
<div class="card"><span class="tag">2 · Close substitutes</span><h4>Available or not</h4><p><b>Substitutes available</b> — elastic: customers switch (butter ⇄ margarine).<br><b>Few or none</b> — inelastic: no switch possible in the short run (insulin, tap water).</p></div>
<div class="card"><span class="tag">3 · Time horizon</span><h4>Short vs long run</h4><p><b>Short run</b> — less elastic: equipment and habits are fixed.<br><b>Long run</b> — more elastic: people reorganise. Petrol: in the short run you keep your car and drive almost as much; in the long run you switch to diesel, electric or public transport.</p></div>
<div class="card"><span class="tag">4 · Market definition</span><h4>Broad vs narrow</h4><p>Elasticity is a property of the <b>reference market</b>, not of the good. <b>Broad</b> (cars in general): ε ≈ −1. <b>Narrow</b> (a brand or model — Tesla Model 3): ε ≈ −3 to −5.</p></div>
</div>
<div class="callout"><strong>Key point</strong>The more essential a good, the fewer its substitutes and the shorter the horizon, the more rigid its demand. And the narrower the market, the higher the elasticity: an elasticity figure only means something together with its scope.</div>''',
        f'''<h2><span class="badge">1</span>Élasticité-prix de la demande</h2>
<div class="grid">
<div class="card"><h4>Définition</h4><p>Variation en % de la quantité demandée suite à une variation de 1 % du prix de marché.</p><p class="formula">ε = {f_pd}</p></div>
<div class="card"><h4>Propriétés clés</h4><ul><li>ε &lt; 0 toujours (P ↑ ⇒ Qd ↓) ; on cite souvent |ε|</li><li>|ε| &gt; 1 → demande <b>élastique</b></li><li>|ε| &lt; 1 → demande <b>inélastique</b> (rigide)</li><li>|ε| = 1 → élasticité <b>unitaire</b></li></ul></div>
</div>
<h3>Qu'est-ce qui rend la demande plus ou moins élastique ?</h3>
<div class="grid">
<div class="card"><span class="tag">1 · Nature du bien</span><h4>Essentiel vs luxe</h4><p><b>Biens essentiels</b> — demande rigide, peu compressible : eau, gaz, électricité, médicaments.<br><b>Biens de luxe ou superflus</b> — élastique : l'achat peut être différé ou abandonné : bijoux, haute couture, voyages d'agrément.</p></div>
<div class="card"><span class="tag">2 · Substituts proches</span><h4>Disponibles ou non</h4><p><b>Substituts disponibles</b> — élastique : le client se reporte (beurre ⇄ margarine).<br><b>Peu ou pas de substituts</b> — inélastique : aucun report possible à court terme (insuline, eau courante).</p></div>
<div class="card"><span class="tag">3 · Horizon temporel</span><h4>Court vs long terme</h4><p><b>Court terme</b> — peu élastique : équipements et habitudes figés.<br><b>Long terme</b> — plus élastique : on réorganise ses choix. Essence : à CT on garde sa voiture et on roule presque autant ; à LT on arbitre essence / diesel / électrique ou transports en commun.</p></div>
<div class="card"><span class="tag">4 · Périmètre du marché</span><h4>Large vs étroit</h4><p>L'élasticité est une propriété du <b>marché de référence</b>, pas du bien. <b>Marché large</b> (automobile) : ε ≈ −1. <b>Marché étroit</b> (marque, modèle — Tesla Model 3) : ε ≈ −3 à −5.</p></div>
</div>
<div class="callout"><strong>À retenir</strong>Plus un bien est essentiel, sans substitut et considéré à court terme, plus sa demande est rigide. Et plus le marché de référence est étroit, plus l'élasticité est forte : un chiffre d'élasticité n'a de sens qu'avec son périmètre.</div>'''))
    b.append(L(
        f'''<h2><span class="badge">2</span>Measuring elasticity</h2>
<h3>A local measure</h3>
<p class="formula">ε = (ΔQ / Q) ÷ (ΔP / P) = (ΔQ / ΔP) × (P / Q)</p>
<p>For a linear demand <b>Q = a + b·P</b>: <b>ε = b × P / Q</b>, where b = dQ/dP is the slope. The slope is constant, but P/Q changes at every point — so elasticity is read <b>at the point (P, Q)</b> where you are.</p>
<figure>{svg_linear_zones("en")}<figcaption>Q = 8 − 4P: b = −4 everywhere, but ε varies. Top of the line (high P, low Q): |ε| large, very elastic. Middle (P = 1, Q = 4): |ε| = 1. Bottom (low P, high Q): |ε| → 0, rigid. This sliding of elasticity along the curve holds for a <i>linear</i> demand.</figcaption></figure>
<h3>Discrete measure — elasticity between two points</h3>
<div class="grid">
<div class="card"><span class="tag">Method 1</span><h4>Base on the starting point</h4><p class="formula">ε = (ΔQ / Q₁) ÷ (ΔP / P₁)</p><p>Changes are divided by the initial values. Drawback: the direction of the change picks the base (€10 or €12?), so a rise and a fall give two different ε. The gap disappears as ΔP → 0.</p></div>
<div class="card"><span class="tag">Method 2</span><h4>Midpoint base — arc elasticity</h4><p class="formula">ε = (ΔQ / Q̄) ÷ (ΔP / P̄)</p><p>with Q̄ = (Q₁+Q₂)/2 and P̄ = (P₁+P₂)/2. Same value up or down: the ambiguity disappears. It is the elasticity <i>at the midpoint</i> of the segment — not the average of the two ends.</p></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Discrete measure</th><th>Advantages</th><th>Limits</th></tr></thead><tbody>
<tr><td>Two observed points suffice</td><td>Minimal data, no model needed — the measure you read directly from a real price test. Midpoint base: symmetric.</td><td>A segment value, not the price actually charged; smooths non-linear curves. No control for season, promotions, competition; no statistical precision or confidence interval.</td></tr></tbody></table></div>
<h3>Continuous measure — elasticity at a point</h3>
<p class="formula">ε = (dQ/dP) × (P/Q) = d ln Q / d ln P</p>
<p>The limit of the discrete measure as ΔP → 0: defined at a point, with no base or direction to choose.</p>
<div class="grid">
<div class="card"><span class="tag">Way 1</span><h4>Differentiate the demand function</h4><p>You need the demand function (or its slope). Gives an exact value at a precise (P, Q) — it changes everywhere else on the curve.</p></div>
<div class="card"><span class="tag">Way 2</span><h4>Log-log regression</h4><p class="formula">ln Q = β₀ + β₁ ln P + controls ⇒ β₁ = ε</p><p>No need to know the function: estimate it from sales history. The iso-elastic model Q = A·P<sup>−b</sup> has the same elasticity everywhere, so β₁ reads directly — but it needs much more data.</p></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Continuous measure</th><th>Advantages</th><th>Limits</th></tr></thead><tbody>
<tr><td>Exact local value</td><td>True value at (P, Q), unambiguous — the elasticity used for marginal revenue and optimal pricing. Regression controls for season, promotions and competition.</td><td>Requires a known demand function or a long sales history. Log-log imposes a constant elasticity at every point.</td></tr></tbody></table></div>''',
        f'''<h2><span class="badge">2</span>Mesurer l'élasticité</h2>
<h3>Une mesure locale</h3>
<p class="formula">ε = (ΔQ / Q) ÷ (ΔP / P) = (ΔQ / ΔP) × (P / Q)</p>
<p>Pour une demande linéaire <b>Q = a + b·P</b> : <b>ε = b × P / Q</b>, où b = dQ/dP est la pente. La pente est constante, mais le rapport P/Q change en chaque point : l'élasticité se lit <b>au point (P, Q)</b> où l'on se trouve.</p>
<figure>{svg_linear_zones("fr")}<figcaption>Q = 8 − 4P : b = −4 partout, mais ε varie. Haut de la droite (P élevé, Q faible) : |ε| grand, très élastique. Milieu (P = 1, Q = 4) : |ε| = 1. Bas de la droite (P faible, Q élevé) : |ε| → 0, rigide. Ce glissement vaut pour une demande <i>linéaire</i>.</figcaption></figure>
<h3>Mesure discrète — l'élasticité entre deux points</h3>
<div class="grid">
<div class="card"><span class="tag">Mesure 1</span><h4>Base sur le point de départ</h4><p class="formula">ε = (ΔQ / Q₁) ÷ (ΔP / P₁)</p><p>On rapporte les variations aux valeurs initiales. Inconvénient : le sens de la variation choisit le point de base (10 € ou 12 € ?), d'où deux ε différentes à la hausse et à la baisse. L'écart s'annule quand ΔP → 0.</p></div>
<div class="card"><span class="tag">Mesure 2</span><h4>Base au point milieu — élasticité d'arc</h4><p class="formula">ε = (ΔQ / Q̄) ÷ (ΔP / P̄)</p><p>avec Q̄ = (Q₁+Q₂)/2 et P̄ = (P₁+P₂)/2. Même valeur à la hausse comme à la baisse : l'ambiguïté disparaît. C'est l'élasticité <i>au point milieu</i> du segment — pas la moyenne des extrémités.</p></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Mesure discrète</th><th>Avantages</th><th>Limites</th></tr></thead><tbody>
<tr><td>Deux points observés suffisent</td><td>Données minimales, aucun modèle — la mesure directement lisible d'un test de prix réel. Base au point milieu : symétrique.</td><td>Valeur de segment, pas au prix pratiqué ; lisse les courbes non linéaires. Aucun contrôle (saison, promotions, concurrence) ; ni précision statistique ni intervalle de confiance.</td></tr></tbody></table></div>
<h3>Mesure continue — l'élasticité en un point</h3>
<p class="formula">ε = (dQ/dP) × (P/Q) = d ln Q / d ln P</p>
<p>La limite de la mesure discrète quand ΔP → 0 : définie en un point, sans base ni sens à choisir.</p>
<div class="grid">
<div class="card"><span class="tag">Voie 1</span><h4>Dériver la fonction de demande</h4><p>Il faut connaître la fonction de demande (ou sa pente). On obtient une valeur exacte en un point (P, Q) précis — elle change partout ailleurs sur la courbe.</p></div>
<div class="card"><span class="tag">Voie 2</span><h4>Régression log-log</h4><p class="formula">ln Q = β₀ + β₁ ln P + contrôles ⇒ β₁ = ε</p><p>Pas besoin de connaître la fonction : on l'estime à partir d'un historique de ventes. Le modèle iso-élastique Q = A·P<sup>−b</sup> a la même élasticité en tout point, β₁ se lit directement — mais il exige beaucoup plus de données.</p></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Mesure continue</th><th>Avantages</th><th>Limites</th></tr></thead><tbody>
<tr><td>Valeur locale exacte</td><td>Valeur vraie au point (P, Q), sans ambiguïté — celle qu'utilisent la recette marginale et le prix optimal. La régression contrôle saison, promotions et concurrence.</td><td>Suppose la demande connue ou un long historique de ventes. Le log-log impose une élasticité constante en tout point.</td></tr></tbody></table></div>'''))
    b.append(L(
        '''<h3>Worked example — demand for ice cream</h3>
<p><b>Q = 30 − 10P</b> · Point A: P₁ = €2.00, Q₁ = 10 · Point B: P₂ = €2.20, Q₂ = 8 · ΔP = +€0.20, ΔQ = −2</p>
<div class="stats"><div class="stat"><div class="v">−2.00</div><div class="l">ε at A = −10 × 2.00 / 10. At €2, a 1 % price rise cuts demand by 2 %.</div></div><div class="stat"><div class="v">−2.75</div><div class="l">ε at B = −10 × 2.20 / 8. Same slope, higher P/Q → more elastic.</div></div><div class="stat"><div class="v">−2.33</div><div class="l">Arc A–B = (−2 / 9) ÷ (0.20 / 2.10), at the midpoint (P = 2.10; Q = 9).</div></div></div>
<p>−2.75 &lt; −2.33 &lt; −2.00. The arc value is <i>not</i> the average of the two (−2.375). <b>Three numbers, one demand:</b> the result depends on where you measure. Saying “ice-cream demand has an elasticity of −2” only makes sense if you add “at €2.00”.</p>
<h3>What a regression would say</h3>
<p>Qᵢ = β₀ + β₁·Pᵢ + β₂·Tempᵢ + β₃·Weekendᵢ + uᵢ, estimated by OLS on 120 days of sales.</p>
<div class="table-wrap"><table><thead><tr><th>Variable</th><th class="num">Coef.</th><th class="num">Std. err.</th><th class="num">t</th><th class="num">p</th></tr></thead><tbody>
<tr><td>Constant</td><td class="num">29.40</td><td class="num">1.20</td><td class="num">24.5</td><td class="num">&lt;0.001</td></tr>
<tr class="hl"><td>Price (€)</td><td class="num">−9.80</td><td class="num">0.90</td><td class="num">−10.9</td><td class="num">&lt;0.001</td></tr>
<tr><td>Temperature (°C)</td><td class="num">0.42</td><td class="num">0.08</td><td class="num">5.3</td><td class="num">&lt;0.001</td></tr>
<tr><td>Weekend</td><td class="num">1.70</td><td class="num">0.52</td><td class="num">3.3</td><td class="num">0.001</td></tr></tbody></table></div>
<p style="font-size:.85rem;color:var(--muted)">n = 120 · R² = 0.78 · robust standard errors</p>
<div class="grid">
<div class="card"><span class="tag">1</span><h4>β₁ = −9.8 is a slope, not an elasticity</h4><p>It measures dQ/dP: +€1 on the price loses 9.8 ice creams a day. It depends on units and can't be compared across products.</p></div>
<div class="card"><span class="tag">2</span><h4>From slope to elasticity: ε̂ = β₁ × P/Q</h4><p>ε̂(€2.00) = −9.8 × 2.00 / 10 = −1.96<br>ε̂(€2.20) = −9.8 × 2.20 / 8 = −2.70<br>Very close to the true −2.00 and −2.75.</p></div>
<div class="card"><span class="tag">3</span><h4>Confidence interval</h4><p>CI₉₅(β₁) = −9.80 ± 1.98 × 0.90 = [−11.6; −8.0] ⇒ CI₉₅(ε at €2) = [−2.32; −1.60]. It excludes 0 (the price effect is real) and stays below −1: demand is elastic throughout — the pricing decision is robust.</p></div>
</div>
<div class="callout"><strong>Key point</strong>In levels, the price coefficient is a slope; elasticity follows only at a precise point (P, Q). In log-log (ln Q = β₀ + β₁·ln P + u), β₁ would be the elasticity directly, constant everywhere — at the cost of that assumption.</div>
<h3>Four cases of demand elasticity</h3>''',
        '''<h3>Exemple appliqué — demande de glace</h3>
<p><b>Q = 30 − 10P</b> · Point A : P₁ = 2,00 €, Q₁ = 10 · Point B : P₂ = 2,20 €, Q₂ = 8 · ΔP = +0,20 €, ΔQ = −2</p>
<div class="stats"><div class="stat"><div class="v">−2,00</div><div class="l">ε en A = −10 × 2,00 / 10. À 2 €, une hausse de prix de 1 % fait reculer la demande de 2 %.</div></div><div class="stat"><div class="v">−2,75</div><div class="l">ε en B = −10 × 2,20 / 8. Même pente, P/Q plus élevé → plus élastique.</div></div><div class="stat"><div class="v">−2,33</div><div class="l">Arc A–B = (−2 / 9) ÷ (0,20 / 2,10), au point médian (P = 2,10 ; Q = 9).</div></div></div>
<p>−2,75 &lt; −2,33 &lt; −2,00. La valeur d'arc n'est <i>pas</i> la moyenne des deux (−2,375). <b>Trois chiffres, une seule demande :</b> le résultat dépend de l'endroit où l'on mesure. Dire « la demande de glace a une élasticité de −2 » n'a de sens qu'en précisant « à 2,00 € ».</p>
<h3>Ce que dirait une régression</h3>
<p>Qᵢ = β₀ + β₁·Pᵢ + β₂·Tempᵢ + β₃·Week-endᵢ + uᵢ, estimée par MCO sur 120 jours de ventes.</p>
<div class="table-wrap"><table><thead><tr><th>Variable</th><th class="num">Coef.</th><th class="num">Err.-type</th><th class="num">t</th><th class="num">p</th></tr></thead><tbody>
<tr><td>Constante</td><td class="num">29,40</td><td class="num">1,20</td><td class="num">24,5</td><td class="num">&lt;0,001</td></tr>
<tr class="hl"><td>Prix (€)</td><td class="num">−9,80</td><td class="num">0,90</td><td class="num">−10,9</td><td class="num">&lt;0,001</td></tr>
<tr><td>Température (°C)</td><td class="num">0,42</td><td class="num">0,08</td><td class="num">5,3</td><td class="num">&lt;0,001</td></tr>
<tr><td>Week-end</td><td class="num">1,70</td><td class="num">0,52</td><td class="num">3,3</td><td class="num">0,001</td></tr></tbody></table></div>
<p style="font-size:.85rem;color:var(--muted)">n = 120 · R² = 0,78 · erreurs-types robustes</p>
<div class="grid">
<div class="card"><span class="tag">1</span><h4>β₁ = −9,8 : une pente, pas une élasticité</h4><p>Il mesure dQ/dP : +1 € sur le prix fait perdre 9,8 glaces par jour. Dépend des unités, non comparable entre produits.</p></div>
<div class="card"><span class="tag">2</span><h4>De la pente à l'élasticité : ε̂ = β₁ × P/Q</h4><p>ε̂(2,00 €) = −9,8 × 2,00 / 10 = −1,96<br>ε̂(2,20 €) = −9,8 × 2,20 / 8 = −2,70<br>Très proche des vraies valeurs −2,00 et −2,75.</p></div>
<div class="card"><span class="tag">3</span><h4>L'intervalle de confiance</h4><p>IC₉₅(β₁) = −9,80 ± 1,98 × 0,90 = [−11,6 ; −8,0] ⇒ IC₉₅(ε à 2 €) = [−2,32 ; −1,60]. Il exclut 0 (l'effet prix est réel) et reste sous −1 : la demande est élastique partout dans l'intervalle — la décision de prix est robuste.</p></div>
</div>
<div class="callout"><strong>À retenir</strong>En niveau, le coefficient du prix est une pente ; l'élasticité ne s'en déduit qu'en un point (P, Q) précis. En log-log (ln Q = β₀ + β₁·ln P + u), β₁ serait directement l'élasticité, constante en tout point — au prix de cette hypothèse.</div>
<h3>Quatre cas d'élasticité de la demande</h3>'''))
    b.append(L(cases_grid("en", "d"), cases_grid("fr", "d")))
    b.append(L(
        '''<h2><span class="badge">3</span>Should I raise or cut my price?</h2>
<p><b>The question:</b> at what price is revenue maximised? Demand <b>Q = 120 − 20P</b>; only the starting point changes — and with it ε.</p>
<div class="table-wrap"><table><thead><tr><th>Start</th><th class="num">ε</th><th class="num">Revenue</th><th class="num">Price +10 %</th><th class="num">Price −10 %</th><th>Decision</th></tr></thead><tbody>
<tr><td>P = 1 · Q = 100 (bottom, inelastic)</td><td class="num">−0.2</td><td class="num">100</td><td class="num">107.8 (+7.8 %)</td><td class="num">91.8 (−8.2 %)</td><td><b>Raise</b> the price</td></tr>
<tr class="hl"><td>P = 3 · Q = 60 (tipping point)</td><td class="num">−1</td><td class="num">180</td><td class="num">178.2 (−1 %)</td><td class="num">178.2 (−1 %)</td><td><b>Don't move</b></td></tr>
<tr><td>P = 4 · Q = 40 (top, elastic)</td><td class="num">−2</td><td class="num">160</td><td class="num">140.8 (−12 %)</td><td class="num">172.8 (+8 %)</td><td><b>Cut</b> the price</td></tr></tbody></table></div>''',
        '''<h2><span class="badge">3</span>Faut-il monter ou baisser mon prix ?</h2>
<p><b>La question :</b> à quel prix le chiffre d'affaires (CA) est-il maximal ? Demande <b>Q = 120 − 20P</b> ; seul le point de départ change — et avec lui ε.</p>
<div class="table-wrap"><table><thead><tr><th>Départ</th><th class="num">ε</th><th class="num">CA</th><th class="num">Prix +10 %</th><th class="num">Prix −10 %</th><th>Décision</th></tr></thead><tbody>
<tr><td>P = 1 · Q = 100 (bas, inélastique)</td><td class="num">−0,2</td><td class="num">100</td><td class="num">107,8 (+7,8 %)</td><td class="num">91,8 (−8,2 %)</td><td><b>Monter</b> le prix</td></tr>
<tr class="hl"><td>P = 3 · Q = 60 (point de bascule)</td><td class="num">−1</td><td class="num">180</td><td class="num">178,2 (−1 %)</td><td class="num">178,2 (−1 %)</td><td><b>Ne pas bouger</b></td></tr>
<tr><td>P = 4 · Q = 40 (haut, élastique)</td><td class="num">−2</td><td class="num">160</td><td class="num">140,8 (−12 %)</td><td class="num">172,8 (+8 %)</td><td><b>Baisser</b> le prix</td></tr></tbody></table></div>'''))
    b.append(EL_WIDGET)
    b.append(L(
        '''<div class="callout"><strong>The answer</strong>Raise the price while |ε| &lt; 1, cut it while |ε| &gt; 1, stop at |ε| = 1: here P = 3, Q = 60, maximum revenue = 180. In the inelastic zone quantity moves less than price, so a higher price grows the revenue rectangle; in the elastic zone quantity moves more than price, so a lower price grows it. Either way, the winning move pushes the price towards |ε| = 1. <b>Prerequisite:</b> you must know ε at the current price. <b>Caution:</b> this maximises revenue, not profit — the profit optimum remains MR = MC.</div>''',
        '''<div class="callout"><strong>La réponse</strong>Monter le prix tant que |ε| &lt; 1, le baisser tant que |ε| &gt; 1, s'arrêter à |ε| = 1 : ici P = 3, Q = 60, CA maximal = 180. En zone inélastique, la quantité bouge moins que le prix : un prix plus élevé agrandit le rectangle de CA ; en zone élastique, la quantité bouge plus que le prix : un prix plus bas l'agrandit. Dans les deux cas, le mouvement gagnant rapproche le prix de |ε| = 1. <b>Prérequis :</b> connaître ε au prix pratiqué. <b>Attention :</b> on maximise le CA, pas le profit — l'optimum reste Rm = Cm.</div>'''))
    b.append(L(
        f'''<h2><span class="badge">4</span>Other elasticities</h2>
<h3>Cross-price elasticity of demand</h3>
<p class="formula">εᵢⱼ = {f_x}</p>
<p>The % change in quantity demanded of good i following a 1 % change in the price of good j. <b>The sign reveals the relationship.</b></p>
<div class="grid">
<div class="card"><span class="tag">Sign + · εᵢⱼ &gt; 0</span><h4>Substitutes</h4><p>Price of j ↑ ⇒ demand for i ↑. The goods replace each other: ice cream ⇄ sorbet, butter ⇄ margarine, train ⇄ plane (short trips). The higher εᵢⱼ, the stronger the competition.</p></div>
<div class="card"><span class="tag">Sign − · εᵢⱼ &lt; 0</span><h4>Complements</h4><p>Price of j ↑ ⇒ demand for i ↓. The goods are used together: petrol + car, printer + ink cartridges, console + video games. The more negative εᵢⱼ, the more they sell together.</p></div>
</div>
<h3>Income elasticity of demand</h3>
<p class="formula">Eʸ = {f_inc}</p>
<div class="grid">
<div class="card"><span class="tag">Eʸ &gt; 0, small</span><h4>Normal necessities</h4><p>Demand rises with income, but less than proportionally: basic food, everyday clothing, heating, basic medical care.</p></div>
<div class="card"><span class="tag">Eʸ &gt; 0, high</span><h4>Normal luxuries</h4><p>Demand rises more than proportionally with income: sports cars, high-end jewellery, caviar, luxury travel.</p></div>
<div class="card"><span class="tag">Eʸ &lt; 0</span><h4>Inferior goods</h4><p>Demand falls as income rises — people switch to better-quality alternatives: hard-discount food, second-hand goods.</p></div>
</div>
<h2><span class="badge">5</span>Price elasticity of supply</h2>
<div class="grid">
<div class="card"><h4>Definition</h4><p>The % change in quantity supplied following a 1 % change in the market price. Mirror of demand elasticity, on the producer side.</p><p class="formula">εₛ = {f_s}</p><p>Linear supply Q = a + bP ⇒ εₛ = b × P/Q.</p></div>
<div class="card"><h4>Properties</h4><ul><li>εₛ &gt; 0 always (P ↑ ⇒ Qₛ ↑)</li><li>εₛ &gt; 1 → elastic supply</li><li>εₛ &lt; 1 → inelastic (rigid) supply</li></ul><p><b>Key determinant — time:</b> short run, capacity fixed ⇒ rigid; long run, capacity adjustable ⇒ elastic.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">1 · Flexibility &amp; capacity</span><h4>Can sellers change output?</h4><p><b>Inflexible ⇒ inelastic:</b> new seafront housing (limited land, building takes time).<br><b>Flexible ⇒ elastic:</b> everyday manufactured goods.</p></div>
<div class="card"><span class="tag">2 · Time horizon</span><h4>Usually more elastic in the long run</h4><p><b>Short run:</b> fixed capacity, contracts, limited stocks, slow adjustment.<br><b>Long run:</b> new investment, entry/exit of producers, technological adjustment.</p></div>
</div>
<div class="stats"><div class="stat"><div class="v">εₛ = 1.5</div><div class="l">Q = −5 + 5P at A (P = 3, Q = 10): εₛ = 5 × 3/10. If P ↑ 1 %, Qₛ ↑ 1.5 %.</div></div></div>
<p>Supply elasticity also varies along the curve. Low zone (low P and Q): spare capacity ⇒ high ε. High zone (high P and Q): capacity saturated ⇒ low ε.</p>
<h3>Four cases of supply elasticity</h3>''',
        f'''<h2><span class="badge">4</span>Autres élasticités</h2>
<h3>Élasticité-prix croisée de la demande</h3>
<p class="formula">εᵢⱼ = {f_x}</p>
<p>Variation en % de la quantité demandée du bien i suite à une variation de 1 % du prix du bien j. <b>Le signe révèle la nature de la relation.</b></p>
<div class="grid">
<div class="card"><span class="tag">Signe + · εᵢⱼ &gt; 0</span><h4>Biens substituables</h4><p>Prix de j ↑ ⇒ demande de i ↑. Les biens se remplacent : glace ⇄ sorbet, beurre ⇄ margarine, train ⇄ avion (trajet court). Plus εᵢⱼ est élevé, plus la concurrence est forte.</p></div>
<div class="card"><span class="tag">Signe − · εᵢⱼ &lt; 0</span><h4>Biens complémentaires</h4><p>Prix de j ↑ ⇒ demande de i ↓. Les biens s'utilisent ensemble : essence + voiture, imprimante + cartouches, console + jeux vidéo. Plus εᵢⱼ est négatif, plus ils se vendent ensemble.</p></div>
</div>
<h3>Élasticité-revenu de la demande</h3>
<p class="formula">Eʸ = {f_inc}</p>
<div class="grid">
<div class="card"><span class="tag">Eʸ &gt; 0, faible</span><h4>Biens normaux indispensables</h4><p>La demande augmente avec le revenu, mais moins que proportionnellement : nourriture de base, vêtements courants, chauffage, soins médicaux de base.</p></div>
<div class="card"><span class="tag">Eʸ &gt; 0, élevée</span><h4>Biens normaux de luxe</h4><p>La demande augmente plus que proportionnellement au revenu : voitures de sport, bijoux haut de gamme, caviar, voyages de luxe.</p></div>
<div class="card"><span class="tag">Eʸ &lt; 0</span><h4>Biens inférieurs</h4><p>La demande diminue quand le revenu augmente — on se tourne vers une meilleure qualité : alimentation hard-discount, biens de seconde main.</p></div>
</div>
<h2><span class="badge">5</span>Élasticité-prix de l'offre</h2>
<div class="grid">
<div class="card"><h4>Définition</h4><p>Variation en % de la quantité offerte suite à une variation de 1 % du prix de marché. Symétrique de l'élasticité de la demande, côté producteur.</p><p class="formula">εₒ = {f_o}</p><p>Offre linéaire Q = a + bP ⇒ εₒ = b × P/Q.</p></div>
<div class="card"><h4>Propriétés</h4><ul><li>εₒ &gt; 0 toujours (P ↑ ⇒ Qₒ ↑)</li><li>εₒ &gt; 1 → offre élastique</li><li>εₒ &lt; 1 → offre inélastique (rigide)</li></ul><p><b>Déterminant clé — l'horizon :</b> court terme, capacités figées ⇒ rigide ; long terme, capacités ajustables ⇒ élastique.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">1 · Flexibilité et capacité</span><h4>Les vendeurs peuvent-ils ajuster ?</h4><p><b>Peu flexible ⇒ inélastique :</b> immobilier neuf en bord de mer (foncier limité, construire prend du temps).<br><b>Flexible ⇒ élastique :</b> biens manufacturés courants.</p></div>
<div class="card"><span class="tag">2 · Horizon temporel</span><h4>Plus élastique à long terme</h4><p><b>Court terme :</b> capacité fixée, contrats, stocks limités, ajustement lent.<br><b>Long terme :</b> nouveaux investissements, entrée/sortie de producteurs, ajustements technologiques.</p></div>
</div>
<div class="stats"><div class="stat"><div class="v">εₒ = 1,5</div><div class="l">Q = −5 + 5P en A (P = 3, Q = 10) : εₒ = 5 × 3/10. Si P ↑ de 1 %, Qₒ ↑ de 1,5 %.</div></div></div>
<p>L'élasticité de l'offre varie aussi le long de la courbe. Zone basse (P et Q faibles) : capacités inutilisées ⇒ ε élevé. Zone haute (P et Q forts) : capacités saturées ⇒ ε faible.</p>
<h3>Quatre cas d'élasticité de l'offre</h3>'''))
    b.append(L(cases_grid("en", "s"), cases_grid("fr", "s")))
    b.append(L(
        '''<h2>Check yourself</h2>
<details class="q"><summary>The price of a concert ticket rises from €40 to €50 and sales fall from 1,000 to 800. Compute the arc elasticity.</summary>ΔQ/Q̄ = −200 / 900 = −0.222; ΔP/P̄ = 10 / 45 = 0.222 ⇒ ε = −1.0 (unit elastic).</details>
<details class="q"><summary>Demand Q = 100 − 5P. What is the elasticity at P = 4? At P = 15?</summary>At P = 4: Q = 80, ε = −5 × 4/80 = −0.25 (inelastic). At P = 15: Q = 25, ε = −5 × 15/25 = −3 (elastic).</details>
<details class="q"><summary>With Q = 100 − 5P, at which price is revenue maximised?</summary>Where |ε| = 1, i.e. the midpoint of the line: P = 10, Q = 50, revenue = 500.</details>
<details class="q"><summary>The price of printers rises 10 % and cartridge sales fall 5 %. Cross elasticity and relationship?</summary>ε = −5 / 10 = −0.5 &lt; 0: complements.</details>
<details class="q"><summary>Income rises 10 % and second-hand clothes sales fall 3 %. What kind of good?</summary>Eʸ = −0.3 &lt; 0: an inferior good.</details>
<details class="q"><summary>Why is the regression coefficient −9.8 not an elasticity?</summary>It is a slope dQ/dP (ice creams per euro). Elasticity requires multiplying by P/Q at a given point: −9.8 × 2/10 = −1.96 at €2.</details>''',
        '''<h2>Testez-vous</h2>
<details class="q"><summary>Le prix d'un billet de concert passe de 40 € à 50 € et les ventes de 1 000 à 800. Calculez l'élasticité d'arc.</summary>ΔQ/Q̄ = −200 / 900 = −0,222 ; ΔP/P̄ = 10 / 45 = 0,222 ⇒ ε = −1,0 (élasticité unitaire).</details>
<details class="q"><summary>Demande Q = 100 − 5P. Quelle est l'élasticité à P = 4 ? À P = 15 ?</summary>À P = 4 : Q = 80, ε = −5 × 4/80 = −0,25 (inélastique). À P = 15 : Q = 25, ε = −5 × 15/25 = −3 (élastique).</details>
<details class="q"><summary>Avec Q = 100 − 5P, à quel prix le CA est-il maximal ?</summary>Là où |ε| = 1, au milieu de la droite : P = 10, Q = 50, CA = 500.</details>
<details class="q"><summary>Le prix des imprimantes augmente de 10 % et les ventes de cartouches baissent de 5 %. Élasticité croisée et relation ?</summary>ε = −5 / 10 = −0,5 &lt; 0 : biens complémentaires.</details>
<details class="q"><summary>Le revenu augmente de 10 % et les ventes de vêtements de seconde main baissent de 3 %. Quel type de bien ?</summary>Eʸ = −0,3 &lt; 0 : un bien inférieur.</details>
<details class="q"><summary>Pourquoi le coefficient de régression −9,8 n'est-il pas une élasticité ?</summary>C'est une pente dQ/dP (glaces par euro). L'élasticité exige de multiplier par P/Q en un point donné : −9,8 × 2/10 = −1,96 à 2 €.</details>'''))
    write("lessons/s2-elasticite.html", ("Elasticity", "L'élasticité"), b, extra=EL_JS)



# ================================================================== SESSIONS 3 & 4

def curve(f, x0, x1, n=60, ymax=None):
    pts = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        y = f(x)
        if ymax is None or y <= ymax:
            pts.append((x, y))
    return pts


def lab_NH(lang):
    return (("Food (N)", "Clothing (H)") if lang == "en" else ("Alimentation (N)", "Vêtements (H)"))


def svg_baskets(lang):
    xl, yl = lab_NH(lang)
    ser = [dict(pts=curve(lambda n: 10 + 400 / n, 8, 58), cls="line1", label="U₁", lpos=(58, 10 + 400 / 58), dx=4, dy=4)]
    mk = [dict(q=20, p=30, label="A (20, 30)", dx=8, dy=-6),
          dict(q=10, p=50, label="B", dx=8, dy=-4),
          dict(q=40, p=20, label="D", dx=6, dy=-8),
          dict(q=30, p=40, label="E ≻ A", dx=8, dy=-4, cls="c2"),
          dict(q=10, p=20, label="G ≺ A", dx=8, dy=4, kind="open"),
          dict(q=10, p=40, label="H ≺ A", dx=8, dy=4, kind="open")]
    return chart(lang, 60, 60, [0, 10, 20, 30, 40, 50, 60], [0, 10, 20, 30, 40, 50, 60], ser, mk, xl=xl, yl=yl, W=420, H=280, aria="baskets")


def svg_cross(lang):
    xl, yl = lab_NH(lang)
    ser = [dict(pts=[(5, 60), (25, 0)], cls="line1", label="U₁", lpos=(5, 60), dx=6, dy=4),
           dict(pts=[(2, 56), (28, 4)], cls="line2", label="U₂", lpos=(2, 56), dx=-6, dy=0, anchor="end")]
    # U1 through A(15,30), B(10,45): slope -3 ; U2 through A(15,30), D(10,40): slope -2
    ser = [dict(pts=[(5, 60), (25, 0)], cls="line1", label="U₁", lpos=(5, 60), dx=6, dy=6),
           dict(pts=[(0, 60), (30, 0)], cls="line2", label="U₂", lpos=(30, 0), dx=-4, dy=-8, anchor="end")]
    mk = [dict(q=15, p=30, label="A (15, 30)", dx=8, dy=-4),
          dict(q=10, p=45, label="B (10, 45)", dx=8, dy=-2),
          dict(q=10, p=40, label="D (10, 40)", dx=-8, dy=4, anchor="end", cls="c2")]
    return chart(lang, 32, 62, [0, 10, 20, 30], [0, 10, 20, 30, 40, 50, 60], ser, mk, xl=xl, yl=yl, W=360, H=260, aria="crossing")


def svg_mrs(lang):
    xl, yl = lab_NH(lang)
    tm = "MRS" if lang == "en" else "TMS"

    def tangents(X, Y):
        s = ""
        for n, h in [(10, 60), (20, 30), (30, 20)]:
            m = -h / n
            d = 1.8 if n == 10 else 9
            s += f'<line x1="{X(n - d):.1f}" y1="{Y(h - m * d):.1f}" x2="{X(n + d):.1f}" y2="{Y(h + m * d):.1f}" style="stroke:var(--muted)" stroke-width="1.5" stroke-dasharray="4 3"/>'
        return s
    ser = [dict(pts=curve(lambda n: 300 / n, 4.3, 50), cls="line1", label="U₁ = 300", lpos=(50, 6), dx=4, dy=4),
           dict(pts=curve(lambda n: 600 / n, 8.6, 50), cls="line1", label="U₂ = 600", lpos=(50, 12), dx=4, dy=4),
           dict(pts=curve(lambda n: 900 / n, 12.9, 50), cls="line1", label="U₃ = 900", lpos=(50, 18), dx=4, dy=4)]
    mk = [dict(q=10, p=60, label=f"A · {tm} = 6", dx=8, dy=-4, cls="c2"),
          dict(q=20, p=30, label=f"B · {tm} = {num(1.5, lang)}", dx=8, dy=-6, cls="c2"),
          dict(q=30, p=20, label=f"C · {tm} = {num(0.67, lang)}", dx=6, dy=-10, cls="c2")]
    return chart(lang, 60, 72, [0, 10, 20, 30, 40, 50, 60], [0, 20, 40, 60], ser, mk, xl=xl, yl=yl, W=460, H=290, extra=tangents, aria="MRS")


def svg_special(lang):
    t = {"en": ("Normal substitutes", "Perfect substitutes", "Perfect complements", "Diminishing MRS", "Constant MRS", "MRS = 0 or ∞",
                "USB keys 1 GB (X)", "USB keys 2 GB (Y)", "Right shoes", "Left shoes"),
         "fr": ("Normalement substituables", "Substituts parfaits", "Complémentaires parfaits", "TMS décroissant", "TMS constant", "TMS = 0 ou ∞",
                "Clés 1 Go (X)", "Clés 2 Go (Y)", "Chaussures droites", "Chaussures gauches")}[lang]
    xl, yl = lab_NH(lang)
    a = chart(lang, 50, 60, [0, 25, 50], [0, 30, 60],
              [dict(pts=curve(lambda n: k / n, k / 60, 50), cls="line1", label=u, lpos=(50, k / 50), dx=4, dy=4) for k, u in [(300, "U₁"), (600, "U₂"), (900, "U₃")]],
              xl=xl.split(" (")[0], yl=yl.split(" (")[0], title=t[0], W=240, H=200, aria=t[0])
    b = chart(lang, 17, 9, [0, 4, 8, 12, 16], [0, 4, 8],
              [dict(pts=[(0, u / 2), (u, 0)], cls="line1", label=f"{u} Go" if lang == "fr" else f"{u} GB", lpos=(0, u / 2), dx=6, dy=4) for u in (8, 12, 16)],
              xl=t[6], yl=t[7], title=t[1], W=240, H=200, aria=t[1])
    c = chart(lang, 20, 20, [0, 5, 10, 15, 20], [0, 5, 10, 15, 20],
              [dict(pts=[(k, 19), (k, k), (19, k)], cls="line1", label=f"U = {k}", lpos=(19, k), dx=-2, dy=-6, anchor="end") for k in (5, 10, 15)],
              [dict(q=k, p=k, cls="c1") for k in (5, 10, 15)],
              xl=t[8], yl=t[9], title=t[2], W=240, H=200, aria=t[2])
    caps = [f"<b>{t[3]}</b> · U = N<sup>α</sup>·H<sup>β</sup> (Cobb-Douglas)", f"<b>{t[4]}</b> · U = X + 2Y",
            f"<b>{t[5]}</b> · U = min(N, H) (Leontief)"]
    return '<div class="grid" style="margin:0">' + "".join(f'<div>{s}<p style="font-size:.85rem;margin:4px 0 0">{c_}</p></div>' for s, c_ in zip((a, b, c), caps)) + "</div>"


def svg_budget(lang, mode):
    xl, yl = lab_NH(lang)
    if mode == "base":
        ser = [dict(pts=[(0, 40), (80, 0)], cls="line1", label="L₁ : 2H + N = 80" if lang == "fr" else "L₁: 2H + N = 80", lpos=(50, 15), dx=6, dy=-8)]
        mk = [dict(q=n, p=h, label=k, dx=6, dy=-8) for k, n, h in [("A", 0, 40), ("B", 20, 30), ("C", 40, 20), ("D", 60, 10), ("E", 80, 0)]]
        return chart(lang, 170, 85, [0, 40, 80, 120, 160], [0, 20, 40, 60, 80], ser, mk, xl=xl, yl=yl, W=420, H=260,
                     title=("Budget line (R = €80, P_H = €2, P_N = €1)" if lang == "en" else "Droite de budget (R = 80 €, P_H = 2 €, P_N = 1 €)"), aria="budget")
    if mode == "income":
        ser = [dict(pts=[(0, 40), (80, 0)], cls="line1", label="L₁ (R = 80)", lpos=(40, 20), dx=6, dy=-8),
               dict(pts=[(0, 80), (160, 0)], cls="line2", label="L₂ (R = 160)", lpos=(90, 35), dx=6, dy=-8)]
        t = "Income doubles → parallel shift" if lang == "en" else "Le revenu double → déplacement parallèle"
    else:
        ser = [dict(pts=[(0, 40), (80, 0)], cls="line1", label="L₁ (P_N = 1)", lpos=(40, 20), dx=-6, dy=14, anchor="end"),
               dict(pts=[(0, 40), (160, 0)], cls="line2", label=("L₂ (P_N = 0,5)" if lang == "fr" else "L₂ (P_N = 0.5)"), lpos=(110, 12.5), dx=6, dy=-8)]
        t = "P_N falls → rotation" if lang == "en" else "P_N baisse → rotation"
    return chart(lang, 170, 85, [0, 40, 80, 120, 160], [0, 20, 40, 60, 80], ser, [], xl=xl, yl=yl, W=320, H=240, title=t, aria=t)


def svg_cost_curves(lang):
    CV = [0, 50, 78, 98, 112, 130, 150, 175, 204, 242, 300, 385]
    ctm = [(q, (50 + CV[q]) / q) for q in range(2, 12)]
    cvm = [(q, CV[q] / q) for q in range(1, 12)]
    cfm = [(q, 50 / q) for q in range(1, 12)]
    cm = [(q - 0.5, CV[q] - CV[q - 1]) for q in range(1, 12)]
    names = {"en": ("ATC", "AVC", "AFC", "MC"), "fr": ("CTM", "CVM", "CFM", "Cm")}[lang]
    ser = [dict(pts=ctm, cls="lineT", label=names[0], lpos=ctm[-1], dx=6, dy=4),
           dict(pts=cvm, cls="line1", label=names[1], lpos=cvm[-1], dx=6, dy=4),
           dict(pts=cfm, cls="line1", dash=True, label=names[2], lpos=cfm[-1], dx=6, dy=4),
           dict(pts=cm, cls="line2", label=names[3], lpos=(10.5, 85), dx=6, dy=4)]
    mk = [dict(q=8, p=31.75, label="★", dx=-4, dy=-10, anchor="middle"),
          dict(q=7, p=25, label=("min AVC 25" if lang == "en" else "min CVM 25"), dx=-8, dy=16, anchor="end", cls="c1"),
          dict(q=3.5, p=14, label=("min MC 14" if lang == "en" else "min Cm 14"), dx=0, dy=16, anchor="middle", cls="c2")]
    return chart(lang, 12, 100, range(0, 13, 2), [0, 20, 40, 60, 80, 100], ser, mk, xl=("Quantity Q" if lang == "en" else "Quantité Q"), yl="€",
                 W=520, H=300, aria="cost curves")


def svg_isoquant(lang):
    xl = "Machines (K)" if lang == "en" else "Machines (K)"
    yl = "Workers (L)" if lang == "en" else "Ouvriers (L)"
    iso = [(1, 6), (2, 3), (3, 2), (6, 1)]
    ser = [dict(pts=iso, cls="lineT", label=("isoquant: 100 t-shirts" if lang == "en" else "isoquante : 100 t-shirts"), lpos=(1.5, 4.5), dx=8, dy=0),
           dict(pts=[(0, 380 / 60), (3.8, 0)], cls="line1", label=("isocost €380" if lang == "en" else "isocoût 380 €"), lpos=(0, 380 / 60), dx=6, dy=-6),
           dict(pts=[(0, 660 / 60), (6.6, 0)], cls="line1", dash=True, label=("isocost €660" if lang == "en" else "isocoût 660 €"), lpos=(2.2, 11 - 2.2 * 100 / 60), dx=8, dy=-4),
           dict(pts=[(0, 4.5), (5.4, 0)], cls="line2", dash=True, label=("€270 if K = €50" if lang == "en" else "270 € si K = 50 €"), lpos=(0, 4.5), dx=6, dy=14)]
    mk = [dict(q=1, p=6, label="A", dx=8, dy=-4, kind="open"), dict(q=2, p=3, label="B ★", dx=8, dy=-6),
          dict(q=3, p=2, label="C", dx=8, dy=-6, cls="c2"), dict(q=6, p=1, label="D", dx=-2, dy=-10, kind="open")]
    return chart(lang, 7, 11.5, range(0, 8), [0, 2, 4, 6, 8, 10], ser, mk, xl=xl, yl=yl, W=460, H=280, aria="isoquant")


def svg_merit(lang):
    techs = {"en": ["Renewables", "Nuclear", "Biomass", "CCGT gas", "Peakers (OCGT)"], "fr": ["Renouvelables", "Nucléaire", "Biomasse", "CCGT gaz", "Pointe (OCGT)"]}[lang]
    cm = [0, 12, 60, 103, 180]
    cap = [4, 4, 1.5, 4, 2]  # illustrative widths
    W, H = 560, 280
    L_, R_, T_, B_ = 46, W - 14, 16, H - 40
    tot = sum(cap)
    X = lambda q: L_ + q / (tot + 1) * (R_ - L_)
    Y = lambda p: B_ - p / 200 * (B_ - T_)
    s = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="merit order">']
    for v in (0, 50, 100, 150, 200):
        s.append(f'<line class="gridline" x1="{L_}" y1="{Y(v):.1f}" x2="{R_}" y2="{Y(v):.1f}"/><text x="{L_ - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" class="muted small">{v}</text>')
    s.append(f'<line class="axis" x1="{L_}" y1="{B_}" x2="{R_}" y2="{B_}"/><line class="axis" x1="{L_}" y1="{B_}" x2="{L_}" y2="{T_}"/>')
    s.append(f'<text x="{L_ + 4}" y="{T_ + 4}" class="muted small">€/MWh</text><text x="{R_}" y="{H - 6}" text-anchor="end" class="muted small">{"Capacity called (illustrative)" if lang == "en" else "Capacité appelée (illustratif)"}</text>')
    q = 0
    for name, c, w in zip(techs, cm, cap):
        x0, x1 = X(q) + 1, X(q + w) - 1
        top = Y(max(c, 2))
        cls = "fill2" if name.startswith("CCGT") else "fill1"
        s.append(f'<g><title>{name}: ~{c} €/MWh</title>{vbar(x0, top, x1 - x0, B_, cls)}</g>')
        s.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{top - 6:.1f}" text-anchor="middle" class="small bold">{c}</text>')
        s.append(f'<text x="{(x0 + x1) / 2:.1f}" y="{B_ + 14}" text-anchor="middle" class="small">{name}</text>')
        q += w
    dx = X(12)
    s.append(f'<line x1="{dx:.1f}" y1="{T_}" x2="{dx:.1f}" y2="{B_}" style="stroke:var(--text)" stroke-width="2" stroke-dasharray="6 4"/>')
    s.append(f'<text x="{dx + 6:.1f}" y="{T_ + 12}" class="small bold">{"Demand" if lang == "en" else "Demande"}</text>')
    s.append(f'<line x1="{L_}" y1="{Y(103):.1f}" x2="{dx:.1f}" y2="{Y(103):.1f}" style="stroke:var(--c2)" stroke-dasharray="3 3"/>')
    s.append(f'<text x="{L_ + 6}" y="{Y(103) - 6:.1f}" class="small bold">{"Spot price ≈ €103/MWh" if lang == "en" else "Prix spot ≈ 103 €/MWh"}</text>')
    s.append("</svg>")
    return "".join(s)


def svg_industry(lang):
    S = "S" if lang == "en" else "O"
    # D1: p = 70 - q ; S1: p = q - 6.5  -> A (38.25, 31.75)
    # D2: p = 106.5 - q -> B with S1 at p = 50 (q = 56.5) ; C with LR line at q = 74.75 ; S3: p = q - 43
    ser = [dict(pts=[(10, 60), (60, 10)], cls="line1", label="D₁", lpos=(60, 10), dx=4, dy=4),
           dict(pts=[(36.5, 70), (86.5, 20)], cls="line1", dash=True, label="D₂", lpos=(86.5, 20), dx=4, dy=4),
           dict(pts=[(16.5, 10), (76.5, 70)], cls="line2", label=f"{S}₁", lpos=(76.5, 70), dx=4, dy=4),
           dict(pts=[(53, 10), (100, 57)], cls="line2", dash=True, label=f"{S}₃", lpos=(100, 57), dx=-4, dy=-6, anchor="end"),
           dict(pts=[(0, 31.75), (100, 31.75)], cls="lineT", label=("p = min ATC (long run)" if lang == "en" else "p = min CTM (LT)"), lpos=(0, 31.75), dx=4, dy=-8)]
    mk = [dict(q=38.25, p=31.75, label="A", dx=-2, dy=18, anchor="middle"),
          dict(q=56.5, p=50, label=("B · p₂ = 50" if lang == "en" else "B · p₂ = 50"), dx=-10, dy=-4, anchor="end", cls="c2"),
          dict(q=74.75, p=31.75, label="C", dx=0, dy=18, anchor="middle")]
    return chart(lang, 100, 75, [0, 25, 50, 75, 100], [0, 25, 50, 75], ser, mk, xl=("Market quantity" if lang == "en" else "Quantité de marché"), yl="p (€)",
                 W=500, H=280, aria="industry adjustment")


CS_WIDGET = '''<div class="tot" id="cs">
<b><span class="en">Try it: find the optimal basket</span><span class="fr">À vous : trouvez le panier optimal</span></b>
<p style="margin:6px 0 10px;font-size:.92rem"><span class="en">Budget 2H + N = 80, utility U = N·H. Slide along the budget line.</span><span class="fr">Budget 2H + N = 80, utilité U = N·H. Glissez le long de la droite de budget.</span></p>
<div style="font-size:1.25rem;font-weight:700">N = <span id="csn"></span> · H = <span id="csh"></span> · U = <span id="csu"></span></div>
<input type="range" id="css" min="40" max="760" step="5" aria-label="food">
<svg viewBox="0 0 420 270" id="cssvg" aria-hidden="true"></svg>
<div class="row"><span id="cst"></span><span><span class="en">Price ratio P<sub>N</sub>/P<sub>H</sub> = 0.5</span><span class="fr">Rapport des prix P<sub>N</sub>/P<sub>H</sub> = 0,5</span></span></div>
<div class="verdict" id="csv"></div>
</div>'''

CS_JS = '''<script>
(function(){
  var s=document.getElementById("css"),svg=document.getElementById("cssvg");
  var L=42,R=406,T=14,B=236,NM=85,HM=60;
  var X=function(n){return L+n/NM*(R-L)},Y=function(h){return B-h/HM*(B-T)};
  var fr=function(){return document.documentElement.lang==="fr"};
  var f=function(x,d){var t=x.toFixed(d);return fr()?t.replace(".",","):t};
  var T_=function(en,frs){return '<span class="en">'+en+'</span><span class="fr">'+frs+'</span>'};
  function ic(u,cls,dash){var p=[];for(var n=u/HM;n<=NM;n+=0.5){p.push(X(n).toFixed(1)+","+Y(u/n).toFixed(1))}return '<polyline points="'+p.join(" ")+'" class="'+cls+'"'+(dash?' stroke-dasharray="5 4"':'')+'/>'}
  function render(){
    var n=s.value/10,h=40-n/2,u=n*h,mrs=h/n;
    document.getElementById("csn").textContent=f(n,1);document.getElementById("csh").textContent=f(h,1);document.getElementById("csu").textContent=f(u,0);
    var g="";
    [0,20,40,60].forEach(function(v){g+='<line class="gridline" x1="'+L+'" y1="'+Y(v)+'" x2="'+R+'" y2="'+Y(v)+'"/><text x="'+(L-6)+'" y="'+(Y(v)+4)+'" text-anchor="end" class="muted small">'+v+'</text>'});
    [0,20,40,60,80].forEach(function(v){g+='<text x="'+X(v)+'" y="'+(B+15)+'" text-anchor="middle" class="muted small">'+v+'</text>'});
    g+='<line class="axis" x1="'+L+'" y1="'+B+'" x2="'+R+'" y2="'+B+'"/><line class="axis" x1="'+L+'" y1="'+B+'" x2="'+L+'" y2="'+(T-4)+'"/>';
    g+='<text x="'+R+'" y="'+(B+30)+'" text-anchor="end" class="muted small">N</text><text x="'+(L+5)+'" y="'+(T+6)+'" class="muted small">H</text>';
    g+=ic(800,"line1",true)+'<text x="'+(X(80)-4)+'" y="'+(Y(10)-6)+'" text-anchor="end" class="muted small">U = 800</text>';
    g+='<polyline class="lineT" points="'+X(0)+','+Y(40)+' '+X(80)+','+Y(0)+'"/>';
    g+=ic(u,"line2",false);
    var d=8;g+='<line x1="'+X(n-d)+'" y1="'+Y(h+mrs*d)+'" x2="'+X(n+d)+'" y2="'+Y(h-mrs*d)+'" style="stroke:var(--c2)" stroke-width="1.5"/>';
    g+='<circle cx="'+X(n)+'" cy="'+Y(h)+'" r="6" class="c2 ring"/>';
    svg.innerHTML=g;
    document.getElementById("cst").innerHTML=T_("MRS = H/N = ","TMS = H/N = ")+"<b>"+f(mrs,2)+"</b>";
    var v=document.getElementById("csv");
    if(Math.abs(mrs-0.5)<0.03) v.innerHTML='<span class="ok">'+T_("Optimum: MRS = price ratio. The indifference curve is tangent to the budget line (N = 40, H = 20, U = 800).","Optimum : TMS = rapport des prix. La courbe d’indifférence est tangente à la droite de budget (N = 40, H = 20, U = 800).")+'</span>';
    else if(mrs>0.5) v.innerHTML='<span class="no">'+T_("MRS &gt; 0.5: you value food more than the market does → buy more N, less H.","TMS &gt; 0,5 : vous valorisez l’alimentation plus que le marché → achetez plus de N, moins de H.")+'</span>';
    else v.innerHTML='<span class="no">'+T_("MRS &lt; 0.5: you value food less than the market does → buy less N, more H.","TMS &lt; 0,5 : vous valorisez l’alimentation moins que le marché → achetez moins de N, plus de H.")+'</span>';
  }
  s.addEventListener("input",render);
  document.querySelectorAll(".lang-switch button").forEach(function(b){b.addEventListener("click",function(){setTimeout(render,0)})});
  s.value=150; render();
})();
</script>'''

PF_WIDGET = '''<div class="tot" id="pf">
<b><span class="en">Try it: the firm's decision at each price</span><span class="fr">À vous : la décision de la firme à chaque prix</span></b>
<p style="margin:6px 0 10px;font-size:.92rem"><span class="en">Cost table of the course (fixed cost = 50). The firm picks the quantity that maximises profit.</span><span class="fr">Tableau de coûts du cours (coût fixe = 50). La firme choisit la quantité qui maximise le profit.</span></p>
<div style="font-size:1.25rem;font-weight:700">p = <span id="pfp"></span> € · Q* = <span id="pfq"></span> · <span class="en">profit</span><span class="fr">profit</span> = <span id="pfr"></span></div>
<input type="range" id="pfs" min="10" max="90" step="1" aria-label="price">
<svg viewBox="0 0 460 280" id="pfsvg" aria-hidden="true"></svg>
<div class="verdict" id="pfv"></div>
<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:10px"><button type="button" data-p="20">p = 20</button><button type="button" data-p="28">p = 28</button><button type="button" data-p="32">p = 32</button><button type="button" data-p="50">p = 50</button></div>
</div>'''

PF_JS = '''<script>
(function(){
  var CV=[0,50,78,98,112,130,150,175,204,242,300,385],CF=50;
  var s=document.getElementById("pfs"),svg=document.getElementById("pfsvg");
  var L=42,R=446,T=14,B=244,QM=12,PM=100;
  var X=function(q){return L+q/QM*(R-L)},Y=function(p){return B-Math.min(p,PM)/PM*(B-T)};
  var fr=function(){return document.documentElement.lang==="fr"};
  var f=function(x,d){var t=x.toFixed(d);return fr()?t.replace(".",","):t};
  var T_=function(en,frs){return '<span class="en">'+en+'</span><span class="fr">'+frs+'</span>'};
  function poly(pts,cls,dash){return '<polyline class="'+cls+'"'+(dash?' stroke-dasharray="6 4"':'')+' points="'+pts.map(function(p){return X(p[0]).toFixed(1)+","+Y(p[1]).toFixed(1)}).join(" ")+'"/>'}
  function render(){
    var p=+s.value,best=0,bp=-CF;
    for(var q=1;q<=11;q++){var pr=p*q-CF-CV[q];if(pr>bp+1e-9){bp=pr;best=q}}
    document.getElementById("pfp").textContent=p;document.getElementById("pfq").textContent=best;document.getElementById("pfr").textContent=(bp>0?"+":"")+bp;
    var g="",n=fr()?["CTM","CVM","Cm"]:["ATC","AVC","MC"];
    [0,20,40,60,80,100].forEach(function(v){g+='<line class="gridline" x1="'+L+'" y1="'+Y(v)+'" x2="'+R+'" y2="'+Y(v)+'"/><text x="'+(L-6)+'" y="'+(Y(v)+4)+'" text-anchor="end" class="muted small">'+v+'</text>'});
    [0,2,4,6,8,10,12].forEach(function(v){g+='<text x="'+X(v)+'" y="'+(B+15)+'" text-anchor="middle" class="muted small">'+v+'</text>'});
    if(best>0){var atc=(CF+CV[best])/best;g+='<rect x="'+L+'" y="'+Math.min(Y(p),Y(atc))+'" width="'+(X(best)-L)+'" height="'+Math.abs(Y(p)-Y(atc))+'" class="'+(bp>=0?"fill1":"fill2")+'" opacity=".3"/>';}
    g+='<line class="axis" x1="'+L+'" y1="'+B+'" x2="'+R+'" y2="'+B+'"/><line class="axis" x1="'+L+'" y1="'+B+'" x2="'+L+'" y2="'+(T-4)+'"/>';
    var ctm=[],cvm=[],cm=[];for(q=1;q<=11;q++){if(q>1)ctm.push([q,(CF+CV[q])/q]);cvm.push([q,CV[q]/q]);cm.push([q-0.5,CV[q]-CV[q-1]])}
    g+=poly(ctm,"lineT")+poly(cvm,"line1")+poly(cm,"line2");
    g+='<text x="'+(X(11)+5)+'" y="'+(Y(39.5)+4)+'" class="small bold">'+n[0]+'</text><text x="'+(X(11)+5)+'" y="'+(Y(35)+14)+'" class="small bold">'+n[1]+'</text><text x="'+(X(10.5)+6)+'" y="'+(Y(85)+4)+'" class="small bold">'+n[2]+'</text>';
    g+='<line x1="'+L+'" y1="'+Y(p)+'" x2="'+R+'" y2="'+Y(p)+'" style="stroke:var(--text)" stroke-dasharray="5 4"/><text x="'+(R-4)+'" y="'+(Y(p)-6)+'" text-anchor="end" class="small bold">p = Rm</text>';
    if(best>0)g+='<circle cx="'+X(best)+'" cy="'+Y(p)+'" r="6" class="c2 ring"/>';
    svg.innerHTML=g;
    var v=document.getElementById("pfv");
    if(p<25) v.innerHTML='<span class="no">'+T_("p &lt; min AVC (25): SHUT DOWN. Producing would lose more than the fixed cost; loss = CF = 50.","p &lt; min CVM (25) : FERMER. Produire ferait perdre plus que le coût fixe ; perte = CF = 50.")+'</span>';
    else if(p<31.75) v.innerHTML='<span class="no">'+T_("min AVC &lt; p &lt; min ATC: loss ("+bp+"), but smaller than shutting down (−50). Keep producing in the short run.","min CVM &lt; p &lt; min CTM : perte ("+bp+"), mais inférieure à celle de la fermeture (−50). Continuer à produire à court terme.")+'</span>';
    else v.innerHTML='<span class="ok">'+T_("p &gt; min ATC (31.75): positive profit — PRODUCE. In the long run, profits attract entrants and p falls towards 31.75.","p &gt; min CTM (31,75) : profit positif — PRODUIRE. À long terme, les profits attirent des entrants et p baisse vers 31,75.")+'</span>';
  }
  s.addEventListener("input",render);
  document.querySelectorAll("#pf button").forEach(function(b){b.addEventListener("click",function(){s.value=b.dataset.p;render()})});
  document.querySelectorAll(".lang-switch button").forEach(function(b){b.addEventListener("click",function(){setTimeout(render,0)})});
  s.value=50; render();
})();
</script>'''


# ---------------- page 3.1

def page_s3():
    b = []
    b.append(L(
        '''<p class="kicker">Session 3</p><h1>Consumer choice</h1><p class="lead">How does a consumer with a limited income decide what to buy? Preferences · budget · optimum · behaviour.</p>
<div class="toc"><b>In this lesson</b><ol><li>Preferences — baskets, indifference curves, MRS, special cases</li><li>The budget constraint — budget line, income and price effects</li><li>The optimal choice — tangency between indifference curve and budget</li><li>Behavioural critiques — Kahneman, Tversky, Thaler, framing</li></ol></div>''',
        '''<p class="kicker">Séance 3</p><h1>Le choix du consommateur</h1><p class="lead">Comment un consommateur, contraint par un revenu limité, décide-t-il de ses achats ? Préférences · budget · optimum · comportement.</p>
<div class="toc"><b>Au programme</b><ol><li>Les préférences — paniers, courbes d'indifférence, TMS, cas particuliers</li><li>La contrainte budgétaire — droite de budget, effets revenu et prix</li><li>Le choix optimal — tangence entre courbe d'indifférence et budget</li><li>Critiques comportementales — Kahneman, Tversky, Thaler, effet de framing</li></ol></div>'''))
    b.append(L(
        f'''<h2><span class="badge">1</span>Preferences</h2>
<p>Preferences can be inferred from observed behaviour. Neoclassical theory assumes a rational framework built on three axioms.</p>
<div class="grid">
<div class="card"><span class="tag">① Completeness</span><h4>Every basket can be ranked</h4><p>For any A and B: A ≻ B, B ≻ A or A ~ B.</p><p style="font-size:.85rem;color:var(--muted)">Hidden assumption: preferences are exogenous — given before the choice, stable, independent of context and peers.</p></div>
<div class="card"><span class="tag">② Transitivity</span><h4>Consistency</h4><p>If A ≻ B and B ≻ C ⟹ A ≻ C. Guarantees a stable ordinal ranking of baskets.</p></div>
<div class="card"><span class="tag">③ Non-satiation</span><h4>More is better</h4><p>More of a good always increases satisfaction. Graphically: indifference curves slope downwards.</p></div>
</div>
<h3>Baskets of goods</h3>
<p>Two goods only: <b>food (N)</b> and <b>clothing (H)</b>. A basket is a pair (N, H). (Source: Pindyck &amp; Rubinfeld, 2012.)</p>
<figure>{svg_baskets("en")}<figcaption>A, B and D lie on the same indifference curve U₁: the consumer is indifferent between them. E ≻ A (more of both — non-satiation); G and H lie below U₁, so A is preferred to them.</figcaption></figure>
<h3>Indifference curves</h3>
<div class="callout"><strong>Definition</strong>The set of baskets (N, H) that give the <b>same level of satisfaction</b>. Curves further from the origin are better: U₃ ≻ U₂ ≻ U₁.</div>
<div class="grid">
<div class="card"><h4>Negative slope</h4><p>To get more of one good you must give up some of the other (non-satiation).</p></div>
<div class="card"><h4>Convexity</h4><p>Diminishing MRS: a taste for variety.</p></div>
<div class="card"><h4>They never cross</h4><p>Follows from transitivity + non-satiation (proof below).</p></div>
</div>
<p><b>Three common utility functions:</b> Cobb-Douglas U = X<sup>α</sup>·Y<sup>β</sup> · perfect substitutes U = aX + bY (straight-line curves) · perfect complements U = min(aX, bY) (L-shaped curves).</p>
<h3>Why indifference curves can never cross</h3>
<div class="grid" style="align-items:start">
<figure style="margin:0">{svg_cross("en")}</figure>
<div><p>Proof by contradiction — suppose U₁ and U₂ cross at A:</p><ol><li>A and B are on U₁ ⟹ A ~ B</li><li>A and D are on U₂ ⟹ A ~ D</li><li>Transitivity ⟹ B ~ D</li><li>But B = (10, 45) and D = (10, 40): same food, more clothing in B. Non-satiation ⟹ B ≻ D. <b>Contradiction.</b></li></ol><p>So two indifference curves can never cross. ∎</p></div>
</div>
<h3>Ordinal utility</h3>
<p>Only the <b>ranking</b> matters, not the number. With U = N·H, (5, 5) = 25 and (5, 10) = 50; with U = 4·N·H, 100 and 200 — same conclusion: (5, 10) is preferred.</p>
<div class="grid">
<div class="card"><span class="tag">Walras</span><h4>Cardinal utility</h4><p>Give each basket an objective, measurable value.</p></div>
<div class="card"><span class="tag">Pareto, Samuelson, Hicks</span><h4>Ordinal utility</h4><p>Only the ranking counts: individuals cannot assign a precise, objective value.</p></div>
</div>
<h3>The marginal rate of substitution (MRS)</h3>
<div class="callout"><strong>Definition</strong>The amount of one good a consumer is willing to give up to get one more unit of another, keeping satisfaction unchanged. <span class="formula">MRS(N,H) = −ΔH/ΔN = (∂U/∂N) ÷ (∂U/∂H) &gt; 0</span> — the absolute value of the slope of the indifference curve.</div>
<figure>{svg_mrs("en")}<figcaption>On U₂ = N·H = 600 the MRS = H/N falls as you move right: 6 at A (very willing to give up clothing), 1.5 at B, 0.67 at C (hardly willing). <b>Convexity = taste for variety:</b> mixing A (10, 60) and C (30, 20) half-and-half gives (20, 40), with U = 800 &gt; 600 — strictly preferred.</figcaption></figure>
<details class="q"><summary>Derivation: why is MRS = U′ₓ / U′ᵧ?</summary>Take U = f(x, y). Total differential: dU = (∂U/∂x)dx + (∂U/∂y)dy. On an indifference curve dU = 0, so (∂U/∂x)dx = −(∂U/∂y)dy and therefore −dy/dx = (∂U/∂x)/(∂U/∂y). With U = N·H: U′<sub>N</sub> = H, U′<sub>H</sub> = N, so MRS = H/N. The MRS is the consumer's “subjective price” of N in units of H.</details>
<h3>Special cases</h3>
<figure>{svg_special("en")}<figcaption>The relationship between the goods shapes the curves. Perfect substitutes: the consumer swaps at a fixed rate (one 2 GB key = two 1 GB keys). Perfect complements: satisfaction rises only if both goods rise together (a left shoe is useless without a right one).</figcaption></figure>''',
        f'''<h2><span class="badge">1</span>Les préférences</h2>
<p>Les préférences peuvent être déduites de l'observation du comportement. La théorie néoclassique suppose un cadre rationnel fondé sur trois axiomes.</p>
<div class="grid">
<div class="card"><span class="tag">① Complétude</span><h4>Tous les paniers sont comparables</h4><p>Pour tout A et B : A ≻ B, B ≻ A ou A ~ B.</p><p style="font-size:.85rem;color:var(--muted)">Hypothèse cachée : les préférences sont exogènes — données avant le choix, stables, indépendantes du contexte et des pairs.</p></div>
<div class="card"><span class="tag">② Transitivité</span><h4>Cohérence</h4><p>Si A ≻ B et B ≻ C ⟹ A ≻ C. Garantit un classement ordinal stable des paniers.</p></div>
<div class="card"><span class="tag">③ Non-satiété</span><h4>Plus est préféré à moins</h4><p>Davantage d'un bien augmente toujours la satisfaction. Graphiquement : les courbes d'indifférence ont une pente négative.</p></div>
</div>
<h3>Les paniers de biens</h3>
<p>Deux biens seulement : <b>produits alimentaires (N)</b> et <b>vêtements (H)</b>. Un panier est un couple (N, H). (Source : Pindyck et Rubinfeld, 2012.)</p>
<figure>{svg_baskets("fr")}<figcaption>A, B et D sont sur la même courbe d'indifférence U₁ : le consommateur est indifférent entre eux. E ≻ A (plus des deux biens — non-satiété) ; G et H sont sous U₁, A leur est donc préféré.</figcaption></figure>
<h3>Les courbes d'indifférence</h3>
<div class="callout"><strong>Définition</strong>Ensemble des paniers (N, H) qui procurent le <b>même niveau de satisfaction</b>. Plus loin de l'origine = mieux : U₃ ≻ U₂ ≻ U₁.</div>
<div class="grid">
<div class="card"><h4>Pente négative</h4><p>Pour obtenir plus d'un bien, il faut renoncer à l'autre (non-satiété).</p></div>
<div class="card"><h4>Convexité</h4><p>TMS décroissant : préférence pour la diversité.</p></div>
<div class="card"><h4>Non-croisement</h4><p>Découle de la transitivité + non-satiété (démonstration ci-dessous).</p></div>
</div>
<p><b>Trois fonctions d'utilité courantes :</b> Cobb-Douglas U = X<sup>α</sup>·Y<sup>β</sup> · substituts parfaits U = aX + bY (CI linéaires) · complémentaires parfaits U = min(aX, bY) (CI en L).</p>
<h3>Pourquoi les CI ne peuvent jamais se croiser</h3>
<div class="grid" style="align-items:start">
<figure style="margin:0">{svg_cross("fr")}</figure>
<div><p>Raisonnement par l'absurde — supposons que U₁ et U₂ se croisent en A :</p><ol><li>A et B sont sur U₁ ⟹ A ~ B</li><li>A et D sont sur U₂ ⟹ A ~ D</li><li>Transitivité ⟹ B ~ D</li><li>Or B = (10, 45) et D = (10, 40) : même N, plus de H en B. Non-satiété ⟹ B ≻ D. <b>Contradiction.</b></li></ol><p>Deux courbes d'indifférence ne peuvent donc jamais se croiser. CQFD</p></div>
</div>
<h3>Utilité ordinale</h3>
<p>Seul le <b>classement</b> compte, pas la valeur. Avec U = N·H, (5, 5) = 25 et (5, 10) = 50 ; avec U = 4·N·H, 100 et 200 — même conclusion : (5, 10) est préféré.</p>
<div class="grid">
<div class="card"><span class="tag">Walras</span><h4>Utilité cardinale</h4><p>Attribuer une valeur mesurable et objective à chaque panier.</p></div>
<div class="card"><span class="tag">Pareto, Samuelson, Hicks</span><h4>Utilité ordinale</h4><p>Seul le classement importe : les individus ne peuvent pas attribuer une valeur précise et objective.</p></div>
</div>
<h3>Le taux marginal de substitution (TMS)</h3>
<div class="callout"><strong>Définition</strong>Quantité d'un bien à laquelle le consommateur est prêt à renoncer pour obtenir une unité supplémentaire d'un autre, à satisfaction inchangée. <span class="formula">TMS(N,H) = −ΔH/ΔN = (∂U/∂N) ÷ (∂U/∂H) &gt; 0</span> — la valeur absolue de la pente de la courbe d'indifférence.</div>
<figure>{svg_mrs("fr")}<figcaption>Sur U₂ = N·H = 600, le TMS = H/N diminue vers la droite : 6 en A (très prêt à sacrifier des vêtements), 1,5 en B, 0,67 en C (très peu disposé). <b>Convexité = goût pour la diversité :</b> le mélange à parts égales de A (10, 60) et C (30, 20) donne (20, 40), avec U = 800 &gt; 600 — strictement préféré.</figcaption></figure>
<details class="q"><summary>Dérivation : pourquoi TMS = U′ₓ / U′ᵧ ?</summary>Soit U = f(x, y). Différentielle totale : dU = (∂U/∂x)dx + (∂U/∂y)dy. Sur une courbe d'indifférence dU = 0, donc (∂U/∂x)dx = −(∂U/∂y)dy et −dy/dx = (∂U/∂x)/(∂U/∂y). Avec U = N·H : U′<sub>N</sub> = H, U′<sub>H</sub> = N, donc TMS = H/N. Le TMS est le « prix subjectif » de N exprimé en H.</details>
<h3>Cas particuliers</h3>
<figure>{svg_special("fr")}<figcaption>La relation entre les biens détermine la forme des courbes. Substituts parfaits : le consommateur échange à taux fixe (une clé de 2 Go = deux clés de 1 Go). Complémentaires parfaits : la satisfaction n'augmente que si les deux biens augmentent ensemble (une chaussure gauche ne sert à rien sans la droite).</figcaption></figure>'''))
    rows = lambda lang: "".join(f'<tr><td>{k}</td><td class="num">{n}</td><td class="num">{h}</td><td class="num">{n} + {2 * h} = 80 €</td></tr>'.replace(" €", " €" if lang == "fr" else "") for k, n, h in [("A", 0, 40), ("B", 20, 30), ("C", 40, 20), ("D", 60, 10), ("E", 80, 0)])
    b.append(L(
        f'''<h2><span class="badge">2</span>The budget constraint</h2>
<p>The <b>budget line</b> is the set of baskets whose cost exactly equals disposable income R.</p>
<p class="formula">P<sub>H</sub>·H + P<sub>N</sub>·N = R &nbsp;⟹&nbsp; H = R/P<sub>H</sub> − (P<sub>N</sub>/P<sub>H</sub>)·N</p>
<p>Example: R = €80 per week, P<sub>H</sub> = €2, P<sub>N</sub> = €1 ⟹ 2H + N = 80 ⟹ <b>H = 40 − N/2</b>.</p>
<div class="grid" style="align-items:start">
<div class="table-wrap"><table><thead><tr><th>Basket</th><th class="num">Food N</th><th class="num">Clothing H</th><th class="num">Spending (€)</th></tr></thead><tbody>{rows("en")}</tbody></table></div>
<figure style="margin:14px 0">{svg_budget("en", "base")}</figure>
</div>
<div class="grid">
<div class="card"><span class="tag">Intercepts</span><h4>Maximum of each good</h4><p>H-intercept (N = 0): R/P<sub>H</sub> = 40. N-intercept (H = 0): R/P<sub>N</sub> = 80.</p></div>
<div class="card"><span class="tag">Slope = −P<sub>N</sub>/P<sub>H</sub> = −1/2</span><h4>The market trade-off</h4><p>Give up 1 unit of clothing to get 2 units of food. Constant along the line (from B to C: ΔH/ΔN = −10/20). It does not depend on income.</p></div>
</div>
<figure><div class="grid" style="margin:0">{svg_budget("en", "income")}{svg_budget("en", "price")}</div><figcaption><b>Left:</b> a change in income R moves the line <b>parallel</b> to itself; the slope stays −1/2, only the intercepts change. <b>Right:</b> a change in one price <b>rotates</b> the line: P<sub>N</sub> 1 → 0.5 makes the slope −1/4; the H-intercept stays at 40, the N-intercept goes from 80 to 160. A heavy food buyer gains a lot of purchasing power; someone who only buys clothing is unaffected.</figcaption></figure>
<div class="callout"><strong>Summary</strong>R changes → parallel shift · P<sub>N</sub> changes → rotation around the H-intercept · P<sub>H</sub> changes → rotation around the N-intercept · R, P<sub>N</sub> and P<sub>H</sub> all ×2 (proportional inflation) → the line does not move: real purchasing power is unchanged.</div>''',
        f'''<h2><span class="badge">2</span>La contrainte budgétaire</h2>
<p>La <b>droite de budget</b> est l'ensemble des paniers dont la dépense est exactement égale au revenu disponible R.</p>
<p class="formula">P<sub>H</sub>·H + P<sub>N</sub>·N = R &nbsp;⟹&nbsp; H = R/P<sub>H</sub> − (P<sub>N</sub>/P<sub>H</sub>)·N</p>
<p>Exemple : R = 80 € par semaine, P<sub>H</sub> = 2 €, P<sub>N</sub> = 1 € ⟹ 2H + N = 80 ⟹ <b>H = 40 − N/2</b>.</p>
<div class="grid" style="align-items:start">
<div class="table-wrap"><table><thead><tr><th>Panier</th><th class="num">Alim. N</th><th class="num">Vêt. H</th><th class="num">Dépense</th></tr></thead><tbody>{rows("fr")}</tbody></table></div>
<figure style="margin:14px 0">{svg_budget("fr", "base")}</figure>
</div>
<div class="grid">
<div class="card"><span class="tag">Intercepts</span><h4>Maximum de chaque bien</h4><p>Intercept H (N = 0) : R/P<sub>H</sub> = 40. Intercept N (H = 0) : R/P<sub>N</sub> = 80.</p></div>
<div class="card"><span class="tag">Pente = −P<sub>N</sub>/P<sub>H</sub> = −1/2</span><h4>L'arbitrage du marché</h4><p>Abandonner 1 unité de vêtements pour obtenir 2 unités d'alimentation. Constante sur toute la droite (de B à C : ΔH/ΔN = −10/20). Indépendante du revenu.</p></div>
</div>
<figure><div class="grid" style="margin:0">{svg_budget("fr", "income")}{svg_budget("fr", "price")}</div><figcaption><b>À gauche :</b> une variation du revenu R déplace la droite <b>parallèlement</b> ; la pente reste −1/2, seuls les intercepts changent. <b>À droite :</b> la variation d'un prix fait <b>pivoter</b> la droite : P<sub>N</sub> 1 → 0,5 donne une pente de −1/4 ; l'intercept H reste à 40, l'intercept N passe de 80 à 160. Un gros acheteur d'alimentation gagne beaucoup de pouvoir d'achat ; celui qui n'achète que des vêtements n'est pas affecté.</figcaption></figure>
<div class="callout"><strong>Récapitulatif</strong>R varie → déplacement parallèle · P<sub>N</sub> varie → rotation autour de l'intercept H · P<sub>H</sub> varie → rotation autour de l'intercept N · R, P<sub>N</sub> et P<sub>H</sub> tous ×2 (inflation proportionnelle) → la droite ne bouge pas : le pouvoir d'achat réel est inchangé.</div>'''))
    b.append(L(
        '''<h2><span class="badge">3</span>The optimal choice</h2>
<p>Combining preferences (indifference curves) and the budget (line) tells us how the consumer allocates income. The optimal basket must:</p>
<div class="grid">
<div class="card"><span class="tag">①</span><h4>Lie on the budget line</h4><p>Use exactly all income. Below the line: money left unused (sub-optimal, unless saving). Above: unaffordable.</p></div>
<div class="card"><span class="tag">②</span><h4>Reach the highest indifference curve</h4><p>The highest curve that still touches the budget line. Higher curves are out of budget; lower ones are affordable but sub-optimal.</p></div>
</div>''',
        '''<h2><span class="badge">3</span>Le choix optimal</h2>
<p>En combinant les préférences (courbes d'indifférence) et le budget (droite), on détermine comment le consommateur alloue son revenu. Le panier optimal doit :</p>
<div class="grid">
<div class="card"><span class="tag">①</span><h4>Appartenir à la droite de budget</h4><p>Utiliser exactement tout le revenu. Sous la droite : budget non utilisé (sous-optimal, sauf épargne). Au-dessus : inaccessible.</p></div>
<div class="card"><span class="tag">②</span><h4>Atteindre la CI la plus haute</h4><p>La plus haute qui touche encore la droite de budget. Les CI plus hautes sont hors budget ; les plus basses accessibles mais sous-optimales.</p></div>
</div>'''))
    b.append(CS_WIDGET)
    b.append(L(
        '''<div class="callout"><strong>Optimality condition</strong>At the optimum A, the indifference curve is <b>tangent</b> to the budget line: <span class="formula">MRS(N, H) = P<sub>N</sub>/P<sub>H</sub></span> The MRS is the subjective value of the good (preferences); the price ratio is its market value. At the optimum, subjective value = market value: no more mutually beneficial swap is possible.</div>
<div class="table-wrap"><table><thead><tr><th>Basket</th><th class="num">MRS = H/N</th><th class="num">Slope of budget</th><th class="num">U = N·H</th><th>Verdict</th></tr></thead><tbody>
<tr class="hl"><td>A (N = 40, H = 20)</td><td class="num">0.5</td><td class="num">0.5</td><td class="num">800</td><td>Optimum ✓</td></tr>
<tr><td>B (N ≈ 26.7, H ≈ 26.7)</td><td class="num">1</td><td class="num">0.5</td><td class="num">≈ 711</td><td>Sub-optimal: the consumer would give up 1 H for 1 N, but the market only asks ½ H → buy more food</td></tr></tbody></table></div>''',
        '''<div class="callout"><strong>Condition d'optimalité</strong>À l'optimum A, la courbe d'indifférence est <b>tangente</b> à la droite de budget : <span class="formula">TMS(N, H) = P<sub>N</sub>/P<sub>H</sub></span> Le TMS mesure la valeur subjective du bien (préférences) ; le rapport des prix, sa valeur de marché. À l'optimum, valeur subjective = valeur de marché : plus aucun échange mutuellement avantageux n'est possible.</div>
<div class="table-wrap"><table><thead><tr><th>Panier</th><th class="num">TMS = H/N</th><th class="num">Pente du budget</th><th class="num">U = N·H</th><th>Verdict</th></tr></thead><tbody>
<tr class="hl"><td>A (N = 40, H = 20)</td><td class="num">0,5</td><td class="num">0,5</td><td class="num">800</td><td>Optimum ✓</td></tr>
<tr><td>B (N ≈ 26,7, H ≈ 26,7)</td><td class="num">1</td><td class="num">0,5</td><td class="num">≈ 711</td><td>Sous-optimal : le consommateur céderait 1 H pour 1 N, mais le marché ne demande que ½ H → acheter plus d'alimentation</td></tr></tbody></table></div>'''))
    b.append(L(
        '''<h2><span class="badge">4</span>Critiques of the rationality assumption</h2>
<p>A large body of lab and field evidence shows that people often behave contrary to rational-choice theory (Kahneman 2002, Thaler 2017).</p>
<div class="grid">
<div class="card"><span class="tag">① Unstable preferences</span><h4>Time inconsistency</h4><p>Decide today, give up soon after: “gym from Monday”, “I'll quit after this pack”.</p></div>
<div class="card"><span class="tag">② Errors of judgement</span><h4>Behavioural biases</h4><p>Optimism bias (skipping flood insurance), misjudged probabilities (playing the lottery despite tiny odds).</p></div>
<div class="card"><span class="tag">③ Preferences shaped by others</span><h4>Not exogenous</h4><p>Preferences depend on context and peers: Uᵢ depends on j's choices. Completeness and transitivity still hold, but the indifference map moves with the social group. E.g. a teenager buying an iPhone without real need on a modest income; buying what neighbours buy.</p></div>
</div>
<div class="callout"><strong>Framing effect</strong>How a choice is presented changes the decision. Station A: petrol €1.55 with a 5-cent discount for cash. Station B: €1.50 with a 5-cent surcharge for card. The cash price is identical, yet the “discount” offer wins (reference point + loss aversion). See <i>Misbehaving</i> by Richard Thaler (Nobel Prize 2017).</div>
<h2>Check yourself</h2>
<details class="q"><summary>Why must indifference curves slope downwards?</summary>Non-satiation: if you get more of one good, you must have less of the other to stay equally satisfied.</details>
<details class="q"><summary>With U = N·H, what is the MRS at (N = 25, H = 50)?</summary>MRS = H/N = 50/25 = 2: the consumer would give up 2 units of H for one more N.</details>
<details class="q"><summary>R = 120, P<sub>N</sub> = 2, P<sub>H</sub> = 3. Write the budget line and its intercepts.</summary>3H + 2N = 120 ⟹ H = 40 − (2/3)N. Intercepts: H = 40 (N = 0), N = 60 (H = 0). Slope −2/3.</details>
<details class="q"><summary>With U = N·H and the budget of the previous question, find the optimum.</summary>Tangency: H/N = 2/3 ⟹ H = (2/3)N. Budget: 3·(2/3)N + 2N = 120 ⟹ 4N = 120 ⟹ N = 30, H = 20, U = 600. (With Cobb-Douglas U = N·H, half of income goes to each good.)</details>
<details class="q"><summary>Income and all prices double. What happens to the budget line?</summary>Nothing: R/P<sub>H</sub>, R/P<sub>N</sub> and the slope are unchanged. Proportional inflation is neutral.</details>
<details class="q"><summary>What are the indifference curves for left and right shoes, and why?</summary>L-shaped (perfect complements, U = min(L, R)): an extra left shoe without a right one adds nothing.</details>''',
        '''<h2><span class="badge">4</span>Critiques de l'hypothèse de rationalité</h2>
<p>Une solide base empirique, en laboratoire et sur le terrain, montre que les comportements sont souvent contraires à la théorie du choix rationnel (Kahneman 2002, Thaler 2017).</p>
<div class="grid">
<div class="card"><span class="tag">① Préférences instables</span><h4>Incohérence temporelle</h4><p>Décider aujourd'hui, abandonner peu après : « la gym à partir de lundi », « j'arrête après ce paquet ».</p></div>
<div class="card"><span class="tag">② Erreurs de jugement</span><h4>Biais comportementaux</h4><p>Biais d'optimisme (ne pas s'assurer contre les inondations), mauvaise estimation des probabilités (jouer à la loterie malgré une chance infime).</p></div>
<div class="card"><span class="tag">③ Préférences influencées par autrui</span><h4>Non exogènes</h4><p>Les préférences dépendent du contexte et du groupe : Uᵢ dépend des choix de j. Complétude et transitivité restent vérifiées, mais la carte d'indifférence se déplace avec le groupe social. Ex. : un adolescent qui achète un iPhone sans réel besoin et avec un revenu modeste ; acheter les mêmes biens que ses voisins.</p></div>
</div>
<div class="callout"><strong>Effet de framing</strong>La façon de présenter un choix modifie la décision. Station A : essence à 1,55 € avec remise de 5 cts en espèces. Station B : 1,50 € avec majoration de 5 cts par carte. Le prix en espèces est identique, mais l'offre « avec remise » l'emporte (point de référence + aversion aux pertes). Voir <i>Misbehaving</i> de Richard Thaler (prix Nobel 2017).</div>
<h2>Testez-vous</h2>
<details class="q"><summary>Pourquoi les courbes d'indifférence ont-elles une pente négative ?</summary>Non-satiété : si l'on a plus d'un bien, il faut moins de l'autre pour rester aussi satisfait.</details>
<details class="q"><summary>Avec U = N·H, quel est le TMS en (N = 25, H = 50) ?</summary>TMS = H/N = 50/25 = 2 : le consommateur céderait 2 unités de H pour une unité de N en plus.</details>
<details class="q"><summary>R = 120, P<sub>N</sub> = 2, P<sub>H</sub> = 3. Écrivez la droite de budget et ses intercepts.</summary>3H + 2N = 120 ⟹ H = 40 − (2/3)N. Intercepts : H = 40 (N = 0), N = 60 (H = 0). Pente −2/3.</details>
<details class="q"><summary>Avec U = N·H et le budget précédent, trouvez l'optimum.</summary>Tangence : H/N = 2/3 ⟹ H = (2/3)N. Budget : 3·(2/3)N + 2N = 120 ⟹ 4N = 120 ⟹ N = 30, H = 20, U = 600. (Avec U = N·H, la moitié du revenu va à chaque bien.)</details>
<details class="q"><summary>Le revenu et tous les prix doublent. Que devient la droite de budget ?</summary>Rien : R/P<sub>H</sub>, R/P<sub>N</sub> et la pente sont inchangés. L'inflation proportionnelle est neutre.</details>
<details class="q"><summary>Quelles sont les courbes d'indifférence pour chaussures gauches et droites, et pourquoi ?</summary>En L (complémentaires parfaits, U = min(G, D)) : une chaussure gauche de plus sans la droite n'apporte rien.</details>'''))
    write("lessons/s3-consommateur.html", ("Consumer choice", "Le choix du consommateur"), b, extra=CS_JS)


# ---------------- page 4.1 costs

def page_s4_couts():
    b = []
    CF = 50
    CV = [0, 50, 78, 98, 112, 130, 150, 175, 204, 242, 300, 385]

    def cost_rows(lang):
        r = ""
        for q in range(0, 12):
            ct = CF + CV[q]
            cm = "—" if q == 0 else CV[q] - CV[q - 1]
            avg = ("—", "—", "—") if q == 0 else (num(CF / q, lang, 2), num(CV[q] / q, lang, 2), num(ct / q, lang, 2))
            hl = ' class="hl"' if q in (4, 7, 8) else ""
            r += f'<tr{hl}><td class="num">{q}</td><td class="num">{CF}</td><td class="num">{CV[q]}</td><td class="num">{ct}</td><td class="num">{cm}</td><td class="num">{avg[0]}</td><td class="num">{avg[1]}</td><td class="num">{avg[2]}</td></tr>'
        return r
    b.append(L(
        '''<p class="kicker">Session 4 · Part A</p><h1>Production costs</h1><p class="lead">Technology, factor combinations and cost curves — the building blocks of the theory of the firm.</p>
<h2>Market structures at a glance</h2>
<div class="grid">
<div class="card"><span class="tag">Perfect competition</span><h4>Price taker</h4><ul><li>Many buyers and sellers (atomicity)</li><li>Homogeneous good</li><li>Free entry and exit</li></ul><p>E.g. agricultural markets</p></div>
<div class="card"><span class="tag">Monopolistic competition</span><h4>Limited market power</h4><ul><li>Many sellers</li><li>Differentiated goods (close substitutes)</li><li>Few entry barriers</li></ul><p>E.g. hygiene/beauty, sporting goods</p></div>
<div class="card"><span class="tag">Oligopoly</span><h4>Strategic interdependence</h4><ul><li>Few sellers</li><li>Homogeneous or differentiated good</li><li>High entry barriers</li></ul><p>E.g. cars, aerospace, steel</p></div>
<div class="card"><span class="tag">Monopoly</span><h4>Price maker</h4><ul><li>A single seller</li><li>Insurmountable barriers</li></ul><p>E.g. water distribution, electricity distribution</p></div>
</div>
<h2><span class="badge">1</span>Technology and cost minimisation</h2>
<div class="callout"><strong>The question</strong>A cereal farmer wants to produce 800 t of milling wheat (≥ 11 % protein) on 100 ha. How many tractors, workers and how much fertiliser? Powerful machinery, or shared equipment and more labour? → the <b>optimal combination of factors of production</b>.</div>
<div class="flow"><span class="step">1 · Best combination of factors?</span><span class="arr">→</span><span class="step">2 · How do costs change with output?</span><span class="arr">→</span><span class="step key">3 · Which output maximises profit?</span></div>
<p>For a target output Q, the firm looks for the cheapest combination of <b>K</b> (capital), <b>L</b> (labour) and <b>MP</b> (raw materials). Total cost is a function of output: at each Q, the minimum spending needed.</p>
<div class="grid">
<div class="card"><span class="tag">K — physical capital</span><h4>Fixed in the short run</h4><p>Installations, equipment, capacity (tractors, combines, silos, sheds). Fixed in the short run, variable in the long run: in the short run K is a constraint.</p></div>
<div class="card"><span class="tag">L &amp; MP — variable factors</span><h4>Adjustable right away</h4><p>Labour and raw materials can change in the short run → variable costs. In the long run K, L and MP all vary → every cost is variable.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">1</span><h4>Capital-intensive</h4><p>New, powerful machinery; little labour. Key cost: capital (interest rates, fuel).</p></div>
<div class="card"><span class="tag">2</span><h4>Labour-intensive</h4><p>Old or shared machinery; more working hours. Key cost: wages.</p></div>
<div class="card"><span class="tag">3</span><h4>Input-intensive</h4><p>More nitrogen fertiliser and treatments to secure yield and quality. Key cost: nitrogen price.</p></div>
</div>
<p><b>Key point:</b> the <i>relative</i> price of factors (fuel, nitrogen, wages, interest rates) decides which combination is cheapest.</p>''',
        '''<p class="kicker">Séance 4 · Partie A</p><h1>Les coûts de production</h1><p class="lead">Technologie, combinaison des facteurs et courbes de coûts — les briques de la théorie de la firme.</p>
<h2>Panorama des structures de marché</h2>
<div class="grid">
<div class="card"><span class="tag">Concurrence parfaite</span><h4>Preneur de prix</h4><ul><li>Grand nombre d'acheteurs et de vendeurs (atomicité)</li><li>Bien homogène</li><li>Libre entrée et sortie</li></ul><p>Ex. : marchés agricoles</p></div>
<div class="card"><span class="tag">Concurrence monopolistique</span><h4>Pouvoir de marché limité</h4><ul><li>Grand nombre de vendeurs</li><li>Biens différenciés (substituts proches)</li><li>Peu de barrières à l'entrée</li></ul><p>Ex. : hygiène/beauté, articles de sport</p></div>
<div class="card"><span class="tag">Oligopole</span><h4>Interdépendance stratégique</h4><ul><li>Petit nombre de vendeurs</li><li>Bien homogène ou différencié</li><li>Barrières importantes à l'entrée</li></ul><p>Ex. : automobile, aéronautique, acier</p></div>
<div class="card"><span class="tag">Monopole</span><h4>Faiseur de prix</h4><ul><li>Un seul vendeur</li><li>Barrières insurmontables</li></ul><p>Ex. : distribution d'eau, distribution d'électricité</p></div>
</div>
<h2><span class="badge">1</span>Technologie et minimisation des coûts</h2>
<div class="callout"><strong>La question</strong>Un céréalier veut produire 800 t de blé meunier (≥ 11 % de protéines) sur 100 ha. Combien de tracteurs, de salariés, d'engrais ? Du matériel puissant, ou du matériel partagé et plus de main-d'œuvre ? → la <b>combinaison optimale des facteurs de production</b>.</div>
<div class="flow"><span class="step">1 · Meilleure combinaison de facteurs ?</span><span class="arr">→</span><span class="step">2 · Comment les coûts évoluent-ils avec la production ?</span><span class="arr">→</span><span class="step key">3 · Quelle production maximise le profit ?</span></div>
<p>Pour un niveau Q voulu, la firme cherche la combinaison la moins chère de <b>K</b> (capital), <b>L</b> (travail) et <b>MP</b> (matières premières). Le coût total est fonction de la production : à chaque Q, la dépense minimale nécessaire.</p>
<div class="grid">
<div class="card"><span class="tag">K — capital physique</span><h4>Fixe à court terme</h4><p>Installations, équipements, capacités (tracteurs, moissonneuses, silos, hangars). Fixe à CT, variable à LT : à CT, K est une contrainte.</p></div>
<div class="card"><span class="tag">L et MP — facteurs variables</span><h4>Ajustables dès le CT</h4><p>Main-d'œuvre et matières premières varient à CT → coûts variables. À LT, K, L et MP varient → tous les coûts sont variables.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">1</span><h4>Capital intensif</h4><p>Matériel neuf et puissant ; peu de main-d'œuvre. Coût clé : capital (taux d'intérêt, carburant).</p></div>
<div class="card"><span class="tag">2</span><h4>Travail intensif</h4><p>Matériel ancien ou partagé ; plus d'heures de travail. Coût clé : salaires.</p></div>
<div class="card"><span class="tag">3</span><h4>Intrants intensifs</h4><p>Plus d'engrais azoté et de traitements pour sécuriser rendement et qualité. Coût clé : prix de l'azote.</p></div>
</div>
<p><b>À retenir :</b> c'est le prix <i>relatif</i> des facteurs (carburant, azote, salaires, taux d'intérêt) qui détermine la combinaison la moins coûteuse.</p>'''))
    b.append(L(
        f'''<h2><span class="badge">2</span>Short-run cost functions</h2>
<p class="formula">TC = FC + VC · MC = ΔTC/ΔQ = ΔVC/ΔQ · ATC = TC/Q · AFC = FC/Q · AVC = VC/Q</p>
<div class="table-wrap"><table><thead><tr><th class="num">Q</th><th class="num">FC</th><th class="num">VC</th><th class="num">TC</th><th class="num">MC</th><th class="num">AFC</th><th class="num">AVC</th><th class="num">ATC</th></tr></thead><tbody>{cost_rows("en")}</tbody></table></div>
<p style="font-size:.85rem;color:var(--muted)">Highlighted: Q = 4 (minimum MC = 14) · Q = 7 (minimum AVC = 25, the shutdown point) · Q = 8 (minimum ATC = 31.75, the short-run optimal size).</p>
<figure>{svg_cost_curves("en")}<figcaption>★ = minimum ATC (31.75 at Q = 8), the short-run optimal size. AFC always falls (the fixed cost is spread over more units). AVC and ATC are U-shaped. <b>MC cuts AVC and ATC at their minimum</b> — an algebraic property: while the marginal unit costs less than the average, it pulls the average down; once it costs more, it pulls it up. MC is plotted between quantities (e.g. 14 between Q = 3 and 4).</figcaption></figure>
<h3>Why is total cost S-shaped? Marginal product of labour</h3>
<p><b>MPL = ΔQ/ΔL</b>: the extra output from one more worker. With K fixed, each extra worker has less equipment to use. <b>Law of diminishing marginal returns:</b> beyond a threshold, each extra worker adds less (same logic for fertiliser on fixed land). If labour is the only variable factor at wage w: <b>MC = w / MPL</b> — MPL ↑ ⇒ MC ↓; MC minimum ⇔ MPL maximum.</p>
<div class="grid">
<div class="card"><span class="tag">Phase 1 · MPL ↑ → MC ↓</span><h4>Specialisation</h4><p>Better organisation: each new worker adds more than the previous one. MC 50 (Q = 1) → 14 (Q = 4); TC concave.</p></div>
<div class="card"><span class="tag">Pivot · MPL max → MC min</span><h4>Q = 4</h4><p>MC = 14, the table's minimum: the inflection point of TC.</p></div>
<div class="card"><span class="tag">Phase 2 · MPL ↓ → MC ↑</span><h4>Saturation</h4><p>Fixed K saturated: congestion, overtime. MC 18 (Q = 5) → 85 (Q = 11); TC convex.</p></div>
</div>
<p>Economies of scale already in the short run: ATC falls (fixed costs spread + MPL ↑) up to Q = 8, then diseconomies (ATC ↑). Hence VC and TC in an S, and MC in a U.</p>
<div class="callout"><strong>Watch out</strong>Diminishing marginal returns (short run, K fixed) ≠ returns to scale (long run, all factors variable).</div>''',
        f'''<h2><span class="badge">2</span>Fonctions de coût à court terme</h2>
<p class="formula">CT = CF + CV · Cm = ΔCT/ΔQ = ΔCV/ΔQ · CTM = CT/Q · CFM = CF/Q · CVM = CV/Q</p>
<div class="table-wrap"><table><thead><tr><th class="num">Q</th><th class="num">CF</th><th class="num">CV</th><th class="num">CT</th><th class="num">Cm</th><th class="num">CFM</th><th class="num">CVM</th><th class="num">CTM</th></tr></thead><tbody>{cost_rows("fr")}</tbody></table></div>
<p style="font-size:.85rem;color:var(--muted)">Surlignés : Q = 4 (Cm minimum = 14) · Q = 7 (CVM minimum = 25, seuil de fermeture) · Q = 8 (CTM minimum = 31,75, taille optimale de CT).</p>
<figure>{svg_cost_curves("fr")}<figcaption>★ = minimum du CTM (31,75 en Q = 8), la taille optimale de CT. Le CFM décroît toujours (le coût fixe est étalé sur plus d'unités). CVM et CTM sont en U. <b>Le Cm coupe CVM et CTM à leur minimum</b> — propriété algébrique : tant que l'unité marginale coûte moins que la moyenne, elle la tire vers le bas ; dès qu'elle coûte plus, elle la tire vers le haut. Le Cm est tracé entre deux quantités (ex. 14 entre Q = 3 et 4).</figcaption></figure>
<h3>Pourquoi le coût total est-il en S ? La productivité marginale du travail</h3>
<p><b>PmL = ΔQ/ΔL</b> : la production supplémentaire d'un travailleur en plus. À K fixe, chaque travailleur supplémentaire dispose de moins d'équipement. <b>Loi des rendements marginaux décroissants :</b> passé un seuil, chaque travailleur de plus rapporte moins (même logique pour l'engrais sur une surface fixe). Si L est le seul facteur variable et w constant : <b>Cm = w / PmL</b> — PmL ↑ ⇒ Cm ↓ ; Cm minimum ⇔ PmL maximale.</p>
<div class="grid">
<div class="card"><span class="tag">Phase 1 · PmL ↑ → Cm ↓</span><h4>Spécialisation</h4><p>Meilleure organisation : chaque nouveau travailleur rapporte plus que le précédent. Cm 50 (Q = 1) → 14 (Q = 4) ; CT concave.</p></div>
<div class="card"><span class="tag">Pivot · PmL max → Cm min</span><h4>Q = 4</h4><p>Cm = 14, minimum du tableau : point d'inflexion de la courbe de CT.</p></div>
<div class="card"><span class="tag">Phase 2 · PmL ↓ → Cm ↑</span><h4>Saturation</h4><p>K fixe saturé : congestion, heures supplémentaires. Cm 18 (Q = 5) → 85 (Q = 11) ; CT convexe.</p></div>
</div>
<p>Économies d'échelle dès le CT : le CTM baisse (CF étalés + PmL ↑) jusqu'à Q = 8, puis déséconomies (CTM ↑). D'où le CV et le CT en S, et le Cm en U.</p>
<div class="callout"><strong>Point d'attention</strong>Rendements marginaux décroissants (court terme, K fixe) ≠ rendements d'échelle (long terme, tous facteurs variables).</div>'''))
    b.append(L(
        f'''<h2><span class="badge">3</span>Application: a t-shirt workshop</h2>
<p>100 printed t-shirts a day, four possible techniques. Prices: machine (K) €100/day (daily leasing → variable cost), worker (L) €60/day, premises €200/day (the only fixed cost).</p>
<div class="table-wrap"><table><thead><tr><th>Technique</th><th class="num">K</th><th class="num">L</th><th class="num">Cost K + L</th><th class="num">Per t-shirt</th><th class="num">If K = €50</th></tr></thead><tbody>
<tr><td>A — manual handling</td><td class="num">1</td><td class="num">6</td><td class="num">€460</td><td class="num">€4.60</td><td class="num">€410</td></tr>
<tr class="hl"><td>B — balanced ★</td><td class="num">2</td><td class="num">3</td><td class="num">€380</td><td class="num">€3.80</td><td class="num">€280</td></tr>
<tr><td>C — mostly automated</td><td class="num">3</td><td class="num">2</td><td class="num">€420</td><td class="num">€4.20</td><td class="num">€270 ★</td></tr>
<tr><td>D — highly automated</td><td class="num">6</td><td class="num">1</td><td class="num">€660</td><td class="num">€6.60</td><td class="num">€360</td></tr></tbody></table></div>
<figure>{svg_isoquant("en")}<figcaption><b>Isoquant:</b> all (K, L) combinations producing the same output (100 t-shirts). <b>Isocost:</b> all combinations costing the same amount, 100K + 60L = C. Lower the budget until the last point of contact: <b>B</b> (€380 + €200 rent = €580), €280 cheaper than D. If machine leasing falls to €50/day, the optimum moves to <b>C</b>: capital replaces labour — no new technology, only relative prices changed.</figcaption></figure>
<div class="callout"><strong>Key point</strong>All four techniques are technically efficient: technology alone cannot choose, prices are needed. No combination is “good” in itself — the optimum comes from a technology meeting a price system. And since the workshop is in perfect competition (hundreds of identical workshops, a standardised t-shirt, rented machines and premises so free entry and exit), it is a <b>price taker</b>: its only lever is minimising cost.</div>
<h2><span class="badge">4</span>Short run vs long run</h2>
<div class="grid">
<div class="card"><span class="tag">Short run</span><h4>Some factors fixed</h4><p>K is fixed; only L and MP vary; the firm cannot change size. Fixed costs exist and cannot be recovered. TC is S-shaped.</p></div>
<div class="card"><span class="tag">Long run</span><h4>All factors vary</h4><p>The firm can change its size; no cost is fixed. The long-run average cost curve is the <b>envelope</b> of the short-run ones. Only horizon where we speak of returns to scale.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">Technical notion · long run</span><h4>Returns to scale</h4><p>How <b>output</b> responds when all factors increase in the same proportion. Measures the efficiency of the technology.</p></div>
<div class="card"><span class="tag">Cost notion · short and long run</span><h4>Economies of scale</h4><p>How <b>unit cost</b> (ATC) responds to output; also depends on factor prices. ATC falls with Q ⇒ economies of scale; ATC rises ⇒ diseconomies.</p></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Returns to scale</th><th>Definition</th><th>Why</th><th>Usual effect on ATC</th></tr></thead><tbody>
<tr><td><b>Increasing</b></td><td>F(bK, bL) &gt; b·F(K, L)</td><td>Specialisation, indivisible factors. (1 tractor, 3 workers) → (2 tractors, 6 workers) more than doubles output: specialised teams (harvest, shuttle, silo), shared trailer and mechanic.</td><td>ATC ↓ (economies of scale)</td></tr>
<tr><td><b>Constant</b></td><td>F(bK, bL) = b·F(K, L)</td><td>Rare; very standardised processes.</td><td>ATC stable</td></tr>
<tr><td><b>Decreasing</b></td><td>F(bK, bL) &lt; b·F(K, L)</td><td>Congestion, managerial complexity, resource scarcity, HR problems.</td><td>ATC ↑ (diseconomies)</td></tr></tbody></table></div>
<div class="callout"><strong>Two exceptions</strong>① Increasing returns but ATC ↑: factor prices or organisation costs (management, bureaucracy) grow faster than productivity — rare but possible. ② Constant returns but ATC ↓: economies of scale without technical gains, from spreading volume-independent costs (R&amp;D, marketing, head office), purchasing discounts, better access to finance.</div>
<h2>Check yourself</h2>
<details class="q"><summary>FC = 100 and VC = 300 at Q = 20. Compute TC, AFC, AVC and ATC.</summary>TC = 400; AFC = 5; AVC = 15; ATC = 20.</details>
<details class="q"><summary>Why does MC cut ATC at its minimum?</summary>If the marginal unit costs less than the average, it lowers the average; if it costs more, it raises it. So the average stops falling exactly where MC = ATC.</details>
<details class="q"><summary>Wage = €120/day, MPL = 40 units. What is MC?</summary>MC = w / MPL = 120 / 40 = €3 per unit.</details>
<details class="q"><summary>In the t-shirt workshop, wages rise to €100/day (K still €100). Which technique is cheapest?</summary>A: 100 + 600 = 700; B: 200 + 300 = 500; C: 300 + 200 = 500; D: 600 + 100 = 700. B and C tie at €500 — the optimum moves towards more capital.</details>
<details class="q"><summary>Diminishing marginal returns vs decreasing returns to scale?</summary>Diminishing marginal returns: short run, one factor varies with K fixed. Decreasing returns to scale: long run, all factors increase in the same proportion and output rises less than proportionally.</details>''',
        f'''<h2><span class="badge">3</span>Application : un atelier de t-shirts</h2>
<p>100 t-shirts imprimés par jour, quatre techniques possibles. Prix : machine (K) 100 €/jour (leasing journalier → coût variable), ouvrier (L) 60 €/jour, local 200 €/jour (seul coût fixe).</p>
<div class="table-wrap"><table><thead><tr><th>Technique</th><th class="num">K</th><th class="num">L</th><th class="num">Coût K + L</th><th class="num">Par t-shirt</th><th class="num">Si K = 50 €</th></tr></thead><tbody>
<tr><td>A — manutention manuelle</td><td class="num">1</td><td class="num">6</td><td class="num">460 €</td><td class="num">4,60 €</td><td class="num">410 €</td></tr>
<tr class="hl"><td>B — organisation équilibrée ★</td><td class="num">2</td><td class="num">3</td><td class="num">380 €</td><td class="num">3,80 €</td><td class="num">280 €</td></tr>
<tr><td>C — plutôt automatisée</td><td class="num">3</td><td class="num">2</td><td class="num">420 €</td><td class="num">4,20 €</td><td class="num">270 € ★</td></tr>
<tr><td>D — très automatisée</td><td class="num">6</td><td class="num">1</td><td class="num">660 €</td><td class="num">6,60 €</td><td class="num">360 €</td></tr></tbody></table></div>
<figure>{svg_isoquant("fr")}<figcaption><b>Isoquante :</b> toutes les combinaisons (K, L) produisant la même quantité (100 t-shirts). <b>Isocoût :</b> toutes les combinaisons de même coût, 100K + 60L = C. On baisse le budget jusqu'au dernier contact : <b>B</b> (380 € + 200 € de loyer = 580 €), 280 € de moins que D. Si le leasing tombe à 50 €/jour, l'optimum passe en <b>C</b> : on substitue du capital au travail — aucune technologie nouvelle, seul le prix relatif a changé.</figcaption></figure>
<div class="callout"><strong>À retenir</strong>Les quatre techniques sont techniquement efficaces : la technologie seule ne permet pas de choisir, il faut les prix. Aucune combinaison n'est « bonne » en soi — l'optimum naît de la rencontre entre une technologie et un système de prix. Et comme l'atelier est en concurrence parfaite (des centaines d'ateliers identiques, t-shirt standardisé, machines et local loués donc libre entrée et sortie), il est <b>preneur de prix</b> : son seul levier est la minimisation du coût.</div>
<h2><span class="badge">4</span>Court terme vs long terme</h2>
<div class="grid">
<div class="card"><span class="tag">Court terme</span><h4>Certains facteurs fixes</h4><p>K est fixe ; seuls L et MP varient ; la firme ne peut pas changer de taille. Les CF existent et sont non récupérables. CT en S.</p></div>
<div class="card"><span class="tag">Long terme</span><h4>Tous les facteurs varient</h4><p>La firme peut changer de taille ; aucun coût n'est fixe. La courbe de coût moyen de LT est l'<b>enveloppe</b> des courbes de CT. Seul horizon où l'on parle de rendements d'échelle.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">Notion technique · long terme</span><h4>Rendements d'échelle</h4><p>Sensibilité de la <b>production</b> à une variation équiproportionnelle de tous les facteurs. Mesure l'efficacité de la technologie.</p></div>
<div class="card"><span class="tag">Notion de coût · CT et LT</span><h4>Économies d'échelle</h4><p>Sensibilité du <b>coût unitaire</b> (CTM) au niveau de production ; dépend aussi du prix des facteurs. CTM ↓ avec Q ⇒ économies d'échelle ; CTM ↑ ⇒ déséconomies.</p></div>
</div>
<div class="table-wrap"><table><thead><tr><th>Rendements d'échelle</th><th>Définition</th><th>Pourquoi</th><th>Effet habituel sur le CTM</th></tr></thead><tbody>
<tr><td><b>Croissants</b></td><td>F(bK, bL) &gt; b·F(K, L)</td><td>Spécialisation, facteurs indivisibles. (1 tracteur, 3 ouvriers) → (2 tracteurs, 6 ouvriers) : production plus que doublée — équipes spécialisées (récolte, navette, silo), benne et mécanicien partagés.</td><td>CTM ↓ (économies d'échelle)</td></tr>
<tr><td><b>Constants</b></td><td>F(bK, bL) = b·F(K, L)</td><td>Rare ; processus très standardisés.</td><td>CTM stable</td></tr>
<tr><td><b>Décroissants</b></td><td>F(bK, bL) &lt; b·F(K, L)</td><td>Congestion, complexité managériale, pénurie de ressources, problèmes RH.</td><td>CTM ↑ (déséconomies)</td></tr></tbody></table></div>
<div class="callout"><strong>Deux exceptions</strong>① RE croissants mais CTM ↑ : prix des facteurs ou coûts d'organisation (management, bureaucratie) qui croissent plus vite que la productivité — rare mais possible. ② RE constants mais CTM ↓ : économies d'échelle sans gain technique, grâce à l'étalement de coûts indépendants du volume (R&amp;D, marketing, siège), aux remises sur achats, à un meilleur accès au financement.</div>
<h2>Testez-vous</h2>
<details class="q"><summary>CF = 100 et CV = 300 pour Q = 20. Calculez CT, CFM, CVM et CTM.</summary>CT = 400 ; CFM = 5 ; CVM = 15 ; CTM = 20.</details>
<details class="q"><summary>Pourquoi le Cm coupe-t-il le CTM à son minimum ?</summary>Si l'unité marginale coûte moins que la moyenne, elle fait baisser la moyenne ; si elle coûte plus, elle la fait monter. La moyenne cesse donc de baisser exactement là où Cm = CTM.</details>
<details class="q"><summary>Salaire = 120 €/jour, PmL = 40 unités. Quel est le Cm ?</summary>Cm = w / PmL = 120 / 40 = 3 € par unité.</details>
<details class="q"><summary>Dans l'atelier de t-shirts, les salaires passent à 100 €/jour (K toujours à 100 €). Quelle technique est la moins chère ?</summary>A : 100 + 600 = 700 ; B : 200 + 300 = 500 ; C : 300 + 200 = 500 ; D : 600 + 100 = 700. B et C à égalité à 500 € — l'optimum glisse vers plus de capital.</details>
<details class="q"><summary>Rendements marginaux décroissants vs rendements d'échelle décroissants ?</summary>Rendements marginaux décroissants : court terme, un facteur varie avec K fixe. Rendements d'échelle décroissants : long terme, tous les facteurs augmentent dans la même proportion et la production augmente moins que proportionnellement.</details>'''))
    write("lessons/s4-couts.html", ("Production costs", "Les coûts de production"), b)


# ---------------- page 4.2 perfect competition

def page_s4_cp():
    b = []
    b.append(L(
        '''<p class="kicker">Session 4 · Part B</p><h1>The firm in perfect competition</h1><p class="lead">Profit maximisation (MR = MC = p), the short-run supply curve, and long-run industry equilibrium.</p>
<h2><span class="badge">1</span>The optimality condition: MR = MC = p</h2>
<div class="grid">
<div class="card"><h4>The firm is a price taker</h4><p>Total revenue TR(Q) = p × Q, so marginal revenue MR = dTR/dQ = (dp/dQ)·Q + p = 0·Q + p = <b>p</b>.</p></div>
<div class="card"><h4>Maximise profit</h4><p>dπ/dQ = MR − MC = 0 ⟹ <b>p = MC</b>. The firm produces up to the quantity q* where the cost of the last unit equals the market price.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">Result 1</span><h4>p = MC</h4><p>The optimality condition.</p></div>
<div class="card"><span class="tag">Result 2</span><h4>Supply curve</h4><p>The rising part of MC above minimum AVC (the shutdown point).</p></div>
<div class="card"><span class="tag">Result 3</span><h4>Profit &gt; 0 if p &gt; min ATC</h4><p>The long-run viability condition.</p></div>
</div>''',
        '''<p class="kicker">Séance 4 · Partie B</p><h1>La firme en concurrence parfaite</h1><p class="lead">Maximisation du profit (Rm = Cm = p), courbe d'offre de court terme et équilibre d'industrie à long terme.</p>
<h2><span class="badge">1</span>La condition d'optimalité : Rm = Cm = p</h2>
<div class="grid">
<div class="card"><h4>La firme est preneuse de prix</h4><p>Recette totale RT(Q) = p × Q, donc recette marginale Rm = dRT/dQ = (dp/dQ)·Q + p = 0·Q + p = <b>p</b>.</p></div>
<div class="card"><h4>Maximiser le profit</h4><p>dπ/dQ = Rm − Cm = 0 ⟹ <b>p = Cm</b>. La firme produit jusqu'à la quantité q* où le coût de la dernière unité égale le prix de marché.</p></div>
</div>
<div class="grid">
<div class="card"><span class="tag">Résultat 1</span><h4>p = Cm</h4><p>La condition d'optimalité.</p></div>
<div class="card"><span class="tag">Résultat 2</span><h4>Courbe d'offre</h4><p>La partie croissante du Cm au-dessus du minimum du CVM (le seuil de fermeture).</p></div>
<div class="card"><span class="tag">Résultat 3</span><h4>Profit &gt; 0 si p &gt; min CTM</h4><p>La condition de viabilité de long terme.</p></div>
</div>'''))
    b.append(PF_WIDGET)
    b.append(L(
        '''<p style="font-size:.85rem;color:var(--muted)">The slider uses the cost table from <a href="s4-couts.html">4.1</a> (whole units). The shaded rectangle is profit (green) or loss (orange) = (p − ATC) × Q*. At p = 50 the table gives Q* = 9 and a profit of 158; with smooth curves the course finds Q* ≈ 9.4.</p>
<h2><span class="badge">2</span>The short-run decision with fixed costs</h2>
<div class="table-wrap"><table><thead><tr><th>Price</th><th>Situation</th><th>Why</th><th>Decision</th></tr></thead><tbody>
<tr><td><b>p &gt; min ATC</b> (31.75)</td><td>Profit &gt; 0</td><td>TR = p × Q* &gt; TC = ATC × Q*; profit = (p − ATC) × Q*</td><td class="ok">Produce ✓</td></tr>
<tr><td><b>min AVC &lt; p &lt; min ATC</b> (25 – 31.75)</td><td>Loss, but smaller than shutting down</td><td>Producing: loss = FC − (p − AVC) × Q*. Not producing: loss = FC. The surplus (p − AVC) × Q* &gt; 0 covers part of the fixed cost.</td><td class="ok">Produce anyway ✓</td></tr>
<tr><td><b>p &lt; min AVC</b> (25)</td><td>Loss &gt; FC</td><td>The price does not even cover variable costs: producing makes the loss worse.</td><td class="no">Shut down ✗ (loss = FC)</td></tr></tbody></table></div>
<div class="callout"><strong>Intuition</strong>In the short run fixed costs (rent, machines) exist and cannot be recovered: shutting down still costs FC. So the firm keeps producing as long as revenue covers at least its variable costs.</div>
<div class="grid">
<div class="card"><h4>Producer surplus</h4><p>PS = Σ (p − MC) over the units produced = TR − VC: unit margins net of <i>variable</i> costs only.</p></div>
<div class="card"><h4>Profit</h4><p>π = TR − TC = (p − ATC) × Q*: ATC includes the average fixed cost.</p></div>
</div>
<p><b>Profit = surplus − FC:</b> the surplus must first pay the fixed costs; what remains is profit. The two coincide in the long run, when no cost is fixed.</p>''',
        '''<p style="font-size:.85rem;color:var(--muted)">Le curseur utilise le tableau de coûts de <a href="s4-couts.html">4.1</a> (unités entières). Le rectangle grisé est le profit (vert) ou la perte (orange) = (p − CTM) × Q*. À p = 50, le tableau donne Q* = 9 et un profit de 158 ; avec des courbes continues, le cours trouve Q* ≈ 9,4.</p>
<h2><span class="badge">2</span>La décision de court terme avec des coûts fixes</h2>
<div class="table-wrap"><table><thead><tr><th>Prix</th><th>Situation</th><th>Pourquoi</th><th>Décision</th></tr></thead><tbody>
<tr><td><b>p &gt; min CTM</b> (31,75)</td><td>Profit &gt; 0</td><td>RT = p × Q* &gt; CT = CTM × Q* ; profit = (p − CTM) × Q*</td><td class="ok">Produire ✓</td></tr>
<tr><td><b>min CVM &lt; p &lt; min CTM</b> (25 – 31,75)</td><td>Perte, mais inférieure à la fermeture</td><td>En produisant : perte = CF − (p − CVM) × Q*. Sans produire : perte = CF. Le surplus (p − CVM) × Q* &gt; 0 couvre une partie des CF.</td><td class="ok">Produire quand même ✓</td></tr>
<tr><td><b>p &lt; min CVM</b> (25)</td><td>Perte &gt; CF</td><td>Le prix ne couvre même pas les coûts variables : produire aggrave la perte.</td><td class="no">Fermer ✗ (perte = CF)</td></tr></tbody></table></div>
<div class="callout"><strong>Intuition</strong>À court terme, les coûts fixes (loyer, machines) existent et sont irrécupérables : fermer coûte quand même CF. La firme continue donc à produire tant que ses recettes couvrent au moins ses coûts variables.</div>
<div class="grid">
<div class="card"><h4>Surplus du producteur</h4><p>SP = Σ (p − Cm) sur les unités produites = RT − CV : marges unitaires nettes des seuls coûts <i>variables</i>.</p></div>
<div class="card"><h4>Profit</h4><p>π = RT − CT = (p − CTM) × Q* : le CTM inclut le coût fixe moyen.</p></div>
</div>
<p><b>Profit = surplus − CF :</b> le surplus doit d'abord payer les coûts fixes ; ce qui reste est le profit. Les deux coïncident à long terme, quand plus aucun coût n'est fixe.</p>'''))
    b.append(L(
        f'''<h2><span class="badge">3</span>Industry equilibrium</h2>
<div class="callout"><strong>Key result</strong>In the long run, under perfect competition, the market price converges to <b>minimum average total cost</b>: p = min ATC → economic profit = 0, maximum allocative efficiency, free entry and exit.</div>
<p><b>Industry supply:</b> with free access to technology, all firms in a sector share the same production function, so industry supply = the sum of individual supplies = <b>n × individual supply</b> (same curves, horizontal axis × n). Every firm is a price taker; the price is set where aggregate supply meets demand.</p>
<h3>Example: the fodder-beet market</h3>
<figure>{svg_industry("en")}<figcaption><b>A:</b> initial equilibrium, p₁ = min ATC = 31.75, zero economic profit. <b>Demand shock</b> D₁ → D₂: in the short run the price jumps to p₂ = 50 (<b>B</b>); existing firms produce more and earn a profit = (p₂ − ATC) × q₂. <b>Long run:</b> profits attract new entrants (other farmers switch crops), supply shifts right (S₁ → S₃) and the price falls back to min ATC (<b>C</b>): p* = p₁ but Q₃ &gt; Q₁, with more firms.</figcaption></figure>
<div class="flow"><span class="step">1 · Short run: demand shock → p ↑, profits ↑</span><span class="arr">→</span><span class="step">2 · Entry of new firms → supply ↑</span><span class="arr">→</span><span class="step key">3 · Long run: p = min ATC, economic profit = 0</span></div>
<p><b>Long-run supply is perfectly elastic</b> at p* = min ATC because of free entry and exit: p &gt; min ATC → entry → supply ↑ → p ↓; p &lt; min ATC → exit → supply ↓ → p ↑.</p>
<div class="grid">
<div class="card"><h4>Economic ≠ accounting profit</h4><p>Economic profit = accounting profit − opportunity costs (e.g. the return the owner's capital and time could earn elsewhere). Zero economic profit is not poor performance: the firm earns a normal return, as good as the best alternative investment.</p></div>
<div class="card"><h4>A theoretical target</h4><p>Economic life is a series of shocks (costs, demand, technology). Each one creates temporary profits or losses, which trigger entry and exit. The market heads towards equilibrium without ever settling there.</p></div>
<div class="card"><h4>Identical firms?</h4><p>Zero profit for all assumes identical costs. If firms differ (cheaper inputs, better location), only the <b>marginal firm</b> earns zero; infra-marginal firms keep a <b>Ricardian rent</b>.</p></div>
</div>
<div class="callout"><strong>Welfare</strong>W = consumer surplus + producer surplus (value to buyers − cost of production). With identical firms, PS = 0 in the long run; with heterogeneous costs PS &gt; 0. Both outcomes are efficient (p = MC, no deadweight loss), and at the same p* welfare is higher with heterogeneous firms: the same units are produced with fewer resources. Monopoly, taxes or quotas create a deadweight loss.</div>''',
        f'''<h2><span class="badge">3</span>L'équilibre d'industrie</h2>
<div class="callout"><strong>Résultat clé</strong>À long terme, en concurrence parfaite, le prix de marché converge vers le <b>minimum du coût moyen total</b> : p = min CTM → profit économique = 0, efficacité allocative maximale, libre entrée et sortie.</div>
<p><b>Offre d'industrie :</b> avec libre accès aux technologies, toutes les firmes d'un secteur ont la même fonction de production ; l'offre agrégée = somme des offres individuelles = <b>n × offre individuelle</b> (mêmes courbes, axe horizontal × n). Toutes les firmes sont preneuses de prix ; le prix se fixe à l'intersection de l'offre agrégée et de la demande.</p>
<h3>Exemple : le marché de la betterave fourragère</h3>
<figure>{svg_industry("fr")}<figcaption><b>A :</b> équilibre initial, p₁ = min CTM = 31,75, profit économique nul. <b>Choc de demande</b> D₁ → D₂ : à court terme le prix monte à p₂ = 50 (<b>B</b>) ; les firmes existantes produisent plus et réalisent un profit = (p₂ − CTM) × q₂. <b>Long terme :</b> les profits attirent de nouveaux entrants (d'autres agriculteurs reconvertissent leur culture), l'offre se déplace vers la droite (O₁ → O₃) et le prix revient à min CTM (<b>C</b>) : p* = p₁ mais Q₃ &gt; Q₁, avec plus de firmes.</figcaption></figure>
<div class="flow"><span class="step">1 · CT : choc de demande → p ↑, profits ↑</span><span class="arr">→</span><span class="step">2 · Entrée de nouvelles firmes → offre ↑</span><span class="arr">→</span><span class="step key">3 · LT : p = min CTM, profit éco = 0</span></div>
<p><b>L'offre de long terme est parfaitement élastique</b> au prix p* = min CTM grâce à la libre entrée et sortie : p &gt; min CTM → entrée → offre ↑ → p ↓ ; p &lt; min CTM → sortie → offre ↓ → p ↑.</p>
<div class="grid">
<div class="card"><h4>Profit économique ≠ profit comptable</h4><p>Profit économique = profit comptable − coûts d'opportunité (ex. ce que le capital et le temps du propriétaire rapporteraient ailleurs). Un profit économique nul n'est pas une mauvaise performance : la firme obtient un rendement normal, aussi bon que le meilleur placement alternatif.</p></div>
<div class="card"><h4>Une cible théorique</h4><p>La vie économique est une succession de chocs (coûts, demande, technologie). Chacun recrée des profits ou des pertes temporaires, qui déclenchent entrées et sorties. Le marché converge vers l'équilibre sans jamais s'y fixer.</p></div>
<div class="card"><h4>Des firmes identiques ?</h4><p>Un profit nul pour toutes suppose des coûts identiques. Si les firmes diffèrent (facteurs moins chers, meilleur site), seule la <b>firme marginale</b> a un profit nul ; les firmes infra-marginales conservent une <b>rente ricardienne</b>.</p></div>
</div>
<div class="callout"><strong>Bien-être</strong>W = surplus du consommateur + surplus du producteur (valeur pour les acheteurs − coût de production). Avec des firmes identiques, SP = 0 à LT ; avec des coûts hétérogènes, SP &gt; 0. Les deux situations sont efficaces (p = Cm, pas de perte sèche), et à p* égal le bien-être est plus élevé avec des firmes hétérogènes : les mêmes unités sont produites avec moins de ressources. Monopole, taxe ou quota créent une perte sèche.</div>'''))
    b.append(L(
        f'''<h2><span class="badge">4</span>Real-world application: the electricity spot market</h2>
<p>On wholesale electricity markets, power plants are called in order of increasing marginal cost — the <b>merit order</b>. The spot price is set by the marginal cost of the last unit called (the marginal producer).</p>
<figure>{svg_merit("en")}<figcaption>Marginal costs: renewables ~€0/MWh (no fuel) · nuclear (Doel 4, Tihange 3) ~€12 (uranium + O&amp;M) · biomass &amp; waste ~€60 · CCGT gas ~€103 (gas + CO₂) · peakers (OCGT) ~€180 (gas + CO₂, low efficiency). Capacity widths are illustrative.</figcaption></figure>
<div class="grid">
<div class="card"><h4>The merit-order effect</h4><p>Renewables have MC ≈ 0. Adding them shifts supply to the right, pushing the most expensive plants out and lowering the spot price.</p></div>
<div class="card"><h4>Belpex — July 2026</h4><p>Belpex / EPEX SPOT Belgium, coupled with neighbouring markets (day-ahead prices). Monthly average July 2026: <b>€105.64/MWh</b>. CCGT MC ≈ 40/0.55 + 0.37 × 81 ≈ €103/MWh (TTF gas ≈ €40/MWh, CO₂ ≈ €81/t) → <b>gas CCGT is still the marginal producer in Belgium</b>.</p></div>
</div>
<h2>Exercise — your turn</h2>
<p>A firm produces up to 100 units a day. The first 80 units are made in normal working time; units 81–100 need overtime. Raw materials: €8/unit. Wages: €30/unit (normal time), €50/unit (overtime).</p>
<ol><li>Find AVC and MC at Q = 80 and Q = 100.</li><li>For p = €35, €50 and €80: what is the optimal quantity Q*, and the variable profit?</li></ol>
<details class="q"><summary>Show the solution</summary>
<p><b>Costs.</b> Units 1–80: MC = 8 + 30 = €38. Units 81–100: MC = 8 + 50 = €58.<br>At Q = 80: AVC = €38, MC = €38. At Q = 100: VC = 80 × 38 + 20 × 58 = 4,200 → AVC = €42, MC = €58.</p>
<p><b>Decisions</b> (min AVC = 38):</p>
<ul><li><b>p = 35</b> &lt; min AVC → Q* = 0 (shut down); variable profit 0, the loss is the fixed cost.</li><li><b>p = 50</b>: 38 &lt; 50 &lt; 58 → Q* = 80; variable profit = (50 − 38) × 80 = <b>€960</b>.</li><li><b>p = 80</b> &gt; 58 → Q* = 100; variable profit = 8,000 − 4,200 = <b>€3,800</b>.</li></ul></details>
<h2>Check yourself</h2>
<details class="q"><summary>Why is marginal revenue equal to the price for a competitive firm?</summary>The firm is a price taker: selling one more unit does not change the price, so each extra unit brings in exactly p.</details>
<details class="q"><summary>With the course cost table, p = 28. Produce or shut down?</summary>Produce (Q* = 7): 28 is above min AVC (25) but below min ATC (31.75). The loss is 29, less than the 50 lost by shutting down.</details>
<details class="q"><summary>Why does economic profit fall to zero in the long run?</summary>Positive profits attract entrants; supply rises and the price falls until p = min ATC. Losses cause exit and the reverse.</details>
<details class="q"><summary>What sets the electricity spot price?</summary>The marginal cost of the last (most expensive) plant needed to meet demand — in Belgium, usually a gas CCGT.</details>''',
        f'''<h2><span class="badge">4</span>Application réelle : le marché spot de l'électricité</h2>
<p>Sur les marchés de gros de l'électricité, les centrales sont appelées par ordre de coût marginal croissant — le <b>merit order</b>. Le prix spot est fixé par le coût marginal de la dernière unité appelée (le producteur marginal).</p>
<figure>{svg_merit("fr")}<figcaption>Coûts marginaux : renouvelables ~0 €/MWh (pas de combustible) · nucléaire (Doel 4, Tihange 3) ~12 € (uranium + O&amp;M) · biomasse et déchets ~60 € · CCGT gaz ~103 € (gaz + CO₂) · pointe (OCGT) ~180 € (gaz + CO₂, faible rendement). Les capacités sont illustratives.</figcaption></figure>
<div class="grid">
<div class="card"><h4>L'effet merit order</h4><p>Les ENR ont un Cm ≈ 0. Leur arrivée déplace l'offre vers la droite, évince les producteurs les plus chers et fait baisser le prix spot.</p></div>
<div class="card"><h4>Belpex — juillet 2026</h4><p>Belpex / EPEX SPOT Belgium, couplée aux marchés voisins (prix day-ahead). Moyenne mensuelle juillet 2026 : <b>105,64 €/MWh</b>. Cm du CCGT ≈ 40/0,55 + 0,37 × 81 ≈ 103 €/MWh (gaz TTF ≈ 40 €/MWh, CO₂ ≈ 81 €/t) → <b>le CCGT reste le producteur marginal en Belgique</b>.</p></div>
</div>
<h2>Exercice — à vous de jouer</h2>
<p>Une entreprise produit jusqu'à 100 unités par jour. Les 80 premières sont produites en temps normal ; les unités 81 à 100 exigent des heures supplémentaires. Matières premières : 8 €/unité. Salaires : 30 €/unité (temps normal), 50 €/unité (heures sup.).</p>
<ol><li>Identifiez le CVM et le Cm à Q = 80 et Q = 100.</li><li>Pour p = 35, 50 et 80 € : quelle est la quantité optimale Q* et le profit variable ?</li></ol>
<details class="q"><summary>Voir la solution</summary>
<p><b>Coûts.</b> Unités 1–80 : Cm = 8 + 30 = 38 €. Unités 81–100 : Cm = 8 + 50 = 58 €.<br>À Q = 80 : CVM = 38 €, Cm = 38 €. À Q = 100 : CV = 80 × 38 + 20 × 58 = 4 200 → CVM = 42 €, Cm = 58 €.</p>
<p><b>Décisions</b> (min CVM = 38) :</p>
<ul><li><b>p = 35</b> &lt; min CVM → Q* = 0 (fermer) ; profit variable 0, la perte est le coût fixe.</li><li><b>p = 50</b> : 38 &lt; 50 &lt; 58 → Q* = 80 ; profit variable = (50 − 38) × 80 = <b>960 €</b>.</li><li><b>p = 80</b> &gt; 58 → Q* = 100 ; profit variable = 8 000 − 4 200 = <b>3 800 €</b>.</li></ul></details>
<h2>Testez-vous</h2>
<details class="q"><summary>Pourquoi la recette marginale est-elle égale au prix pour une firme concurrentielle ?</summary>La firme est preneuse de prix : vendre une unité de plus ne change pas le prix, chaque unité supplémentaire rapporte donc exactement p.</details>
<details class="q"><summary>Avec le tableau de coûts du cours, p = 28. Produire ou fermer ?</summary>Produire (Q* = 7) : 28 est au-dessus du min CVM (25) mais sous le min CTM (31,75). La perte est de 29, moins que les 50 perdus en fermant.</details>
<details class="q"><summary>Pourquoi le profit économique tend-il vers zéro à long terme ?</summary>Les profits positifs attirent des entrants ; l'offre augmente et le prix baisse jusqu'à p = min CTM. Les pertes provoquent des sorties et l'inverse.</details>
<details class="q"><summary>Qu'est-ce qui fixe le prix spot de l'électricité ?</summary>Le coût marginal de la dernière centrale (la plus chère) nécessaire pour satisfaire la demande — en Belgique, généralement un CCGT au gaz.</details>'''))
    write("lessons/s4-concurrence-parfaite.html", ("The firm in perfect competition", "La firme en concurrence parfaite"), b, extra=PF_JS)



os.makedirs(os.path.join(SITE, "lessons"), exist_ok=True)
page_home()
page_syllabus()
page_pensee()
page_principes()
page_echange()
page_s2_od()
page_s2_elasticite()
page_s3()
page_s4_couts()
page_s4_cp()
page_upcoming("monopole.html", "Monopoly", "Monopole",
              ["Sources of monopoly power", "MR = MC and the monopoly price", "Deadweight loss", "Price discrimination and regulation"],
              ["Sources du pouvoir de monopole", "Rm = Cm et le prix de monopole", "Perte sèche", "Discrimination par les prix et régulation"])
page_upcoming("oligopole-jeux.html", "Oligopoly &amp; game theory", "Oligopole et théorie des jeux",
              ["Oligopoly: few firms, strategic interaction", "Payoff matrices and dominant strategies", "Nash equilibrium", "Prisoner's dilemma, collusion and cartels"],
              ["Oligopole : peu d'entreprises, interaction stratégique", "Matrices de gains et stratégies dominantes", "Équilibre de Nash", "Dilemme du prisonnier, collusion et cartels"])
print("ok")
