"""Transparent, exportable OOTD synthetic persona interview documentation."""
from __future__ import annotations

import csv
from datetime import datetime, timezone
import io
import json
from collections import Counter
from typing import Any

from persona_data import (GROUP_ASSUMPTIONS, PERSONAS, PROJECT, QUESTION_BANK,
                          RECOMMENDATIONS, SOURCE_MAP, NEED_TO_FEATURE)
from persona_engine import answer_offline, build_system_prompt, classify_question

EXAMPLE_QUESTIONS = [
    "Walk me through your morning outfit routine. What feels difficult?",
    "How does changing weather in Germany influence what you wear?",
    "Would you upload your wardrobe photos? What would make that easy or difficult?",
    "Which OOTD features would matter most to you, and why?",
    "Would weekly planning or AI travel packing be useful to you?",
    "What do you think about OOTD's freemium business model?",
    "What is your reaction to a proposed premium price of €3.99 per month?",
    "Would you consider €29.99 per year after a free trial? Why or why not?",
    "How do you feel about sponsored outfit suggestions or affiliate links?",
    "What would you need to know about wardrobe privacy and data deletion?",
    "What should OOTD change before you would recommend it to a friend?",
]


def sample_interviews() -> dict[str, list[dict[str, str]]]:
    result: dict[str, list[dict[str, str]]] = {}
    for persona_id in PERSONAS:
        result[persona_id] = [
            {"question": q, "answer": answer_offline(persona_id, q),
             "topic": classify_question(q), "mode": "Prewritten synthetic demo (rule-based)",
             "timestamp": "Example; not a real interview"}
            for q in EXAMPLE_QUESTIONS
        ]
    return result


def counts_for(entries: dict[str, list[dict[str, str]]]) -> dict[str, int]:
    return {persona: len(entries.get(persona, [])) for persona in PERSONAS}


def thematic_rows(entries: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    rows = []
    for persona_id, items in entries.items():
        for item in items:
            rows.append({
                "Persona": PERSONAS[persona_id]["name"],
                "Theme": item.get("topic", "general").replace("_", " ").title(),
                "Question": item.get("question", ""),
                "Simulated response": item.get("answer", ""),
                "Mode": item.get("mode", ""),
            })
    return rows


def to_csv(entries: dict[str, list[dict[str, str]]]) -> str:
    output = io.StringIO()
    fields = ["Persona", "Theme", "Question", "Simulated response", "Mode"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(thematic_rows(entries))
    return output.getvalue()


def to_json(entries: dict[str, list[dict[str, str]]], human_notes: dict[str, str],
            reviewed: dict[str, bool], decisions: dict[str, bool],
            engine_label: str) -> str:
    data = {
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
        "research_type": "Synthetic, hypothetical personas — NOT real primary research",
        "project": PROJECT, "personas": PERSONAS, "human_notes": human_notes,
        "human_review_flags": reviewed, "bot_mode_selected": engine_label,
        "transcripts": entries, "proposed_tests": decisions,
        "customer_needs_and_ootd_planned_responses": NEED_TO_FEATURE,
        "sources": SOURCE_MAP,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def report_markdown(entries: dict[str, list[dict[str, str]]],
                    human_notes: dict[str, str], reviewed: dict[str, bool],
                    decisions: dict[str, bool], engine_label: str) -> str:
    """Deliver all six academic requirements in a comprehensive Markdown file."""
    now = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    out = [
        "# OOTD — AI Persona Interview & Product Decision Report",
        "**Style meets the forecast**  |  Germany pilot / proposed EU-27 expansion",
        f"**Generated:** {now}",
        "", "**Academic integrity statement:** Everything below labelled 'persona' or 'interview' is fictional "
        "and AI-assisted or rule-based simulation. These outputs are **not primary consumer interviews, "
        "not validated willingness to pay, and not evidence that OOTD has product-market fit**. "
        "The team should interview 5–8 real people as proposed in the group research report §5.",
        "", "## 1. Company context and research objective", "",
        f"**OOTD concept:** {PROJECT['concept']}",
        f"**Market:** {PROJECT['market']}.",
        "", "The objective is to test assumptions about everyday outfit friction, weather "
        "relevance, digital wardrobe adoption, travel planning, privacy, free/premium "
        "pricing, sponsored content, and customer acquisition channels.",
        "", "## 2. Human input BEFORE AI personas", "",
        "The group must actively discuss, correct and approve the two fictional profiles. "
        "These draft hypotheses are provided for review, not represented as human-validated.",
    ]
    for i, assumption in enumerate(GROUP_ASSUMPTIONS, 1):
        out.append(f"{i}. {assumption}")
    out.extend(["", "**Actual group discussion as entered in the app:**",
                human_notes.get("group_discussion", "No group discussion notes supplied yet."), ""])
    for key, p in PERSONAS.items():
        out.extend(["", f"**{p['name']} — human review:** {'Reviewed by team' if reviewed.get(key) else 'PENDING (draft)'}",
                    human_notes.get(key, p["human_design_note"]), ""])
    out.extend(["", "## 3. Two customer personas and persona images", ""])
    for key, p in PERSONAS.items():
        out.extend([
            f"### {p['name']} (fictional, {p['age']})", "",
            f"![Generated representation of {p['name']}]({p['portrait']})", "",
            f"- **Segment:** {p['segment']}", f"- **Location:** {p['location']}",
            f"- **Role:** {p['role']}", f"- **Background:** {p['bio']}",
            f"- **Lifestyle:** {p.get('lifestyle', '')}",
            f"- **Personality traits:** {'; '.join(p.get('personality', []))}",
            f"- **Interview behaviour:** {p.get('interview_behaviour', '')}",
            f"- **Style:** {p['style']}", f"- **Quote:** “{p['quote']}”",
            f"- **Goals:** {'; '.join(p['goals'])}",
            f"- **Pains:** {'; '.join(p['pains'])}",
            f"- **Behaviours:** {'; '.join(p['behaviour'])}",
            f"- **Feature priorities:** {'; '.join(p['feature_priority'])}",
            f"- **Illustrative pricing view:** {p['pricing_view']}",
            f"- **Subscription stance:** {p['subscription_view']}",
            f"- **Privacy expectations:** {p['privacy_view']}", "",
        ])
    out.extend(["## 4. Reusable AI persona chatbots — exact prompts", "",
                "Interactive bot interviews use only the locally installed Ollama model. "
                "The profiles below are passed as **system messages**, and conversation "
                "history provides continuity. The bundled example transcripts are prewritten "
                "and explicitly labelled as demonstrations; they are not real AI interviews.",
                f"**Currently selected interview engine:** {engine_label}", ""])
    for key, p in PERSONAS.items():
        out.extend([f"### System prompt: {p['name']}", "", "```text",
                    build_system_prompt(key, human_notes.get(key, "")), "```", ""])
    out.extend(["## 5. Interview question guide", ""])
    for section, questions in QUESTION_BANK.items():
        out.extend([f"### {section}", ""])
        out.extend(f"- {q}" for q in questions)
        out.append("")
    out.extend(["## 6. Interview transcripts — simulated answers", "",
                "Each answer is generated by a fictional persona, NOT a response from an interviewed human.", ""])
    for key, p in PERSONAS.items():
        out.extend([f"### {p['name']}", ""])
        items = entries.get(key, [])
        if not items:
            out.append("*No questions were recorded for this persona.*")
        for i, item in enumerate(items, 1):
            out.extend([
                f"**Q{i} [{item.get('topic', 'general')}]** {item.get('question', '')}", "",
                f"**Simulated {p['first_name']}:** {item.get('answer', '')}", "",
                f"*Mode:* {item.get('mode', '')} | *Recorded:* {item.get('timestamp', '')}", "",
            ])
    all_items = [item for values in entries.values() for item in values]
    freq = Counter(i.get("topic", "general") for i in all_items)
    out.extend(["## 7. Thematic analysis and interpretation", "",
                f"**Total simulated Q&A pairs:** {len(all_items)}.",
                "**Research scope:** Only two pre-specified fictional personas; this is a scenario "
                "test to improve interview questions and the MVP, not evidence of market demand.", "",
                "### Topics covered", ""])
    if freq:
        for name, cnt in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0])):
            out.append(f"- {name.replace('_', ' ').title()}: {cnt} simulated question(s)")
    else:
        out.append("- No simulated interviews have been run.")
    out.extend(["", "### Persona-specific *hypotheses* suggested by the exercise", "",
                "- Siraj: reliable destination-weather packing and business-vs-leisure outfit planning "
                "could justify investigating the €3.99 example price, if it beats free alternatives.",
                "- Amina: low-friction daily styling, wardrobe reuse, shareable looks and a convincing "
                "free plan could matter more than paid travel features.",
                "- Both: low-effort onboarding, privacy, trust and transparent promotional content "
                "may affect willingness to adopt.",
                "- These are design hypotheses based on fictional profiles, not emergent findings "
                "from representative customer data.", ""])
    out.extend(["### Requirements described by personas → OOTD proposed response", "",
                "**Hypothetical design mapping:** Persona statements are not validated user evidence.", ""])
    for key, p in PERSONAS.items():
        out.extend([f"**{p['first_name']}:**", ""])
        for row in NEED_TO_FEATURE[key]:
            out.append(f"- **Need:** {row['Customer requirement']}  **OOTD planned response:** {row['OOTD proposed response']}")
        out.append("")
    out.extend(["## 8. Suggested changes to OOTD for REAL-WORLD testing", "",
                "Selected items reflect provisional product decisions, not proven improvements.", ""])
    for i, rec in enumerate(RECOMMENDATIONS, 1):
        out.append(f"{i}. [{'x' if decisions.get(rec, False) else ' '}] {rec}")
    out.extend(["", "### Business model canvas implications", "",
                "- **Value proposition:** Weather-aware recommendations using clothes the user already owns.",
                "- **Customer segments:** Daily Deciders and Social Style Sharers first; "
                "Frequent Travelers as a possible premium segment.",
                "- **Channels:** Pilot approved campus events, QR code flyers and small referrals; "
                "compare against organic social posts.",
                "- **Revenue:** Compare a genuinely useful free tier with proposed €3.99/month "
                "and €29.99/year premium options; test willingness to pay with humans.",
                "- **Trust:** Transparent sponsored labels and privacy/consent controls.", ""])
    out.extend(["## 9. Validation plan and limitations", "",
                "1. Have group members review and sign off on personas and scenario assumptions.",
                "2. Recruit 5–8 actual students/young professionals, as planned in the market research report §5.2.",
                "3. Use open-ended, neutral interview questions; record informed consent and anonymised responses.",
                "4. Test a low-fidelity wardrobe upload and first outfit with real users.",
                "5. Test paid features with realistic pricing choices, not only stated enthusiasm.",
                "6. Distinguish real participant quotes from simulated persona outputs when reporting.",
                "", "**Limitations:** Persona traits are invented. The rule-based demo is not an LLM. "
                "Generative LLM outputs are synthetic and can reflect their prompts and the team's "
                "own assumptions. Secondary market statistics do not establish product demand.", ""])
    out.extend(["## 10. Source traceability", ""])
    for source in SOURCE_MAP:
        out.extend([f"- **{source['file']}**, {source['sections']} — {source['used_for']}."])
    out.extend(["", "**Pricing boundary:** The example monthly (€3.99) and annual (€29.99) "
                "prices are from the group's Business Canvas Summary §9 and are not validated.",
                "**Competitive boundary:** The market report §1 documents existing overlapping "
                "services such as Acloset, Whering and Cladwell; OOTD is not claimed to be first.", ""])
    return "\n".join(out)
