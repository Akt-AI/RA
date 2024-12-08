from flask import Flask, request, jsonify, send_file
import outetts
import os
from io import BytesIO

app = Flask(__name__)

# Configure the GGUF model
model_config = outetts.GGUFModelConfig_v1(
    model_path="/home/arun/workspace/RAG_with_web/OuteTTS-0.2-500M-Q2_K.gguf",
    language="en",
)

# Initialize the interface
interface = outetts.interface.InterfaceGGUF(model_version="0.2", cfg=model_config)

# Load the default speaker
speaker = interface.load_default_speaker(name="male_1")


@app.route('/generate_tts', methods=['POST'])
def generate_tts():
    try:
        # Get input data
        data = request.json
        text = data.get('text', '')
        temperature = float(data.get('temperature', 0.1))
        repetition_penalty = float(data.get('repetition_penalty', 1.1))
        max_length = int(data.get('max_length', 4096))

        # Check if text is provided
        if not text:
            return jsonify({"error": "Text input is required"}), 400

        # Generate speech
        output = interface.generate(
            text=text,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            max_length=max_length,
            speaker=speaker,
        )

        # Save the output to a temporary file
        output_file = "output_gguf.wav"
        output.save(output_file)

        # Send the file as a response
        return send_file(output_file, mimetype='audio/wav', as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

