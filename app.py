import streamlit as st
import requests
import json
import os
from cerebras.cloud.sdk import Cerebras
import asyncio
import aiohttp

st.title("AI Model Comparison powered by Docker")

OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"

CEREBRAS_API_KEY = os.environ.get("CEREBRAS_API_KEY")
if not CEREBRAS_API_KEY:
    st.error("Please set the CEREBRAS_API_KEY environment variable.")
    st.stop()

cerebras_client = Cerebras(api_key=CEREBRAS_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

async def get_local_llama_response(prompt):
    conversation_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    local_payload = {
        "model": "llama3:8b",
        "prompt": f"{conversation_history}\nassistant:",
        "stream": True
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(OLLAMA_API_URL, json=local_payload) as response:
            if response.status == 200:
                response_text = ""
                async for line in response.content:
                    if line:
                        try:
                            json_response = json.loads(line)
                            token = json_response.get('response', '')
                            response_text += token
                            yield response_text
                        except json.JSONDecodeError:
                            continue
            else:
                yield f"Failed to generate response. Status code: {response.status}"

async def get_cerebras_response(prompt):
    try:
        stream = cerebras_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3.1-8b",
            stream=True
        )
        response_text = ""
        for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            response_text += token
            yield response_text
    except Exception as e:
        yield f"Failed to generate response from Cerebras: {str(e)}"

async def stream_local_response(prompt, placeholder):
    async for response in get_local_llama_response(prompt):
        placeholder.markdown(response)
    return response

async def stream_cerebras_response(prompt, placeholder):
    async for response in get_cerebras_response(prompt):
        placeholder.markdown(response)
    return response

if prompt := st.chat_input("Enter your prompt here"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Local Llama Model")
        local_placeholder = st.empty()

    with col2:
        st.subheader("Cerebras Model")
        cerebras_placeholder = st.empty()

    async def update_responses():
        local_task = asyncio.create_task(stream_local_response(prompt, local_placeholder))
        cerebras_task = asyncio.create_task(stream_cerebras_response(prompt, cerebras_placeholder))

        await asyncio.gather(local_task, cerebras_task)

        # Append only the local model response to the conversation history
        st.session_state.messages.append({"role": "assistant", "content": await local_task})

    asyncio.run(update_responses())