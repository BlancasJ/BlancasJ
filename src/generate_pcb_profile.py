"""
GitHub Profile SVG — Hardware + Boot Sequence
Left: oscilloscope + PCB (hardware)
Right: computer monitor showing BIOS-style boot sequence
Connected by USB cable
"""
import math, os, requests

GITHUB_USER = "BlancasJ"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")


def get_github_stats():
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    try:
        user = requests.get(f"https://api.github.com/users/{GITHUB_USER}", headers=headers).json()
        repos = requests.get(f"https://api.github.com/users/{GITHUB_USER}/repos?per_page=100", headers=headers).json()
        return {
            "repos": user.get("public_repos", 0),
            "followers": user.get("followers", 0),
            "stars": sum(r.get("stargazers_count", 0) for r in repos if isinstance(r, dict)),
            "languages": len(set(r.get("language", "") for r in repos if isinstance(r, dict) and r.get("language"))),
        }
    except Exception:
        return {"repos": 50, "followers": 10, "stars": 5, "languages": 12}


def sine_path(x0, yc, amp, period, n):
    pts = []
    t = int(n * 24)
    w = period * n
    for i in range(t + 1):
        x = x0 + (i / t) * w
        y = yc + amp * math.sin(2 * math.pi * i / 24)
        pts.append(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}")
    return " ".join(pts)


def square_path(x0, yc, amp, period, n):
    pts = [f"M{x0},{yc}"]
    for i in range(n):
        x = x0 + i * period
        pts += [f"L{x},{yc-amp}", f"L{x+period*.5},{yc-amp}",
                f"L{x+period*.5},{yc+amp}", f"L{x+period},{yc+amp}"]
    return " ".join(pts)


def P(mode):
    if mode == "dark":
        return {
            "bg": "#0d1117",
            "sc": "#1c1c2e", "scScr": "#001208", "scG": "#0a2a0a", "scGC": "#0a3a0a",
            "scK": "#1a1a2a", "scKB": "#3a3a4a",
            "pcb": "#0a2a0a", "pcbB": "#1c5c1c", "pcbTr": "#1a3a1a",
            "pcbRef": "#2a5a2a", "cu": "#c8960c", "mnt": "#2a5a2a",
            "ic": "#1a1a1a", "icB": "#3a3a3a",
            "sn": "#1a2a5a", "snB": "#3355aa",
            "grn": "#00ff88", "blu": "#58a6ff", "amb": "#d29922",
            "red": "#ff5f57", "yel": "#febc2e", "grn2": "#28c840",
            "tB": "#e0e0e0", "tD": "#8b949e", "dot": "#444",
            "cable": "#444",
            "mon": "#2a2a2a", "monB": "#444", "monScr": "#0a0e12",
            "ok": "#28c840", "bar": "#00ff88", "barBg": "#1a2a1a",
            "tree": "#555",
        }
    return {
        "bg": "#ffffff",
        "sc": "#e8e8f0", "scScr": "#e8f5e8", "scG": "#c0dcc0", "scGC": "#a0c0a0",
        "scK": "#d0d0d8", "scKB": "#aaa",
        "pcb": "#d0e8d0", "pcbB": "#6a9a6a", "pcbTr": "#b0c8b0",
        "pcbRef": "#5a8a5a", "cu": "#8a6000", "mnt": "#8a8a8a",
        "ic": "#e0e0e0", "icB": "#bbb",
        "sn": "#b0c0f0", "snB": "#8099dd",
        "grn": "#1a7f37", "blu": "#0969da", "amb": "#9a6700",
        "red": "#ff5f57", "yel": "#febc2e", "grn2": "#28c840",
        "tB": "#1f2328", "tD": "#57606a", "dot": "#bbb",
        "cable": "#bbb",
        "mon": "#e0e0e0", "monB": "#bbb", "monScr": "#f8f8f8",
        "ok": "#1a7f37", "bar": "#1a7f37", "barBg": "#d0e8d0",
        "tree": "#999",
    }


def generate_svg(stats, mode="dark"):
    c = P(mode)
    ch1 = sine_path(0, 0, 16, 32, 16)
    ch2 = square_path(0, 0, 10, 44, 12)

    # ── Dynamic dates ──
    import datetime
    now = datetime.datetime.now()
    # Age (born Aug 21, 1998)
    born = datetime.datetime(1998, 8, 21)
    age = now - born
    age_y = age.days // 365
    age_m = (age.days % 365) // 30
    age_d = (age.days % 365) % 30
    # Experience (started Feb 15, 2021)
    started = datetime.datetime(2021, 2, 15)
    exp = now - started
    exp_y = exp.days // 365
    exp_m = (exp.days % 365) // 30
    exp_d = (exp.days % 365) % 30

    # ── Boot sequence text ──
    MX = 468
    F = 11
    LH = 13

    boot = []
    y = 48

    # Header
    boot.append(f'<text x="{MX}" y="{y}" font-size="14" font-weight="bold" fill="{c["grn"]}">jorge-blancas v5.0</text>')
    y += LH + 2
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}" fill="{c["dot"]}">{"═"*60}</text>')
    y += LH + 4

    # Animated progress bar (0% → 100%)
    bar_w = 350
    boot.append(f'<rect x="{MX}" y="{y-8}" width="{bar_w}" height="10" rx="1" fill="{c["barBg"]}" opacity="0.3"/>')
    boot.append(f'<rect x="{MX}" y="{y-8}" width="0" height="10" rx="1" fill="{c["bar"]}"><animate attributeName="width" from="0" to="{bar_w}" dur="3s" repeatCount="indefinite"/></rect>')
    # Percentage counter 0→100 (11 stacked texts, each visible for ~0.27s)
    px = MX + bar_w + 10
    steps = list(range(0, 110, 10))  # 0,10,20,...,100
    n = len(steps)  # 11
    for i, pct in enumerate(steps):
        # Each step gets an equal slice of the 3s duration
        # Build keyTimes: 0, fade_in_start, visible_start, visible_end, fade_out_end, 1
        s = i / n        # start fraction
        e = (i + 1) / n  # end fraction
        if i == 0:
            boot.append(f'<text x="{px}" y="{y}" font-size="{F}" fill="{c["grn"]}">{pct}%<animate attributeName="opacity" values="1;1;0;0;0;1" keyTimes="0;{e-.01:.3f};{e:.3f};{e+.01:.3f};{1-1/n:.3f};1" dur="3s" repeatCount="indefinite"/></text>')
        elif i == n - 1:
            boot.append(f'<text x="{px}" y="{y}" font-size="{F}" fill="{c["grn"]}" opacity="0">{pct}%<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{s-.01:.3f};{s:.3f};{.99:.3f};{.995:.3f};1" dur="3s" repeatCount="indefinite"/></text>')
        else:
            boot.append(f'<text x="{px}" y="{y}" font-size="{F}" fill="{c["grn"]}" opacity="0">{pct}%<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;{s-.01:.3f};{s:.3f};{e-.01:.3f};{e:.3f};1" dur="3s" repeatCount="indefinite"/></text>')
    y += LH + 6

    # System info (BIOS-style)
    info = [
        ("BIOS",        "Software Engineer"),
        ("HOST",        "Moz Group (Ziff Davis)"),
        ("CLOCK",       f"{exp_y} years, {exp_m} months, {exp_d} days in production"),
        ("FIRMWARE",    "Embedded → Industrial → Enterprise → FinTech → SEO SaaS"),
        ("BOOT DEVICE", "B.E. Computational Embedded Systems"),
        ("UPTIME",      f"{age_y} years, {age_m} months, {age_d} days"),
    ]
    for label, value in info:
        dots = "." * max(2, 22 - len(label))
        boot.append(f'<text x="{MX}" y="{y}" font-size="{F}"><tspan fill="{c["amb"]}">{label}</tspan><tspan fill="{c["dot"]}"> {dots} </tspan><tspan fill="{c["tB"]}">{value}</tspan></text>')
        y += LH
    y += LH

    # Loading modules (ALL 44 skills, 4-column grid)
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}" fill="{c["tD"]}">LOADING MODULES:</text>')
    y += LH + 2

    modules = [
        ["typescript",  "javascript",  "python",       "c"],
        ["c++",         "c#",          "bash",        "redis"],
        ["postgresql",  "cosmos-db",   "mysql",        "mongodb"],
        ["react",       "redux",       "storybook",    "HTML/CSS/SASS"],
        ["node.js",     "express",     "serverless",   "REST/BFF/graphql"],
        ["jest",        "karate-ui",   "postman",      "chai/mocha"],
        ["azure",       "aws",         "docker",       "terraform"],
        ["pic",         "arduino",     "esp32",        "stm32"],
        ["psoc",        "fpga",        "raspberry-pi", "intel-edison"],
        ["eagle-cad",   "siemens-plc", "labview",      "solidworks"],
    ]
    col_w = 130
    for row in modules:
        for i, mod in enumerate(row):
            x_pos = MX + i * col_w
            boot.append(f'<text x="{x_pos}" y="{y}" font-size="10"><tspan fill="{c["ok"]}">[OK]</tspan><tspan fill="{c["tB"]}"> {mod}</tspan></text>')
        y += LH
    y += LH

    # System log (achievements)
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}" fill="{c["tD"]}">SYSTEM LOG:</text>')
    y += LH + 2

    logs = [
        ("├", f'Migrated <tspan fill="{c["grn"]}">2M+</tspan> Redis keys to v7, zero downtime'),
        ("├", f'Reduced E2E test runtime by <tspan fill="{c["grn"]}">75%</tspan> (46 → 12 min)'),
        ("├", f'Fixed security vulnerability across <tspan fill="{c["grn"]}">15+</tspan> APIs'),
        ("└", f'Mentored <tspan fill="{c["grn"]}">10+</tspan> developers, <tspan fill="{c["grn"]}">2</tspan> promotions'),
    ]
    for branch, text in logs:
        boot.append(f'<text x="{MX}" y="{y}" font-size="{F}"><tspan fill="{c["tree"]}">{branch}─ </tspan><tspan fill="{c["tB"]}">{text}</tspan></text>')
        y += LH
    y += LH

    # Network
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}" fill="{c["tD"]}">NETWORK:</text>')
    y += LH + 2
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}"><tspan fill="{c["tree"]}">├─ </tspan><tspan fill="{c["amb"]}">linkedin</tspan><tspan fill="{c["tree"]}"> ─── </tspan><tspan fill="{c["blu"]}">linkedin.com/in/blancasjc</tspan></text>')
    y += LH
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}"><tspan fill="{c["tree"]}">└─ </tspan><tspan fill="{c["amb"]}">web</tspan><tspan fill="{c["tree"]}"> ──────── </tspan><tspan fill="{c["blu"]}">blancasjc.dev</tspan></text>')
    y += LH + 8

    # Footer
    boot.append(f'<text x="{MX}" y="{y}" font-size="{F}"><tspan fill="{c["grn"]}">▸ </tspan><tspan fill="{c["tD"]}">All systems operational. Ready for new challenges.</tspan></text>')
    y += LH

    SVG_H = max(y + 30, 455)
    MON_H = SVG_H - 28  # monitor total height
    SCR_H = MON_H - 30  # screen height

    boot_text = "\n  ".join(boot)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1050 {SVG_H}" font-family="'Consolas', 'Courier New', monospace">
  <defs>
    <clipPath id="osc-screen"><rect x="22" y="28" width="386" height="155"/></clipPath>
    <linearGradient id="cv" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{c["cable"]}" stop-opacity="0"/>
      <stop offset="40%" stop-color="{c["grn"]}" stop-opacity="0.5"/>
      <stop offset="60%" stop-color="{c["grn"]}" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="{c["cable"]}" stop-opacity="0"/>
      <animate attributeName="y1" values="-100%;100%" dur="1.5s" repeatCount="indefinite"/>
      <animate attributeName="y2" values="0%;200%" dur="1.5s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="tp" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{c["pcb"]}" stop-opacity="0"/>
      <stop offset="40%" stop-color="{c["cu"]}" stop-opacity="0.6"/>
      <stop offset="60%" stop-color="{c["cu"]}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="{c["pcb"]}" stop-opacity="0"/>
      <animate attributeName="x1" values="-100%;100%" dur="3s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="0%;200%" dur="3s" repeatCount="indefinite"/>
    </linearGradient>
    <linearGradient id="csig" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{c["cable"]}" stop-opacity="0"/>
      <stop offset="40%" stop-color="{c["blu"]}" stop-opacity="0.5"/>
      <stop offset="60%" stop-color="{c["blu"]}" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="{c["cable"]}" stop-opacity="0"/>
      <animate attributeName="x1" values="-100%;100%" dur="2s" repeatCount="indefinite"/>
      <animate attributeName="x2" values="0%;200%" dur="2s" repeatCount="indefinite"/>
    </linearGradient>
    <pattern id="pd" width="6" height="6" patternUnits="userSpaceOnUse">
      <circle cx="3" cy="3" r="0.25" fill="{c["pcbTr"]}"/>
    </pattern>
  </defs>

  <rect width="1050" height="{SVG_H}" rx="6" fill="{c["bg"]}"/>

  <!-- ════════════ OSCILLOSCOPE ════════════ -->

  <rect x="15" y="10" width="400" height="225" rx="6" fill="{c["sc"]}" stroke="{c["scKB"]}" stroke-width="1"/>
  <text x="25" y="24" fill="{c["tD"]}" font-size="8" font-weight="bold">DSO-JBC  200MHz</text>
  <circle cx="400" cy="20" r="3" fill="{c["grn"]}"><animate attributeName="opacity" values="0.4;1;0.4" dur="2.5s" repeatCount="indefinite"/></circle>

  <!-- Screen (taller for CH2 clearance) -->
  <rect x="22" y="28" width="386" height="155" rx="3" fill="{c["scScr"]}"/>

  <!-- Grid (taller screen: y=28 to y=183) -->
  <line x1="60" y1="28" x2="60" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="98" y1="28" x2="98" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="136" y1="28" x2="136" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="174" y1="28" x2="174" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="215" y1="28" x2="215" y2="183" stroke="{c["scGC"]}" stroke-width="0.5"/>
  <line x1="253" y1="28" x2="253" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="291" y1="28" x2="291" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="329" y1="28" x2="329" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="367" y1="28" x2="367" y2="183" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="22" y1="59" x2="408" y2="59" stroke="{c["scG"]}" stroke-width="0.15"/>
  <line x1="22" y1="90" x2="408" y2="90" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="22" y1="105" x2="408" y2="105" stroke="{c["scGC"]}" stroke-width="0.5"/>
  <line x1="22" y1="120" x2="408" y2="120" stroke="{c["scG"]}" stroke-width="0.3"/>
  <line x1="22" y1="151" x2="408" y2="151" stroke="{c["scG"]}" stroke-width="0.15"/>

  <!-- Waveforms (CH1 at y=80, CH2 at y=155 — well separated) -->
  <g clip-path="url(#osc-screen)">
    <g transform="translate(22,80)"><path d="{ch1}" stroke="{c["grn"]}" stroke-width="1.8" fill="none" opacity="0.85"><animateTransform attributeName="transform" type="translate" from="0 0" to="-64 0" dur="2s" repeatCount="indefinite"/></path></g>
    <g transform="translate(22,145)"><path d="{ch2}" stroke="{c["blu"]}" stroke-width="1.2" fill="none" opacity="0.65"><animateTransform attributeName="transform" type="translate" from="0 0" to="-88 0" dur="3s" repeatCount="indefinite"/></path></g>
  </g>

  <!-- HUD -->
  <rect x="28" y="32" width="6" height="6" rx="1" fill="{c["grn"]}" opacity="0.8"/>
  <text x="38" y="38" fill="{c["grn"]}" font-size="7">CH1 5.00V/div AC</text>
  <rect x="28" y="42" width="6" height="6" rx="1" fill="{c["blu"]}" opacity="0.8"/>
  <text x="38" y="48" fill="{c["blu"]}" font-size="7">CH2 3.30V/div DC</text>
  <text x="345" y="38" fill="{c["amb"]}" font-size="7">TRIG'D</text>
  <polygon points="407,85 402,82 402,88" fill="{c["amb"]}"/>
  <rect x="25" y="155" width="88" height="22" rx="1" fill="{c["scScr"]}" opacity="0.85" stroke="{c["scG"]}" stroke-width="0.3"/>
  <text x="30" y="165" fill="{c["amb"]}" font-size="6">Vpp: </text><text x="52" y="165" fill="{c["tB"]}" font-size="6">9.80V</text>
  <text x="30" y="173" fill="{c["amb"]}" font-size="6">Freq: </text><text x="56" y="173" fill="{c["tB"]}" font-size="6">1.2kHz</text>
  <text x="165" y="179" fill="{c["tD"]}" font-size="6.5">500us/div</text>
  <text x="285" y="179" fill="{c["tD"]}" font-size="6.5">1GSa/s</text>
  <text x="385" y="179" fill="{c["amb"]}" font-size="7">AUTO</text>

  <!-- Controls -->
  <rect x="22" y="189" width="386" height="40" rx="3" fill="{c["sc"]}" stroke="{c["scKB"]}" stroke-width="0.5"/>
  <circle cx="50" cy="209" r="11" fill="{c["scK"]}" stroke="{c["scKB"]}" stroke-width="1.2"/>
  <line x1="50" y1="200" x2="50" y2="203" stroke="{c["tD"]}" stroke-width="1"/>
  <circle cx="100" cy="209" r="11" fill="{c["scK"]}" stroke="{c["scKB"]}" stroke-width="1.2"/>
  <line x1="96" y1="200" x2="97" y2="203" stroke="{c["tD"]}" stroke-width="1"/>
  <circle cx="148" cy="209" r="9" fill="{c["scK"]}" stroke="{c["scKB"]}" stroke-width="1.2"/>
  <rect x="190" y="203" width="24" height="11" rx="2" fill="{c["scK"]}" stroke="{c["grn"]}" stroke-width="0.6"/>
  <text x="202" y="212" fill="{c["grn"]}" font-size="6" text-anchor="middle">RUN</text>
  <rect x="220" y="203" width="24" height="11" rx="2" fill="{c["scK"]}" stroke="{c["red"]}" stroke-width="0.6"/>
  <text x="232" y="212" fill="{c["red"]}" font-size="6" text-anchor="middle">STOP</text>
  <circle cx="285" cy="209" r="13" fill="{c["scK"]}" stroke="{c["scKB"]}" stroke-width="1"/>
  <circle cx="285" cy="209" r="4.5" fill="{c["sc"]}" stroke="{c["scKB"]}" stroke-width="0.6"/>
  <circle cx="345" cy="209" r="7" fill="{c["scK"]}" stroke="{c["cu"]}" stroke-width="1.2"/>
  <circle cx="345" cy="209" r="2" fill="{c["cu"]}"/>
  <text x="345" y="221" fill="{c["cu"]}" font-size="5" text-anchor="middle">CH1</text>
  <circle cx="380" cy="209" r="7" fill="{c["scK"]}" stroke="{c["blu"]}" stroke-width="1.2"/>
  <circle cx="380" cy="209" r="2" fill="{c["blu"]}"/>
  <text x="380" y="221" fill="{c["blu"]}" font-size="5" text-anchor="middle">CH2</text>

  <!-- ════════════ CABLE (scope → PCB) ════════════ -->
  <path d="M 215,235 C 215,250 160,253 160,268" stroke="{c["cable"]}" stroke-width="1.5" fill="none"/>
  <path d="M 215,235 C 215,250 160,253 160,268" stroke="url(#cv)" stroke-width="1.5" fill="none"/>

  <!-- ════════════ PCB BOARD ════════════ -->
  <g transform="translate(0,28)">

  <rect x="15" y="245" width="400" height="155" rx="3" fill="{c["pcb"]}" stroke="{c["pcbB"]}" stroke-width="1.2"/>
  <rect x="15" y="245" width="400" height="155" rx="3" fill="url(#pd)" opacity="0.5"/>
  <rect x="18" y="380" width="394" height="17" rx="1" fill="{c["pcbTr"]}" opacity="0.15"/>

  <!-- Mounting holes -->
  <circle cx="28" cy="258" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="28" cy="258" r="1.5" fill="{c["mnt"]}"/><circle cx="28" cy="258" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <circle cx="402" cy="258" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="402" cy="258" r="1.5" fill="{c["mnt"]}"/><circle cx="402" cy="258" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <circle cx="28" cy="387" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="28" cy="387" r="1.5" fill="{c["mnt"]}"/><circle cx="28" cy="387" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <circle cx="402" cy="387" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="402" cy="387" r="1.5" fill="{c["mnt"]}"/><circle cx="402" cy="387" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>

  <text x="215" y="260" text-anchor="middle" fill="{c["tD"]}" font-size="5">JBC-PROFILE-MK5 — FROM CIRCUITS TO CLOUD</text>

  <!-- Power rails + traces -->
  <text x="20" y="272" fill="{c["pcbRef"]}" font-size="3">VCC</text>
  <line x1="35" y1="273" x2="405" y2="273" stroke="url(#tp)" stroke-width="1"/>
  <line x1="35" y1="275" x2="405" y2="275" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="35" y1="318" x2="405" y2="318" stroke="url(#tp)" stroke-width="0.6"/>
  <line x1="35" y1="355" x2="240" y2="355" stroke="url(#tp)" stroke-width="0.6"/>
  <line x1="35" y1="378" x2="405" y2="378" stroke="{c["pcbTr"]}" stroke-width="0.6"/>
  <text x="20" y="383" fill="{c["pcbRef"]}" font-size="3">GND</text>
  <line x1="100" y1="263" x2="100" y2="395" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="165" y1="263" x2="165" y2="395" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="245" y1="263" x2="245" y2="395" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="330" y1="263" x2="330" y2="395" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <!-- IC-to-IC + IC-to-sensor routing -->
  <line x1="100" y1="300" x2="120" y2="300" stroke="{c["cu"]}" stroke-width="0.5"/>
  <line x1="70" y1="316" x2="70" y2="330" stroke="{c["cu"]}" stroke-width="0.4"/>
  <line x1="141" y1="316" x2="141" y2="320" stroke="{c["cu"]}" stroke-width="0.4"/>
  <line x1="165" y1="308" x2="185" y2="325" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <!-- Vias -->
  <circle cx="100" cy="245" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="100" cy="245" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="165" cy="245" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="165" cy="245" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="245" cy="318" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="245" cy="318" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="330" cy="245" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="330" cy="245" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="100" cy="318" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="100" cy="318" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="370" cy="318" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="370" cy="318" r="0.7" fill="{c["mnt"]}"/>
  <!-- Data bits -->
  <rect x="35" y="272" width="5" height="2" rx="0.5" fill="{c["cu"]}" opacity="0.5"><animateTransform attributeName="transform" type="translate" from="0 0" to="370 0" dur="3s" repeatCount="indefinite"/></rect>
  <rect x="35" y="272" width="5" height="2" rx="0.5" fill="{c["cu"]}" opacity="0.25"><animateTransform attributeName="transform" type="translate" from="0 0" to="370 0" dur="3s" begin="1.5s" repeatCount="indefinite"/></rect>
  <!-- Decoupling caps -->
  <rect x="55" y="280" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <rect x="85" y="280" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <rect x="135" y="280" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <rect x="150" y="280" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>

  <!-- U1: ESP32 -->
  <rect x="45" y="286" width="50" height="28" rx="1.5" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.8"/>
  <circle cx="51" cy="291" r="1.2" fill="{c["cu"]}" opacity="0.4"/>
  <line x1="40" y1="293" x2="45" y2="293" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="40" y1="300" x2="45" y2="300" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="40" y1="307" x2="45" y2="307" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="95" y1="293" x2="100" y2="293" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="95" y1="300" x2="100" y2="300" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="95" y1="307" x2="100" y2="307" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="57" y1="281" x2="57" y2="286" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="67" y1="281" x2="67" y2="286" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="77" y1="281" x2="77" y2="286" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="87" y1="281" x2="87" y2="286" stroke="{c["cu"]}" stroke-width="0.8"/>
  <text x="70" y="304" text-anchor="middle" fill="{c["tD"]}" font-size="6.5" font-weight="bold">ESP32</text>
  <text x="70" y="312" text-anchor="middle" fill="{c["pcbRef"]}" font-size="4">U1</text>

  <!-- U2: PIC -->
  <rect x="125" y="286" width="32" height="28" rx="1" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.8"/>
  <path d="M 137,286 A 4,4 0 0 1 145,286" fill="none" stroke="{c["icB"]}" stroke-width="0.8"/>
  <line x1="120" y1="293" x2="125" y2="293" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="120" y1="300" x2="125" y2="300" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="120" y1="307" x2="125" y2="307" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="157" y1="293" x2="162" y2="293" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="157" y1="300" x2="162" y2="300" stroke="{c["cu"]}" stroke-width="0.8"/><line x1="157" y1="307" x2="162" y2="307" stroke="{c["cu"]}" stroke-width="0.8"/>
  <text x="141" y="304" text-anchor="middle" fill="{c["tD"]}" font-size="6" font-weight="bold">PIC</text>
  <text x="141" y="312" text-anchor="middle" fill="{c["pcbRef"]}" font-size="4">U2</text>

  <!-- LEDs -->
  <circle cx="195" cy="290" r="3" fill="{c["grn"]}" opacity="0.8"><animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/></circle>
  <circle cx="210" cy="290" r="3" fill="{c["blu"]}"><animate attributeName="opacity" values="0.1;1;0.1" dur="1s" repeatCount="indefinite"/></circle>
  <circle cx="225" cy="290" r="3" fill="{c["amb"]}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite"/></circle>
  <text x="195" y="300" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">PWR</text>
  <text x="210" y="300" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">ACT</text>
  <text x="225" y="300" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">STS</text>

  <!-- Sensors -->
  <rect x="45" y="326" width="24" height="18" rx="1.5" fill="{c["sn"]}" stroke="{c["snB"]}" stroke-width="0.6"/>
  <line x1="51" y1="330" x2="63" y2="330" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <line x1="51" y1="333" x2="63" y2="333" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <line x1="51" y1="336" x2="63" y2="336" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <text x="57" y="342" text-anchor="middle" fill="#6688cc" font-size="3.5">DHT11</text>
  <text x="57" y="352" text-anchor="middle" fill="{c["tD"]}" font-size="4.5">tmp/hum</text>
  <line x1="52" y1="344" x2="52" y2="349" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="57" y1="344" x2="57" y2="349" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="62" y1="344" x2="62" y2="349" stroke="{c["cu"]}" stroke-width="0.6"/>

  <circle cx="108" cy="335" r="10" fill="#333" stroke="#555" stroke-width="0.6"/>
  <circle cx="108" cy="335" r="6.5" fill="#333" stroke="#555" stroke-width="0.4"/>
  <line x1="102" y1="329" x2="114" y2="341" stroke="#555" stroke-width="0.3"/><line x1="114" y1="329" x2="102" y2="341" stroke="#555" stroke-width="0.3"/>
  <line x1="108" y1="328" x2="108" y2="342" stroke="#555" stroke-width="0.3"/><line x1="101" y1="335" x2="115" y2="335" stroke="#555" stroke-width="0.3"/>
  <text x="108" y="352" text-anchor="middle" fill="{c["tD"]}" font-size="4.5">smoke</text>
  <text x="108" y="323" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">MQ-2</text>

  <circle cx="155" cy="335" r="10" fill="#333" stroke="#555" stroke-width="0.6"/>
  <circle cx="155" cy="335" r="6.5" fill="#333" stroke="#555" stroke-width="0.4"/>
  <line x1="149" y1="329" x2="161" y2="341" stroke="#555" stroke-width="0.3"/><line x1="161" y1="329" x2="149" y2="341" stroke="#555" stroke-width="0.3"/>
  <text x="155" y="352" text-anchor="middle" fill="{c["tD"]}" font-size="4.5">air qual</text>
  <text x="155" y="323" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">MQ-135</text>

  <!-- TO-92 LM35 -->
  <path d="M 195,330 A 8,8 0 0 1 211,330" fill="#333" stroke="#555" stroke-width="0.6"/>
  <line x1="195" y1="330" x2="211" y2="330" stroke="#555" stroke-width="0.6"/>
  <line x1="199" y1="330" x2="199" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="203" y1="330" x2="203" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="207" y1="330" x2="207" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <text x="203" y="326" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">LM35</text>
  <text x="203" y="344" text-anchor="middle" fill="{c["tD"]}" font-size="4.5">temp</text>

  <!-- Resistors + diodes + caps -->
  <rect x="250" y="288" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="250" y="288" width="2.5" height="5" fill="{c["cu"]}"/><rect x="259.5" y="288" width="2.5" height="5" fill="{c["cu"]}"/>
  <rect x="275" y="288" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="275" y="288" width="2.5" height="5" fill="{c["cu"]}"/><rect x="284.5" y="288" width="2.5" height="5" fill="{c["cu"]}"/>
  <rect x="300" y="288" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="300" y="288" width="2.5" height="5" fill="{c["cu"]}"/><rect x="309.5" y="288" width="2.5" height="5" fill="{c["cu"]}"/>
  <rect x="325" y="288" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="325" y="288" width="2.5" height="5" fill="{c["cu"]}"/><rect x="334.5" y="288" width="2.5" height="5" fill="{c["cu"]}"/>
  <rect x="350" y="288" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="350" y="288" width="2.5" height="5" fill="{c["cu"]}"/><rect x="359.5" y="288" width="2.5" height="5" fill="{c["cu"]}"/>

  <polygon points="255,328 255,338 265,333" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="265" y1="328" x2="265" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <polygon points="285,328 285,338 295,333" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="295" y1="328" x2="295" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <polygon points="315,328 315,338 325,333" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="325" y1="328" x2="325" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>

  <circle cx="260" cy="362" r="5" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>
  <circle cx="280" cy="362" r="5" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>
  <circle cx="300" cy="362" r="5" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>

  <rect x="330" y="328" width="14" height="7" rx="2" fill="#888" stroke="#aaa" stroke-width="0.4"/>
  <text x="337" y="334" text-anchor="middle" fill="#333" font-size="3" font-weight="bold">16MHz</text>

  <!-- Antenna -->
  <path d="M 365,298 L 372,298 L 372,291 L 379,291" stroke="{c["cu"]}" stroke-width="0.5" fill="none"/>
  <path d="M 372,298 L 372,305" stroke="{c["cu"]}" stroke-width="0.5" fill="none"/>
  <text x="381" y="294" fill="{c["pcbRef"]}" font-size="3">ANT</text>

  <!-- Pin header -->
  <rect x="355" y="340" width="18" height="22" rx="0.5" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.5"/>
  <rect x="357" y="342" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="366" y="342" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="357" y="348" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="366" y="348" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="357" y="354" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="366" y="354" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <text x="364" y="338" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">J1</text>

  <!-- Voltage regulator -->
  <rect x="240" y="358" width="14" height="10" rx="0.5" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.5"/>
  <rect x="241" y="355" width="12" height="3" rx="0.3" fill="{c["icB"]}"/>
  <line x1="244" y1="368" x2="244" y2="373" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="247" y1="368" x2="247" y2="373" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="250" y1="368" x2="250" y2="373" stroke="{c["cu"]}" stroke-width="0.6"/>
  <text x="247" y="366" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">3.3V</text>

  <!-- USB connector -->
  <rect x="400" y="305" width="15" height="14" rx="2" fill="#555" stroke="#777" stroke-width="0.8"/>
  <rect x="403" y="308" width="8" height="8" rx="1" fill="#444"/>
  <text x="407" y="325" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">USB</text>

  <!-- Test points + fiducials -->
  <circle cx="385" cy="370" r="2.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.6"/>
  <text x="385" y="367" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">TP1</text>
  <circle cx="398" cy="370" r="2.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.6"/>
  <text x="398" y="367" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">TP2</text>
  <circle cx="38" cy="375" r="1.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.4"/>
  <circle cx="38" cy="375" r="0.5" fill="{c["mnt"]}"/>

  <!-- Board rev -->
  <text x="55" y="393" fill="{c["pcbRef"]}" font-size="3.5">REV 5.0 · JBC ELECTRONICS · MERIDA MX · LEAD-FREE · ROHS</text>

  </g><!-- end PCB group -->

  <!-- ════════════ USB CABLE (PCB → Monitor) ════════════ -->

  <path d="M 415,340 C 432,340 440,340 455,340" stroke="{c["cable"]}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
  <path d="M 415,340 C 432,340 440,340 455,340" stroke="url(#csig)" stroke-width="2" fill="none"/>

  <!-- ════════════ COMPUTER MONITOR ════════════ -->

  <!-- Bezel -->
  <rect x="440" y="8" width="600" height="{MON_H}" rx="8" fill="{c["mon"]}" stroke="{c["monB"]}" stroke-width="1.5"/>
  <!-- Webcam -->
  <circle cx="740" cy="16" r="2" fill="{c["monB"]}"/>
  <!-- Screen -->
  <rect x="452" y="22" width="576" height="{SCR_H}" rx="4" fill="{c["monScr"]}"/>
  <!-- Power LED -->
  <circle cx="740" cy="{SVG_H - 24}" r="2" fill="{c["grn"]}" opacity="0.4">
    <animate attributeName="opacity" values="0.2;0.5;0.2" dur="4s" repeatCount="indefinite"/>
  </circle>
  <!-- Stand -->
  <rect x="690" y="{SVG_H - 18}" width="100" height="6" rx="2" fill="{c["monB"]}"/>
  <rect x="718" y="{SVG_H - 12}" width="44" height="12" rx="2" fill="{c["mon"]}"/>

  <!-- ═══ BOOT SEQUENCE ═══ -->

  {boot_text}

</svg>'''


def main():
    stats = get_github_stats()
    os.makedirs("dist", exist_ok=True)
    with open("dist/dark_mode.svg", "w") as f:
        f.write(generate_svg(stats, "dark"))
    with open("dist/light_mode.svg", "w") as f:
        f.write(generate_svg(stats, "light"))
    print(f"Generated profile SVGs: {stats}")


if __name__ == "__main__":
    main()
