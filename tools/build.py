"""Generates the bilingual study pages. Run: python3 -I build.py <site_dir>"""
import os, sys, math

SITE = sys.argv[1]
V = "3"  # bump to bust browser cache when CSS/JS change


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
<tr><td>2 →</td><td style="color:var(--muted)">To be added as the course progresses</td></tr></tbody></table></div>
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
<tr><td>2 →</td><td style="color:var(--muted)">À compléter au fil du cours</td></tr></tbody></table></div>
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
<p>See the <a href="syllabus.html">Syllabus</a> for the course organisation and reading list. Use the <b>EN / FR</b> switch at the top right to change language.</p>''',
        '''<p class="kicker">MSG · 1ʳᵉ année · SBS / ULB</p><h1>Microéconomie</h1><p class="lead">Un compagnon d'étude pour le cours : notes, schémas et questions d'auto-évaluation pour chaque séance.</p>
<h2>Séance 1 — Introduction</h2>
<div class="grid">
<a class="card" href="lessons/s1-pensee-economique.html" style="text-decoration:none;color:inherit"><span class="tag">1.1</span><h4>Histoire de la pensée économique</h4><p>Classiques, néoclassiques, marxistes, keynésiens — et alternatives durables.</p></a>
<a class="card" href="lessons/s1-principes.html" style="text-decoration:none;color:inherit"><span class="tag">1.2</span><h4>Les 7 principes</h4><p>Choix, coût d'opportunité, raisonnement à la marge, incitations, échange, marchés, État.</p></a>
<a class="card" href="lessons/s1-echange.html" style="text-decoration:none;color:inherit"><span class="tag">1.3</span><h4>Échange et avantage comparatif</h4><p>Le modèle de Ricardo, les frontières de production et les termes de l'échange — avec un module interactif.</p></a>
</div>
<p>Consultez le <a href="syllabus.html">Programme du cours</a> pour l'organisation et la bibliographie. Utilisez le bouton <b>EN / FR</b> en haut à droite pour changer de langue.</p>''')]
    write("index.html", ("Home", "Accueil"), b, root="")


def page_upcoming(f, en, fr, topics_en, topics_fr):
    b = [L(
        f'<p class="kicker">Coming up</p><h1>{en}</h1><p class="lead">This session has not been covered yet.</p><h2>Expected topics</h2><ul>{"".join(f"<li>{t}</li>" for t in topics_en)}</ul><div class="placeholder">Notes will be added after the session.</div>',
        f'<p class="kicker">À venir</p><h1>{fr}</h1><p class="lead">Cette séance n\'a pas encore eu lieu.</p><h2>Thèmes prévus</h2><ul>{"".join(f"<li>{t}</li>" for t in topics_fr)}</ul><div class="placeholder">Les notes seront ajoutées après la séance.</div>')]
    write("lessons/" + f, (en, fr), b)


os.makedirs(os.path.join(SITE, "lessons"), exist_ok=True)
page_home()
page_syllabus()
page_pensee()
page_principes()
page_echange()
page_upcoming("offre-demande.html", "Supply, demand &amp; equilibrium", "Offre, demande et équilibre",
              ["Demand and its determinants", "Supply and its determinants", "Market equilibrium: quantities and prices", "Shifts of supply and demand"],
              ["La demande et ses déterminants", "L'offre et ses déterminants", "L'équilibre de marché : quantités et prix", "Déplacements de l'offre et de la demande"])
page_upcoming("concurrence-parfaite.html", "Perfect competition", "Concurrence parfaite",
              ["Assumptions of perfect competition", "Profit maximisation: P = MC", "Short run and long run", "Efficiency and surplus"],
              ["Hypothèses de la concurrence pure et parfaite (CPP)", "Maximisation du profit : P = Cm", "Court terme et long terme", "Efficacité et surplus"])
page_upcoming("monopole.html", "Monopoly", "Monopole",
              ["Sources of monopoly power", "MR = MC and the monopoly price", "Deadweight loss", "Price discrimination and regulation"],
              ["Sources du pouvoir de monopole", "Rm = Cm et le prix de monopole", "Perte sèche", "Discrimination par les prix et régulation"])
page_upcoming("oligopole-jeux.html", "Oligopoly &amp; game theory", "Oligopole et théorie des jeux",
              ["Oligopoly: few firms, strategic interaction", "Payoff matrices and dominant strategies", "Nash equilibrium", "Prisoner's dilemma, collusion and cartels"],
              ["Oligopole : peu d'entreprises, interaction stratégique", "Matrices de gains et stratégies dominantes", "Équilibre de Nash", "Dilemme du prisonnier, collusion et cartels"])
print("ok")
