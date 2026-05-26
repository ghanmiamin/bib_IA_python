

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bibliotheque.db")

STATUTS_VALIDES = ["disponible", "emprunté", "réservé"]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialiser_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS livres (
            id_livre            INTEGER PRIMARY KEY AUTOINCREMENT,
            titre               TEXT    NOT NULL,
            auteur              TEXT    NOT NULL,
            categorie           TEXT    NOT NULL,
            annee_publication   INTEGER,
            quantite_disponible INTEGER DEFAULT 1,
            statut              TEXT    DEFAULT 'disponible'
        )
    """)
    conn.commit()
    conn.close()


def ajouter_livre(titre, auteur, categorie, annee, quantite, statut="disponible"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO livres (titre, auteur, categorie, annee_publication,
                            quantite_disponible, statut)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (titre, auteur, categorie, annee, quantite, statut))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def lister_livres():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres ORDER BY id_livre")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def obtenir_livre_par_id(id_livre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM livres WHERE id_livre = ?", (id_livre,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def rechercher_livres(terme):
    conn = get_connection()
    cursor = conn.cursor()
    if str(terme).isdigit():
        cursor.execute("SELECT * FROM livres WHERE id_livre = ?", (int(terme),))
    else:
        like = f"%{terme}%"
        cursor.execute(
            "SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ? OR categorie LIKE ?",
            (like, like, like)
        )
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def modifier_livre(id_livre, titre, auteur, categorie, annee, quantite, statut):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE livres
        SET titre = ?, auteur = ?, categorie = ?,
            annee_publication = ?, quantite_disponible = ?, statut = ?
        WHERE id_livre = ?
    """, (titre, auteur, categorie, annee, quantite, statut, id_livre))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated


def supprimer_livre(id_livre):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM livres WHERE id_livre = ?", (id_livre,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted


def livres_vers_contexte():
    livres = lister_livres()
    if not livres:
        return "La bibliothèque est actuellement vide."
    lignes = ["=== Catalogue de la bibliothèque ==="]
    for l in livres:
        lignes.append(
            f"ID:{l['id_livre']} | Titre: {l['titre']} | Auteur: {l['auteur']} | "
            f"Catégorie: {l['categorie']} | Année: {l['annee_publication']} | "
            f"Qté: {l['quantite_disponible']} | Statut: {l['statut']}"
        )
    return "\n".join(lignes)


def stats_bibliotheque():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM livres")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM livres WHERE statut='disponible'")
    disponibles = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM livres WHERE statut='emprunté'")
    empruntes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM livres WHERE statut='réservé'")
    reserves = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(DISTINCT auteur) FROM livres")
    auteurs = cursor.fetchone()[0]
    conn.close()
    return {
        "total": total,
        "disponibles": disponibles,
        "empruntes": empruntes,
        "reserves": reserves,
        "auteurs": auteurs
    }


def inserer_donnees_demo():
    if lister_livres():
        return
    demo = [
        ("Le Petit Prince",       "Antoine de Saint-Exupéry", "Roman",        1943, 3, "disponible"),
        ("Les Misérables",        "Victor Hugo",               "Roman",        1862, 1, "emprunté"),
        ("Notre-Dame de Paris",   "Victor Hugo",               "Roman",        1831, 2, "disponible"),
        ("Les Contemplations",    "Victor Hugo",               "Poésie",       1856, 1, "disponible"),
        ("Orgueil et Préjugés",   "Jane Austen",               "Roman",        1813, 2, "disponible"),
        ("Jane Eyre",             "Charlotte Brontë",          "Roman",        1847, 1, "disponible"),
        ("Le Rouge et le Noir",   "Stendhal",                  "Roman",        1830, 1, "emprunté"),
        ("L'Étranger",            "Albert Camus",              "Roman",        1942, 2, "disponible"),
        ("Algorithmes en Python", "Thomas H. Cormen",          "Informatique", 2009, 4, "disponible"),
        ("Introduction à l'IA",   "Stuart Russell",            "Informatique", 2020, 2, "réservé"),
        ("Don Quichotte",         "Miguel de Cervantes",       "Roman",        1605, 1, "disponible"),
        ("Madame Bovary",         "Gustave Flaubert",          "Roman",        1857, 2, "disponible"),
    ]
    for t, a, c, an, q, s in demo:
        ajouter_livre(t, a, c, an, q, s)
