import streamlit as st
import google.genai as genai
from google.genai import types
import os

# --- Navbar ---
st.markdown("""
<style>
.navbar {
    background-color: #f8f9fa;
    padding: 10px;
    display: flex;
    justify-content: space-between;
}
.navbar button {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
    border-radius: 5px;
}
</style>
<div class="navbar">
    <a href="https://jamesthedatascientist.com" target="_blank"><button>JTD Home</button></a>
    <button disabled>ParaFlow.ai</button>
    <button onclick="window.location.reload();">Reset Conversation</button>
</div>
""", unsafe_allow_html=True)

# --- Setup Gemini API using google.genai ---
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY) # Initialize client
model = "gemini-2.0-flash" # Specify model here


# --- Load initial prompt from prompt.txt (initial assistant message) ---
try:
    with open("prompt.txt", "r", encoding='utf-8') as f:
        initial_prompt = f.read().strip()
except FileNotFoundError:
    initial_prompt = "Hello, how can I help you today?"
    st.warning("prompt.txt not found. Using default initial message.")

# --- Load instructions from instructions.txt (System Instructions) ---
try:
    with open("instructions.txt", "r", encoding='utf-8') as f:
        system_instructions = f.read().strip()
except FileNotFoundError:
    system_instructions = "You are a helpful and friendly chatbot." # Default system instructions
    st.warning("instructions.txt not found. Using default system instructions.")

st.title("ParaFlow.AI")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "model", "content": initial_prompt}]

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt_text := st.chat_input("Type your message here..."):
    # Display user message in chat message container
    st.session_state.messages.append({"role": "user", "content": prompt_text})
    with st.chat_message("user"):
        st.markdown(prompt_text)

    # --- Gemini API Call with system_instruction using google.genai ---

    contents = []
    # Add Chat History (excluding system instruction and current user prompt)
    for message in st.session_state.messages[:-1]: # Exclude the latest user prompt
        gemini_role = "user" if message["role"] == "user" else "model" # Map streamlit roles to gemini roles
        parts_list = [types.Part.from_text(text=message["content"])] # Create a list containing types.Part
        contents.append(types.Content(role=gemini_role, parts=parts_list)) # Assign the list to parts

    # Add Current User Prompt
    parts_list_user = [types.Part.from_text(text=prompt_text)] # Create a list for user prompt part
    contents.append(types.Content(role="user", parts=parts_list_user)) # Assign the list to parts


    generate_config = types.GenerateContentConfig(
        system_instruction=system_instructions,
        temperature=0.7,
    )

    try:
        response = client.models.generate_content( # Use client.models.generate_content
            model=model,
            contents=contents,
            config=generate_config
        )
        gemini_response = response.text
    except Exception as e:
        gemini_response = f"Error communicating with Gemini API: {e}"
        st.error(gemini_response)

    # Display assistant response in chat message container
    st.session_state.messages.append({"role": "model", "content": gemini_response}) # Use "model" role for assistant
    with st.chat_message("model"): # Use "model" role for display
        st.markdown(gemini_response)