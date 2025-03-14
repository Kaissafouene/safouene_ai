from flask import Flask, request, render_template, jsonify
import requests
import time
import re
import html  # Module pour convertir les entités HTML

app = Flask(__name__)

# Clé API Gemini (à remplacer par votre clé)
API_KEY = "AIzaSyDqDBu-Ga_lCl_FpdtEv0GBM0yOK8i4V9E"
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# Domaine de spécialisation du chatbot
SPECIALIZATION = "entraînement, nutrition et compléments alimentaires"

def ask_gemini(prompt):
    """
    Envoie une requête à l'API Gemini et retourne la réponse.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "maxOutputTokens": 2000  # Augmentez le nombre de tokens pour des réponses plus longues
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()  # Lève une exception si la requête échoue
        result = response.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as err:
        return f"Erreur lors de la communication avec Safouene AI : {err}"

def format_response(response):
    """
    Formate la réponse du chatbot pour supprimer les balises HTML, convertir les entités HTML et améliorer l'affichage.
    """
    # Convertir les entités HTML en caractères normaux (ex : &#39; -> ')
    response = html.unescape(response)
    
    # Supprimer toutes les balises HTML
    response = re.sub(r'<[^>]+>', '', response)
    
    # Remplacer les astérisques par des puces
    response = response.replace("* ", "• ")
    
    # Supprimer les doubles sauts de ligne
    response = response.replace("\n\n", "\n")
    
    # Retourner la réponse formatée
    return response

def is_off_topic(question):
    """
    Vérifie si la question est hors du domaine de spécialisation.
    """
    off_topic_keywords = ["politique", "histoire", "divertissement", "cinéma", "musique", "jeux vidéo", "santé mentale", "médecine"]
    for keyword in off_topic_keywords:
        if keyword in question.lower():
            return True
    return False

@app.route("/", methods=["GET", "POST"])
def home():
    """
    Route principale pour l'interface du chatbot.
    """
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if is_off_topic(user_input):
            response = f"Désolé, je suis un AI spécialisé dans le domaine de l'{SPECIALIZATION}. Posez-moi une question sur ce sujet !"
        else:
            response = ask_gemini(f"Tu es un expert en {SPECIALIZATION}. Réponds à cette question : {user_input}")
            response = format_response(response)  # Formate la réponse
        time.sleep(1)  # Simuler un temps de réponse
        return jsonify({"response": response})
    return render_template("chatbot.html")

if __name__ == "__main__":
    app.run()
