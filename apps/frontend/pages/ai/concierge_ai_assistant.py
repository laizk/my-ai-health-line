import streamlit as st
import requests
import json


BACKEND_API_URL = "http://backend:8010/ask"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        
# React to user input
if prompt := st.chat_input("What is up?"):
    
        try:
            
            # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})   
            
            # Parse JSON
            payload = {
                "prompt": prompt
            }

            # Send to FastAPI endpoint
            response = requests.post(
                BACKEND_API_URL,
                json=payload,
                timeout=8
            )            
            
            data = response.json()
            response_text = (
                data.get("response", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
            )
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response_text)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response_text})                

        except json.JSONDecodeError as e:
            st.error("Invalid JSON format.")
            st.code(str(e))

        except Exception as e:
            st.error("Failed to send request.")
            st.exception(e)    

    
