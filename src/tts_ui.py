import streamlit as st
import requests

# Streamlit app
st.title("Text-to-Speech Generator")

# Input form
with st.form("tts_form"):
    text = st.text_area("Enter text for speech synthesis:", height=150)
    temperature = st.slider("Temperature (stability vs expressiveness)", 0.1, 2.0, 0.1)
    repetition_penalty = st.slider("Repetition Penalty", 0.5, 2.0, 1.1)
    max_length = st.number_input("Maximum Length", min_value=100, max_value=4096, value=4096)

    submitted = st.form_submit_button("Generate Speech")

if submitted:
    # Send the request to the Flask API
    api_url = "http://localhost:5000/generate_tts"
    payload = {
        "text": text,
        "temperature": temperature,
        "repetition_penalty": repetition_penalty,
        "max_length": max_length,
    }

    with st.spinner("Generating speech..."):
        response = requests.post(api_url, json=payload)

    # Check the response
    if response.status_code == 200:
        # Save the audio file
        output_file = "output_gguf.wav"
        with open(output_file, "wb") as f:
            f.write(response.content)

        # Display the audio player
        st.audio(output_file, format="audio/wav")
        st.success("Speech synthesis complete!")
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")

