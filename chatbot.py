import os
import time
import random
from google import genai
from google.genai import types
from dotenv import load_dotenv
from database import livres_vers_contexte

load_dotenv()

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    print("⚠️ Warning: GEMINI_API_KEY not found in .env file!")

client = genai.Client(api_key=GEMINI_API_KEY)

# Replace the old retired list with active Gemini models
MODELS = [
    "gemini-2.5-flash",       # The current primary fast model
    "gemini-2.5-flash-lite",  # The highly efficient fallback model
]

SYSTEME_PROMPT = """
Tu es un assistant intelligent intégré dans une bibliothèque française moderne.
Tu réponds TOUJOURS en français, de façon claire, chaleureuse et utile.

Instructions pour les réponses :

1. QUESTIONS GÉNÉRALES (Histoire, Météo, Culture, Sciences, etc.) :
- Tu es pleinement autorisé à répondre à TOUTES les questions générales en utilisant tes propres connaissances.
- Conserve un ton accueillant, professionnel et curieux (comme un bibliothécaire passionné).

2. QUESTIONS SUR LE CATALOGUE DE LA BIBLIOTHÈQUE :
Si la question porte explicitement sur les livres disponibles dans notre établissement :
- Base-toi uniquement sur les données du catalogue fourni.
- Ne jamais inventer de livres ou d'auteurs absents du catalogue de la bibliothèque.
- Si un livre demandé n'est pas dans le catalogue, dis-le honnêtement (tu peux tout de même en parler de manière culturelle, mais précise bien qu'il n'est pas disponible chez nous).

Format à respecter UNIQUEMENT pour lister les livres du catalogue :
Titre - Auteur | Statut | N exemplaire(s)

Emojis de statut pour le catalogue :
disponible |  emprunte |  reserve
"""

def poser_question(question: str, historique: list) -> str:
    contexte_livres = livres_vers_contexte()

    message_avec_contexte = (
        "Voici le catalogue actuel de la bibliotheque :\n\n"
        + contexte_livres
        + "\n\n---\nQuestion : " + question
    )

    contents = []
    for msg in historique:
        contents.append(
            types.Content(role=msg["role"],
                          parts=[types.Part(text=msg["parts"][0]["text"])])
        )
    contents.append(
        types.Content(role="user",
                      parts=[types.Part(text=message_avec_contexte)])
    )

    last_error = None
    
    for model in MODELS:
        # Retry mechanism for the same model before jumping to the next one
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEME_PROMPT,
                        max_output_tokens=1024,
                        temperature=0.7,
                    )
                )
                reponse_texte = response.text
                historique.append({"role": "user",  "parts": [{"text": question}]})
                historique.append({"role": "model", "parts": [{"text": reponse_texte}]})
                return reponse_texte

            except Exception as e:
                err = str(e)
                
                # If it's a quota error, wait slightly and try again (Exponential Backoff)
                if "429" in err or "quota" in err.lower() or "RESOURCE_EXHAUSTED" in err:
                    last_error = f"quota depasse sur {model}"
                    if attempt < max_retries - 1:
                        # Wait 2s, then 4s, with a little bit of random "jitter"
                        sleep_time = (2 ** attempt) + random.uniform(0, 1)
                        time.sleep(sleep_time)
                        continue # try the same model again
                    else:
                        break # Exceeded retries for this model, move to next model in MODELS
                
                if "404" in err or "not found" in err.lower():
                    last_error = "modele indisponible : " + model
                    break # Move to the next model immediately
                    
                if "401" in err or "403" in err or "API_KEY" in err:
                    return (
                        "Cle API invalide.\n"
                        "Verifiez votre cle sur https://ai.google.devn"
                        "Puis relancez : $env:GEMINI_API_KEY=\"AIzaSyBm_5edTp0mzsZBgSu8IK368cmfZ-yO8Co\""
                    )
                return "Erreur : " + err

    return f"Erreur : Impossible de répondre. Tout les quotas sont épuisés. ({last_error})"