import streamlit as st
import google.generativeai as genai

# --------------------------------------------------
# 1. Safe API key loading
# --------------------------------------------------
st.set_page_config(page_title="AI Assistant (Gemini API)", page_icon="🤖", layout="wide")

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.title("🤖 AI Assistant (Gemini API)")
    st.error('GEMINI_API_KEY is missing in .streamlit/secrets.toml')
    st.code('GEMINI_API_KEY = "your-real-gemini-key-here"', language="toml")
    st.stop()

genai.configure(api_key=API_KEY)

# Use a working text model
MODEL_NAME = "models/gemini-pro-latest"
model = genai.GenerativeModel(MODEL_NAME)

# --------------------------------------------------
# 2. Page header
# --------------------------------------------------
st.title("🤖 AI Assistant (Gemini API)")
st.caption("Integrated via Google AI Studio – CST1510 Week 10")

# --------------------------------------------------
# 3. Sidebar controls
# --------------------------------------------------
with st.sidebar:
    st.subheader("Chat Controls")

    # Domain focus (used to guide the AI)
    domain = st.selectbox(
        "Assistant focus",
        [
            "General help",
            "Cybersecurity incidents",
            "Data / Datasets",
            "IT Support Tickets",
        ],
    )

    # Initialise messages if not present (for counter)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    msg_count = len(st.session_state.messages)
    st.metric("Messages in this session", msg_count)

    # Clear chat
    if st.button("🗑 Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.experimental_rerun()

# --------------------------------------------------
# 4. Helper: build system-style prefix based on domain
# --------------------------------------------------
def build_system_prefix(domain_choice: str) -> str:
    """Return a short instruction to guide Gemini based on the selected domain."""
    if domain_choice == "Cybersecurity incidents":
        return (
            "You are helping a first-year BSc IT student understand cybersecurity incidents.\n"
            "Explain clearly, with simple examples, and connect ideas to things like phishing, alerts, logs, and severity.\n"
        )
    if domain_choice == "Data / Datasets":
        return (
            "You are helping a first-year BSc IT student understand datasets and basic data analysis.\n"
            "Explain rows, columns, trends, summaries, and simple metrics in friendly, non-jargon language.\n"
        )
    if domain_choice == "IT Support Tickets":
        return (
            "You are helping a first-year BSc IT student understand IT support tickets.\n"
            "Explain priorities, statuses, and ticket patterns in a clear and practical way.\n"
        )
    # General help
    return (
        "You are a friendly AI tutor for a first-year BSc IT student.\n"
        "Use short paragraphs, simple language, and avoid heavy jargon.\n"
    )

# --------------------------------------------------
# 5. Initialise chat history
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show previous messages
for chat in st.session_state.messages:
    with st.chat_message(chat["role"]):
        st.markdown(chat["content"])

# --------------------------------------------------
# 6. Get user input
# --------------------------------------------------
prompt = st.chat_input("Ask something about cyber, data, or IT...")

if prompt:
    # 6.1 Add user message to history & display it
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)

    with st.chat_message("user"):
        st.markdown(prompt)

    # --------------------------------------------------
    # 6.2 Build context to send to Gemini
    # We send:
    #   - A short system-style instruction (based on domain)
    #   - Last few turns of the conversation (for context)
    # --------------------------------------------------
    system_prefix = build_system_prefix(domain)

    MAX_TURNS = 10  # only send last 10 messages for efficiency
    history_parts = [system_prefix]

    for msg in st.session_state.messages[-MAX_TURNS:]:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        history_parts.append(f"{role_label}: {msg['content']}")

    # This is the full text Gemini sees
    full_prompt = "\n".join(history_parts)

    # --------------------------------------------------
    # 6.3 Call Gemini safely
    # --------------------------------------------------
    with st.chat_message("assistant"):
        try:
            with st.spinner("Gemini is thinking..."):
                response = model.generate_content(full_prompt)
            reply = response.text if hasattr(response, "text") else str(response)
        except Exception as e:
            reply = (
                "❌ Gemini API error:\n\n"
                f"`{e}`\n\n"
                "Your integration is working, but there is an issue with the API call.\n"
                "Check your GEMINI_API_KEY, model name, or network connection."
            )

        # Show assistant reply
        st.markdown(reply)

    # 6.4 Save assistant reply to history
    st.session_state.messages.append({"role": "assistant", "content": reply})
