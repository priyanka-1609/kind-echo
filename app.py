"""
Kind Echo - leave a voice note, receive a kind one from a stranger.

* Your own voice note is never stored: it is released as soon as you finish.
* You receive a kind voice note left by an earlier stranger (only notes approved by the owner are played).
  If none are approved yet, a built-in encouraging message is read aloud by your browser.
* You can leave a kind note for the next stranger. It waits in a review queue until the owner approves it.

Run locally:  python -m streamlit run app.py
Admin password: set ADMIN_PASSWORD in .streamlit/secrets.toml (locally) or in the app's Secrets on Streamlit Cloud.
"""
import json
import random
import time
import uuid
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Kind Echo", page_icon="🌙", layout="centered")

NOTES = Path(__file__).parent / "notes"
PENDING, APPROVED, REPORTED = NOTES / "pending", NOTES / "approved", NOTES / "reported"
for d in (PENDING, APPROVED, REPORTED):
    d.mkdir(parents=True, exist_ok=True)

MAX_BYTES = 3_000_000          # ~ 1 minute of browser-recorded audio
KIND_WORDS = [
    "Hey. Whatever you're carrying right now, you don't have to carry it perfectly. You're doing better than you think.",
    "I don't know you, but I'm glad you're here. Today counts, even if all you did was get through it.",
    "It's okay to be tired. Rest is not giving up. Tomorrow you can try again, and that is enough.",
    "You've survived every hard day so far. That's a hundred percent record. Be gentle with yourself tonight.",
    "Someone out there is smiling because you exist. Maybe it's me, a stranger, right now.",
    "Small steps still move you forward. Drink some water, breathe slowly, and give yourself some credit.",
    "Your feelings make sense. You don't need to have it all figured out tonight.",
    "You are allowed to take up space, ask for help, and start over as many times as you need.",
]


def speak_button(text):
    """Read a message aloud with the browser's built-in voice (works offline, no API key)."""
    safe = json.dumps(text)
    components.html(f"""
    <div style="font-family:sans-serif">
      <button id="b" style="font-size:16px;padding:10px 18px;border-radius:24px;border:none;
              background:#6d5dfc;color:white;cursor:pointer">▶ Play your kind note</button>
    </div>
    <script>
      const t = {safe};
      document.getElementById('b').onclick = () => {{
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(t);
        u.rate = 0.92; u.pitch = 1.05;
        const v = speechSynthesis.getVoices().find(v => /female|samantha|zira|google uk english female/i.test(v.name));
        if (v) u.voice = v;
        speechSynthesis.speak(u);
      }};
    </script>""", height=60)


def random_approved():
    files = sorted(APPROVED.glob("*.wav"))
    return random.choice(files) if files else None


# ------------------------------------------------------------------ header
st.title("🌙 Kind Echo")
st.markdown("Say what's on your mind — a worry, a win, or just *hi*. Nobody keeps it. "
            "In return, you'll hear a kind word from a stranger.")

# ------------------------------------------------------------------ 1. release your note
st.subheader("1 · Say it out loud")
mine = st.audio_input("Record your voice note", key="mine")
if mine is not None:
    if "gift" not in st.session_state:                      # pick one kind note per recording
        f = random_approved()
        st.session_state.gift = ("file", f.name) if f else ("text", random.choice(KIND_WORDS))
    st.success("🎈 Released. Your note was not saved anywhere.")

    st.subheader("2 · A kind note for you")
    kind, val = st.session_state.gift
    if kind == "file" and (APPROVED / val).exists():
        st.audio(str(APPROVED / val))
        st.caption("Left by a stranger who visited before you.")
        if st.button("🚩 Report this note"):
            (APPROVED / val).rename(REPORTED / val)
            st.session_state.gift = ("text", random.choice(KIND_WORDS))
            st.info("Thank you — it has been removed and will be reviewed.")
            st.rerun()
    else:
        st.markdown(f"> *{val}*")
        speak_button(val)
        st.caption("No stranger notes are available yet, so here's one from us.")
else:
    st.session_state.pop("gift", None)

# ------------------------------------------------------------------ 3. pay it forward
st.divider()
st.subheader("3 · Leave a kind note for the next stranger")
st.markdown("Record something encouraging for whoever comes next. Keep it kind, and please **don't include names, "
            "phone numbers or other personal details**. Notes are checked before anyone hears them.")
agree = st.checkbox("I agree that my kind note may be played to other visitors.")
if st.session_state.get("left_note"):
    st.success("💌 Thank you! Your note is waiting for review and will brighten someone's day.")
else:
    gift_note = st.audio_input("Record your kind note", key="gift_note", disabled=not agree)
    if gift_note is not None and st.button("Send kind note", type="primary"):
        data = gift_note.getvalue()
        if len(data) > MAX_BYTES:
            st.error("That note is a bit long — please keep it under about a minute.")
        else:
            name = f"{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:8]}.wav"
            (PENDING / name).write_bytes(data)
            st.session_state.left_note = True
            st.rerun()

st.caption("If you're going through something heavy, please also reach out to someone you trust "
           "or a local helpline — you deserve real support, not just kind echoes.")

# ------------------------------------------------------------------ owner review
with st.sidebar.expander("🔒 Owner review"):
    pw = st.text_input("Password", type="password")
    secret = st.secrets.get("ADMIN_PASSWORD", None) if hasattr(st, "secrets") else None
    if not secret:
        st.caption("Set ADMIN_PASSWORD in Secrets to enable review.")
    elif pw == secret:
        pending = sorted(PENDING.glob("*.wav"))
        st.write(f"**{len(pending)} waiting** · {len(list(APPROVED.glob('*.wav')))} approved · "
                 f"{len(list(REPORTED.glob('*.wav')))} reported")
        for f in pending[:20]:
            st.audio(str(f))
            a, b = st.columns(2)
            if a.button("✅ Approve", key="a" + f.name):
                f.rename(APPROVED / f.name); st.rerun()
            if b.button("🗑️ Delete", key="d" + f.name):
                f.unlink(); st.rerun()
        for f in sorted(REPORTED.glob("*.wav"))[:20]:
            st.caption(f"Reported: {f.name}")
            st.audio(str(f))
            a, b = st.columns(2)
            if a.button("↩️ Restore", key="r" + f.name):
                f.rename(APPROVED / f.name); st.rerun()
            if b.button("🗑️ Delete", key="x" + f.name):
                f.unlink(); st.rerun()
    elif pw:
        st.error("Wrong password.")
