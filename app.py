from requests.exceptions import ConnectionError
from flask import Flask, request
from flask_cors import CORS
import os

# ------------------ SETUP ------------------

app = Flask(__name__)
CORS(app)  # allows cross-origin requests; configure in production for security

# ------------------ EXCEPTION HANDLERS ------------------

@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return {"error": str(e)}, 500

@app.errorhandler(ConnectionError)
def handle_connection_error(e):
    print(e)
    return {"error": "Internal service error"}, 500

# ------------------ TEST ENDPOINT ------------------

@app.route("/ping", methods=["GET"])
def ping():
    return {"status": "ok"}

# ------------------ CUSTOM API ------------------

@app.route("/chat", methods=["POST"])
def chat():
    from services.custom import Custom
    custom = Custom()
    body = request.json
    return custom.chat(body)

@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    from services.custom import Custom
    custom = Custom()
    body = request.json
    return custom.chat_stream(body)

@app.route("/files", methods=["POST"])
def files():
    from services.custom import Custom
    custom = Custom()
    return custom.files(request)

# ------------------ OPENAI API ------------------

@app.route("/openai-chat", methods=["POST"])
def openai_chat():
    from services.openAI import OpenAI
    open_ai = OpenAI()
    body = request.json
    return open_ai.chat(body)

@app.route("/openai-chat-stream", methods=["POST"])
def openai_chat_stream():
    from services.openAI import OpenAI
    open_ai = OpenAI()
    body = request.json
    return open_ai.chat_stream(body)

@app.route("/openai-image", methods=["POST"])
def openai_image():
    from services.openAI import OpenAI
    open_ai = OpenAI()
    files = request.files.getlist("files")
    return open_ai.image_variation(files)

# ------------------ HUGGING FACE API ------------------

@app.route("/huggingface-conversation", methods=["POST"])
def hugging_face_conversation():
    from services.huggingFace import HuggingFace
    huggingFace = HuggingFace()
    body = request.json
    return huggingFace.conversation(body)

@app.route("/huggingface-image", methods=["POST"])
def hugging_face_image_classification():
    from services.huggingFace import HuggingFace
    huggingFace = HuggingFace()
    files = request.files.getlist("files")
    return huggingFace.image_classification(files)

@app.route("/huggingface-speech", methods=["POST"])
def hugging_face_speech_recognition():
    from services.huggingFace import HuggingFace
    huggingFace = HuggingFace()
    files = request.files.getlist("files")
    return huggingFace.speech_recognition(files)

# ------------------ STABILITY AI API ------------------

@app.route("/stability-text-to-image", methods=["POST"])
def stabilityai_text_to_image():
    from services.stabilityAI import StabilityAI
    stability_ai = StabilityAI()
    body = request.json
    return stability_ai.text_to_image(body)

@app.route("/stability-image-to-image", methods=["POST"])
def stabilityai_image_to_image():
    from services.stabilityAI import StabilityAI
    stability_ai = StabilityAI()
    return stability_ai.image_to_image(request)

@app.route("/stability-image-upscale", methods=["POST"])
def stabilityai_image_to_image_upscale():
    from services.stabilityAI import StabilityAI
    stability_ai = StabilityAI()
    files = request.files.getlist("files")
    return stability_ai.image_to_image_upscale(files)

# ------------------ COHERE API ------------------

@app.route("/cohere-chat", methods=["POST"])
def cohere_chat():
    from services.cohere import Cohere
    cohere = Cohere()
    body = request.json
    return cohere.chat(body)

@app.route("/cohere-generate", methods=["POST"])
def cohere_generate_text():
    from services.cohere import Cohere
    cohere = Cohere()
    body = request.json
    return cohere.generate_text(body)

@app.route("/cohere-summarize", methods=["POST"])
def cohere_summarize_text():
    from services.cohere import Cohere
    cohere = Cohere()
    body = request.json
    return cohere.summarize_text(body)

# ------------------ RUN SERVER ------------------
# No app.run() needed; Railway uses gunicorn
# Ensure Procfile exists with:
# web: gunicorn app:app --bind 0.0.0.0:$PORT
