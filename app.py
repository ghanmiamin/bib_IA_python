

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from database import (
    initialiser_db, inserer_donnees_demo,
    ajouter_livre, lister_livres, obtenir_livre_par_id,
    rechercher_livres, modifier_livre, supprimer_livre,
    stats_bibliotheque, STATUTS_VALIDES
)
from chatbot import poser_question

app = Flask(__name__)
app.secret_key = "bibliotheque_intelligente_2025"

# Historique de conversation du chatbot (en mémoire par session Flask simple)
historique_chat = []

# ──────────────────────────────────────────────────────────────
# Routes principales
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    stats = stats_bibliotheque()
    livres = lister_livres()
    return render_template("index.html", livres=livres, stats=stats,
                           statuts=STATUTS_VALIDES)


@app.route("/rechercher")
def rechercher():
    terme = request.args.get("q", "").strip()
    livres = rechercher_livres(terme) if terme else lister_livres()
    stats = stats_bibliotheque()
    return render_template("index.html", livres=livres, stats=stats,
                           terme=terme, statuts=STATUTS_VALIDES)


# ──────────────────────────────────────────────────────────────
# API REST — CRUD (appelées depuis JavaScript)
# ──────────────────────────────────────────────────────────────

@app.route("/api/livres", methods=["GET"])
def api_lister():
    q = request.args.get("q", "").strip()
    livres = rechercher_livres(q) if q else lister_livres()
    return jsonify(livres)


@app.route("/api/livres/<int:id_livre>", methods=["GET"])
def api_obtenir(id_livre):
    livre = obtenir_livre_par_id(id_livre)
    if not livre:
        return jsonify({"erreur": "Livre introuvable"}), 404
    return jsonify(livre)


@app.route("/api/livres", methods=["POST"])
def api_ajouter():
    data = request.get_json()
    try:
        new_id = ajouter_livre(
            data["titre"], data["auteur"], data["categorie"],
            int(data["annee_publication"]), int(data["quantite_disponible"]),
            data.get("statut", "disponible")
        )
        return jsonify({"success": True, "id_livre": new_id}), 201
    except (KeyError, ValueError) as e:
        return jsonify({"erreur": str(e)}), 400


@app.route("/api/livres/<int:id_livre>", methods=["PUT"])
def api_modifier(id_livre):
    data = request.get_json()
    try:
        ok = modifier_livre(
            id_livre,
            data["titre"], data["auteur"], data["categorie"],
            int(data["annee_publication"]), int(data["quantite_disponible"]),
            data["statut"]
        )
        return jsonify({"success": ok})
    except (KeyError, ValueError) as e:
        return jsonify({"erreur": str(e)}), 400


@app.route("/api/livres/<int:id_livre>", methods=["DELETE"])
def api_supprimer(id_livre):
    ok = supprimer_livre(id_livre)
    return jsonify({"success": ok})


@app.route("/api/stats", methods=["GET"])
def api_stats():
    return jsonify(stats_bibliotheque())


# ──────────────────────────────────────────────────────────────
# Route Chatbot
# ──────────────────────────────────────────────────────────────

@app.route("/chatbot")
def chatbot_page():
    return render_template("chatbot.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    global historique_chat
    data = request.get_json()
    question = data.get("question", "").strip()
    reset = data.get("reset", False)

    if reset:
        historique_chat = []
        return jsonify({"reponse": "Conversation réinitialisée. 👋"})

    if not question:
        return jsonify({"erreur": "Question vide"}), 400

    reponse = poser_question(question, historique_chat)
    return jsonify({"reponse": reponse})


# ──────────────────────────────────────────────────────────────
# Lancement
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    initialiser_db()
    inserer_donnees_demo()
    print("\n" + "═" * 55)
    print("  📚 BIBLIOTHÈQUE INTELLIGENTE — Serveur Web")
    print("═" * 55)
    print("  🌐  Ouvrez votre navigateur sur :")
    print("      http://127.0.0.1:5000")
    print("═" * 55 + "\n")
    app.run(debug=True, host="0.0.0.0", port=5000)
