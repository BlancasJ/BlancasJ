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
    MX = 365
    F = 12
    LH = 14

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
    col_w = 120
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

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 950 {SVG_H}" font-family="'Consolas', 'Courier New', monospace">
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

  <rect width="950" height="{SVG_H}" rx="6" fill="{c["bg"]}"/>

  <!-- ════════════ LEFT COLUMN (scaled down) ════════════ -->
  <g transform="scale(0.75) translate(0, 10)">

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

  <!-- ════════════ PCB BOARD (inspired by Smart Room PCB) ════════════ -->
  <g transform="translate(0,28)">

  <rect x="15" y="245" width="400" height="300" rx="3" fill="{c["pcb"]}" stroke="{c["pcbB"]}" stroke-width="1.2"/>
  <rect x="15" y="245" width="400" height="300" rx="3" fill="url(#pd)" opacity="0.5"/>
  <!-- Ground plane -->
  <rect x="18" y="525" width="394" height="17" rx="1" fill="{c["pcbTr"]}" opacity="0.15"/>

  <!-- Mounting holes with annular rings -->
  <circle cx="28" cy="258" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="28" cy="258" r="1.5" fill="{c["mnt"]}"/><circle cx="28" cy="258" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <circle cx="402" cy="258" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="402" cy="258" r="1.5" fill="{c["mnt"]}"/><circle cx="402" cy="258" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <circle cx="28" cy="532" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="28" cy="532" r="1.5" fill="{c["mnt"]}"/><circle cx="28" cy="532" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <circle cx="402" cy="532" r="4" fill="none" stroke="{c["mnt"]}" stroke-width="1"/><circle cx="402" cy="532" r="1.5" fill="{c["mnt"]}"/><circle cx="402" cy="532" r="5.5" fill="none" stroke="{c["pcbTr"]}" stroke-width="0.3"/>

  <text x="215" y="260" text-anchor="middle" fill="{c["tD"]}" font-size="5">JBC-PROFILE-MK5 — FROM CIRCUITS TO CLOUD</text>

  <!-- ═══ SCREW TERMINALS (top edge, green, like smart room) ═══ -->
  <rect x="40" y="264" width="22" height="10" rx="1.5" fill="#1a5a2a" stroke="#2a7a3a" stroke-width="0.6"/>
  <rect x="43" y="266" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="45.5" cy="269" r="1.5" fill="#2a7a3a"/>
  <rect x="52" y="266" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="54.5" cy="269" r="1.5" fill="#2a7a3a"/>
  <text x="51" y="280" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">J1 VCC</text>

  <rect x="80" y="264" width="22" height="10" rx="1.5" fill="#1a5a2a" stroke="#2a7a3a" stroke-width="0.6"/>
  <rect x="83" y="266" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="85.5" cy="269" r="1.5" fill="#2a7a3a"/>
  <rect x="92" y="266" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="94.5" cy="269" r="1.5" fill="#2a7a3a"/>
  <text x="91" y="280" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">J2 SENS</text>

  <rect x="120" y="264" width="22" height="10" rx="1.5" fill="#1a5a2a" stroke="#2a7a3a" stroke-width="0.6"/>
  <rect x="123" y="266" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="125.5" cy="269" r="1.5" fill="#2a7a3a"/>
  <rect x="132" y="266" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="134.5" cy="269" r="1.5" fill="#2a7a3a"/>
  <text x="131" y="280" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">J3 VALVE</text>

  <!-- ═══ TRACES + POWER RAILS ═══ -->
  <text x="20" y="290" fill="{c["pcbRef"]}" font-size="3">VCC</text>
  <line x1="35" y1="291" x2="405" y2="291" stroke="url(#tp)" stroke-width="1"/>
  <line x1="35" y1="293" x2="405" y2="293" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="35" y1="340" x2="405" y2="340" stroke="url(#tp)" stroke-width="0.6"/>
  <line x1="35" y1="390" x2="405" y2="390" stroke="url(#tp)" stroke-width="0.5"/>
  <line x1="35" y1="440" x2="405" y2="440" stroke="url(#tp)" stroke-width="0.5"/>
  <line x1="35" y1="490" x2="405" y2="490" stroke="url(#tp)" stroke-width="0.5"/>
  <line x1="35" y1="523" x2="405" y2="523" stroke="{c["pcbTr"]}" stroke-width="0.8"/>
  <text x="20" y="528" fill="{c["pcbRef"]}" font-size="3">GND</text>
  <!-- Verticals -->
  <line x1="100" y1="258" x2="100" y2="535" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="165" y1="258" x2="165" y2="535" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="245" y1="258" x2="245" y2="535" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="330" y1="258" x2="330" y2="535" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <!-- Diagonal routing (45°) -->
  <line x1="100" y1="320" x2="120" y2="340" stroke="{c["cu"]}" stroke-width="0.4"/>
  <line x1="165" y1="330" x2="185" y2="350" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="245" y1="380" x2="270" y2="405" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <line x1="330" y1="420" x2="350" y2="440" stroke="{c["pcbTr"]}" stroke-width="0.3"/>
  <!-- IC-to-IC bus -->
  <line x1="100" y1="318" x2="120" y2="318" stroke="{c["cu"]}" stroke-width="0.5"/>
  <line x1="70" y1="336" x2="70" y2="355" stroke="{c["cu"]}" stroke-width="0.4"/>
  <line x1="165" y1="318" x2="200" y2="318" stroke="{c["cu"]}" stroke-width="0.4"/>

  <!-- Data bits on VCC -->
  <rect x="35" y="290" width="5" height="2" rx="0.5" fill="{c["cu"]}" opacity="0.5"><animateTransform attributeName="transform" type="translate" from="0 0" to="370 0" dur="3s" repeatCount="indefinite"/></rect>
  <rect x="35" y="290" width="5" height="2" rx="0.5" fill="{c["cu"]}" opacity="0.25"><animateTransform attributeName="transform" type="translate" from="0 0" to="370 0" dur="3s" begin="1.5s" repeatCount="indefinite"/></rect>

  <!-- ═══ VIAS (scattered for realism) ═══ -->
  <circle cx="100" cy="291" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="100" cy="291" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="165" cy="291" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="165" cy="291" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="245" cy="340" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="245" cy="340" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="330" cy="291" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="330" cy="291" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="100" cy="340" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="100" cy="340" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="370" cy="340" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="370" cy="340" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="165" cy="440" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="165" cy="440" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="330" cy="490" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="330" cy="490" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="100" cy="490" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="100" cy="490" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="245" cy="490" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="245" cy="490" r="0.7" fill="{c["mnt"]}"/>
  <circle cx="370" cy="440" r="2" fill="{c["pcb"]}" stroke="{c["mnt"]}" stroke-width="0.6"/><circle cx="370" cy="440" r="0.7" fill="{c["mnt"]}"/>

  <!-- ═══ U1: ESP32 WROOM (large silver module, like the real one) ═══ -->
  <rect x="40" y="298" width="55" height="35" rx="2" fill="#888" stroke="#aaa" stroke-width="0.8"/>
  <rect x="42" y="300" width="51" height="31" rx="1" fill="#666" stroke="#888" stroke-width="0.4"/>
  <!-- Shield can pattern -->
  <rect x="44" y="302" width="47" height="27" rx="0.5" fill="#777" stroke="#999" stroke-width="0.3"/>
  <circle cx="50" cy="308" r="1.5" fill="{c["cu"]}" opacity="0.4"/>
  <!-- Castellated pads (bottom + sides) -->
  <line x1="48" y1="333" x2="48" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="54" y1="333" x2="54" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="60" y1="333" x2="60" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="66" y1="333" x2="66" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="72" y1="333" x2="72" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="78" y1="333" x2="78" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="84" y1="333" x2="84" y2="338" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="40" y1="310" x2="36" y2="310" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="40" y1="316" x2="36" y2="316" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="40" y1="322" x2="36" y2="322" stroke="{c["cu"]}" stroke-width="0.8"/>
  <text x="67" y="320" text-anchor="middle" fill="#333" font-size="6" font-weight="bold">ESP32</text>
  <text x="67" y="328" text-anchor="middle" fill="#444" font-size="4">WROOM</text>
  <!-- Blue LED on ESP32 -->
  <circle cx="48" cy="326" r="1.5" fill="{c["blu"]}"><animate attributeName="opacity" values="0.2;1;0.2" dur="1.5s" repeatCount="indefinite"/></circle>
  <text x="67" y="344" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">U1</text>

  <!-- WiFi antenna trace (inverted-F, like real ESP32 boards) -->
  <path d="M 95,305 L 105,305 L 105,298 L 115,298" stroke="{c["cu"]}" stroke-width="0.7" fill="none"/>
  <path d="M 105,305 L 105,312" stroke="{c["cu"]}" stroke-width="0.7" fill="none"/>
  <text x="117" y="301" fill="{c["pcbRef"]}" font-size="2.5">ANT1</text>

  <!-- ═══ XBee module (blue, with antenna header, like the real one) ═══ -->
  <rect x="200" y="296" width="42" height="35" rx="2" fill="#2244aa" stroke="#3366cc" stroke-width="0.8"/>
  <text x="221" y="312" text-anchor="middle" fill="#88aaff" font-size="5" font-weight="bold">XBee</text>
  <text x="221" y="320" text-anchor="middle" fill="#6688cc" font-size="3">S2C</text>
  <!-- XBee pins (bottom, 2 rows) -->
  <line x1="206" y1="331" x2="206" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="211" y1="331" x2="211" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="216" y1="331" x2="216" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="221" y1="331" x2="221" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="226" y1="331" x2="226" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="231" y1="331" x2="231" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="236" y1="331" x2="236" y2="336" stroke="{c["cu"]}" stroke-width="0.6"/>
  <!-- SMA antenna connector -->
  <circle cx="221" cy="293" r="4" fill="{c["cu"]}" opacity="0.6"/>
  <circle cx="221" cy="293" r="2" fill="#333"/>
  <text x="221" y="342" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">U5</text>

  <!-- ═══ U2: PIC16F88 (DIP with notch) ═══ -->
  <rect x="130" y="296" width="32" height="38" rx="1" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.8"/>
  <path d="M 141,296 A 4,4 0 0 1 149,296" fill="none" stroke="{c["icB"]}" stroke-width="0.8"/>
  <circle cx="136" cy="302" r="1" fill="{c["cu"]}" opacity="0.4"/>
  <line x1="125" y1="303" x2="130" y2="303" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="125" y1="310" x2="130" y2="310" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="125" y1="317" x2="130" y2="317" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="125" y1="324" x2="130" y2="324" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="162" y1="303" x2="167" y2="303" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="162" y1="310" x2="167" y2="310" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="162" y1="317" x2="167" y2="317" stroke="{c["cu"]}" stroke-width="0.8"/>
  <line x1="162" y1="324" x2="167" y2="324" stroke="{c["cu"]}" stroke-width="0.8"/>
  <text x="146" y="316" text-anchor="middle" fill="{c["tD"]}" font-size="5.5" font-weight="bold">PIC</text>
  <text x="146" y="324" text-anchor="middle" fill="{c["tD"]}" font-size="4">16F88</text>
  <text x="146" y="340" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3.5">U2</text>

  <!-- ═══ LEDs (like the real board — blue ESP32, red relay, green PWR) ═══ -->
  <circle cx="270" cy="300" r="3" fill="{c["grn"]}" opacity="0.8"><animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/></circle>
  <text x="270" y="310" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">D1</text>
  <circle cx="285" cy="300" r="3" fill="{c["blu"]}"><animate attributeName="opacity" values="0.1;1;0.1" dur="1s" repeatCount="indefinite"/></circle>
  <text x="285" y="310" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">D2</text>
  <circle cx="300" cy="300" r="3" fill="{c["red"]}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2.5s" repeatCount="indefinite"/></circle>
  <text x="300" y="310" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">D3</text>
  <circle cx="315" cy="300" r="3" fill="{c["red"]}" opacity="0.6"><animate attributeName="opacity" values="0.2;0.8;0.2" dur="3s" repeatCount="indefinite"/></circle>
  <text x="315" y="310" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">D4</text>

  <!-- Decoupling caps near ICs -->
  <rect x="42" y="344" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <text x="44" y="351" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2">C1</text>
  <rect x="88" y="344" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <text x="90" y="351" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2">C2</text>
  <rect x="125" y="344" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <text x="127" y="351" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2">C3</text>
  <rect x="168" y="344" width="4" height="3" rx="0.3" fill="{c["pcbTr"]}" stroke="{c["mnt"]}" stroke-width="0.3"/>
  <text x="170" y="351" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2">C4</text>

  <!-- ═══ SENSORS (middle zone) ═══ -->
  <!-- DHT11 (blue module with ventilation grille) -->
  <rect x="40" y="360" width="28" height="22" rx="2" fill="{c["sn"]}" stroke="{c["snB"]}" stroke-width="0.7"/>
  <line x1="46" y1="364" x2="62" y2="364" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <line x1="46" y1="367" x2="62" y2="367" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <line x1="46" y1="370" x2="62" y2="370" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <line x1="46" y1="373" x2="62" y2="373" stroke="{c["snB"]}" stroke-width="0.3" opacity="0.5"/>
  <text x="54" y="378" text-anchor="middle" fill="#6688cc" font-size="3.5">DHT11</text>
  <line x1="48" y1="382" x2="48" y2="387" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="54" y1="382" x2="54" y2="387" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="60" y1="382" x2="60" y2="387" stroke="{c["cu"]}" stroke-width="0.6"/>
  <text x="54" y="393" text-anchor="middle" fill="{c["tD"]}" font-size="4">tmp/hum</text>

  <!-- MQ-2 (cylindrical gas sensor with mesh) -->
  <circle cx="108" cy="372" r="12" fill="#333" stroke="#555" stroke-width="0.7"/>
  <circle cx="108" cy="372" r="8" fill="#333" stroke="#555" stroke-width="0.4"/>
  <line x1="101" y1="365" x2="115" y2="379" stroke="#555" stroke-width="0.3"/>
  <line x1="115" y1="365" x2="101" y2="379" stroke="#555" stroke-width="0.3"/>
  <line x1="108" y1="363" x2="108" y2="381" stroke="#555" stroke-width="0.3"/>
  <line x1="99" y1="372" x2="117" y2="372" stroke="#555" stroke-width="0.3"/>
  <text x="108" y="392" text-anchor="middle" fill="{c["tD"]}" font-size="4">smoke</text>
  <text x="108" y="358" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">MQ-2</text>

  <!-- MQ-135 (air quality, similar cylinder) -->
  <circle cx="155" cy="372" r="12" fill="#333" stroke="#555" stroke-width="0.7"/>
  <circle cx="155" cy="372" r="8" fill="#333" stroke="#555" stroke-width="0.4"/>
  <line x1="148" y1="365" x2="162" y2="379" stroke="#555" stroke-width="0.3"/>
  <line x1="162" y1="365" x2="148" y2="379" stroke="#555" stroke-width="0.3"/>
  <text x="155" y="392" text-anchor="middle" fill="{c["tD"]}" font-size="4">air qual</text>
  <text x="155" y="358" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">MQ-135</text>

  <!-- LM35 (TO-92) -->
  <path d="M 195,367 A 9,9 0 0 1 213,367" fill="#333" stroke="#555" stroke-width="0.7"/>
  <line x1="195" y1="367" x2="213" y2="367" stroke="#555" stroke-width="0.7"/>
  <line x1="200" y1="367" x2="200" y2="374" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="204" y1="367" x2="204" y2="374" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="208" y1="367" x2="208" y2="374" stroke="{c["cu"]}" stroke-width="0.6"/>
  <text x="204" y="363" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">LM35</text>
  <text x="204" y="381" text-anchor="middle" fill="{c["tD"]}" font-size="4">temp</text>

  <!-- ═══ RELAY MODULE (black, bottom-left, like the real one) ═══ -->
  <rect x="35" y="400" width="40" height="30" rx="2" fill="#111" stroke="#333" stroke-width="0.8"/>
  <rect x="38" y="403" width="18" height="24" rx="1" fill="#1a1a2a" stroke="#2a2a3a" stroke-width="0.5"/>
  <text x="47" y="418" text-anchor="middle" fill="{c["blu"]}" font-size="4">RELAY</text>
  <!-- Relay screw terminals -->
  <rect x="60" y="405" width="12" height="6" rx="1" fill="#1a5a2a" stroke="#2a7a3a" stroke-width="0.4"/>
  <circle cx="63" cy="408" r="1" fill="#2a7a3a"/><circle cx="69" cy="408" r="1" fill="#2a7a3a"/>
  <rect x="60" y="418" width="12" height="6" rx="1" fill="#1a5a2a" stroke="#2a7a3a" stroke-width="0.4"/>
  <circle cx="63" cy="421" r="1" fill="#2a7a3a"/><circle cx="69" cy="421" r="1" fill="#2a7a3a"/>
  <text x="55" y="436" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">K1</text>
  <!-- Red LEDs on relay -->
  <circle cx="40" cy="427" r="1.5" fill="{c["red"]}" opacity="0.5"><animate attributeName="opacity" values="0.2;0.7;0.2" dur="3s" repeatCount="indefinite"/></circle>
  <circle cx="48" cy="427" r="1.5" fill="{c["red"]}" opacity="0.3"/>

  <!-- ═══ SMD RESISTORS (row, with values) ═══ -->
  <rect x="100" y="400" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="100" y="400" width="2.5" height="5" fill="{c["cu"]}"/><rect x="109.5" y="400" width="2.5" height="5" fill="{c["cu"]}"/>
  <text x="106" y="411" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">R1 4k7</text>
  <rect x="125" y="400" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="125" y="400" width="2.5" height="5" fill="{c["cu"]}"/><rect x="134.5" y="400" width="2.5" height="5" fill="{c["cu"]}"/>
  <text x="131" y="411" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">R2 10k</text>
  <rect x="150" y="400" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="150" y="400" width="2.5" height="5" fill="{c["cu"]}"/><rect x="159.5" y="400" width="2.5" height="5" fill="{c["cu"]}"/>
  <text x="156" y="411" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">R3 330</text>
  <rect x="175" y="400" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="175" y="400" width="2.5" height="5" fill="{c["cu"]}"/><rect x="184.5" y="400" width="2.5" height="5" fill="{c["cu"]}"/>
  <text x="181" y="411" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">R4 1k</text>
  <rect x="200" y="400" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="200" y="400" width="2.5" height="5" fill="{c["cu"]}"/><rect x="209.5" y="400" width="2.5" height="5" fill="{c["cu"]}"/>
  <text x="206" y="411" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">R5 4k7</text>

  <!-- ═══ ELECTROLYTIC CAPS (top view, with polarity) ═══ -->
  <circle cx="260" cy="360" r="6" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>
  <line x1="256" y1="356" x2="264" y2="356" stroke="#3a3a5a" stroke-width="0.4"/>
  <text x="260" y="363" text-anchor="middle" fill="#5555aa" font-size="2.5">+</text>
  <text x="260" y="372" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">C5 100u</text>
  <circle cx="285" cy="360" r="6" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>
  <line x1="281" y1="356" x2="289" y2="356" stroke="#3a3a5a" stroke-width="0.4"/>
  <text x="285" y="372" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">C6 10u</text>

  <!-- ═══ DIODES ═══ -->
  <polygon points="255,400 255,410 267,405" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="267" y1="400" x2="267" y2="410" stroke="{c["cu"]}" stroke-width="0.8"/>
  <text x="261" y="416" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">D5</text>
  <polygon points="280,400 280,410 292,405" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="292" y1="400" x2="292" y2="410" stroke="{c["cu"]}" stroke-width="0.8"/>
  <text x="286" y="416" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">D6</text>

  <!-- ═══ CRYSTAL (16MHz) ═══ -->
  <rect x="240" y="320" width="16" height="8" rx="2.5" fill="#888" stroke="#aaa" stroke-width="0.5"/>
  <text x="248" y="327" text-anchor="middle" fill="#333" font-size="3" font-weight="bold">16MHz</text>
  <text x="248" y="332" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">Y1</text>

  <!-- ═══ VOLTAGE REGULATOR (TO-220 with heatsink tab) ═══ -->
  <rect x="310" y="350" width="16" height="14" rx="0.5" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.6"/>
  <rect x="311" y="347" width="14" height="4" rx="0.3" fill="{c["icB"]}"/>
  <line x1="314" y1="364" x2="314" y2="370" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="318" y1="364" x2="318" y2="370" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="322" y1="364" x2="322" y2="370" stroke="{c["cu"]}" stroke-width="0.6"/>
  <text x="318" y="360" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">3.3V</text>
  <text x="318" y="376" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">VR1</text>

  <!-- ═══ HC-12 radio module (small, near XBee) ═══ -->
  <rect x="260" y="296" width="25" height="16" rx="1" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.6"/>
  <text x="272" y="307" text-anchor="middle" fill="{c["tD"]}" font-size="4" font-weight="bold">HC-12</text>
  <text x="272" y="316" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">U3</text>
  <line x1="264" y1="312" x2="264" y2="317" stroke="{c["cu"]}" stroke-width="0.5"/>
  <line x1="268" y1="312" x2="268" y2="317" stroke="{c["cu"]}" stroke-width="0.5"/>
  <line x1="272" y1="312" x2="272" y2="317" stroke="{c["cu"]}" stroke-width="0.5"/>
  <line x1="276" y1="312" x2="276" y2="317" stroke="{c["cu"]}" stroke-width="0.5"/>
  <line x1="280" y1="312" x2="280" y2="317" stroke="{c["cu"]}" stroke-width="0.5"/>

  <!-- ═══ PIN HEADERS (XBee socket + PIC programming) ═══ -->
  <!-- XBee socket header (2x10) -->
  <text x="221" y="257" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">XBee Socket</text>
  <!-- PIC ICSP header -->
  <rect x="350" y="295" width="8" height="28" rx="0.5" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.5"/>
  <rect x="351.5" y="298" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="351.5" y="304" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="351.5" y="310" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="351.5" y="316" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <text x="354" y="292" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">ICSP</text>

  <!-- ═══ STATUS LEDs (bottom-left, vertical row with labels) ═══ -->
  <text x="38" y="448" fill="{c["pcbRef"]}" font-size="3">STATUS</text>
  <circle cx="42" cy="458" r="2.5" fill="{c["grn"]}"><animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite"/></circle>
  <text x="50" y="461" fill="{c["pcbRef"]}" font-size="2.5">PWR</text>
  <circle cx="42" cy="470" r="2.5" fill="{c["blu"]}"><animate attributeName="opacity" values="0.1;1;0.1" dur="0.8s" repeatCount="indefinite"/></circle>
  <text x="50" y="473" fill="{c["pcbRef"]}" font-size="2.5">WiFi</text>
  <circle cx="42" cy="482" r="2.5" fill="{c["amb"]}"><animate attributeName="opacity" values="0.3;1;0.3" dur="1.5s" repeatCount="indefinite"/></circle>
  <text x="50" y="485" fill="{c["pcbRef"]}" font-size="2.5">MQTT</text>
  <circle cx="42" cy="494" r="2.5" fill="{c["red"]}" opacity="0.4"><animate attributeName="opacity" values="0.2;0.6;0.2" dur="3s" repeatCount="indefinite"/></circle>
  <text x="50" y="497" fill="{c["pcbRef"]}" font-size="2.5">ERR</text>
  <!-- Current-limiting resistors for LEDs -->
  <rect x="60" y="456" width="8" height="3.5" rx="0.3" fill="#2a2a2a" stroke="#555" stroke-width="0.3"/>
  <rect x="60" y="456" width="1.8" height="3.5" fill="{c["cu"]}"/><rect x="66.2" y="456" width="1.8" height="3.5" fill="{c["cu"]}"/>
  <rect x="60" y="468" width="8" height="3.5" rx="0.3" fill="#2a2a2a" stroke="#555" stroke-width="0.3"/>
  <rect x="60" y="468" width="1.8" height="3.5" fill="{c["cu"]}"/><rect x="66.2" y="468" width="1.8" height="3.5" fill="{c["cu"]}"/>
  <rect x="60" y="480" width="8" height="3.5" rx="0.3" fill="#2a2a2a" stroke="#555" stroke-width="0.3"/>
  <rect x="60" y="480" width="1.8" height="3.5" fill="{c["cu"]}"/><rect x="66.2" y="480" width="1.8" height="3.5" fill="{c["cu"]}"/>
  <rect x="60" y="492" width="8" height="3.5" rx="0.3" fill="#2a2a2a" stroke="#555" stroke-width="0.3"/>
  <rect x="60" y="492" width="1.8" height="3.5" fill="{c["cu"]}"/><rect x="66.2" y="492" width="1.8" height="3.5" fill="{c["cu"]}"/>

  <!-- ═══ BOTTOM ZONE: More passives + connectors ═══ -->
  <!-- Resistor array -->
  <rect x="100" y="450" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="100" y="450" width="2.5" height="5" fill="{c["cu"]}"/><rect x="109.5" y="450" width="2.5" height="5" fill="{c["cu"]}"/>
  <rect x="125" y="450" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="125" y="450" width="2.5" height="5" fill="{c["cu"]}"/><rect x="134.5" y="450" width="2.5" height="5" fill="{c["cu"]}"/>
  <rect x="150" y="450" width="12" height="5" rx="0.5" fill="#2a2a2a" stroke="#555" stroke-width="0.4"/>
  <rect x="150" y="450" width="2.5" height="5" fill="{c["cu"]}"/><rect x="159.5" y="450" width="2.5" height="5" fill="{c["cu"]}"/>

  <!-- More electrolytic caps -->
  <circle cx="200" cy="455" r="6" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>
  <line x1="196" y1="451" x2="204" y2="451" stroke="#3a3a5a" stroke-width="0.4"/>
  <text x="200" y="466" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">C7</text>
  <circle cx="225" cy="455" r="6" fill="#1a1a3a" stroke="#3a3a5a" stroke-width="0.6"/>
  <line x1="221" y1="451" x2="229" y2="451" stroke="#3a3a5a" stroke-width="0.4"/>
  <text x="225" y="466" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">C8</text>

  <!-- More diodes -->
  <polygon points="260,448 260,458 272,453" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="272" y1="448" x2="272" y2="458" stroke="{c["cu"]}" stroke-width="0.8"/>
  <polygon points="290,448 290,458 302,453" fill="none" stroke="{c["cu"]}" stroke-width="0.6"/>
  <line x1="302" y1="448" x2="302" y2="458" stroke="{c["cu"]}" stroke-width="0.8"/>

  <!-- Output screw terminal (bottom) -->
  <rect x="340" y="400" width="30" height="10" rx="1.5" fill="#1a5a2a" stroke="#2a7a3a" stroke-width="0.6"/>
  <rect x="343" y="402" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="345.5" cy="405" r="1.5" fill="#2a7a3a"/>
  <rect x="352" y="402" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="354.5" cy="405" r="1.5" fill="#2a7a3a"/>
  <rect x="361" y="402" width="5" height="6" rx="0.5" fill="#0a3a1a"/><circle cx="363.5" cy="405" r="1.5" fill="#2a7a3a"/>
  <text x="355" y="416" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">J4 OUT</text>

  <!-- Big pin header 2x5 (PIC connections) -->
  <rect x="340" y="445" width="20" height="35" rx="0.5" fill="{c["ic"]}" stroke="{c["icB"]}" stroke-width="0.5"/>
  <rect x="342" y="448" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="353" y="448" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="342" y="455" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="353" y="455" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="342" y="462" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="353" y="462" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <rect x="342" y="469" width="5" height="4" rx="0.3" fill="{c["cu"]}"/><rect x="353" y="469" width="5" height="4" rx="0.3" fill="{c["cu"]}"/>
  <text x="350" y="443" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">J5 PIC</text>

  <!-- USB connector (edge) -->
  <rect x="400" y="350" width="15" height="16" rx="2" fill="#555" stroke="#777" stroke-width="0.8"/>
  <rect x="403" y="353" width="8" height="10" rx="1" fill="#444"/>
  <text x="407" y="372" text-anchor="middle" fill="{c["pcbRef"]}" font-size="3">USB</text>

  <!-- ═══ UPY LOGO + silkscreen credits ═══ -->
  <circle cx="310" cy="480" r="12" fill="none" stroke="{c["tD"]}" stroke-width="0.5"/>
  <text x="310" y="478" text-anchor="middle" fill="{c["tD"]}" font-size="5" font-weight="bold">UPY</text>
  <text x="310" y="486" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">Merida, MX</text>
  <text x="215" y="502" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">— Jorge Blancas —</text>

  <!-- Test points -->
  <circle cx="385" cy="510" r="2.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.6"/>
  <text x="385" y="507" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">TP1</text>
  <circle cx="398" cy="510" r="2.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.6"/>
  <text x="398" y="507" text-anchor="middle" fill="{c["pcbRef"]}" font-size="2.5">TP2</text>
  <!-- Fiducials -->
  <circle cx="38" cy="518" r="1.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.4"/><circle cx="38" cy="518" r="0.5" fill="{c["mnt"]}"/>
  <circle cx="395" cy="265" r="1.5" fill="none" stroke="{c["mnt"]}" stroke-width="0.4"/><circle cx="395" cy="265" r="0.5" fill="{c["mnt"]}"/>

  <!-- Board rev + fab marks -->
  <text x="55" y="538" fill="{c["pcbRef"]}" font-size="3.5">REV 5.0 · JBC ELECTRONICS · MERIDA MX · LEAD-FREE · ROHS · 2829168A_V3</text>

  </g><!-- end PCB group -->

  </g><!-- end left column scaled -->

  <!-- ════════════ USB CABLE (PCB → Monitor) ════════════ -->

  <path d="M 315,250 C 328,250 338,250 348,250" stroke="{c["cable"]}" stroke-width="2" fill="none" stroke-linecap="round"/>
  <path d="M 315,250 C 328,250 338,250 348,250" stroke="url(#csig)" stroke-width="1.5" fill="none"/>

  <!-- ════════════ COMPUTER MONITOR ════════════ -->

  <!-- Bezel -->
  <rect x="340" y="8" width="600" height="{MON_H}" rx="8" fill="{c["mon"]}" stroke="{c["monB"]}" stroke-width="1.5"/>
  <!-- Webcam -->
  <circle cx="640" cy="16" r="2" fill="{c["monB"]}"/>
  <!-- Screen -->
  <rect x="350" y="22" width="580" height="{SCR_H}" rx="4" fill="{c["monScr"]}"/>
  <!-- Power LED -->
  <circle cx="640" cy="{SVG_H - 24}" r="2" fill="{c["grn"]}" opacity="0.4">
    <animate attributeName="opacity" values="0.2;0.5;0.2" dur="4s" repeatCount="indefinite"/>
  </circle>
  <!-- Stand -->
  <rect x="590" y="{SVG_H - 18}" width="100" height="6" rx="2" fill="{c["monB"]}"/>
  <rect x="618" y="{SVG_H - 12}" width="44" height="12" rx="2" fill="{c["mon"]}"/>

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
