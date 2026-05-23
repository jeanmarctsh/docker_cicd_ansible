# Utilisation d'une image python légère pour réduire la taille de l'image 
FROM python:3.13-slim

# Métadonnées identifiant l'auteur
LABEL author="APP Download FROM GITHUB and DOKERFILE-DEPLOY BY JM "

# Installation de différentes dépendances système nécessaires (client MySQL)
# Le nettoyage des listes apt permet d'alléger l'image
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Niveau Sécurité : Création d'un groupe et d'un utilisateur non-root (jean)
# But? éviter d'exécuter l'application avec les privilèges administrateur
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1001 jean

# Définition du répertoire de travail dans le conteneur
WORKDIR /home/apk

# Installation de différentes bibliothèques Python de l'application via pip
RUN pip install --no-cache-dir streamlit pillow pandas mysql-connector-python

# Copie des éléments du dossier app vers /home/apk en attribuant directement la propriété à l'utilisateur crée (jean)
COPY --chown=jean:appgroup ./Hotel-Management-using-SQL-main/app .

# Bascule sur l'utilisateur non-root pour l'exécution des commandes suivantes
USER jean

# Conteneur écoutant sur le port 8501(port par défaut de streamlit)
EXPOSE 8501

# Commande lancée au démarrage du conteneur
CMD ["streamlit", "run", "Main_Page.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

