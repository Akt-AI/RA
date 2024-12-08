from flask import Flask, request, jsonify, send_file
import outetts
import whisper
import os
from io import BytesIO

app = Flask(__name__)

# TTS Model configurations
GGUF_MODEL_PATH = "/home/arun/workspace/RAG_with_web/models/OuteTTS-0.2-500M-Q2_K.gguf"
# WISHER_TINY_MODEL_PATH = "/home/arun/workspace/RAG_with_web/WisherTinyModelPath.gguf"

# Initialize GGUF model
gguf_config = outetts.GGUFModelConfig_v1(
    model_path=GGUF_MODEL_PATH,
    language="en",
)
gguf_interface = outetts.interface.InterfaceGGUF(model_version="0.2", cfg=gguf_config)
gguf_speaker = gguf_interface.load_default_speaker(name="male_1")

# Initialize Wisher Tiny model
# )
# wisher_tiny_interface = outetts.interface.InterfaceGGUF(model_version="0.2", cfg=wisher_tiny_config)
# wisher_tiny_speaker = wisher_tiny_interface.load_default_speaker(name="male_1")

# Initialize Whisper model for STT
whisper_model = whisper.load_model("tiny")


@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    try:
        data = request.json
        text = data.get('text', '')
        model_name = data.get('model_name', 'gguf')
        temperature = float(data.get('temperature', 0.1))
        repetition_penalty = float(data.get('repetition_penalty', 1.1))
        max_length = int(data.get('max_length', 4096))

        if not text:
            return jsonify({"error": "Text input is required"}), 400

        if model_name == "gguf":
            interface = gguf_interface
            speaker = gguf_speaker
        elif model_name == "wisher_tiny":
            interface = wisher_tiny_interface
            speaker = wisher_tiny_speaker
        else:
            return jsonify({"error": f"Unknown model: {model_name}"}), 400

        output = interface.generate(
            text=text,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            max_length=max_length,
            speaker=speaker,
        )

        output_file = f"{model_name}_output.wav"
        output.save(output_file)
        return send_file(output_file, mimetype='audio/wav', as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "Audio file is required"}), 400

        file = request.files['file']  # FileStorage object
        if not file:
            return jsonify({"error": "Invalid file"}), 400

        # Save the file temporarily
        temp_file_path = "temp_audio_file.wav"
        file.save(temp_file_path)

        # Load and process audio using Whisper
        audio = whisper.load_audio(temp_file_path)
        audio = whisper.pad_or_trim(audio)

        # Generate Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio).to(whisper_model.device)

        # Detect language
        _, probs = whisper_model.detect_language(mel)
        detected_language = max(probs, key=probs.get)

        # Decode audio
        options = whisper.DecodingOptions()
        result = whisper.decode(whisper_model, mel, options)

        # Remove the temporary file
        os.remove(temp_file_path)

        return jsonify({"transcription": result.text, "language": detected_language})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

