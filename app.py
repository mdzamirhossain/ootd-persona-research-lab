"""OOTD Persona Research Lab — Streamlit marketing coursework application.

Launch from VS Code terminal:
    python -m pip install -r requirements.txt
    python -m streamlit run app.py

Interactive interviews run ONLY through a local Ollama model.
Fictional customers describe their needs; OOTD is the proposed solution.
"""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

import streamlit as st

from persona_data import (
    GROUP_ASSUMPTIONS, PERSONAS, PROJECT, QUESTION_BANK, RECOMMENDATIONS,
    SOURCE_MAP, NEED_TO_FEATURE,
)
from persona_engine import (build_system_prompt, classify_question, get_reply,
                            ollama_connection_info)
from reporting import counts_for, report_markdown, sample_interviews, thematic_rows, to_csv, to_json

ROOT = Path(__file__).resolve().parent
ENGINE_LABEL = "Ollama (local AI)"


def initialise() -> None:
    st.session_state.setdefault("interviews", {key: [] for key in PERSONAS})
    st.session_state.setdefault("selected_persona", "siraj")
    st.session_state.setdefault("selected_decisions", {choice: False for choice in RECOMMENDATIONS})
    for key, persona in PERSONAS.items():
        st.session_state.setdefault(f"notes_{key}", persona["human_design_note"])
        st.session_state.setdefault(f"reviewed_{key}", False)
    st.session_state.setdefault("group_input", "")


def human_notes() -> dict[str, str]:
    return {p: st.session_state[f"notes_{p}"] for p in PERSONAS}


def review_flags() -> dict[str, bool]:
    return {p: st.session_state[f"reviewed_{p}"] for p in PERSONAS}


def get_history(persona_id: str) -> list[dict[str, str]]:
    out = []
    for row in st.session_state["interviews"].get(persona_id, []):
        out.extend([
            {"role": "user", "content": row["question"]},
            {"role": "assistant", "content": row["answer"]},
        ])
    return out


def interview_once(persona_id: str, question: str, model: str) -> bool:
    try:
        with st.spinner(f"Interviewing {PERSONAS[persona_id]['first_name']}…"):
            response = get_reply(
                persona_id=persona_id, question=question,
                history=get_history(persona_id), model=model,
                team_notes=st.session_state[f"notes_{persona_id}"],
            )
        st.session_state["interviews"][persona_id].append({
            "question": question.strip(), "answer": response,
            "topic": classify_question(question), "mode": f"Ollama local AI · {model}",
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        return True
    except Exception as error:
        st.error(f"No response was saved: {error}")
        return False


def render_persona_card(persona_id: str, show_edit: bool = False) -> None:
    persona = PERSONAS[persona_id]
    with st.container(border=True):
        st.image(str(ROOT / persona["portrait"]), use_container_width=True)
        st.markdown(f"### {persona['name']} <span style='color:#9d7bff'>· {persona['age']}</span>",
                    unsafe_allow_html=True)
        st.caption(f"{persona['role']} · {persona['location']}")
        st.markdown(f"**{persona['segment']}**")
        st.markdown(f"<div class='quote'>“{escape(persona['quote'])}”</div>",
                    unsafe_allow_html=True)
        if persona.get("personality"):
            st.markdown("**Personality**")
            for trait in persona["personality"][:3]:
                st.markdown(f"<div class='tiny-bullet'>• {escape(trait)}</div>", unsafe_allow_html=True)
        st.markdown("**What matters to this persona**")
        for goal in persona["feature_priority"][:3]:
            st.markdown(f"<div class='tiny-bullet'>✦ {escape(goal)}</div>", unsafe_allow_html=True)
        if show_edit:
            with st.expander("Full persona profile", expanded=True):
                st.write(persona["bio"])
                if persona.get("personality"):
                    st.markdown("**Personality traits**")
                    for x in persona["personality"]:
                        st.markdown(f"- {x}")
                st.markdown("**Goals**")
                for x in persona["goals"]:
                    st.markdown(f"- {x}")
                st.markdown("**Pain points**")
                for x in persona["pains"]:
                    st.markdown(f"- {x}")
                st.markdown("**Behaviour and style**")
                for x in persona["behaviour"]:
                    st.markdown(f"- {x}")
                st.write(f"**Style:** {persona['style']}")
                if persona.get("lifestyle"):
                    st.write(f"**Lifestyle:** {persona['lifestyle']}")
                if persona.get("relationship_status"):
                    st.write(f"**Living situation:** {persona['relationship_status']}")
                st.write(f"**Budget:** {persona['budget']}")
                st.write(f"**Buying trigger:** {persona['buying_trigger']}")
                st.write(f"**Deal-breaker:** {persona['deal_breaker']}")
                st.write(f"**Price opinion (hypothetical):** {persona['pricing_view']}")
                st.write(f"**Subscription view:** {persona['subscription_view']}")
                st.write(f"**Privacy concern:** {persona['privacy_view']}")
            st.markdown("**Human team input**")
            st.text_area("Edit the team's assumptions, nuances or corrections",
                         key=f"notes_{persona_id}", height=132)
            st.checkbox("A human group member has reviewed and approved this profile",
                        key=f"reviewed_{persona_id}")


def html_metric(title: str, value: str, subtitle: str) -> str:
    return ("<div class='metric-tile'>"
            f"<span class='metric-label'>{escape(title)}</span>"
            f"<div class='metric-value'>{escape(value)}</div>"
            f"<span class='metric-small'>{escape(subtitle)}</span>"
            "</div>")


st.set_page_config(
    page_title="OOTD · Persona Research Lab", page_icon="🌈",
    layout="wide", initial_sidebar_state="expanded",
)
initialise()
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Outfit:wght@500;600;700;800&display=swap');
:root { color-scheme: dark; }
[data-testid="stAppViewContainer"] { background: radial-gradient(ellipse at 60% 0%, #211b47 0%, #101323 42%, #0b101c 100%); }
[data-testid="stSidebar"] { background: linear-gradient(166deg,#161b33 0%,#12152a 70%,#271a50 100%); border-right:1px solid #363b59; }
[data-testid="stHeader"] { background:transparent; }
[data-testid="stToolbar"] {visibility:hidden;}
.block-container {padding-top: 2.1rem !important; max-width: 1440px;}
html, body, [class*="css"], [data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"] {font-family:'DM Sans', sans-serif;}
h1,h2,h3 {font-family:'Outfit', sans-serif !important; letter-spacing:-.025em;}
h1 {font-weight:800 !important; font-size:clamp(2.1rem,3.3vw,3.45rem) !important; line-height:1.14 !important;}
h3 {color:#f4f2ff !important;}
.stButton>button[kind="primary"] { background:linear-gradient(110deg,#8b4bf5,#5c43d3); border:none; color:white; font-weight:700; box-shadow:0 8px 30px #6a45f335; }
.stButton>button {border-radius:13px; min-height:39px; border:1px solid #505275; transition:.2s;}
.stButton>button:hover {border-color:#9d7fff; color:#f8f5ff; transform:translateY(-1px);}
[data-testid="stVerticalBlockBorderWrapper"] {background:#181c33aa; border-color:#353953 !important; border-radius:18px;}
[data-baseweb="tab-list"] {gap:12px; padding: 6px 0 12px;}
button[data-baseweb="tab"] {font-weight:700; font-size:.9rem; border-radius:10px;}
[data-testid="stChatMessage"] {background:#1a1e34; border:1px solid #363a57; border-radius:18px; padding:.45rem 1rem; margin-bottom:.5rem;}
[data-testid="stChatInput"] {border-radius:15px;}
[data-testid="stExpander"] {border-color:#3c3e5e; background:#161a2caa; border-radius:13px;}
[data-testid="stImage"] img {border-radius:13px;}
small, .stCaption {color:#b5b9d6!important;}
.hero {position:relative; padding:30px 35px; border-radius:22px; margin-bottom:22px; background:linear-gradient(115deg,rgba(80,71,171,.68),rgba(91,52,155,.44) 45%,rgba(25,32,63,.95)), radial-gradient(circle at 85% 55%,rgba(197,87,248,.35),transparent 38%); border:1px solid #69618e; box-shadow:0 16px 45px #0004;}
.hero h1 {color:#fff; margin:0 0 .35rem;}
.hero .kicker {font-size:12px; color:#d2bbff; text-transform:uppercase; letter-spacing:.15em; font-weight:800;}
.hero p {color:#d9dbef; max-width:790px; font-size:1.05rem; line-height:1.6; margin:.6rem 0 0;}
.purple {color:#bb86ff;}
.quote {border-left:3px solid #9c72ff; padding:10px 13px; border-radius:0 12px 12px 0; background:#292646; color:#e5d9ff; font-size:.95rem; margin:.8rem 0;}
.tiny-bullet {padding: 4px 0; color:#cbd0e8; font-size:.92rem;}
.metric-tile {background:linear-gradient(145deg,#212540c9,#161a2e); border:1px solid #3a3f64; padding:18px 22px; border-radius:16px; margin-bottom:12px; min-height:132px;}
.metric-label {color:#b4acd5; font-size:.77rem; letter-spacing:.06em; text-transform:uppercase; font-weight:800;}
.metric-value {font-size:1.55rem; font-weight:800; color:white; margin-top:.45rem; font-family:'Outfit',sans-serif;}
.metric-small {font-size:.76rem; color:#bfc6e6;}
.section-intro {color:#c5cae4; padding-bottom:4px; line-height:1.65;}
.research-box {padding:16px 19px; background:#19253b; border-left:3px solid #43b9c9; border-radius:12px; margin:12px 0;}
.soft-label {background:#252348; display:inline-block; border-radius:50px; padding:5px 12px; font-size:.76rem; color:#cfc2ff; font-weight:700; letter-spacing:.02em;}
.sidebar-brand {font-family:'Outfit'; font-size:2.3rem; font-weight:800; text-align:center; color:white; margin:-15px 0 -4px;}
.sidebar-tag {font-size:.9rem; color:#b187ff; text-align:center; font-style:italic; margin-bottom:1.3rem;}
.footer-note {border-top:1px solid #383a54; margin-top:2.5rem; padding-top:1.2rem; font-size:.78rem; color:#a5acc8;}
@media (max-width: 720px) {.hero {padding:22px 20px;}.block-container {padding-left:1rem;padding-right:1rem}}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image(str(ROOT / "assets/ootd_badge.png"), width=122)
    st.markdown("<div class='sidebar-brand'>ootd</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-tag'>style meets the forecast</div>", unsafe_allow_html=True)
    st.caption("MARKETING · PERSONA RESEARCH")
    st.markdown("---")
    st.markdown("#### Local AI interview engine")
    st.markdown("**Ollama only — no cloud AI key required**")
    model = st.text_input("Local model name", value="llama3.2",
                          help="Use a name shown by `ollama list`, e.g. llama3.2 or llama3.2:1b")
    if st.button("↻ Check Ollama connection", use_container_width=True):
        st.rerun()
    connected, downloaded_models, connection_message = ollama_connection_info()
    if connected:
        st.success(connection_message)
        if downloaded_models:
            st.caption("Installed models: " + ", ".join(downloaded_models[:8]))
        if not any((name == model or name.split(":")[0] == model.split(":")[0])
                   for name in downloaded_models):
            st.warning(f"Model '{model}' may be missing. Download it using the command below.")
    else:
        st.warning("Ollama is not running on this computer.")
    with st.expander("Ollama installation and startup"):
        st.markdown("1. Install Ollama from https://ollama.com/download/mac and open the app.\n"
                    "2. In Terminal, download the model once:\n")
        st.code("ollama pull llama3.2", language="bash")
        st.markdown("3. Check which models are installed:")
        st.code("ollama list", language="bash")
        st.caption("If the app is not serving requests, run `ollama serve` "
                   "in a separate terminal. Leave it running while interviewing.")
        if not connected:
            st.caption(connection_message)
    st.markdown("---")
    st.markdown("**Research context**")
    st.caption("🇩🇪 Germany pilot · ages 16–30 in the group market study")
    st.caption("2 fictional personas · 18 guided interview questions")
    st.caption("Original OOTD brand assets and research included in the project ZIP")
    st.markdown("---")
    st.warning("All persona interviews are simulated, not actual customer evidence.", icon="⚠️")

st.markdown("""
<div class="hero">
  <div class="kicker">✦ University marketing project · Germany pilot</div>
  <h1>Meet the people behind <span class="purple">OOTD</span></h1>
</div>
""", unsafe_allow_html=True)

overview, personas_tab, interview_tab, findings_tab, sources_tab = st.tabs([
    "✦ Overview", "♙ Personas", "◉ Interview bots", "▥ Findings & export", "ⓘ Research methods",
])

with overview:
    st.subheader("Your persona research workspace")
    cols = st.columns(4)
    m = [
        ("CUSTOMER PROFILES", "02", "Contrasting segments"),
        ("GUIDED QUESTIONS", str(sum(map(len, QUESTION_BANK.values()))), "Includes price, privacy and business model"),
        ("RECORDED ANSWERS", str(sum(counts_for(st.session_state['interviews']).values())), "Synthetic Q&A pairs"),
        ("PRODUCT PRICE", "€3.99", "Example monthly premium; not validated"),
    ]
    for col, (label, value, desc) in zip(cols, m):
        with col:
            st.markdown(html_metric(label, value, desc), unsafe_allow_html=True)
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown("### The OOTD proposition")
        st.markdown(f"<p class='section-intro'>{escape(PROJECT['concept'])}</p>", unsafe_allow_html=True)
        st.markdown("**Proposed customer journey**")
        st.markdown("1. Onboard with a style profile and a few garment photos.\n"
                    "2. Receive a look based on local weather and the occasion.\n"
                    "3. Swap pieces, give feedback and optionally save the look.\n"
                    "4. Explore weekly planning or destination packing as potential premium value.")
        st.info("Siraj and Amina are interview personas who describe their own problems and requirements. OOTD is the proposed product that could fulfill those needs. This application interviews customers; it is not the consumer outfit-styling app.")
    with right:
        st.markdown("### The professor's six requirements")
        requirements = [
            ("01", "Two detailed customer personas", "Profiles with distinct goals, budgets and objections"),
            ("02", "Human-first thinking", "Editable team notes and explicit review confirmation"),
            ("03", "Persona images", "Two generated fictional portrait images"),
            ("04", "Reusable persona bots", "Consistent fictional customers powered by local Ollama"),
            ("05", "Structured bot interviews", "Features, model, pricing, subscriptions and preferences"),
            ("06", "Document every step", "Prompts, questions, responses, decisions and sources export"),
        ]
        for num, label, detail in requirements:
            st.markdown(f"**<span class='purple'>{num}</span> · {label}**  ", unsafe_allow_html=True)
            st.caption(detail)
    st.markdown("### Meet your two interview scenarios")
    ca, cb = st.columns(2, gap="large")
    with ca: render_persona_card("siraj")
    with cb: render_persona_card("amina")

with personas_tab:
    st.subheader("Personas drafted from OOTD's segments")
    st.markdown("<p class='section-intro'>These are <b>invented but plausible research archetypes</b>, not surveyed individuals. Your group should critically review the story and correct any unsupported assumptions before interviewing the bots.</p>", unsafe_allow_html=True)
    st.markdown("### Step 1 · Think first as a team")
    for hypothesis in GROUP_ASSUMPTIONS:
        st.markdown(f"- {hypothesis}")
    st.text_area("Optional: Record what group members actually discussed or disagreed about",
                 key="group_input", height=110, placeholder="E.g., Our group thinks wardrobe import friction might be more important than price...")
    st.caption("Use your real team notes. The starting bullet points above are AI-assisted draft hypotheses, not proof of human participation.")
    pa, pb = st.columns(2, gap="large")
    with pa: render_persona_card("siraj", show_edit=True)
    with pb: render_persona_card("amina", show_edit=True)
    st.caption("Portraits are AI-generated fictional representations, not photographs of respondents.")
    st.download_button("⬇ Export personas and team annotations (JSON)",
                       data=json.dumps({"personas": PERSONAS, "team_notes": human_notes(),
                                        "group_discussion": st.session_state["group_input"],
                                        "reviewed": review_flags()}, ensure_ascii=False, indent=2),
                       file_name="OOTD_personas_human_review.json", mime="application/json")

with interview_tab:
    st.subheader("Interview the fictional customers")
    st.markdown("<p class='section-intro'>Interview Siraj and Amina as <b>potential customers</b>. They explain what they need from a future OOTD product, not what you should wear. The local Ollama AI follows their profiles and uses the previous conversation for context.</p>", unsafe_allow_html=True)
    selector, engine_col = st.columns([.65, .35], gap="large")
    with selector:
        persona_id = st.radio("Interview subject", list(PERSONAS),
                              format_func=lambda x: f"{PERSONAS[x]['first_name']} · {PERSONAS[x]['segment']}",
                              horizontal=True, key="selected_persona")
    with engine_col:
        st.caption("Current execution mode")
        st.markdown(f"<div class='soft-label'>{escape(ENGINE_LABEL)}</div>", unsafe_allow_html=True)
    person = PERSONAS[persona_id]
    left, right = st.columns([.76, 1.24], gap="large")
    with left:
        st.image(str(ROOT / person["portrait"]), use_container_width=True)
        st.markdown(f"### {person['name']}, {person['age']}")
        st.caption(person["role"])
        st.markdown(f"<div class='quote'>“{escape(person['quote'])}”</div>", unsafe_allow_html=True)
        st.markdown("#### Ask a guided question")
        section = st.selectbox("Interview theme", list(QUESTION_BANK))
        question = st.selectbox("Question", QUESTION_BANK[section])
        if st.button("Ask selected question", type="primary", use_container_width=True):
            if interview_once(persona_id, question, model):
                st.rerun()
        with st.expander("Inspect the exact persona system prompt"):
            st.code(build_system_prompt(persona_id, human_notes()[persona_id]), language="text")
        if st.button("Clear this persona's interview", help="Clears this session's simulated Q&A only"):
            st.session_state["interviews"][persona_id] = []
            st.rerun()
    with right:
        st.markdown("#### Persona interview transcript")
        items = st.session_state["interviews"].get(persona_id, [])
        if not items:
            st.info(f"No interview questions asked yet. Start with a guided question or ask {person['first_name']} something specific.")
        for item in items:
            with st.chat_message("user"):
                st.markdown(item["question"])
            with st.chat_message("assistant", avatar=str(ROOT / "assets/ootd_badge.png")):
                st.markdown(item["answer"])
                st.caption(f"Synthetic response · {item['mode']} · {item['topic'].replace('_',' ').title()}")
        custom = st.chat_input(f"Ask {person['first_name']} about OOTD...")
        if custom:
            if interview_once(persona_id, custom, model):
                st.rerun()
    st.caption("Every interview answer comes from your local Ollama model. There is no canned-answer fallback. These fictional personas are not real research participants.")

with findings_tab:
    st.subheader("Findings, conclusions and documentation")
    st.markdown("<p class='section-intro'>All exports include the persona definitions, human-input annotations, exact bot prompts, guided questions, interview responses, research limitations and proposed OOTD changes.</p>", unsafe_allow_html=True)
    n_total = sum(counts_for(st.session_state["interviews"]).values())
    if n_total == 0:
        st.info("Your session has no interviews yet. For a worked demonstration, load the clearly labelled synthetic example, or start your own bot interviews.")
        if st.button("Load 22 example synthetic Q&A pairs", type="primary"):
            st.session_state["interviews"] = sample_interviews()
            st.rerun()
    else:
        lc, mc, rc = st.columns(3)
        for c, k in zip([lc, mc], PERSONAS):
            with c:
                st.markdown(html_metric(PERSONAS[k]["first_name"],
                                        str(len(st.session_state['interviews'][k])),
                                        "Synthetic interview answers recorded"),
                            unsafe_allow_html=True)
        with rc:
            st.markdown(html_metric("TOTAL TOPICS", str(len({row['topic'] for items in st.session_state['interviews'].values() for row in items})),
                                    "Heuristic topic labels, not statistical analysis"), unsafe_allow_html=True)
        st.markdown("### Interview evidence matrix")
        st.dataframe(thematic_rows(st.session_state["interviews"]),
                     use_container_width=True, hide_index=True,
                     column_config={"Simulated response": st.column_config.TextColumn(width="large"),
                                    "Question": st.column_config.TextColumn(width="medium")})
        st.caption("The matrix represents generated or rule-based synthetic utterances — not quotes from fieldwork.")
    st.markdown("### Interpretation: hypotheses, not validated insights")
    ca, cb = st.columns(2, gap="large")
    with ca:
        with st.container(border=True):
            st.markdown("#### Siraj · travel scenario")
            st.write("Evaluate destination-weather packing lists and business-vs-leisure outfit planning as possible premium value. Test forecast accuracy, manual effort and whether a €3.99/month plan beats his weather app and ordinary packing lists.")
            st.markdown("**Potential product risk:** unreliable packing advice, too much manual work or privacy doubts about wardrobe photos.")
    with cb:
        with st.container(border=True):
            st.markdown("#### Amina · student scenario")
            st.write("Evaluate quick, weather-aware outfits from existing clothes, shareable looks and a useful free tier. Test the friction of uploading a wardrobe and sensitivity to recurring costs on a student budget.")
            st.markdown("**Potential product risk:** onboarding effort or pushy fashion ads.")
    st.markdown("### Customer requirements → planned OOTD solutions")
    st.caption("These connections are product hypotheses drafted from the two fictional personas, not proven customer demand or delivered features.")
    for p_id in PERSONAS:
        with st.expander(f"{PERSONAS[p_id]['first_name']}: needs and how OOTD could respond", expanded=True):
            st.dataframe(NEED_TO_FEATURE[p_id], use_container_width=True, hide_index=True)
    st.markdown("### Step 6 · Proposed product changes to TEST")
    st.caption("Select the hypotheses your team wants to explore in a future real-user prototype. These choices are exported as proposals, not claims of implemented improvements.")
    for choice in RECOMMENDATIONS:
        checked = st.checkbox(choice, value=st.session_state["selected_decisions"][choice], key=f"dec_{RECOMMENDATIONS.index(choice)}")
        st.session_state["selected_decisions"][choice] = checked
    st.markdown("### Export complete coursework documentation")
    report_notes = human_notes()
    if st.session_state.get("group_input", "").strip():
        report_notes = dict(report_notes)
        report_notes["group_discussion"] = st.session_state["group_input"]
    md = report_markdown(st.session_state["interviews"], report_notes,
                         review_flags(), st.session_state["selected_decisions"],
                         f"{ENGINE_LABEL} · {model}")
    json_content = to_json(st.session_state["interviews"], report_notes, review_flags(),
                           st.session_state["selected_decisions"],
                           f"{ENGINE_LABEL} · {model}")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("⬇ Full research report (.md)", md,
                           file_name="OOTD_Persona_Research_Report.md", mime="text/markdown",
                           type="primary", use_container_width=True)
    with d2:
        st.download_button("⬇ Evidence & prompts (.json)", json_content,
                           file_name="OOTD_Research_Archive.json", mime="application/json",
                           use_container_width=True)
    with d3:
        st.download_button("⬇ Q&A matrix (.csv)", to_csv(st.session_state["interviews"]),
                           file_name="OOTD_Simulated_Interview_Matrix.csv", mime="text/csv",
                           use_container_width=True)
    st.caption("Markdown opens in VS Code and can be pasted into Word. JSON preserves all structured data and full prompts; CSV opens in Excel.")

with sources_tab:
    st.subheader("Research design and source traceability")
    st.markdown("#### Method: six requirements as a reproducible workflow")
    st.markdown("""
1. **Human brainstorming:** Critique initial needs, behaviors, budgets and channel assumptions before AI interviews.
2. **Two archetypes:** Use a student and a traveling professional to explore different value propositions.
3. **Persona portraits:** Display generated fictional representations with explicit labels.
4. **Reusable bots:** Lock each persona's background and constraints into an exportable system prompt.
5. **Interview guide:** Ask neutral questions about mornings, weather, onboarding, features, free/premium pricing, advertising and privacy.
6. **Decision log:** Compare simulated responses, propose experiments and export the complete trail.
""")
    st.markdown("#### Source files and exact sections")
    for src in SOURCE_MAP:
        with st.expander(src["file"]):
            st.markdown(f"**Where:** {src['sections']}")
            st.markdown(f"**Applied to:** {src['used_for']}")
    st.markdown("#### Carefully bounded desk-research context")
    st.markdown("<div class='research-box'><b>48%</b> of German weather-app users in the team's cited Bitkom survey reported using the forecast to decide what to wear. This supports relevance of weather information, <b>not</b> OOTD demand or pricing. <br><small>Group Market Research Report §4.1.5 (Bitkom, 2025).</small></div>",
                unsafe_allow_html=True)
    st.markdown("<div class='research-box'><b>€3.99/month and €29.99/year</b> are example subscription prices from the group's Business Canvas Summary §9. They are <b>not validated price points</b>. Only fieldwork or realistic price tests can evaluate willingness to pay.</div>",
                unsafe_allow_html=True)
    st.markdown("#### Fieldwork that would be needed next")
    st.markdown("The group's market report §5.2 proposes **5–8 qualitative interviews** with German students and young professionals aged 20–30. Conduct actual informed-consent interviews, separate their answers from this app's fictional bot output, and test an onboarding/outfit prototype before reporting a real market finding.")
    st.warning("Do not describe synthetic bot answers as primary interviews, representative research, validated purchase intention, or proof that OOTD will be successful.")

st.markdown("<div class='footer-note'>OOTD · style meets the forecast · AI-assisted marketing coursework demonstrator. Source-grounded business concept; fictional personas and clearly labelled synthetic interviews.</div>", unsafe_allow_html=True)
