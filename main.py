import nltk
import spacy
import random
import tkinter as tk
import requests
import re

from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')

nlp = spacy.load("pt_core_news_sm")


url = "https://www.todamateria.com.br/sistema-solar/"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

for tag in soup(["nav","footer","aside","header","ul","a"]):
    tag.extract()

paragraphs = soup.find_all("p")
paragraphs = paragraphs[:12]

text = ""

for p in paragraphs:
    text += p.get_text() + " "

sentences = nltk.sent_tokenize(text)


filtered = []

for s in sentences:

    s = s.strip()

    if len(s) < 25:
        continue

    if len(s) > 200:
        continue

    bad = ["segundo","imagem","figura","veja","clique","fonte"]

    if any(b in s.lower() for b in bad):
        continue

    filtered.append(s)

sentences = filtered



def preprocessing(sentence):

    sentence = sentence.lower()

    doc = nlp(sentence)

    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct
    ]

    return " ".join(tokens)



def answer(user_text):

    all_sentences = sentences.copy()
    all_sentences.append(user_text)

    cleaned = [preprocessing(s) for s in all_sentences]

    tfidf = TfidfVectorizer()
    vectors = tfidf.fit_transform(cleaned)

    similarity = cosine_similarity(vectors[-1], vectors[:-1])
    scores = similarity.flatten()

    keywords = preprocessing(user_text).split()

    for i, s in enumerate(sentences):

        s_lower = s.lower()

        for word in keywords:

            if re.search(r"\b" + word + r"\b", s_lower):
                scores[i] += 0.25


        for word in keywords:
            if s_lower.startswith(word):
                scores[i] += 0.40

        
        if " é " in s_lower or " são " in s_lower:
            scores[i] += 0.05

    index = scores.argmax()
    score = scores[index]

    if score < 0.15:
        return "Não encontrei uma resposta."

    return sentences[index]



inputs = ["oi","olá","ola"]

outputs = [
    "Olá! Sou um chatbot sobre o Sistema Solar.",
    "Pergunte algo sobre planetas ou o Sol.",
    "Posso responder sobre o sistema solar."
]

def greeting(text):

    for word in text.split():
        if word.lower() in inputs:
            return random.choice(outputs)

# TKINTER

def send(event=None):

    user = entry.get()

    if not user.strip():
        return

    chat.insert(tk.END, "Você: " + user + "\n")

    greet = greeting(user)

    if greet != None:
        response = greet
    else:
        response = answer(user)

    chat.insert(tk.END, "Bot: " + response + "\n\n")

    entry.delete(0, tk.END)

    chat.see(tk.END)


def clear_chat():
    chat.delete("1.0", tk.END)


window = tk.Tk()
window.title("Chatbot Sistema Solar")
window.geometry("700x500")

frame_chat = tk.Frame(window)
frame_chat.pack(pady=10)

chat = tk.Text(frame_chat, height=20, width=75, wrap="word")
chat.pack(side=tk.LEFT)

scrollbar = tk.Scrollbar(frame_chat, command=chat.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

chat.config(yscrollcommand=scrollbar.set)

frame_input = tk.Frame(window)
frame_input.pack(pady=10)

entry = tk.Entry(frame_input, width=50)
entry.pack(side=tk.LEFT, padx=10)

entry.bind("<Return>", send)

btn_send = tk.Button(frame_input, text="Enviar", command=send)
btn_send.pack(side=tk.LEFT, padx=5)

btn_clear = tk.Button(frame_input, text="Limpar Chat", command=clear_chat)
btn_clear.pack(side=tk.LEFT, padx=5)

window.mainloop()