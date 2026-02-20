import re
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="Caregiver Support (Demo)", page_icon="🤝", layout="centered")

# -------------------------
# Safety + rule-based logic
# -------------------------
DISCLAIMER = """
**Demo-only caregiver support tool (non-diagnostic).**
- This app does **not** provide medical diagnosis or treatment.
- It does **not** recommend starting/stopping/changing medications.
- If you think there is an emergency, call your local emergency number immediately.
"""

EMERGENCY_MSG = """
### 🚨 Possible emergency (“red flag”) detected
Based on the text you entered, this may need **urgent attention**.

**Do now (general guidance):**
1. If the person is in immediate danger or you suspect stroke/heart attack/severe breathing trouble: **call emergency services now**.
2. If unsure, **contact a local nurse line / urgent care / clinician** for guidance.
3. Stay with the person if it’s safe to do so.
"""

NON_URGENT_MSG = """
### ✅ No emergency keywords detected (based on simple rules)
This does **not** mean everything is fine—this tool is limited and rule-based.

**Helpful next steps (general, non-medical):**
- Monitor changes and write down what you observe (time, triggers, what helps).
- Consider contacting the person’s clinician if symptoms are new, worsening, or concerning.
- Focus on comfort, hydration, rest, and safety in the environment (as appropriate).
"""

# Red-flag patterns (keyword + regex). Keep conservative and simple.
RED_FLAGS = [
    # Breathing / consciousness
    (r"\b(can't breathe|cannot breathe|trouble breathing|difficulty breathing|shortness of breath|blue lips|turning blue)\b", "Breathing trouble"),
    (r"\b(unconscious|not waking|won't wake|passed out|fainted)\b", "Unresponsive / fainting"),
    (r"\b(seizure|convulsion|fit)\b", "Seizure"),
    # Stroke-like
    (r"\b(face droop|slurred speech|can't speak|weakness on one side|one-sided weakness|sudden numbness)\b", "Possible stroke signs"),
    # Chest pain
    (r"\b(chest pain|pressure in chest|tightness in chest)\b", "Chest pain/pressure"),
    # Severe bleeding / injury
    (r"\b(heavy bleeding|won't stop bleeding|bleeding won't stop)\b", "Uncontrolled bleeding"),
    (r"\b(head injury|hit (his|her|their) head|concussion)\b", "Head injury"),
    # Suicidal/self-harm language
    (r"\b(suicide|kill myself|self harm|hurt myself)\b", "Self-harm risk"),
]

# Non-emergency, supportive suggestions (rule-based)
SUGGESTION_RULES = [
    (r"\b(confused|confusion|disoriented)\b", "Confusion can have many causes. Consider checking for recent changes (sleep, hydration, stress, new routines). If sudden or severe, contact a clinician."),
    (r"\b(fever|high temperature)\b", "Fever can be a sign of infection. If fever is high, persistent, or with worsening symptoms, contact a clinician."),
    (r"\b(fall|fell|slipped)\b", "After a fall, watch for pain, dizziness, confusion, or head injury signs. If there’s severe pain, head impact, or worsening symptoms, seek urgent care."),
    (r"\b(vomiting|throwing up)\b", "If vomiting is persistent, there are signs of dehydration, or blood appears, contact urgent care/clinician."),
    (r"\b(dehydrated|dehydration|not drinking)\b", "Encourage small, frequent sips of water if safe. If the person can’t keep fluids down or seems very weak, contact a clinician."),
    (r"\b(agitated|anxious|panic)\b", "Try a calm environment, slow breathing, reassurance, and reduce noise. If agitation is severe or unsafe, seek professional help."),
    (r"\b(pain)\b", "Track pain location, severity (0–10), start time, and what worsens/relieves it. If severe or sudden, contact a clinician."),
]

def find_red_flags(text: str):
    hits = []
    for pattern, label in RED_FLAGS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            hits.append(label)
    return sorted(set(hits))

def generate_support_suggestions(text: str):
    suggestions = []
    for pattern, suggestion in SUGGESTION_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            suggestions.append(suggestion)
    # If no matches, give general advice only
    if not suggestions:
        suggestions.append("Consider logging what you observe (when it started, what changed, what helps). If symptoms worsen or feel concerning, contact a clinician.")
    return suggestions

def format_log_entry(person_name, relationship, concern_text, severity, notes):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""## Care Log Entry ({now})

**Person:** {person_name or "N/A"}  
**Relationship:** {relationship or "N/A"}  
**Severity (caregiver-rated):** {severity}/10  

### What I observed
{concern_text.strip() if concern_text else "N/A"}

### Extra notes
{notes.strip() if notes else "N/A"}
"""

# -------------------------
# UI
# -------------------------
st.title("🤝 Caregiver Support (Demo-only, No AI)")
st.info(DISCLAIMER)

tab1, tab2, tab3 = st.tabs(["Quick Check", "Care Log", "Plan & Resources"])

with tab1:
    st.subheader("Quick Check (rule-based)")
    st.caption("Type what you’re seeing. The app checks for **simple red-flag keywords** only.")

    concern_text = st.text_area(
        "What’s happening right now?",
        placeholder="Example: sudden chest pain, trouble breathing, fell and hit head, very confused...",
        height=140,
    )

    if st.button("Run Quick Check"):
        text = concern_text.strip()
        if not text:
            st.warning("Please type something first.")
        else:
            red_flags = find_red_flags(text)
            if red_flags:
                st.error(EMERGENCY_MSG)
                st.write("**Red-flag matches:**")
                st.write(", ".join(red_flags))
            else:
                st.success(NON_URGENT_MSG)

            st.divider()
            st.subheader("Supportive suggestions (general, non-medical)")
            for s in generate_support_suggestions(text):
                st.write(f"- {s}")

            st.divider()
            st.caption("Tip: If you want, copy the text into the Care Log tab to keep a record.")

with tab2:
    st.subheader("Care Log (copy/paste friendly)")
    st.caption("Create a structured note you can save or share with a clinician (without making medical claims).")

    col1, col2 = st.columns(2)
    with col1:
        person_name = st.text_input("Person’s name (optional)")
        relationship = st.text_input("Your relationship (optional)", placeholder="e.g., daughter, spouse, aide")
    with col2:
        severity = st.slider("How severe does it feel to you?", 0, 10, 5)

    observed = st.text_area("What you observed (copy/paste here)", height=140)
    notes = st.text_area("Extra notes (optional)", placeholder="Triggers, what helped, what changed today...", height=100)

    if st.button("Generate log entry"):
        entry = format_log_entry(person_name, relationship, observed, severity, notes)
        st.text_area("Generated note (copy this)", entry, height=260)

        # Basic safety check on the observed text as well
        red_flags = find_red_flags(observed or "")
        if red_flags:
            st.warning("Red-flag keywords were detected in your observation note:")
            st.write(", ".join(red_flags))

with tab3:
    st.subheader("Simple Plan & Resources (non-medical)")
    st.markdown(
        """
**A simple caregiver plan (general):**
1. **Safety first:** prevent falls, keep walkways clear, supervise if needed.
2. **Observe + write it down:** when it started, what changed, what helps/worsens.
3. **Communicate:** share the log with family/care team.
4. **Escalate when needed:** new/worsening symptoms, red flags, or caregiver intuition.

**Helpful checklists (general):**
- Water/fluids available (if safe)
- Comfortable position and temperature
- Noise/light reduced
- Med list and emergency contacts accessible
- Recent changes noted (sleep, food, routine, stress)

**Emergency reminders:**
- If severe breathing trouble, chest pain/pressure, stroke signs, seizure, uncontrolled bleeding, or unresponsiveness: **call emergency services**.
"""
    )

st.caption("Built for workshops: no keys, no AI, rule-based only.")
