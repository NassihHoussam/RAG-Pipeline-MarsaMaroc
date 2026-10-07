import re
from typing import List, Dict, Any

class RAGGenerator:
    def __init__(self):
        pass

    def generate_response(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not retrieved_chunks:
            return {
                "answer": "Désolé, aucun élément d'information pertinent n'a été trouvé dans le document pour répondre à votre question.",
                "sources": [],
                "confidence_score": 0.0
            }

        context_texts = []
        sources = []
        scores = []
        
        for item in retrieved_chunks:
            chunk = item["chunk"]
            score = item.get("score", 0.0)
            scores.append(score)
            
            page_num = chunk.get("page_number", "N/A")
            chunk_id = chunk.get("id", "N/A")
            
            context_texts.append(chunk["text"])
            sources.append({
                "chunk_id": chunk_id,
                "page": page_num,
                "score": round(score, 3),
                "snippet": chunk["text"][:180] + "..."
            })

        top_score = max(scores) if scores else 0.0
        
        # Extractive summarization logic for clean French response
        query_words = set(re.findall(r'\w+', query.lower()))
        matched_sentences = []
        
        for text in context_texts:
            sentences = re.split(r'(?<=[.!?])\s+', text)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 20:
                    s_words = set(re.findall(r'\w+', s_clean.lower()))
                    overlap = len(query_words.intersection(s_words))
                    if overlap > 0:
                        matched_sentences.append((overlap, s_clean))

        matched_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s[1] for s in matched_sentences[:4]]

        if top_sentences:
            response_body = " ".join(top_sentences)
        else:
            response_body = context_texts[0][:400] + "..."

        answer_markdown = f"""### Réponse Générée (Basée sur le Document)

{response_body}

---
*Informations extraites de {len(sources)} passage(s) pertinent(s) du document RAG.*
"""

        return {
            "answer": answer_markdown,
            "sources": sources,
            "confidence_score": round(top_score, 3)
        }
