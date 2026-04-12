from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from transformers import pipeline
import os
import requests

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
model = os.getenv("MISTRAL_MODEL")

emotion_classifier = pipeline("sentiment-analysis", model="j-hartmann/emotion-english-distilroberta-base", top_k=1)

url = "https://openrouter.ai/api/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://ai-psychology.local",
    "X-Title": "AI Psychology Chatbot",
    "Content-Type": "application/json"
}

app = Flask(__name__)

danger_keywords = [
    "kill myself", "suicide", "end my life", "hurt others", "no reason live", "want to die",
    "kill everyone", "ending the world", "i will kill", "i hate my life"
]

system_prompt = {
    "role": "system",
    "content": "You are an AI Expert Psychologist with 20 years of experience in CBT therapy. Respond with empathy and professionalism. Keep responses under 6 lines. Always end with a follow-up question."
}

messages = [system_prompt]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message", "")

    if any(phrase in user_input.lower() for phrase in danger_keywords):
        return jsonify({"reply": "I hear how much pain you are in. You are not alone. Please speak to a licensed psychologist or call a crisis helpline immediately."})

    emotion_result = emotion_classifier(user_input)[0][0]
    detected_emotion = emotion_result['label']

    messages.append({
        "role": "user",
        "content": f"{user_input} (emotion detected: {detected_emotion})"
    })

    data = {
        "model": model,
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        if response.status_code == 200:
            resp_json = response.json()
            reply = resp_json["choices"][0]["message"]["content"]
            messages.append({"role": "assistant", "content": reply})
            return jsonify({"reply": reply})
        else:
            return jsonify({"reply": f"API Error: {response.text}"})
    except Exception as e:
        return jsonify({"reply": "Error: " + str(e)})

if __name__ == "__main__":
    app.run(debug=True)