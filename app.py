from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from transformers import pipeline
import os
import requests

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

print("KEY:", api_key[:8] if api_key else "MISSING")

app = Flask(__name__)

# Emotion Model 
emotion_classifier = pipeline(
    "sentiment-analysis",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

#  OpenRouter Config 
OR_URL = "https://openrouter.ai/api/v1/chat/completions"
OR_HEADERS = {
    "Authorization": f"Bearer {api_key}",
    "HTTP-Referer": "https://ai-psychology.local",
    "X-Title": "MindEase Chatbot",
    "Content-Type": "application/json"
}

MODELS = [
    "openai/gpt-oss-20b:free",                  
    "openai/gpt-oss-120b:free",                 
    "mistralai/devstral-small:free",            
    "google/gemma-3-4b-it:free",               
]

CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die",
    "dont want to live", "don't want to live", "no reason to live",
    "hurt myself", "hurt others", "i will kill", "kill everyone",
    "khud ko maarna", "marna chahta", "zindagi khatam",
    "jeena nahi chahta", "mujhe jeena nahi", "mar jao"
    "want to give up", "give up", "nothing feels worth it", "not worth it",
]

CRISIS_REPLY = (
    "I hear how much pain you are in right now. You are not alone. "
    "Please call Umang Pakistan immediately: 0317-4288665. "
    "They are available 24/7 and truly care about you. 💙"
)

EMOTION_KEYWORDS = {
    "neutral": [
        "hi", "hello", "hey", "hiya", "salam", "aoa", "helo", "assalam",
        "fine", "good", "okay", "ok", "great", "alright", "happy", "better"
    ],
    "guilt": [
        "my fault", "is my fault", "all my fault", "fault", "blame",
        "guilty", "guilt", "failed", "failure", "ruined",
        "i failed", "ashamed", "shame", "regret", "sorry for",
        "i ruined", "because of me", "i should have"
        "blaming myself", "blame myself", "self blame", "my fault again",
        "stop blaming", "cant stop blaming", "keep blaming",
    ],
    "anxiety": [
        "anxious", "anxiety", "stressed", "stress", "tension", "tense",
        "worried", "worry", "worrying", "overthink", "overthinking",
        "panic", "nervous", "fear", "scared", "tense",
        # Roman Urdu
        "tension ho", "ghabra", "dar lag", "fikar", "pareshan"
        "pareshan",
        "kia krn ab", "samajh nahi aa rha", "muje nahi pata", "confused",
    ],
    "anger": [
        "angry", "anger", "furious", "hate", "rage", "frustrated",
        "frustrating", "irritated", "irritating", "annoyed", "annoying",
        # Roman Urdu
        "gussa", "naraaz", "nafrat"
    ],
    "sadness": [
        "broken", "exhausted", "empty", "hopeless", "sad", "sadness",
        "depressed", "depression", "tired", "lonely", "alone", "cry",
        "crying", "tears", "hurt", "pain", "grief", "lost", "miss",
        "stuck", "numb", "overwhelmed", "helpless", "worthless", "useless",
        # Roman Urdu
        "udaas", "dukhi", "rona", "akela", "thaka", "toota" "toota",
        "koi nahi", "kon bny", "dost nahi", "ghr waly", "glt khty",
        "smjh nahi", "kia krun", "akela hun", "muje smjh",
    ],
}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are MindEase, a warm and empathetic mental health support assistant trained in CBT.\n\n"
        "LANGUAGE: Detect the CURRENT message language and reply ONLY in that language. Short greetings like hi, hello, hey are English, reply in English. If Urdu script or Roman Urdu, reply in Urdu. Never mix.\n\n"
        "STYLE: Max 2 sentences only. Short, warm, simple words. No bullet points. No lists.\n\n"
        "BEHAVIOR:\n"
        "- First message: Ask how they are feeling today.\n"
        "- Never ask how they are feeling if they already described their emotions.\n"
        "- Always acknowledge the specific emotion mentioned before asking a question.\n"
        "- Validate feelings before giving advice.\n"
        "- Gently apply CBT techniques when appropriate.\n"
        "- Never diagnose. Recommend professional help when needed.\n\n"
        "CRISIS: If suicide or self-harm is mentioned say: "
        "I hear your pain. Please call Umang Pakistan: 0317-4288665. You are not alone.\n\n"
        "Always end with one gentle caring question or encouraging sentence."
        "Never use dashes (— or -) in replies. Use commas instead.\n\n"
        
    )
}

def detect_emotion(text: str) -> str:
    """Keyword-first, then ML fallback. Returns: neutral | guilt | anxiety | anger | sadness"""
    import re
    lower = text.lower()

    def matches(word, text):
        if " " in word:           # multi-word phrase: simple substring
            return word in text
        return bool(re.search(r'\b' + re.escape(word) + r'\b', text))

    # Keyword check — priority order matters (neutral first to catch greetings)
    for emotion, words in EMOTION_KEYWORDS.items():
        if any(matches(w, lower) for w in words):
            return emotion

    # ML fallback — only trust high-confidence predictions
    try:
        result = emotion_classifier(text)[0][0]
        label, score = result["label"].lower(), result["score"]
        if score > 0.75 and label in ("sadness", "fear", "anger", "disgust"):
            mapping = {"fear": "anxiety", "disgust": "anger"}
            return mapping.get(label, label)
    except Exception as e:
        print("Emotion model error:", e)

    return "neutral"


def build_messages(history: list, user_input: str) -> list:
    # Detect language from current message
    urdu_chars = "ابپتٹثجچحخدڈذرڑزژسشصضطظعغفقکگلمنوہھیے"
    roman_urdu = ["muje", "mujhe", "kia", "krn", "ghr", "waly", "smjh", "nh", "kon", "bny", "onhein", "bohat", "nahi", "hyn", "hain", "rha", "karo", "tha", "thi", "ho", "ar", "aj"]
    is_urdu = any(c in urdu_chars for c in user_input) or any(w in user_input.lower().split() for w in roman_urdu)
    lang = "Urdu" if is_urdu else "English"
    
    lang_msg = {"role": "user", "content": f"[SYSTEM NOTE: Reply in {lang} only]"}
    
    messages = [SYSTEM_PROMPT]
    messages.extend(history)
    messages.append(lang_msg)
    messages.append({"role": "user", "content": user_input})
    return messages


def call_openrouter(messages: list) -> str | None:
    """Try each model in MODELS list until one returns a valid reply."""
    for model_name in MODELS:
        try:
            payload = {
                "model": model_name,
                "messages": messages,
                "max_tokens": 150,
                "temperature": 0.7
            }
            resp = requests.post(OR_URL, headers=OR_HEADERS, json=payload, timeout=15)
            print(f"[{model_name}] STATUS: {resp.status_code}")

            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"].get("content", "").strip()
                if content:
                    print(f"[{model_name}] SUCCESS ✓")
                    return content
                print(f"[{model_name}] Empty response — trying next model")

            else:
                print(f"[{model_name}] ERROR {resp.status_code} — trying next model")

        except requests.exceptions.Timeout:
            print(f"[{model_name}] TIMEOUT — trying next model")
        except Exception as e:
            print(f"[{model_name}] EXCEPTION: {e} — trying next model")

    return None 

def trim_to_two_sentences(text: str) -> str:
    import re
    text = text.replace("—", ",").replace("–", ",")
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s for s in sentences if s.strip()]
    return " ".join(sentences[:2])


#  Routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat-page")
def chat_page():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    data       = request.json or {}
    user_input = data.get("message", "").strip()
    history    = data.get("history", [])

    if not user_input:
        return jsonify({"reply": "Please share what's on your mind. I'm here for you."})

    # Crisis check — highest priority
    if any(phrase in user_input.lower() for phrase in CRISIS_KEYWORDS):
        return jsonify({"reply": CRISIS_REPLY, "emotion": "crisis"})

    # Detect emotion
    emotion = detect_emotion(user_input)

    # Call LLM with fallback chain
    messages = build_messages(history, user_input)
    reply    = call_openrouter(messages)

    if not reply:
        reply = "I'm here for you. Could you tell me a little more about how you're feeling?"

    reply = trim_to_two_sentences(reply)
    return jsonify({"reply": reply, "emotion": emotion})
    

# Run
if __name__ == "__main__":
    app.run(debug=True)