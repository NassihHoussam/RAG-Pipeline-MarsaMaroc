# RAG Pipeline & Web Platform - Marsa Maroc

Une solution complète de **Retrieval-Augmented Generation (RAG)** avec une architecture modulaire en Python/FastAPI et une interface Web interactive.

![RAG Architecture](https://img.shields.io/badge/FastAPI-0.136-009688.svg?style=flat&logo=FastAPI&logoColor=white)
![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB.svg?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

---

## 📌 Présentation du Projet

Ce projet implémente une chaîne complète de traitement **RAG (Retrieval-Augmented Generation)** appliquée à l'analyse de documents scientifiques et techniques au format PDF.

Il intègre :
- **Parsing PDF** : Extraction et nettoyage avec PyMuPDF.
- **Chunking Multi-Stratégie** : Taille fixe, découpage par phrases, découpage sémantique.
- **Vectorisation / Embedding** : Modèles `Sentence-BERT` et `TF-IDF`.
- **Recherche d'Information (Retrieval)** : Benchmark entre Cosinus brut, FAISS (ANN), BM25, DPR et Recherche Hybride / Re-Ranking.
- **Génération Contextuelle** : Synthèse de réponse avec calcul de scores de confiance et citations des sources.
- **Dashboard Web Interactive** : Visualisation des performances et interface de chat.

---

## 📁 Structure du Projet

```text
├── backend/
│   ├── main.py            # Serveur API FastAPI & points d'entrée
│   ├── pdf_parser.py      # Extraction & nettoyage des PDF
│   ├── chunking.py        # Moteur de découpage de texte
│   ├── embedding.py       # Moteur d'embeddings & métriques
│   ├── retrieval.py       # Algorithmes de recherche & benchmarking
│   └── generation.py      # Synthèse contextuelle RAG
├── frontend/
│   ├── index.html         # Application Web Single Page (SPA)
│   ├── app.js             # Logique d'interaction AJAX
│   └── styles.css         # Styles de l'interface
├── Document_Data_Reduit.pdf # Document source exemple
├── generate_pptx.py       # Génération de présentation PowerPoint
├── rapport_complet_marsa_rag.tex # Rapport complet en LaTeX
└── README.md
```

---

## 🚀 Installation et Lancement

### 1. Prérequis
- Python 3.10+
- Git

### 2. Installation des dépendances
```bash
pip install fastapi uvicorn pymupdf sentence-transformers rank-bm25 faiss-cpu scikit-learn numpy pandas
```

### 3. Démarrer le serveur
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 4. Accéder à l'application
- **Interface Web** : [http://localhost:8000](http://localhost:8000)
- **Documentation API (Swagger)** : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 👤 Auteur
**Houssam Nassih**  
GitHub : [@NassihHoussam](https://github.com/NassihHoussam)
