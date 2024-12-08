import streamlit as st
import requests

st.title("Speech-to-Text (STT) and Text-to-Speech (TTS)")

# Tabs for STT and TTS
tab1, tab2 = st.tabs(["🗣️ Speech-to-Text", "📝 Text-to-Speech"])

with tab1:
    st.header("Speech-to-Text")
    audio_file = st.file_uploader("Upload an audio file:", type=["wav", "mp3", "m4a"])

    if st.button("Transcribe Audio"):
        if audio_file:
            try:
                api_url = "http://localhost:5000/transcribe_audio"
                files = {"file": audio_file.getvalue()}
                with st.spinner("Transcribing audio..."):
                    response = requests.post(api_url, files={"file": audio_file})

                if response.status_code == 200:
                    result = response.json()
                    st.success("Transcription Complete!")
                    st.write(f"**Detected Language:** {result['language']}")
                    st.write(f"**Transcription:** {result['transcription']}")
                else:
                    st.error(f"Error: {response.json().get('error', 'Unknown error')}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
        else:
            st.warning("Please upload an audio file.")

with tab2:
    st.header("Text-to-Speech")
    with st.form("tts_form"):
        model_name = st.selectbox(
            "Select a model:",
            ["gguf", "wisher_tiny"],
            help="Choose between GGUF or Wisher Tiny for speech synthesis.",
        )
        text = st.text_area("Enter text for speech synthesis:", height=150)
        temperature = st.slider("Temperature (stability vs expressiveness)", 0.1, 2.0, 0.1)
        repetition_penalty = st.slider("Repetition Penalty", 0.5, 2.0, 1.1)
        max_length = st.number_input("Maximum Length", min_value=100, max_value=4096, value=4096)

        submitted = st.form_submit_button("Generate Speech")

    if submitted:
        api_url = "http://localhost:5000/generate_tts"
        payload = {
            "text": text,
            "model_name": model_name,
            "temperature": temperature,
            "repetition_penalty": repetition_penalty,
            "max_length": max_length,
        }

        with st.spinner("Generating speech..."):
            response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            output_file = f"{model_name}_output.wav"
            with open(output_file, "wb") as f:
                f.write(response.content)

            st.audio(output_file, format="audio/wav")
            st.success("Speech synthesis complete!")
        else:
            st.error(f"Error: {response.json().get('error', 'Unknown error')}")

