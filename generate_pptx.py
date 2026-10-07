import sys
import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    C_NAVY = RGBColor(15, 23, 42)       # #0F172A
    C_ROYAL = RGBColor(30, 58, 138)     # #1E3A8A
    C_BLUE = RGBColor(37, 99, 235)      # #2563EB
    C_ORANGE = RGBColor(234, 88, 12)    # #EA580C
    C_GREEN = RGBColor(16, 185, 129)    # #10B981
    C_LIGHT_BG = RGBColor(248, 250, 252)# #F8FAFC
    C_WHITE = RGBColor(255, 255, 255)
    C_DARK = RGBColor(30, 41, 59)
    C_MUTED = RGBColor(100, 116, 139)

    blank_layout = prs.slide_layouts[6]

    def add_header(slide, title_text, category_text="MARSA MAROC & EMSI — SYSTÈME RAG & ANALYTICS"):
        # Header background banner
        header_shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(1.1))
        header_shape.fill.solid()
        header_shape.fill.fore_color.rgb = C_NAVY
        header_shape.line.fill.background()

        # Category / Subtitle
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.12), Inches(11.5), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_ORANGE

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_WHITE

        # Bottom subtle accent line
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(1.1), Inches(13.333), Inches(0.05))
        line.fill.solid()
        line.fill.fore_color.rgb = C_BLUE
        line.line.fill.background()

    def add_card(slide, left, top, width, height, title, items, bg_color=C_LIGHT_BG, border_color=C_BLUE):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)

        tf = card.text_frame
        tf.vertical_anchor = MSO_ANCHOR.TOP
        tf.margin_left = Inches(0.25)
        tf.margin_right = Inches(0.25)
        tf.margin_top = Inches(0.2)
        tf.margin_bottom = Inches(0.2)
        tf.word_wrap = True

        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = C_ROYAL

        for item in items:
            p = tf.add_paragraph()
            p.text = f"•  {item}"
            p.font.size = Pt(13)
            p.font.color.rgb = C_DARK
            p.space_before = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: Title Slide (Cover)
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    bg1 = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg1.fill.solid()
    bg1.fill.fore_color.rgb = C_NAVY
    bg1.line.fill.background()

    # Decorative top bar
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = C_ORANGE
    top_bar.line.fill.background()

    # Logos placeholder text / Header
    tb_inst = slide1.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(11.733), Inches(0.6))
    p_inst = tb_inst.text_frame.paragraphs[0]
    p_inst.text = "ÉCOLE MAROCAINE DES SCIENCES DE L'INGÉNIEUR (EMSI)  |  MARSA MAROC"
    p_inst.font.size = Pt(12)
    p_inst.font.bold = True
    p_inst.font.color.rgb = C_ORANGE

    # Main Title
    tb_main = slide1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(2.2))
    tf_main = tb_main.text_frame
    tf_main.word_wrap = True
    p_m1 = tf_main.paragraphs[0]
    p_m1.text = "EXPLOITATION ET LOGISTIQUE PORTUAIRE"
    p_m1.font.size = Pt(28)
    p_m1.font.bold = True
    p_m1.font.color.rgb = C_WHITE

    p_m2 = tf_main.add_paragraph()
    p_m2.text = "Conception d'un Tableau de Bord Analytique et Intégration d'un Système RAG pour le Suivi des Flux"
    p_m2.font.size = Pt(20)
    p_m2.font.color.rgb = C_BLUE
    p_m2.space_before = Pt(12)

    # Subtitle Badge
    sub_card = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(4.0), Inches(11.733), Inches(0.8))
    sub_card.fill.solid()
    sub_card.fill.fore_color.rgb = RGBColor(30, 41, 59)
    sub_card.line.color.rgb = C_BLUE
    tf_sub = sub_card.text_frame
    p_sub = tf_sub.paragraphs[0]
    p_sub.text = "Soutenance de Stage d'Immersion Professionnelle  •  Projet à Deux Moteurs : Data Analytics & RAG"
    p_sub.font.size = Pt(14)
    p_sub.font.bold = True
    p_sub.font.color.rgb = C_GREEN
    p_sub.alignment = PP_ALIGN.CENTER

    # Authors & Supervisors
    tb_auth = slide1.shapes.add_textbox(Inches(0.8), Inches(5.2), Inches(5.5), Inches(1.5))
    tf_auth = tb_auth.text_frame
    p_a1 = tf_auth.paragraphs[0]
    p_a1.text = "Réalisé par :"
    p_a1.font.size = Pt(13)
    p_a1.font.bold = True
    p_a1.font.color.rgb = C_ORANGE
    p_a2 = tf_auth.add_paragraph()
    p_a2.text = "• NASSIH Houssam\n• NASSIH Anas\n(Élèves Ingénieurs EMSI)"
    p_a2.font.size = Pt(12)
    p_a2.font.color.rgb = C_WHITE

    tb_sup = slide1.shapes.add_textbox(Inches(7.0), Inches(5.2), Inches(5.5), Inches(1.5))
    tf_sup = tb_sup.text_frame
    p_s1 = tf_sup.paragraphs[0]
    p_s1.text = "Encadrement :"
    p_s1.font.size = Pt(13)
    p_s1.font.bold = True
    p_s1.font.color.rgb = C_ORANGE
    p_s2 = tf_sup.add_paragraph()
    p_s2.text = "• Mme Zakia AIT ABDELLAH (Marsa Maroc)\n• Mme Mouna EL MKHALET (EMSI)"
    p_s2.font.size = Pt(12)
    p_s2.font.color.rgb = C_WHITE

    # -------------------------------------------------------------
    # SLIDE 2: Context & Enterprise Presentation (Marsa Maroc)
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    add_header(slide2, "Présentation de l'Organisme d'Accueil & Contexte Portuaire")

    # 3 Stat Cards
    c1 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(3.6), Inches(1.5))
    c1.fill.solid()
    c1.fill.fore_color.rgb = C_ROYAL
    c1.line.fill.background()
    p = c1.text_frame.paragraphs[0]
    p.text = "10 Ports Stratégiques\n"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.CENTER
    p2 = c1.text_frame.add_paragraph()
    p2.text = "Casablanca, Tanger Med, Agadir, Safi, Jorf Lasfar, Nador..."
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_LIGHT_BG
    p2.alignment = PP_ALIGN.CENTER

    c2 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(4.8), Inches(1.5), Inches(3.6), Inches(1.5))
    c2.fill.solid()
    c2.fill.fore_color.rgb = C_BLUE
    c2.line.fill.background()
    p = c2.text_frame.paragraphs[0]
    p.text = "2 300+ Collaborateurs\n"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.CENTER
    p2 = c2.text_frame.add_paragraph()
    p2.text = "Réseau humain et logistique couvrant le territoire national"
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_LIGHT_BG
    p2.alignment = PP_ALIGN.CENTER

    c3 = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.8), Inches(1.5), Inches(3.733), Inches(1.5))
    c3.fill.solid()
    c3.fill.fore_color.rgb = C_ORANGE
    c3.line.fill.background()
    p = c3.text_frame.paragraphs[0]
    p.text = "3 Piliers Métier\n"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_WHITE
    p.alignment = PP_ALIGN.CENTER
    p2 = c3.text_frame.add_paragraph()
    p2.text = "Services Marchandises • Services Navires • Logistique Terrestre"
    p2.font.size = Pt(11)
    p2.font.color.rgb = C_LIGHT_BG
    p2.alignment = PP_ALIGN.CENTER

    # Context Card below
    add_card(slide2, Inches(0.8), Inches(3.3), Inches(11.733), Inches(3.6),
             "Cadre Réglementaire (Loi 15-02) & Problématique Globale",
             [
                 "Réforme de la Loi 15-02 (Promulguée le 15/12/2006) : Scission de l'ancien monopole ODEP en deux entités distinctes : ANP (Régulation) et SODEP / Marsa Maroc (Exploitation Commerciale).",
                 "Enjeu Métier Majeur : Supervision des flux massifs de pesage routier et ferroviaire au niveau des terminaux portuaires.",
                 "Problématique Globale : Comment concilier l'analyse décisionnelle classique en entreprise (Data Analytics) et l'accès intelligent à l'information non structurée (RAG) ?",
                 "Approche à deux moteurs : 'Une donnée structurée pour piloter ; une donnée non structurée pour expliquer'."
             ], C_LIGHT_BG, C_BLUE)

    # -------------------------------------------------------------
    # SLIDE 3: Dual-Engine Vision & Global Architecture
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    add_header(slide3, "Vision Globale du Projet : Structure à Deux Moteurs")

    add_card(slide3, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3),
             "Volet 1 : Data Analytics (Dashboard)",
             [
                 "Modélisation & Agrégation des pesées (355K enregistrements, 9.17M Tonnes).",
                 "Visualisation des KPIs globaux et suivi des ponts-bascules actifs (13 ponts).",
                 "Analyse de la saisonnalité (pics trimestriels en Qtr 2).",
                 "Détection des goulots d'étranglement (Pont PB 19 > 63K pesées).",
                 "Comparatif structurel des flux (Import > 98% vs Export < 2%).",
                 "Optimisation des temps de transit par zone de stockage (Sortie Directe)."
             ], C_LIGHT_BG, C_ROYAL)

    add_card(slide3, Inches(6.9), Inches(1.5), Inches(5.633), Inches(5.3),
             "Volet 2 : Recherche & RAG Pipeline",
             [
                 "Extraction & Nettoyage de documents PDF complexes.",
                 "Benchmark des 7 stratégies de Chunking (Fixed, Recursive, NLTK, SpaCy, Tiktoken, ST-Token, Semantic).",
                 "Benchmark des 7 modèles d'Embedding (Word2Vec, GloVe, FastText, BERT, SBERT, TF-IDF, BM25).",
                 "Benchmark des 6 méthodes de Retrieval (Similarité brute, ANN FAISS, BM25, DPR, Hybride, Re-ranking).",
                 "Génération contextuelle basée sur LLM local (Ollama).",
                 "Application web fullstack réactive (FastAPI + React)."
             ], C_LIGHT_BG, C_ORANGE)

    # -------------------------------------------------------------
    # SLIDE 4: VOLET 1 - Power BI / Analytics KPIs & Seasonal Trends
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    add_header(slide4, "Volet 1 : Data Analytics — KPIs Globaux & Évolution Temporelle")

    # 4 KPI Cards Top
    kpis = [
        ("355K", "Total Pesées Enregistrées", C_ROYAL),
        ("194,61 min", "Temps Transit Moyen", C_BLUE),
        ("9,17M T", "Tonnage Total Fret Net", C_GREEN),
        ("13", "Ponts-Bascules Actifs", C_ORANGE)
    ]
    for idx, (val, label, col) in enumerate(kpis):
        x = Inches(0.8 + idx * 2.98)
        k_box = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.4), Inches(2.8), Inches(1.3))
        k_box.fill.solid()
        k_box.fill.fore_color.rgb = col
        k_box.line.fill.background()
        tf = k_box.text_frame
        p1 = tf.paragraphs[0]
        p1.text = val
        p1.font.size = Pt(20)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p1.alignment = PP_ALIGN.CENTER
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.size = Pt(10)
        p2.font.color.rgb = C_LIGHT_BG
        p2.alignment = PP_ALIGN.CENTER

    add_card(slide4, Inches(0.8), Inches(2.9), Inches(11.733), Inches(4.1),
             "Analyse de l'Évolution Temporelle (Trafic et Tonnage 2024 - 2026)",
             [
                 "Saisonnalité Trimestrielle : Pics d'activité systématiques au 2ème trimestre (Avril - Mai) dépassant 16K à 18K pesées mensuelles et jusqu'à 0.5M Tonnes par mois (campagnes d'importation de vracs).",
                 "Saisons Creuses : Baisse d'activité observée aux mois de Novembre et Décembre (Qtr 4) entre 4K et 7K pesées.",
                 "Constance du Tonnage : Corrélation étroite entre le nombre de passages de véhicules routiers et le tonnage total net transporté.",
                 "Décision Métier : Planification prédictive des effectifs d'agents de pesée en fonction des pics trimestriels identifiés."
             ], C_LIGHT_BG, C_BLUE)

    # -------------------------------------------------------------
    # SLIDE 5: VOLET 1 - Weighbridge Analysis & Bottleneck Detection
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    add_header(slide5, "Volet 1 : Supervision des Ponts-Bascules & Goulots d'Étranglement")

    add_card(slide5, Inches(0.8), Inches(1.5), Inches(5.6), Inches(5.3),
             "Sollicitation des Ponts-Bascules",
             [
                 "Goulot Majeur (Pont PB 19) : Enregistre à lui seul plus de 63 000 pesées, constituant la porte d'accès la plus engorgée du terminal.",
                 "Ponts Secondaires à Forte Charge :",
                 "  • PB 8 : ~49 000 pesées",
                 "  • PB 7 : ~44 000 pesées",
                 "  • PB 14.0 : ~36 000 pesées",
                 "Ponts Inutilisés / Sous-Exploités : Stations OUT 01, OUT 02, IN 02, IN 03 avec des volumes proches de zéro.",
                 "Action Préconisée : Rééquilibrage dynamique des flux à l'entrée du port vers les balances secondaires."
             ], C_LIGHT_BG, C_ROYAL)

    add_card(slide5, Inches(6.9), Inches(1.5), Inches(5.633), Inches(5.3),
             "Temps de Transit & Déséquilibre Import / Export",
             [
                 "Fluctuations Mensuelles du Temps de Transit :",
                 "  • Maximum : Janvier (223 min) et Avril (218 min) lors des encombrements de pointe.",
                 "  • Minimum : Juin (154 min) offrant la meilleure fluidité logistique.",
                 "Déséquilibre Structurel Import / Export :",
                 "  • Camions Import : > 98% du trafic total (jusqu'à 150K+ camions/an).",
                 "  • Camions Export : < 2% du trafic enregistré.",
                 "Impact Opérationnel : Priorisation du contrôle d'accès sur l'évacuation du fret importé."
             ], C_LIGHT_BG, C_ORANGE)

    # -------------------------------------------------------------
    # SLIDE 6: VOLET 2 - RAG Roadmap & Engineering Pipeline
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    add_header(slide6, "Volet 2 : Pipeline RAG — Roadmap & Architecture Ingénierie")

    steps = [
        ("1. Data Preprocessing", "PyPDFLoader\nExtraction & Nettoyage PDF\n93 pages valides", C_ROYAL),
        ("2. Chunking Strategies", "7 Méthodes évaluées\nFixed, Recursive, NLTK,\nSpaCy, Token, Semantic", C_BLUE),
        ("3. Embeddings", "7 Modèles denses/sparses\nWord2Vec, GloVe, FastText,\nBERT, SBERT, TF-IDF, BM25", C_BLUE),
        ("4. Hybrid Retrieval", "6 Algorithmes de recherche\nFAISS, BM25, DPR,\nFusion RRF, Re-ranking", C_ORANGE),
        ("5. LLM Generation", "Ollama Local LLM\n(Llama3 / Mistral)\nPrompt Contextuel", C_GREEN),
        ("6. Fullstack Web App", "FastAPI REST Server\nFrontend HTML5 / React\nDashboard Chart.js", C_NAVY)
    ]

    for idx, (stitle, sdesc, scol) in enumerate(steps):
        row = idx // 3
        col = idx % 3
        x = Inches(0.8 + col * 3.98)
        y = Inches(1.5 + row * 2.7)
        box = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.75), Inches(2.4))
        box.fill.solid()
        box.fill.fore_color.rgb = scol
        box.line.fill.background()
        tf = box.text_frame
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.15)
        p1 = tf.paragraphs[0]
        p1.text = stitle
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p2 = tf.add_paragraph()
        p2.text = sdesc
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_LIGHT_BG
        p2.space_before = Pt(8)

    # -------------------------------------------------------------
    # SLIDE 7: VOLET 2 - Chunking Benchmark & F1-score Formula
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    add_header(slide7, "Volet 2 : Benchmark Chunking (7 Méthodes) & Formule F1-Score")

    # Formula Box
    f_box = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.9))
    f_box.fill.solid()
    f_box.fill.fore_color.rgb = C_ROYAL
    f_box.line.fill.background()
    tf_f = f_box.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "Formule Exacte de Couverture & Performance Chunking :\n"
    p_f.font.size = Pt(11)
    p_f.font.color.rgb = C_ORANGE
    p_f2 = tf_f.add_paragraph()
    p_f2.text = "F1-score = 2 × (Precision@k × Recall@k) / (Precision@k + Recall@k)"
    p_f2.font.size = Pt(16)
    p_f2.font.bold = True
    p_f2.font.color.rgb = C_WHITE

    # Table of Chunking Results
    rows, cols = 8, 8
    table_shape = slide7.shapes.add_table(rows, cols, Inches(0.8), Inches(2.4), Inches(11.733), Inches(4.4))
    table = table_shape.table

    headers = ["Méthode Chunking", "Nb Chunks", "Long. Moy.", "Écart-type", "Intra Sim.", "Recall@k", "Prec.@k", "F1-score"]
    chunk_data = [
        ["Fixed Character Splitter 🏆", "497", "399", "1.9", "0.850", "0.808", "0.849", "0.828"],
        ["Recursive Character Splitter", "448", "441", "75.5", "0.850", "0.805", "0.821", "0.813"],
        ["NLTK Splitter", "426", "462", "960.7", "0.848", "0.828", "0.678", "0.746"],
        ["SpaCy Splitter", "327", "595", "1183.8", "0.850", "0.812", "0.680", "0.740"],
        ["Token Splitter (Tiktoken)", "188", "1056", "228.9", "0.850", "0.760", "0.813", "0.786"],
        ["ST-Token Splitter", "474", "528", "122.7", "0.850", "0.724", "0.811", "0.765"],
        ["Semantic Chunker", "1108", "175", "601.9", "0.843", "0.861", "0.674", "0.756"]
    ]

    for c_idx, h in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    for r_idx, r_data in enumerate(chunk_data):
        for c_idx, val in enumerate(r_data):
            cell = table.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if r_idx == 0:
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245)
            else:
                cell.fill.fore_color.rgb = C_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(10)
            if r_idx == 0:
                p.font.bold = True
                p.font.color.rgb = C_GREEN
            else:
                p.font.color.rgb = C_DARK

    # -------------------------------------------------------------
    # SLIDE 8: VOLET 2 - Embedding Benchmark & Score Formula
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    add_header(slide8, "Volet 2 : Benchmark Embedding (7 Modèles) & Score Synthétique")

    # Formula Box
    f_box8 = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.9))
    f_box8.fill.solid()
    f_box8.fill.fore_color.rgb = C_ROYAL
    f_box8.line.fill.background()
    tf_f8 = f_box8.text_frame
    p_f8 = tf_f8.paragraphs[0]
    p_f8.text = "Formule Synthétique de Qualité d'Embedding :\n"
    p_f8.font.size = Pt(11)
    p_f8.font.color.rgb = C_ORANGE
    p_f82 = tf_f8.add_paragraph()
    p_f82.text = "Score_Embedding = 0.6 × NDCG@k + 0.4 × MAP"
    p_f82.font.size = Pt(16)
    p_f82.font.bold = True
    p_f82.font.color.rgb = C_WHITE

    rows, cols = 8, 8
    t8_shape = slide8.shapes.add_table(rows, cols, Inches(0.8), Inches(2.4), Inches(11.733), Inches(4.4))
    t8 = t8_shape.table

    h8 = ["Modèle Embedding", "Cosine Sim.", "Intra Sim.", "Inter Sim.", "Prec.@k", "MAP", "NDCG", "Score Embedding"]
    emb_data = [
        ["Word2Vec 🏆", "0.444", "0.559", "0.441", "0.600", "1.000", "1.000", "1.000"],
        ["GloVe 🏆", "0.444", "0.559", "0.441", "0.600", "1.000", "1.000", "1.000"],
        ["FastText 🏆", "0.444", "0.559", "0.441", "0.600", "1.000", "1.000", "1.000"],
        ["BERT Embedding", "0.393", "0.427", "0.573", "0.600", "1.000", "1.000", "1.000"],
        ["Sentence-BERT (SBERT)", "0.344", "0.380", "0.620", "0.600", "1.000", "1.000", "1.000"],
        ["TF-IDF Vector Space", "0.344", "0.380", "0.620", "0.600", "1.000", "1.000", "1.000"],
        ["BM25 Sparse Vector", "0.537", "0.600", "0.400", "0.600", "1.000", "1.000", "1.000"]
    ]

    for c_idx, h in enumerate(h8):
        cell = t8.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    for r_idx, r_data in enumerate(emb_data):
        for c_idx, val in enumerate(r_data):
            cell = t8.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if r_idx in [0, 1, 2]:
                cell.fill.fore_color.rgb = RGBColor(239, 246, 255)
            else:
                cell.fill.fore_color.rgb = C_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(10)
            if r_idx in [0, 1, 2]:
                p.font.bold = True
                p.font.color.rgb = C_ROYAL
            else:
                p.font.color.rgb = C_DARK

    # -------------------------------------------------------------
    # SLIDE 9: VOLET 2 - Retrieval Benchmark & Score Formula
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    add_header(slide9, "Volet 2 : Benchmark Retrieval (6 Méthodes - 6 Colonnes Exactes)")

    # Formula Box
    f_box9 = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.3), Inches(11.733), Inches(0.9))
    f_box9.fill.solid()
    f_box9.fill.fore_color.rgb = C_ROYAL
    f_box9.line.fill.background()
    tf_f9 = f_box9.text_frame
    p_f9 = tf_f9.paragraphs[0]
    p_f9.text = "Formule Équilibrée de Performance Retrieval :\n"
    p_f9.font.size = Pt(11)
    p_f9.font.color.rgb = C_ORANGE
    p_f92 = tf_f9.add_paragraph()
    p_f92.text = "Score_Retrieval = 0.5 × MRR + 0.5 × NDCG@k"
    p_f92.font.size = Pt(16)
    p_f92.font.bold = True
    p_f92.font.color.rgb = C_WHITE

    rows, cols = 7, 7
    t9_shape = slide9.shapes.add_table(rows, cols, Inches(0.8), Inches(2.4), Inches(11.733), Inches(4.4))
    t9 = t9_shape.table

    h9 = ["Méthode Retrieval", "Precision@5", "Recall@5", "MRR", "NDCG@5", "Latence (ms)", "Score Retrieval"]
    ret_data = [
        ["Similarité brute 🏆", "0.600", "1.000", "1.000", "1.000", "15.88 ms", "1.000"],
        ["ANN (FAISS, Milvus) 🏆", "0.600", "1.000", "1.000", "1.000", "14.62 ms", "1.000"],
        ["BM25 / TF-IDF", "0.560", "0.933", "1.000", "0.940", "2.50 ms", "0.970"],
        ["DPR 🏆", "0.600", "1.000", "1.000", "1.000", "14.41 ms", "1.000"],
        ["Hybride", "0.600", "1.000", "1.000", "0.983", "17.21 ms", "0.9915"],
        ["Re-ranking", "0.520", "0.867", "1.000", "0.866", "17.62 ms", "0.933"]
    ]

    for c_idx, h in enumerate(h9):
        cell = t9.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = C_NAVY
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_WHITE

    for r_idx, r_data in enumerate(ret_data):
        for c_idx, val in enumerate(r_data):
            cell = t9.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            if r_idx in [0, 1, 3]:
                cell.fill.fore_color.rgb = RGBColor(243, 232, 255)
            else:
                cell.fill.fore_color.rgb = C_WHITE
            p = cell.text_frame.paragraphs[0]
            p.text = val
            p.font.size = Pt(10)
            if r_idx in [0, 1, 3]:
                p.font.bold = True
                p.font.color.rgb = RGBColor(126, 34, 206)
            else:
                p.font.color.rgb = C_DARK

    # -------------------------------------------------------------
    # SLIDE 10: DEMONSTRATION SLIDE (Page de Démonstration)
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    add_header(slide10, "Démonstration en Direct : Plateforme RAG & Dashboard Analytique")

    demo_bg = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))
    demo_bg.fill.solid()
    demo_bg.fill.fore_color.rgb = RGBColor(15, 23, 42)
    demo_bg.line.color.rgb = C_ORANGE
    demo_bg.line.width = Pt(2)

    tf_d = demo_bg.text_frame
    tf_d.margin_left = Inches(0.4)
    tf_d.margin_top = Inches(0.3)

    p_d1 = tf_d.paragraphs[0]
    p_d1.text = "💻 PAGE DE DÉMONSTRATION EN DIRECT DU PROJET"
    p_d1.font.size = Pt(22)
    p_d1.font.bold = True
    p_d1.font.color.rgb = C_ORANGE

    p_d2 = tf_d.add_paragraph()
    p_d2.text = "Étapes de la présentation interactive sur la plateforme web (http://127.0.0.1:8000) :"
    p_d2.font.size = Pt(14)
    p_d2.font.color.rgb = C_WHITE
    p_d2.space_before = Pt(10)

    demo_items = [
        "1. Volet Analytics : Navigation interactive sur le Dashboard Power BI / Web (355K pesées, filtre par pont PB 19).",
        "2. Bouton Query RAG : Exécution d'une recherche en langage naturel ('Quel est le temps de transit moyen sur PB19 en Février ?').",
        "3. Changement Dynamique des Méthodes : Test instantané entre Hybride, Re-ranking et Similarité brute.",
        "4. Visualisation des Réponses LLM (Ollama) : Génération de la réponse contextuelle avec score de confiance.",
        "5. Dashboard des Métriques en Temps Réel : Affichage dynamique des graphiques comparatifs (Chunking, Embedding, Retrieval)."
    ]

    for item in demo_items:
        p = tf_d.add_paragraph()
        p.text = item
        p.font.size = Pt(13)
        p.font.color.rgb = C_LIGHT_BG
        p.space_before = Pt(12)

    # -------------------------------------------------------------
    # SLIDE 11: PERSPECTIVES D'ÉVOLUTION & CONCLUSION
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    add_header(slide11, "Perspectives d'Évolution & Conclusion Générale")

    persp_items = [
        ("Perspective 1 : Agentic RAG Multi-Hop", "Intégration d'agents autonomes (LangGraph / AutoGen) pour la reformulation de requêtes complexes et le raisonnement multi-étapes.", C_ROYAL),
        ("Perspective 2 : Passage à l'Échelle avec Milvus / Qdrant", "Migration de FAISS vers une base vectorielle distribuée Enterprise pour traiter des dizaines de millions de pesées en temps réel.", C_BLUE),
        ("Perspective 3 : RAG Multimodal (ColPali / Vision-LLM)", "Prise en charge native des documents visuels (schémas de cargaison, bons manuscrits, images de camions).", C_ORANGE)
    ]

    for idx, (title, desc, col) in enumerate(persp_items):
        x = Inches(0.8 + idx * 3.98)
        p_card = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(1.5), Inches(3.75), Inches(3.2))
        p_card.fill.solid()
        p_card.fill.fore_color.rgb = C_LIGHT_BG
        p_card.line.color.rgb = col
        p_card.line.width = Pt(2)
        tf_p = p_card.text_frame
        tf_p.margin_left = Inches(0.2)
        tf_p.margin_top = Inches(0.2)
        tf_p.word_wrap = True

        p1 = tf_p.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = tf_p.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_DARK
        p2.space_before = Pt(10)

    # Conclusion Card Bottom
    add_card(slide11, Inches(0.8), Inches(4.9), Inches(11.733), Inches(2.0),
             "Conclusion Générale",
             [
                 "Le projet apporte une réponse concrète aux enjeux de modernisation logistique de Marsa Maroc.",
                 "Combinaison réussie entre la rigueur analytique de supervision (Power BI) et la puissance du RAG local (Ollama).",
                 "Merci pour votre attention ! Nous sommes disposés à répondre à vos questions."
             ], C_NAVY, C_GREEN)
    
    # Change text color of conclusion card to white/light
    # Re-apply styling for conclusion text box
    conc_shape = slide11.shapes[-1]
    for p in conc_shape.text_frame.paragraphs:
        if p.text.startswith("Conclusion"):
            p.font.color.rgb = C_ORANGE
        else:
            p.font.color.rgb = C_WHITE

    output_path = r"c:\Users\user\Desktop\IA\Presentation_Projet_Marsa_RAG.pptx"
    prs.save(output_path)
    print(f"Presentation saved successfully to {output_path}")

if __name__ == "__main__":
    create_presentation()
