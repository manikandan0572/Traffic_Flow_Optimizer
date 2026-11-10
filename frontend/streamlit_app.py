import streamlit as st
import requests
import pandas as pd
import random
import time
import base64

API_ENDPOINT = "https://traffic-flow-apii.onrender.com/predict"
HEALTH_ENDPOINT = "https://traffic-flow-apii.onrender.com/"

st.set_page_config(
    page_title="RL Traffic Flow Optimizer",
    page_icon=":traffic_light:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS — dark tech aesthetic ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden; height: 0px !important;}

[data-testid="stAppViewBlockContainer"], .block-container {
    padding-top: 2rem !important;
}

.stApp {
    background: #0a0e1a;
    background-image:
        radial-gradient(ellipse at 20% 50%, rgba(0, 255, 136, 0.03) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 149, 255, 0.04) 0%, transparent 50%);
}

[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #1e2d40 !important;
}

h1 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #00ff88 !important;
    letter-spacing: -0.5px;
    margin-bottom: 0.5rem !important;
    margin-top: 0 !important;
}

.stAlert {
    background: rgba(0, 149, 255, 0.05) !important;
    border: 1px solid rgba(0, 149, 255, 0.2) !important;
    border-radius: 8px !important;
    color: #8ab4d4 !important;
    font-size: 0.85rem !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1117 0%, #111827 100%);
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 1.2rem 1.5rem !important;
    transition: border-color 0.2s ease;
}
[data-testid="stMetric"]:hover { border-color: #00ff88; }
[data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #4a6b8a !important;
}
[data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: #e2e8f0 !important;
}
[data-testid="stMetricDelta"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #00ff88, #00cfff) !important;
    color: #0a0e1a !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 20px rgba(0, 255, 136, 0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 0 30px rgba(0, 255, 136, 0.4) !important;
}

.stButton > button:not([kind="primary"]) {
    background: transparent !important;
    border: 1px solid #1e2d40 !important;
    color: #4a6b8a !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
    border-color: #00ff88 !important;
    color: #00ff88 !important;
}

.phase-display {
    background: linear-gradient(135deg, #0d1117, #111827);
    border: 1px solid #1e2d40;
    border-left: 3px solid #00ff88;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    margin: 0.5rem 0 1rem 0;
    font-family: 'JetBrains Mono', monospace;
}
.phase-step {
    font-size: 0.7rem;
    color: #4a6b8a;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.phase-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #00ff88;
}
.phase-timer {
    font-size: 0.75rem;
    color: #4a6b8a;
    margin-top: 0.2rem;
}

.efficiency-box {
    background: linear-gradient(135deg, rgba(0,255,136,0.05), rgba(0,207,255,0.05));
    border: 1px solid rgba(0, 255, 136, 0.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
}
.efficiency-title {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #00ff88;
    margin-bottom: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
}
.efficiency-stats {
    display: flex;
    gap: 2rem;
    flex-wrap: wrap;
    align-items: center;
}
.eff-stat { text-align: center; }
.eff-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
}
.eff-label {
    font-size: 0.65rem;
    color: #4a6b8a;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.2rem;
}

hr { border-color: #1e2d40 !important; margin: 1.5rem 0 !important; }

[data-testid="stExpander"] {
    background: #0d1117 !important;
    border: 1px solid #1e2d40 !important;
    border-radius: 8px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1e2d40 !important;
    border-radius: 8px !important;
}

[data-testid="stSlider"] > div > div { color: #00ff88 !important; }

.stSelectbox > div > div {
    background: #0d1117 !important;
    border-color: #1e2d40 !important;
    color: #e2e8f0 !important;
}

[data-testid="stToggle"] > label { color: #8ab4d4 !important; }

h3 {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #4a6b8a !important;
    margin-bottom: 0.8rem !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] li {
    font-size: 0.82rem !important;
    color: #4a6b8a !important;
    line-height: 1.6 !important;
}
[data-testid="stSidebar"] strong { color: #8ab4d4 !important; }
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #e2e8f0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}

.stSuccess {
    background: rgba(0, 255, 136, 0.05) !important;
    border: 1px solid rgba(0, 255, 136, 0.2) !important;
    color: #00ff88 !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Phase config ──────────────────────────────────────────────────────────────
phase_names = {
    0: "North-South (Straight)",
    1: "East-West (Straight)",
    2: "North-South (Left Turn)",
    3: "East-West (Left Turn)"
}
phase_colors = {0: "#00ff88", 1: "#00cfff", 2: "#7b61ff", 3: "#ff6b6b"}

# ── Initialize session state ──────────────────────────────────────────────────
if "sim_step" not in st.session_state:
    st.session_state.sim_step = 0
    init_queues = [float(random.randint(2, 5)) for _ in range(4)]
    st.session_state.sim_queues = init_queues.copy()
    st.session_state.sim_fixed_queues = init_queues.copy()
    st.session_state.sim_active_phase = 0
    st.session_state.sim_total_routed = 0
    st.session_state.sim_time_on_phase = 0
    st.session_state.sim_rl_history = [sum(init_queues)]
    st.session_state.sim_fixed_history = [sum(init_queues)]
    st.session_state.sim_table_data = []
    st.session_state.sim_prev_total_queue = sum(init_queues)
    st.session_state.sim_prev_avg_queue = sum(init_queues)
    st.session_state.sim_queue_sum_accumulator = sum(init_queues)
    st.session_state.sim_fixed_queue_sum = sum(init_queues)

if "auto_target_step" not in st.session_state:
    st.session_state.auto_target_step = 0

# ── ADDITION 1: Silent Render API warm-up ping on first page load ─────────────────
if "api_warmed" not in st.session_state:
    st.session_state.api_warmed = False
    try:
        requests.get(HEALTH_ENDPOINT, timeout=120)
        st.session_state.api_warmed = True
    except Exception:
        st.session_state.api_warmed = False

if st.session_state.get("sim_show_reset_msg", False):
    st.success("Simulation reset. Click Step Forward to begin.")
    st.session_state.sim_show_reset_msg = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚦 Controls")

    if st.button(" Reset Simulation"):
        for key in list(st.session_state.keys()):
            if key.startswith("sim_") or key == "auto_target_step":
                del st.session_state[key]
        st.session_state.sim_show_reset_msg = True
        st.rerun()

    st.markdown("---")
    st.markdown("### Auto-Run")

    auto_steps = st.slider(
        "Steps to run",
        min_value=5,
        max_value=100,
        value=20,
        step=5,
        help="Number of steps to run automatically"
    )
    auto_speed = st.select_slider(
        "Speed",
        options=["Slow", "Medium", "Fast"],
        value="Medium"
    )
    speed_map = {"Slow": 1.0, "Medium": 0.6, "Fast": 0.3}

    is_running = st.session_state.sim_step < st.session_state.get("auto_target_step", 0)

    if is_running:
        if st.button("Stop Auto-Run", use_container_width=True):
            st.session_state.auto_target_step = st.session_state.sim_step
            st.rerun()
    else:
        if st.button("Start Auto-Run", type="primary", use_container_width=True):
            st.session_state.auto_target_step = st.session_state.sim_step + auto_steps
            st.rerun()

    st.markdown("---")
    st.markdown("### About")
    st.markdown("PPO-trained RL agent controlling a 4-way intersection in real time.")
    st.markdown("**Model:** PPO · Stable-Baselines3")
    st.markdown("**Env:** Custom Gymnasium")
    st.markdown("**Deploy:** Render · FastAPI")
    st.markdown("**Frontend:** Streamlit · Streamlit Cloud")

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("""
- Agent observes queue lengths across all 4 lanes
- Selects optimal signal phase each step
- Trained to minimize total wait time
- Compare against fixed 30s cycle timer
    """)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🚦 Autonomous Traffic Flow Optimizer")
st.info("The RL agent was trained using PPO (Proximal Policy Optimization) on a custom Gymnasium environment. At each step, it observes queue lengths across all 4 lanes and decides which signal phase minimizes total wait time — unlike fixed timers that cycle blindly regardless of traffic.")

# ── ADDITION 3: Cold start notice — only shown on step 0 ─────────────────────
if st.session_state.sim_step == 0:
    warmed = st.session_state.get("api_warmed", False)
    if warmed:
        st.markdown("""
        <div style="
            background: rgba(0,255,136,0.04);
            border: 1px solid rgba(0,255,136,0.15);
            border-left: 3px solid #00ff88;
            border-radius: 8px;
            padding: 0.65rem 1rem;
            font-size: 0.8rem;
            color: #6fcfa0;
            margin-bottom: 0.5rem;
        ">
            ✅ <strong style="color:#00ff88">Render API is ready</strong> — 
            Cloud inference container loaded and ready. 
            First step will respond quickly. ⚡
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background: rgba(123,97,255,0.06);
            border: 1px solid rgba(123,97,255,0.2);
            border-left: 3px solid #7b61ff;
            border-radius: 8px;
            padding: 0.65rem 1rem;
            font-size: 0.8rem;
            color: #a89be8;
            margin-bottom: 0.5rem;
        ">
            <strong style="color:#7b61ff">Heads up:</strong>
            This app runs on <strong>Render API</strong> infrastructure.
            The <strong>first Step Forward</strong> may take 5–15 seconds
            while the cloud container cold-starts.
            Subsequent steps will be near-instant. ⚡
        </div>
        """, unsafe_allow_html=True)

# ── API status placeholder ────────────────────────────────────────────────────
api_status = st.empty()

# ── Metric cards ──────────────────────────────────────────────────────────────
current_total = sum(st.session_state.sim_queues)
avg_queue = st.session_state.sim_queue_sum_accumulator / max(1, st.session_state.sim_step + 1)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Cars Routed", int(st.session_state.sim_total_routed))
with col2:
    st.metric(
        "Current Total Queue",
        int(current_total),
        delta=int(current_total - st.session_state.sim_prev_total_queue),
        delta_color="inverse"
    )
with col3:
    st.metric(
        "Avg Queue Per Step",
        f"{avg_queue:.1f}",
        delta=f"{avg_queue - st.session_state.sim_prev_avg_queue:.1f}",
        delta_color="inverse"
    )
with col4:
    st.metric("Simulation Step", st.session_state.sim_step)

st.markdown("---")

# ── Intersection diagram + phase display ─────────────────────────────────────
left_col, right_col = st.columns([1, 1.5])

with left_col:
    phase = st.session_state.sim_active_phase
    colors = ["#1e2d40", "#1e2d40", "#1e2d40", "#1e2d40"]
    colors[phase] = phase_colors[phase]
    road_color = "#1a2332"

    fill0 = "#0a0e1a" if phase == 0 else "#2a3f55"
    fill1 = "#0a0e1a" if phase == 1 else "#2a3f55"
    fill2 = "#0a0e1a" if phase == 2 else "#2a3f55"
    fill3 = "#0a0e1a" if phase == 3 else "#2a3f55"
    glow_color = phase_colors[phase]

    svg = f"""
    <svg width="220" height="220" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <rect width="200" height="200" fill="#0d1117" rx="12"/>
      <rect x="80" y="0" width="40" height="200" fill="{road_color}"/>
      <rect x="0" y="80" width="200" height="40" fill="{road_color}"/>
      <rect x="80" y="80" width="40" height="40" fill="{road_color}"/>
      <line x1="100" y1="0" x2="100" y2="75" stroke="#2a3f55" stroke-width="1" stroke-dasharray="6,4"/>
      <line x1="100" y1="125" x2="100" y2="200" stroke="#2a3f55" stroke-width="1" stroke-dasharray="6,4"/>
      <line x1="0" y1="100" x2="75" y2="100" stroke="#2a3f55" stroke-width="1" stroke-dasharray="6,4"/>
      <line x1="125" y1="100" x2="200" y2="100" stroke="#2a3f55" stroke-width="1" stroke-dasharray="6,4"/>
      <rect x="83" y="4" width="14" height="70" fill="{colors[0]}" rx="3" opacity="0.8"/>
      <rect x="83" y="126" width="14" height="70" fill="{colors[0]}" rx="3" opacity="0.8"/>
      <text x="90" y="44" text-anchor="middle" fill="{fill0}" font-size="14" font-weight="bold">&#x2191;</text>
      <text x="90" y="170" text-anchor="middle" fill="{fill0}" font-size="14" font-weight="bold">&#x2193;</text>
      <rect x="4" y="83" width="70" height="14" fill="{colors[1]}" rx="3" opacity="0.8"/>
      <rect x="126" y="83" width="70" height="14" fill="{colors[1]}" rx="3" opacity="0.8"/>
      <text x="40" y="93" text-anchor="middle" fill="{fill1}" font-size="14" font-weight="bold">&#x2190;</text>
      <text x="162" y="93" text-anchor="middle" fill="{fill1}" font-size="14" font-weight="bold">&#x2192;</text>
      <rect x="97" y="4" width="14" height="70" fill="{colors[2]}" rx="3" opacity="0.8"/>
      <rect x="97" y="126" width="14" height="70" fill="{colors[2]}" rx="3" opacity="0.8"/>
      <text x="104" y="44" text-anchor="middle" fill="{fill2}" font-size="12" font-weight="bold">&#x21B0;</text>
      <text x="104" y="170" text-anchor="middle" fill="{fill2}" font-size="12" font-weight="bold">&#x21B1;</text>
      <rect x="4" y="97" width="70" height="14" fill="{colors[3]}" rx="3" opacity="0.8"/>
      <rect x="126" y="97" width="70" height="14" fill="{colors[3]}" rx="3" opacity="0.8"/>
      <text x="40" y="108" text-anchor="middle" fill="{fill3}" font-size="12" font-weight="bold">&#x21B2;</text>
      <text x="162" y="108" text-anchor="middle" fill="{fill3}" font-size="12" font-weight="bold">&#x21B3;</text>
      <text x="90" y="15" text-anchor="middle" fill="#e2e8f0" font-size="9" font-family="monospace">{int(st.session_state.sim_queues[0])}</text>
      <text x="90" y="192" text-anchor="middle" fill="#e2e8f0" font-size="9" font-family="monospace">{int(st.session_state.sim_queues[0])}</text>
      <text x="12" y="97" text-anchor="middle" fill="#e2e8f0" font-size="9" font-family="monospace">{int(st.session_state.sim_queues[1])}</text>
      <text x="188" y="97" text-anchor="middle" fill="#e2e8f0" font-size="9" font-family="monospace">{int(st.session_state.sim_queues[1])}</text>
      <rect x="82" y="82" width="36" height="36" fill="none"
            stroke="{glow_color}" stroke-width="2" rx="4" opacity="0.6"/>
      <circle cx="100" cy="100" r="6" fill="{glow_color}" opacity="0.9"/>
    </svg>
    """

    b64_svg = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    img_tag = f'<img src="data:image/svg+xml;base64,{b64_svg}" width="220" alt="Intersection Diagram" />'
    st.markdown(f'<div style="display:flex;justify-content:center">{img_tag}</div>', unsafe_allow_html=True)

with right_col:
    color = phase_colors[st.session_state.sim_active_phase]
    st.markdown(f"""
    <div class="phase-display" style="border-left-color: {color}">
        <div class="phase-step">Step {st.session_state.sim_step} · Active Signal</div>
        <div class="phase-name" style="color: {color}">● {phase_names[st.session_state.sim_active_phase]}</div>
        <div class="phase-timer">⏱ {st.session_state.sim_time_on_phase * 5} seconds on current phase</div>
    </div>
    """, unsafe_allow_html=True)

    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    q_col1.metric("N-S Straight", int(st.session_state.sim_queues[0]))
    q_col2.metric("E-W Straight", int(st.session_state.sim_queues[1]))
    q_col3.metric("N-S Left", int(st.session_state.sim_queues[2]))
    q_col4.metric("E-W Left", int(st.session_state.sim_queues[3]))

    btn_col1, btn_col2 = st.columns([1, 3])
    with btn_col1:
        step_clicked = st.button(" Step Forward", type="primary", use_container_width=True)

# ── Step execution function ───────────────────────────────────────────────────
def execute_step():
    arrivals = [
        int(random.random() < 0.8) + int(random.random() < 0.8),
        int(random.random() < 0.8) + int(random.random() < 0.8),
        int(random.random() < 0.3) + int(random.random() < 0.3),
        int(random.random() < 0.3) + int(random.random() < 0.3)
    ]

    queues_after_arrivals = [q + a for q, a in zip(st.session_state.sim_queues, arrivals)]

    payload = {
        "queues": queues_after_arrivals,
        "current_phase": st.session_state.sim_active_phase,
        "time_on_phase": st.session_state.sim_time_on_phase
    }

    # ── ADDITION 2: Informative status message during API call ─────────────
    with api_status:
        st.markdown("""
        <div style="
            background: rgba(0,207,255,0.05);
            border: 1px solid rgba(0,207,255,0.2);
            border-radius: 8px;
            padding: 0.55rem 1rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.76rem;
            color: #00cfff;
        ">
             &nbsp;<strong>Calling Render API</strong>
            &nbsp;·&nbsp; Serverless inference running on Render
            &nbsp;·&nbsp; Cold start may take 5–10s on first call
        </div>
        """, unsafe_allow_html=True)

        try:
            response = requests.post(API_ENDPOINT, json=payload, timeout=120)
            if response.status_code == 200:
                rl_phase = response.json().get("phase", 0)
            else:
                rl_phase = st.session_state.sim_active_phase
        except Exception:
            rl_phase = st.session_state.sim_active_phase

    # Clear the status message after response received
    api_status.empty()

    if rl_phase == st.session_state.sim_active_phase:
        st.session_state.sim_time_on_phase += 1
    else:
        st.session_state.sim_time_on_phase = 1

    st.session_state.sim_active_phase = rl_phase

    rl_departures = min(queues_after_arrivals[rl_phase], 3)
    queues_after_arrivals[rl_phase] -= rl_departures
    st.session_state.sim_queues = queues_after_arrivals
    st.session_state.sim_total_routed += rl_departures

    fixed_phase = (st.session_state.sim_step // 3) % 4
    fixed_queues_after = [q + a for q, a in zip(st.session_state.sim_fixed_queues, arrivals)]
    fixed_departures = min(fixed_queues_after[fixed_phase], 3)
    fixed_queues_after[fixed_phase] -= fixed_departures
    st.session_state.sim_fixed_queues = fixed_queues_after

    st.session_state.sim_step += 1
    new_total = sum(st.session_state.sim_queues)
    new_fixed_total = sum(st.session_state.sim_fixed_queues)

    st.session_state.sim_rl_history.append(new_total)
    st.session_state.sim_fixed_history.append(new_fixed_total)

    st.session_state.sim_prev_total_queue = current_total
    st.session_state.sim_prev_avg_queue = avg_queue
    st.session_state.sim_queue_sum_accumulator += new_total
    st.session_state.sim_fixed_queue_sum = (
        st.session_state.get("sim_fixed_queue_sum", new_fixed_total) + new_fixed_total
    )

    step_record = {
        "Step": st.session_state.sim_step,
        "Active Signal": phase_names[rl_phase],
        "N-S Queue": int(st.session_state.sim_queues[0]),
        "E-W Queue": int(st.session_state.sim_queues[1]),
        "N-S Left Queue": int(st.session_state.sim_queues[2]),
        "E-W Left Queue": int(st.session_state.sim_queues[3]),
        "Total Queue": int(new_total),
        "Cars Routed This Step": int(rl_departures)
    }
    st.session_state.sim_table_data.append(step_record)

# ── Handle step button ────────────────────────────────────────────────────────
if step_clicked:
    execute_step()
    st.rerun()

# ── Efficiency summary ────────────────────────────────────────────────────────
rl_avg = st.session_state.sim_queue_sum_accumulator / max(1, st.session_state.sim_step + 1)
fixed_sum = sum(st.session_state.sim_fixed_history)
fixed_avg = fixed_sum / max(1, len(st.session_state.sim_fixed_history))

# Calculate efficiency percentage
efficiency_pct = ((fixed_avg - rl_avg) / fixed_avg) * 100 if fixed_avg > 0 else 0.0

if st.session_state.sim_step == 0:
    winner_text = "– Simulation Ready"
    winner_color = "#4a6b8a"
    efficiency_label = "Waiting for data..."
else:
    # State 1: RL Agent is strictly better
    if efficiency_pct > 0:
        winner_text = "✓ RL Agent Winning"
        winner_color = "#00ff88"
        efficiency_label = f"{abs(efficiency_pct):.1f}% more efficient than Fixed Timer"
        
    # State 2: Completely tied
    elif efficiency_pct == 0:
        winner_text = "⚖ Tied"
        winner_color = "#4a6b8a"
        efficiency_label = "Tied. Run more steps to see a variance difference."
        
    # State 3: Fixed timer is better
    else:
        winner_text = "⚠ Fixed Timer Leading"
        winner_color = "#ff6b6b"
        efficiency_label = f"{abs(efficiency_pct):.1f}% less efficient than Fixed Timer"

st.markdown(f"""
<div class="efficiency-box">
    <div class="efficiency-title">⚡ Live Performance Summary</div>
    <div class="efficiency-stats">
        <div class="eff-stat">
            <div class="eff-val" style="color:#00ff88">{rl_avg:.1f}</div>
            <div class="eff-label">RL Agent Avg Queue</div>
        </div>
        <div class="eff-stat">
            <div class="eff-val" style="color:#4a6b8a">{fixed_avg:.1f}</div>
            <div class="eff-label">Fixed Timer Avg Queue</div>
        </div>
        <div class="eff-stat">
            <div class="eff-val" style="color:#00cfff">{st.session_state.sim_total_routed}</div>
            <div class="eff-label">Total Cars Cleared</div>
        </div>
        <div class="eff-stat">
            <div class="eff-val" style="color:#7b61ff">{st.session_state.sim_step}</div>
            <div class="eff-label">Steps Completed</div>
        </div>
        <div class="eff-stat">
            <div class="eff-val" style="color:{winner_color};font-size:0.95rem">{winner_text}</div>
            <div class="eff-label">{efficiency_label}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Comparison chart ──────────────────────────────────────────────────────────
st.markdown("### 📈 RL Agent vs Fixed Timer — Total Queue Length Over Time")
chart_df = pd.DataFrame({
    "RL Agent": st.session_state.sim_rl_history,
    "Fixed Timer": st.session_state.sim_fixed_history
})
st.line_chart(chart_df, use_container_width=True)

st.markdown("---")

# ── Step history table ────────────────────────────────────────────────────────
with st.expander("📋 Step-by-Step History", expanded=False):
    if st.session_state.sim_table_data:
        history_df = pd.DataFrame(st.session_state.sim_table_data)
        st.dataframe(history_df.iloc[::-1], use_container_width=True, hide_index=True)
    else:
        st.markdown(
            "<p style='color:#4a6b8a;font-size:0.85rem'>No steps taken yet. Click Step Forward to begin.</p>",
            unsafe_allow_html=True
        )

# ── Auto-run execution loop ───────────────────────────────────────────────────
if st.session_state.sim_step < st.session_state.get("auto_target_step", 0):
    steps_left = st.session_state.auto_target_step - st.session_state.sim_step

    # Toast on very first auto-run step only
    if steps_left == auto_steps:
        st.toast(" First step may be slow — Render API waking up!", icon="⚡")

    st.caption(f" **Auto-running...** {steps_left} steps remaining — metrics updating live")
    execute_step()
    time.sleep(speed_map[auto_speed])
    st.rerun()
