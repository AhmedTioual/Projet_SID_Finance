# generator.py
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker('fr_FR')
Faker.seed(42)
random.seed(42)

# --- Paramètres généraux ---
nb_clients = 100
nb_foyers = 50
nb_produits = 5
nb_comptes = 120
nb_agences = 10
nb_conseillers = 20
mois_historique = 36  # 3 ans
output_dir = "../output/"

# ------------------ AGENCES ------------------
agences = []
for i in range(1, nb_agences+1):
    agences.append({
        'id_agence': i,
        'nom_agence': f"Agence_{i}",
        'adresse': fake.address(),
        'ville': fake.city(),
        'code_postal': fake.postcode(),
        'telephone': fake.phone_number()
    })
df_agences = pd.DataFrame(agences)
df_agences.to_csv(f"{output_dir}Agences.csv", index=False)

# ------------------ CONSEILLERS ------------------
conseillers = []
for i in range(1, nb_conseillers+1):
    agence = random.choice(df_agences['id_agence'])
    conseillers.append({
        'id_conseiller': i,
        'nom': fake.last_name(),
        'prenom': fake.first_name(),
        'email': fake.email(),
        'telephone': fake.phone_number(),
        'id_agence': agence
    })
df_conseillers = pd.DataFrame(conseillers)
df_conseillers.to_csv(f"{output_dir}Conseillers.csv", index=False)

# ------------------ FOYERS ------------------
foyers = []
for i in range(1, nb_foyers+1):
    date_debut = fake.date_between(start_date='-5y', end_date='-3y')
    date_fin = date_debut + timedelta(days=random.randint(365, 3*365))
    foyers.append({
        'id_foyer': i,
        'nom_foyer': f"Foyer_{i}",
        'type_foyer': random.choice(['célibataire', 'couple', 'famille']),
        'nombre_adultes': random.randint(1, 2),
        'nombre_enfants': random.randint(0, 4),
        'revenu_mensuel_estime': random.randint(1000, 8000),
        'date_debut': date_debut,
        'date_fin': date_fin
    })
df_foyers = pd.DataFrame(foyers)
df_foyers.to_csv(f"{output_dir}Foyers.csv", index=False)

# ------------------ CLIENTS ------------------
clients = []
for i in range(1, nb_clients+1):
    foyer = random.choice(df_foyers['id_foyer'])
    conseiller = random.choice(df_conseillers['id_conseiller'])
    clients.append({
        'id_client': i,
        'numero_client': f"C{i:04d}",
        'nom': fake.last_name(),
        'prenom': fake.first_name(),
        'sexe': random.choice(['M', 'F']),
        'date_naissance': fake.date_of_birth(minimum_age=18, maximum_age=75),
        'email': fake.email(),
        'telephone': fake.phone_number(),
        'adresse': fake.street_address(),
        'ville': fake.city(),
        'code_postal': fake.postcode(),
        'date_creation_client': fake.date_between(start_date='-5y', end_date='today'),
        'statut_client': random.choice(['actif', 'inactif']),
        'id_foyer': foyer,
        'id_conseiller': conseiller
    })
df_clients = pd.DataFrame(clients)
df_clients.to_csv(f"{output_dir}Clients.csv", index=False)

# ------------------ PRODUITS ------------------
produits = [
    {'id_produit': i+1, 'code_produit': f"P{i+1:02d}", 'libelle_produit': name,
     'categorie': 'compte', 'taux_interet': round(random.uniform(0.1, 2.0),2),
     'plafond': random.randint(5000, 20000)}
    for i, name in enumerate(['Courant', 'Épargne', 'Jeune', 'Entreprise', 'Premium'])
]
df_produits = pd.DataFrame(produits)
df_produits.to_csv(f"{output_dir}Produits.csv", index=False)

# ------------------ COMPTES ------------------
comptes = []
for i in range(1, nb_comptes+1):
    foyer = random.choice(df_foyers['id_foyer'])
    produit = random.choice(df_produits['id_produit'])
    agence = random.choice(df_agences['id_agence'])
    date_ouverture = fake.date_between(start_date='-5y', end_date='-1y')
    date_cloture = date_ouverture + timedelta(days=random.randint(365, 3*365))
    comptes.append({
        'id_compte': i,
        'numero_compte': f"AC{i:06d}",
        'date_ouverture': date_ouverture,
        'date_cloture': date_cloture,
        'autorisation_decouvert': random.choice([True, False]),
        'solde_courant': random.randint(0, 10000),
        'devise': 'EUR',
        'statut': random.choice(['actif', 'fermé']),
        'id_produit': produit,
        'id_agence': agence,
        'id_foyer': foyer
    })
df_comptes = pd.DataFrame(comptes)
df_comptes.to_csv(f"{output_dir}Comptes.csv", index=False)

# ------------------ CLIENT_COMPTE (N-N) ------------------
client_compte = []
for compte in df_comptes['id_compte']:
    nb_clients_compte = random.randint(1, 2)  # comptes joints possibles
    clients_for_account = random.sample(list(df_clients['id_client']), nb_clients_compte)
    for cid in clients_for_account:
        date_debut = fake.date_between(start_date='-5y', end_date='today')
        date_fin = date_debut + timedelta(days=random.randint(365, 3*365))
        client_compte.append({
            'id_client': cid,
            'id_compte': compte,
            'role_client': random.choice(['titulaire', 'cotitulaire']),
            'date_debut': date_debut,
            'date_fin': date_fin
        })
df_client_compte = pd.DataFrame(client_compte)
df_client_compte.to_csv(f"{output_dir}Client_Compte.csv", index=False)

# ------------------ SCORING ------------------
scorings = []
for compte in df_comptes['id_compte']:
    for m in range(mois_historique):
        date_score = datetime.today() - pd.DateOffset(months=m)
        scorings.append({
            'id_scoring': len(scorings)+1,
            'type_score': 'compte',
            'date_scoring': date_score.date(),
            'valeur_score': random.randint(300, 850),
            'commentaire': fake.sentence(),
            'id_compte': compte,
            'id_foyer': None
        })
for foyer in df_foyers['id_foyer']:
    for m in range(mois_historique):
        date_score = datetime.today() - pd.DateOffset(months=m)
        scorings.append({
            'id_scoring': len(scorings)+1,
            'type_score': 'foyer',
            'date_scoring': date_score.date(),
            'valeur_score': random.randint(300, 850),
            'commentaire': fake.sentence(),
            'id_compte': None,
            'id_foyer': foyer
        })
df_scoring = pd.DataFrame(scorings)
df_scoring.to_csv(f"{output_dir}Scoring.csv", index=False)

# ------------------ TRANSACTIONS / OPERATIONS ------------------
transactions = []
for compte in df_comptes['id_compte']:
    for m in range(mois_historique):
        date_base = datetime.today() - pd.DateOffset(months=m)
        nb_tx = random.randint(3, 5)  # 3-5 transactions par mois
        for t in range(nb_tx):
            date_op = date_base - timedelta(days=random.randint(0,27))
            montant = random.randint(10, 2000)
            sens = random.choice(['DEBIT', 'CREDIT'])
            transactions.append({
                'id_operation': len(transactions)+1,
                'reference': f"OP{len(transactions)+1:06d}",
                'libelle_operation': fake.sentence(nb_words=3),
                'date_operation': date_op.date(),
                'date_comptable': date_op.date(),
                'montant': montant,
                'sens': sens,
                'type_operation': random.choice(['virement', 'retrait', 'versement']),
                'statut_operation': random.choice(['valide', 'en attente']),
                'id_compte': compte
            })
df_transactions = pd.DataFrame(transactions)
df_transactions.to_csv(f"{output_dir}Transactions.csv", index=False)

print("Génération terminée : toutes les 9 tables CSV créées dans", output_dir)