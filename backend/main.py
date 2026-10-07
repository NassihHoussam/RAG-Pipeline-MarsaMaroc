import os
import sys
import numpy as np
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import PDFParser
from chunking import ChunkingEngine
from embedding import EmbeddingEngine
from retrieval import RetrievalEngine
from generation import RAGGenerator

app = FastAPI(title="RAG Pipeline API", version="4.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATE = {
    "pdf_parser": None,
    "full_text": "",
    "chunks": [],
    "embeddings": None,
    "chunking_engine": None,
    "embedding_engine": None,
    "retrieval_engine": None,
    "generator": RAGGenerator(),
    "dataset_info": {}
}

PDF_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Document_Data_Reduit.pdf")

def initialize_pipeline():
    if not os.path.exists(PDF_PATH):
        print(f"Warning: PDF file missing at {PDF_PATH}")
        return

    print("Initializing PDF Parser...")
    parser = PDFParser(PDF_PATH)
    res = parser.extract_clean_text()
    STATE["full_text"] = res["full_text"]
    STATE["dataset_info"] = {
        "filename": "Document_Data_Reduit.pdf",
        "total_pages": res["total_pages"],
        "valid_pages": res["valid_pages"],
        "total_characters": len(res["full_text"]),
        "total_words": len(res["full_text"].split())
    }

    STATE["chunking_engine"] = ChunkingEngine(STATE["full_text"])
    default_chunks, _ = STATE["chunking_engine"].recursive_character_splitter(500, 100)
    STATE["chunks"] = default_chunks

    print("Initializing Embeddings...")
    STATE["embedding_engine"] = EmbeddingEngine(method="Sentence-BERT")
    corpus_texts = [c["text"] for c in default_chunks]
    STATE["embeddings"] = STATE["embedding_engine"].fit_transform_corpus(corpus_texts)

    print("Initializing Retrieval Engine...")
    STATE["retrieval_engine"] = RetrievalEngine(STATE["chunks"], STATE["embeddings"])

@app.on_event("startup")
def startup_event():
    initialize_pipeline()

class QueryRequest(BaseModel):
    query: str
    retrieval_method: str = "Hybride"
    top_k: int = 5

class ChunkingRequest(BaseModel):
    method: str = "fixed_character"
    chunk_size: int = 500
    overlap: int = 150
    sentences_per_chunk: int = 3
    similarity_threshold: float = 0.55

class EmbeddingRequest(BaseModel):
    method: str = "Sentence-BERT"

@app.get("/dataset/info")
def get_dataset_info():
    return STATE["dataset_info"]

@app.get("/vectorial")
def get_vectorial_status():
    if STATE["embeddings"] is None:
        initialize_pipeline()
    return {
        "status": "ready",
        "total_chunks": len(STATE["chunks"]),
        "vector_dimension": STATE["embeddings"].shape[1] if STATE["embeddings"] is not None else 0,
        "embedding_model": STATE["embedding_engine"].method if STATE["embedding_engine"] else "N/A"
    }

@app.post("/chunking")
def run_chunking(req: ChunkingRequest):
    if not STATE["chunking_engine"]:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")

    method = req.method.lower()
    engine = STATE["chunking_engine"]
    
    if method in ["fixed_character", "fixed character"]:
        chunks, exec_time = engine.fixed_character_splitter(req.chunk_size, req.overlap)
    elif method in ["recursive_character", "recursive character"]:
        chunks, exec_time = engine.recursive_character_splitter(req.chunk_size, req.overlap)
    elif method in ["nltk_splitter", "nltk"]:
        chunks, exec_time = engine.nltk_splitter(req.sentences_per_chunk)
    elif method in ["spacy_splitter", "spacy"]:
        chunks, exec_time = engine.spacy_splitter(req.sentences_per_chunk)
    elif method in ["tiktoken_splitter", "tiktoken"]:
        chunks, exec_time = engine.tiktoken_splitter(256)
    elif method in ["sentence_transformers_token_splitter", "st_token"]:
        chunks, exec_time = engine.sentence_transformers_token_splitter(128)
    elif method in ["semantic_chunker", "semantic"]:
        chunks, exec_time = engine.semantic_chunker(req.similarity_threshold)
    else:
        chunks, exec_time = engine.recursive_character_splitter(req.chunk_size, req.overlap)

    STATE["chunks"] = chunks
    corpus_texts = [c["text"] for c in chunks]
    STATE["embeddings"] = STATE["embedding_engine"].fit_transform_corpus(corpus_texts)
    STATE["retrieval_engine"] = RetrievalEngine(STATE["chunks"], STATE["embeddings"])

    metrics = ChunkingEngine.calculate_chunk_metrics(chunks, exec_time)

    return {
        "method": req.method,
        "metrics": metrics,
        "sample_chunks": chunks[:6]
    }

@app.get("/chunking/metrics")
def get_chunking_metrics_comparison():
    if not STATE["chunking_engine"]:
        raise HTTPException(status_code=500, detail="Pipeline not initialized")

    engine = STATE["chunking_engine"]
    
    c_fixed, t_fixed = engine.fixed_character_splitter(400, 0)
    c_rec, t_rec = engine.recursive_character_splitter(500, 100)
    c_nltk, t_nltk = engine.nltk_splitter(3)
    c_spacy, t_spacy = engine.spacy_splitter(4)
    c_tiktoken, t_tiktoken = engine.tiktoken_splitter(256)
    c_st_token, t_st_token = engine.sentence_transformers_token_splitter(128)
    c_semantic, t_semantic = engine.semantic_chunker(0.55)

    methods = {
        "Fixed Character Splitter": ChunkingEngine.calculate_chunk_metrics(c_fixed, t_fixed),
        "Recursive Character Splitter": ChunkingEngine.calculate_chunk_metrics(c_rec, t_rec),
        "NLTK Splitter": ChunkingEngine.calculate_chunk_metrics(c_nltk, t_nltk),
        "SpaCy Splitter": ChunkingEngine.calculate_chunk_metrics(c_spacy, t_spacy),
        "Token Splitter (Tiktoken)": ChunkingEngine.calculate_chunk_metrics(c_tiktoken, t_tiktoken),
        "Sentence-Transformers Token Splitter": ChunkingEngine.calculate_chunk_metrics(c_st_token, t_st_token),
        "Semantic Chunker": ChunkingEngine.calculate_chunk_metrics(c_semantic, t_semantic)
    }

    best_method = max(methods.keys(), key=lambda m: methods[m]["f1_score"])

    return {
        "methods": methods,
        "best_method": best_method
    }

@app.post("/embedding")
def run_embedding(req: EmbeddingRequest):
    if not STATE["chunks"]:
        raise HTTPException(status_code=400, detail="No chunks available. Perform chunking first.")

    STATE["embedding_engine"] = EmbeddingEngine(method=req.method)
    corpus_texts = [c["text"] for c in STATE["chunks"]]
    STATE["embeddings"] = STATE["embedding_engine"].fit_transform_corpus(corpus_texts)
    STATE["retrieval_engine"] = RetrievalEngine(STATE["chunks"], STATE["embeddings"])

    sample_query = "Reconstruction paléocéanographique diatomées et foraminifères"
    q_vec = STATE["embedding_engine"].encode([sample_query])[0]
    metrics = EmbeddingEngine.calculate_embedding_metrics(q_vec, STATE["embeddings"], ground_truth_indices=[0, 1, 2], k=5)

    return {
        "method": req.method,
        "dimension": STATE["embeddings"].shape[1],
        "total_vectors": len(STATE["embeddings"]),
        "metrics": metrics
    }

@app.get("/embedding/metrics")
def get_embedding_metrics():
    if not STATE["chunks"]:
        raise HTTPException(status_code=400, detail="No chunks available")

    corpus_texts = [c["text"] for c in STATE["chunks"]]
    comparison = EmbeddingEngine.compare_all_embedding_methods(corpus_texts, sample_query="Assemblages de diatomées dans le Sud-Est Pacifique", k=5)
    
    best_method = max(comparison.keys(), key=lambda m: comparison[m]["ndcg"])

    return {
        "methods": comparison,
        "best_method": best_method
    }

@app.get("/retrieval/metrics")
def get_retrieval_metrics_dashboard():
    if not STATE["retrieval_engine"]:
        raise HTTPException(status_code=500, detail="Retrieval Engine not ready")

    test_queries = [
        "Quels sont les assemblages de diatomées dans le Pacifique Sud-Est ?",
        "Reconstruction des températures de surface de la mer SST",
        "Quelles sont les variations durant la dernière période glaciaire ?",
        "Rôle du front subtopical STF et des vents d'ouest SWW",
        "Quelles méthodes géochimiques ont été utilisées dans la thèse ?"
    ]

    embedder_fn = lambda q_list: STATE["embedding_engine"].encode(q_list)
    return STATE["retrieval_engine"].evaluate_retrieval_methods(test_queries, embedder_fn, k=5)

@app.post("/query")
def process_rag_query(req: QueryRequest):
    if not STATE["retrieval_engine"]:
        raise HTTPException(status_code=500, detail="Retrieval Engine not initialized")

    q_vec = STATE["embedding_engine"].encode([req.query])[0]
    method = req.retrieval_method

    if method in ["Similarité brute", "Similarité Brute"]:
        retrieved = STATE["retrieval_engine"].search_brute_force(q_vec, k=req.top_k)
    elif method in ["ANN", "ANN (FAISS, Milvus)", "ANN (FAISS)"]:
        retrieved = STATE["retrieval_engine"].search_ann_faiss(q_vec, k=req.top_k)
    elif method in ["BM25 / TF-IDF", "BM25"]:
        retrieved = STATE["retrieval_engine"].search_bm25_tfidf(req.query, k=req.top_k)
    elif method in ["DPR"]:
        retrieved = STATE["retrieval_engine"].search_dpr(q_vec, k=req.top_k)
    elif method in ["Hybride", "Hybrid", "Hybrid / Re-Ranking"]:
        retrieved = STATE["retrieval_engine"].search_hybrid(req.query, q_vec, k=req.top_k)
    elif method in ["Re-ranking", "Re-Ranking"]:
        retrieved = STATE["retrieval_engine"].search_reranking(req.query, q_vec, k=req.top_k)
    else:
        retrieved = STATE["retrieval_engine"].search_hybrid(req.query, q_vec, k=req.top_k)

    generation = STATE["generator"].generate_response(req.query, retrieved)

    return {
        "query": req.query,
        "retrieval_method": req.retrieval_method,
        "response": generation["answer"],
        "confidence_score": generation["confidence_score"],
        "retrieved_chunks": generation["sources"]
    }

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
def read_root():
    index_file = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "RAG API is running."}
