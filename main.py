import tkinter as tk
import nltk
import spacy
import random
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gtts import gTTS
import pygame
import tempfile


nltk.download('punkt')
nltk.download('punkt_tab')

nlp = spacy.load("pt_core_news_sm")

pygame.mixer.init()
voice_enabled = True

#conhecimento

with open("conhecimento.txt", "r", encoding="utf-8") as file:
    text = file.read()

sentences = nltk.sent_tokenize(text)

filtered = []

for s in sentences:

    s = s.strip()

    if len(s) < 15:
        continue

    if len(s) > 250:
        continue

    filtered.append(s)

sentences = filtered

#pré-processamento

def preprocessing(sentence):

    sentence = sentence.lower()

    doc = nlp(sentence)

    tokens = [

        token.lemma_

        for token in doc

        if not token.is_stop
        and not token.is_punct

    ]

    return " ".join(tokens)

#sentimento

def sentiment(text):

    text = text.lower()

    positive_words = [

    "feliz", "animado", "alegre", "ótimo",
    "excelente", "bom", "maravilhoso",
    "contente", "empolgado", "motivado"

    ]

    negative_words = [

    "triste", "chateado", "mal",
    "ruim", "péssimo", "deprimido",
    "cansado", "desanimado", "estressado"

    ]

    for word in positive_words:

        if word in text:
            return "positivo"

    for word in negative_words:

        if word in text:
            return "negativo"

    return "neutro"

def toggle_voice():

    global voice_enabled

    voice_enabled = not voice_enabled

    if voice_enabled:

        btn_voice.config(
            text="🔊 Voz ON"
        )

    else:

        btn_voice.config(
            text="🔇 Voz OFF"
        )

#voz

def speak(text):

    global voice_enabled

    if not voice_enabled:
        return

    try:

        tts = gTTS(
            text=text,
            lang="pt-br"
        )

        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        temp_name = temp_file.name

        temp_file.close()

        tts.save(temp_name)

        pygame.mixer.music.load(temp_name)

        pygame.mixer.music.play()

    except Exception:

        print("Falha ao reproduzir voz.")

#resposta

def answer(user_text):

    user_lower = user_text.lower()

    direct_matches = {

        "sol":
        "O Sol é uma estrela localizada no centro do Sistema Solar. O Sol fornece luz e calor para todos os planetas do Sistema Solar.",

        "marte":
        "Marte é conhecido como planeta vermelho devido à presença de óxido de ferro. Marte possui montanhas gigantescas e vulcões enormes.",

        "júpiter":
        "Júpiter é o maior planeta do Sistema Solar. Júpiter possui dezenas de luas.",

        "saturno":
        "Saturno é o planeta que possui anéis compostos por gelo e partículas rochosas. Os anéis de Saturno são uma das características mais conhecidas do Sistema Solar.",

        "terra":
        "A Terra é o terceiro planeta do Sistema Solar e o único conhecido por abrigar vida.",

        "mercúrio":
        "Mercúrio é o planeta mais próximo do Sol.",

        "vênus":
        "Vênus é o segundo planeta do Sistema Solar.",

        "urano":
        "Urano é um planeta gasoso que gira inclinado.",

        "netuno":
        "Netuno é o planeta mais distante do Sol."

    }

    for key in direct_matches:

        if re.search(r"\b" + re.escape(key) + r"\b", user_lower):

            return direct_matches[key]

    if "vermelho" in user_lower:

        return "Marte é conhecido como planeta vermelho devido à presença de óxido de ferro."

    if "anel" in user_lower:

        return "Saturno é o planeta que possui anéis compostos por gelo e partículas rochosas."

    if "maior planeta" in user_lower:

        return "Júpiter é o maior planeta do Sistema Solar."

    if "galáxia" in user_lower:

        return "A Via Láctea é a galáxia onde se encontra o Sistema Solar."
    

    all_sentences = sentences.copy()

    all_sentences.append(user_text)

    cleaned = [

        preprocessing(s)

        for s in all_sentences

    ]

    tfidf = TfidfVectorizer()

    vectors = tfidf.fit_transform(cleaned)

    similarity = cosine_similarity(

        vectors[-1],
        vectors[:-1]

    )

    scores = similarity.flatten()

    if len(scores) == 0:

        return "Não encontrei uma resposta sobre o Sistema Solar."

    best_index = scores.argmax()

    if scores[best_index] < 0.15:

        return "Não encontrei uma resposta sobre o Sistema Solar."

    return sentences[best_index]


random_answers = [

    "Boa pergunta!",
    "Interessante!",
    "Vamos descobrir.",
    "Posso ajudar com isso.",
    "Ótima dúvida."

]

outputs = [

    "Olá! Sou um chatbot sobre o Sistema Solar.",
    "Posso responder perguntas sobre o Sistema Solar.",
    "Pergunte algo sobre planetas, Sol ou galáxias."

]

def greeting(text):

    text = text.lower().strip()

    greetings = [

        "oi",
        "olá",
        "ola",
        "bom dia",
        "boa tarde",
        "boa noite"

    ]

    if text in greetings:

        return random.choice(outputs)

    return None


def send(event=None):

    user = entry.get()

    if not user.strip():
        return

    chat.insert(
        tk.END,
        f"Você: {user}\n"
    )

    greet = greeting(user)

    if greet:

        response = greet

    else:

        mood = sentiment(user)

        knowledge = answer(user)

        if knowledge == "Não encontrei uma resposta sobre o Sistema Solar.":

            if mood == "positivo":

                response = (
                    "Que bom que você está feliz! "
                    "Posso ajudar com perguntas sobre o Sistema Solar."
                )

            elif mood == "negativo":

                response = (
                    "Espero que seu dia melhore. "
                    "Se quiser, também posso responder dúvidas sobre o Sistema Solar."
                )

            else:

                response = knowledge

        else:

            intro = random.choice(random_answers)

            if mood == "positivo":

                response = (
                    "Que bom ver sua animação! "
                    + intro
                    + " "
                    + knowledge
                )

            elif mood == "negativo":

                response = (
                    "Espero ajudar você. "
                    + intro
                    + " "
                    + knowledge
                )

            else:

                response = (
                    intro
                    + " "
                    + knowledge
                )

    chat.insert(
        tk.END,
        f"Bot: {response}\n\n"
    )

    speak(response)

    entry.delete(0, tk.END)

    chat.see(tk.END)


def clear_chat():

    chat.delete(
        "1.0",
        tk.END
    )

#interface

window = tk.Tk()

window.title("🚀 AstroBot - Sistema Solar")

window.geometry("900x650")

window.configure(bg="#0B1026")

frame_chat = tk.Frame(
    window,
    bg="#0B1026"
)

frame_chat.pack(pady=10)

chat = tk.Text(
    frame_chat,
    width=90,
    height=25,
    wrap="word",
    bg="#111827",
    fg="#E5E7EB",
    insertbackground="white",
    font=("Consolas", 11)
)

chat.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(
    frame_chat,
    command=chat.yview
)

scrollbar.pack(
    side=tk.RIGHT,
    fill=tk.Y
)

chat.config(
    yscrollcommand=scrollbar.set
)

frame_input = tk.Frame(
    window,
    bg="#0B1026"
)

frame_input.pack(pady=10)

entry = tk.Entry(
    frame_input,
    width=60,
    bg="#1F2937",
    fg="white",
    insertbackground="white",
    font=("Arial", 11)
)

entry.pack(
    side=tk.LEFT,
    padx=10
)

entry.bind(
    "<Return>",
    send
)

btn_send = tk.Button(
    frame_input,
    text="🚀 Enviar",
    command=send,
    bg="#2563EB",
    fg="white",
    font=("Arial", 10, "bold")
)

btn_send.pack(
    side=tk.LEFT,
    padx=5
)

btn_clear = tk.Button(
    frame_input,
    text="🗑 Limpar",
    command=clear_chat,
    bg="#DC2626",
    fg="white",
    font=("Arial", 10, "bold")
)

btn_clear.pack(
    side=tk.LEFT,
    padx=5
)

btn_voice = tk.Button(
    frame_input,
    text="🔊 Voz ON",
    command=toggle_voice,
    bg="#059669",
    fg="white",
    font=("Arial", 10, "bold")
)

btn_voice.pack(
    side=tk.LEFT,
    padx=5
)

chat.insert(
    tk.END,
    "🚀 AstroBot iniciado!\n"
    "Pergunte qualquer coisa sobre o Sistema Solar.\n\n"
)

window.mainloop()