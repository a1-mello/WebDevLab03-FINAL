# Lab 3: Chatbot page
# TODO: Rename this file to fit your page. Keep the number at the front.
#
# A chatbot built with Pydantic AI (see the Pydantic AI pages on Canvas).
# It should:
#   - use a Pydantic AI Agent with instructions that fit your project's theme (no tools yet)
#   - use Streamlit's chat elements: st.chat_message and st.chat_input
#   - remember the conversation (message_history, saved in st.session_state)
#   - use try/except so an error shows a message instead of crashing the page
#   - stay on theme, without using any API or external data
#
# Your Gemini API key goes in .streamlit/secrets.toml as GOOGLE_API_KEY.

import streamlit as st
from pydantic_ai import Agent

st.title(" 🏥 🫀 HealthLine 🧬 💊")

with st.chat_message("user"):
    st.write("Hello 👋 Want to learn about different conditions and diseases? Give me a specific name or just a body system! I'll explain some symptoms, causes, and recommened prevention tips")
# STEP 1-2: instructions + create the agent


agent = Agent(
    "google:gemini-3.5-flash-lite",
    instructions=(
        "You are a friendly assistant for students learning about diseases and conditions. "
        " You talk about what body system a condition/disease affects and their symptoms, causes, and prevention. If someone asks about something else, prompt them to stay on topic. "
        " You cannot look up live data, so answer only from general knowledge in under 5 sentences and say when you are not sure. "
        " When asked about a specific disease or condition, answer with what body system it affects, its symptoms, causes, and recommended prevention. "
        "For example, when asked to tell the user about a condition, respond with a 2-3 sentence summary. "
        "Don't include a message saying that you cannot give advice unless the user explicitly trys to ask for it. "
        "Don't include that you unsure about something unless the user specifically asks you for something you don't know. "
        " Never give personal medical advice or diagnoses. If someone describes their symtoms, respond with general recommended prevention tips but add that you cannot give a disagnosis and that they should consult a professional."
    ),
)

# STEP 3: set up st.session_state (only if it doesn't exist yet)
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "memory" not in st.session_state:
    st.session_state["memory"] = []

# STEP 4: show old messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])
# STEP 5-6: get new input, show it, call the agent inside try/except, show + save the reply
prompt = st.chat_input("messages")
if prompt:
    with st.chat_message("user"):
        st.write(prompt)
    st.session_state["messages"].append({"role":"user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            result = agent.run_sync(prompt, message_history=st.session_state["memory"])
            reply = result.output
            st.session_state["memory"] = result.all_messages()
        except Exception:
            reply = "Sorry, something went wrong. Trying asking another question"
        st.write(reply)

    st.session_state["messages"].append({"role": "assistant", "content" : reply})



