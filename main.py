

import os, sys
from database import (
    initialiser_db, inserer_donnees_demo,
    ajouter_livre, lister_livres, obtenir_livre_par_id,
    rechercher_livres, modifier_livre, supprimer_livre
)
from chatbot import poser_question

SEP = "─" * 68

def c(code, txt):
    codes = {"titre":"\033[1;36m","ok":"\033[1;32m","err":"\033[1;31m",
             "info":"\033[1;33m","bot":"\033[1;35m","r":"\033[0m"}
    return f"{codes[code]}{txt}{codes['r']}" if sys.stdout.isatty() else txt

def afficher(l, compact=False):
    em = {"disponible":"disponible","emprunté":"emprunté","réservé":"réservé"}.get(l["statut"],"❓")
    if compact:
        print(f"  [{l['id_livre']:>3}] {l['titre'][:38]:<38} {l['auteur'][:22]:<22} {em} {l['statut']}")
    else:
        for k,v in [("ID",l['id_livre']),("Titre",l['titre']),("Auteur",l['auteur']),
                    ("Catégorie",l['categorie']),("Année",l['annee_publication']),
                    ("Quantité",l['quantite_disponible']),("Statut",f"{em} {l['statut']}")]:
            print(f"  {k:<22}: {v}")

def saisir(msg, defaut=""):
    v = input(f"  {msg}{f' [{defaut}]' if defaut else ''} : ").strip()
    return v or defaut

def saisir_int(msg, defaut=None):
    while True:
        r = saisir(msg, str(defaut) if defaut is not None else "")
        try: return int(r)
        except ValueError: print(c("err","  Entrez un entier."))

def menu_lister():
    print(c("titre","\n  CATALOGUE COMPLET")); print(SEP)
    ls = lister_livres()
    if not ls: print("  Bibliothèque vide."); return
    print(f"  {'ID':>5}  {'Titre':<39} {'Auteur':<23} Statut")
    print("  " + "─"*66)
    for l in ls: afficher(l, compact=True)
    print(f"\n  Total : {len(ls)} livre(s)")

def menu_ajouter():
    print(c("titre","\n AJOUTER UN LIVRE")); print(SEP)
    t = saisir("Titre"); 
    if not t: print(c("err","  Titre obligatoire.")); return
    a = saisir("Auteur"); cat = saisir("Catégorie")
    an = saisir_int("Année", 2024); q = saisir_int("Quantité", 1)
    s = saisir("Statut (disponible/emprunté/réservé)", "disponible")
    nid = ajouter_livre(t, a, cat, an, q, s)
    print(c("ok", f"\n    Ajouté ! ID = {nid}"))

def menu_rechercher():
    print(c("titre","\n🔍  RECHERCHER")); print(SEP)
    terme = saisir("Titre, auteur ou ID")
    res = rechercher_livres(terme)
    if not res: print(c("info","  Aucun résultat.")); return
    print(f"\n  {len(res)} résultat(s) :")
    for l in res: print(f"\n  {'─'*42}"); afficher(l)

def menu_modifier():
    print(c("titre","\n  MODIFIER")); print(SEP)
    id_ = saisir_int("ID du livre")
    l = obtenir_livre_par_id(id_)
    if not l: print(c("err",f"  Introuvable.")); return
    afficher(l); print(c("info","\n  (Entrée = conserver)\n"))
    t  = saisir("Titre",    l["titre"])
    a  = saisir("Auteur",   l["auteur"])
    cat= saisir("Catégorie",l["categorie"])
    an = saisir_int("Année", l["annee_publication"])
    q  = saisir_int("Quantité", l["quantite_disponible"])
    s  = saisir("Statut",   l["statut"])
    if modifier_livre(id_, t, a, cat, an, q, s): print(c("ok","    Mis à jour !"))
    else: print(c("err","  Échec."))

def menu_supprimer():
    print(c("titre","\n   SUPPRIMER")); print(SEP)
    id_ = saisir_int("ID du livre")
    l = obtenir_livre_par_id(id_)
    if not l: print(c("err","  Introuvable.")); return
    print(f"  → « {l['titre']} » — {l['auteur']}")
    if input("  Confirmer ? (o/N) : ").strip().lower() == "o":
        supprimer_livre(id_); print(c("ok","   Supprimé."))
    else: print("  Annulé.")

def menu_chatbot():
    print(c("bot","\n CHATBOT IA")); print(SEP)
    print("  Tapez 'quitter' pour revenir.\n")
    hist = []
    while True:
        try: q = input(c("info","  Vous : ")).strip()
        except (EOFError, KeyboardInterrupt): print(); break
        if not q: continue
        if q.lower() in ("quitter","exit","q"): break
        rep = poser_question(q, hist)
        print(c("bot","\n  🤖 Assistant :"))
        for ln in rep.split("\n"): print(f"     {ln}")
        print()

MENU = """
{sep}
  {t}
{sep}
  [1]   Lister    [2]   Ajouter    [3]   Rechercher
  [4]   Modifier   [5]   Supprimer  [6]   Chatbot IA
  [0]   Quitter
{sep}
"""

def main():
    os.system("cls" if os.name=="nt" else "clear")
    print(c("titre","\n"+"═"*68))
    print(c("titre","      BIBLIOTHÈQUE INTELLIGENTE — Interface CLI"))
    print(c("titre","═"*68))
    initialiser_db(); inserer_donnees_demo()
    print(c("ok","    Base de données prête.\n"))
    print(c("info","    Interface graphique disponible : python app.py"))
    actions = {"1":menu_lister,"2":menu_ajouter,"3":menu_rechercher,
               "4":menu_modifier,"5":menu_supprimer,"6":menu_chatbot}
    while True:
        print(MENU.format(sep=SEP, t=c("titre","  MENU PRINCIPAL")))
        ch = input("  Choix : ").strip()
        if ch == "0": print(c("ok","\n  Au revoir ! \n")); sys.exit(0)
        elif ch in actions:
            actions[ch]()
            input(c("info","\n  [Entrée pour continuer…]"))
        else:
            print(c("err","  Choix invalide."))

if __name__ == "__main__":
    main()
