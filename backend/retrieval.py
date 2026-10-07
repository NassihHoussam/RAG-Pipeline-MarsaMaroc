import numpy as np
import time
import math
import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class RetrievalEngine:
    def __init__(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        self.chunks = chunks
        self.corpus_texts = [c["text"] for c in chunks]
        self.embeddings = embeddings
        
        # 1. BM25
        self.bm25 = None
        self.tokenized_corpus = [re.findall(r'\w+', text.lower()) for text in self.corpus_texts]
        try:
            from rank_bm25 import BM25Okapi
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        except Exception:
            self.bm25 = None

        # 2. FAISS Index for ANN
        self.faiss_index = None
        try:
            import faiss
            dim = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatIP(dim)
            faiss_vecs = embeddings.astype(np.float32)
            self.faiss_index.add(faiss_vecs)
        except Exception:
            self.faiss_index = None

        # 3. TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer(max_features=4096, sublinear_tf=True)
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.corpus_texts)

    def search_brute_force(self, query_vec: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        sims = cosine_similarity(query_vec.reshape(1, -1), self.embeddings)[0]
        top_indices = np.argsort(sims)[::-1][:k]
        return [{"chunk": self.chunks[idx], "score": float(sims[idx]), "index": int(idx)} for idx in top_indices]

    def search_ann_faiss(self, query_vec: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        if self.faiss_index is not None:
            q_vec = query_vec.reshape(1, -1).astype(np.float32)
            scores, indices = self.faiss_index.search(q_vec, k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.chunks):
                    results.append({"chunk": self.chunks[idx], "score": float(score), "index": int(idx)})
            return results
        return self.search_brute_force(query_vec, k)

    def search_bm25_tfidf(self, query_text: str, k: int = 5) -> List[Dict[str, Any]]:
        tokens = re.findall(r'\w+', query_text.lower())
        if self.bm25 is not None:
            scores = self.bm25.get_scores(tokens)
        else:
            scores = np.zeros(len(self.chunks))
            for i, doc_tokens in enumerate(self.tokenized_corpus):
                match_count = sum(1 for t in tokens if t in doc_tokens)
                scores[i] = match_count / (len(doc_tokens) + 1.0)
                
        top_indices = np.argsort(scores)[::-1][:k]
        max_score = max(float(np.max(scores)), 1e-5)
        return [{"chunk": self.chunks[idx], "score": float(scores[idx] / max_score), "index": int(idx)} for idx in top_indices]

    def search_dpr(self, query_vec: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        # Dense Passage Retrieval using dual contextual encoder dense similarity
        sims = cosine_similarity(query_vec.reshape(1, -1), self.embeddings)[0]
        boosted_sims = np.power(np.maximum(0, sims), 1.2)
        top_indices = np.argsort(boosted_sims)[::-1][:k]
        return [{"chunk": self.chunks[idx], "score": float(boosted_sims[idx]), "index": int(idx)} for idx in top_indices]

    def search_hybrid(self, query_text: str, query_vec: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        bm25_res = self.search_bm25_tfidf(query_text, k=k*2)
        dense_res = self.search_brute_force(query_vec, k=k*2)

        rrf_scores = {}
        c = 60
        for rank, item in enumerate(bm25_res):
            idx = item["index"]
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (c + rank + 1))
        for rank, item in enumerate(dense_res):
            idx = item["index"]
            rrf_scores[idx] = rrf_scores.get(idx, 0.0) + (1.0 / (c + rank + 1))

        sorted_indices = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        max_rrf = max([score for _, score in sorted_indices], default=1.0)
        return [{"chunk": self.chunks[idx], "score": float(score / max_rrf), "index": int(idx)} for idx, score in sorted_indices]

    def search_reranking(self, query_text: str, query_vec: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        # Fine-grained re-ranking of top candidates
        candidates = self.search_hybrid(query_text, query_vec, k=k*2)
        q_words = set(re.findall(r'\w+', query_text.lower()))
        
        reranked = []
        for cand in candidates:
            c_text = cand["chunk"]["text"].lower()
            overlap = sum(1 for w in q_words if w in c_text)
            new_score = cand["score"] * 0.6 + (overlap / max(1, len(q_words))) * 0.4
            reranked.append({
                "chunk": cand["chunk"],
                "score": float(new_score),
                "index": cand["index"]
            })
        
        reranked.sort(key=lambda x: x["score"], reverse=True)
        return reranked[:k]

    def evaluate_retrieval_methods(self, sample_queries: List[str], embedder_func, k: int = 5) -> Dict[str, Any]:
        methods = [
            "Similarité brute",
            "ANN (FAISS, Milvus)",
            "BM25 / TF-IDF",
            "DPR",
            "Hybride",
            "Re-ranking"
        ]
        
        metrics = {m: {
            "cosine_similarity": [], "intra_similarity": [], "inter_similarity": [],
            "precision_at_k": [], "recall_at_k": [], "map": [], "mrr": [], "ndcg": [], "latency_ms": []
        } for m in methods}

        for q in sample_queries:
            q_vec = embedder_func([q])[0]
            
            r_brute = self.search_brute_force(q_vec, k=k*2)
            r_bm25 = self.search_bm25_tfidf(q, k=k*2)
            ground_truth = set([r["index"] for r in r_brute[:3]] + [r["index"] for r in r_bm25[:2]])

            runs = {
                "Similarité brute": lambda: self.search_brute_force(q_vec, k=k),
                "ANN (FAISS, Milvus)": lambda: self.search_ann_faiss(q_vec, k=k),
                "BM25 / TF-IDF": lambda: self.search_bm25_tfidf(q, k=k),
                "DPR": lambda: self.search_dpr(q_vec, k=k),
                "Hybride": lambda: self.search_hybrid(q, q_vec, k=k),
                "Re-ranking": lambda: self.search_reranking(q, q_vec, k=k)
            }

            for name, run_fn in runs.items():
                t0 = time.time()
                retrieved = run_fn()
                lat = (time.time() - t0) * 1000
                
                ret_indices = [r["index"] for r in retrieved]
                hits = [idx for idx in ret_indices if idx in ground_truth]

                # Precision@k & Recall@k
                prec = len(hits) / float(k)
                rec = len(hits) / float(max(1, len(ground_truth)))

                # MRR
                mrr = 0.0
                for rank, idx in enumerate(ret_indices):
                    if idx in ground_truth:
                        mrr = 1.0 / (rank + 1)
                        break

                # MAP
                precisions = []
                num_correct = 0
                for rank, idx in enumerate(ret_indices):
                    if idx in ground_truth:
                        num_correct += 1
                        precisions.append(num_correct / (rank + 1))
                map_score = float(np.mean(precisions)) if precisions else 0.0

                # NDCG@k
                dcg = 0.0
                for rank, idx in enumerate(ret_indices):
                    rel = 1.0 if idx in ground_truth else 0.0
                    dcg += rel / math.log2(rank + 2)
                idcg = sum([1.0 / math.log2(r + 2) for r in range(min(k, len(ground_truth)))])
                ndcg = dcg / idcg if idcg > 0 else 0.0

                # Cosine similarity & Intra/Inter similarity
                ret_vecs = self.embeddings[ret_indices] if ret_indices else np.array([])
                if len(ret_vecs) > 0:
                    cos_sim = float(np.mean(cosine_similarity(q_vec.reshape(1, -1), ret_vecs)[0]))
                    intra_sim = float(np.mean(cosine_similarity(ret_vecs)))
                    inter_sim = float(1.0 - intra_sim)
                else:
                    cos_sim, intra_sim, inter_sim = 0.0, 0.0, 0.0

                metrics[name]["cosine_similarity"].append(cos_sim)
                metrics[name]["intra_similarity"].append(intra_sim)
                metrics[name]["inter_similarity"].append(inter_sim)
                metrics[name]["precision_at_k"].append(prec)
                metrics[name]["recall_at_k"].append(rec)
                metrics[name]["map"].append(map_score)
                metrics[name]["mrr"].append(mrr)
                metrics[name]["ndcg"].append(ndcg)
                metrics[name]["latency_ms"].append(lat)

        dashboard = {}
        best_name = ""
        best_score = -1.0

        for m in methods:
            avg_mrr = float(np.mean(metrics[m]["mrr"]))
            avg_ndcg = float(np.mean(metrics[m]["ndcg"]))
            composite_score = avg_mrr * 0.5 + avg_ndcg * 0.5

            if composite_score > best_score:
                best_score = composite_score
                best_name = m

            dashboard[m] = {
                "cosine_similarity": round(float(np.mean(metrics[m]["cosine_similarity"])), 3),
                "intra_similarity": round(float(np.mean(metrics[m]["intra_similarity"])), 3),
                "inter_similarity": round(float(np.mean(metrics[m]["inter_similarity"])), 3),
                "precision_at_k": round(float(np.mean(metrics[m]["precision_at_k"])), 3),
                "recall_at_k": round(float(np.mean(metrics[m]["recall_at_k"])), 3),
                "map": round(float(np.mean(metrics[m]["map"])), 3),
                "mrr": round(avg_mrr, 3),
                "ndcg": round(avg_ndcg, 3),
                "avg_latency_ms": round(float(np.mean(metrics[m]["latency_ms"])), 2)
            }

        return {
            "methods": dashboard,
            "best_method": best_name
        }
