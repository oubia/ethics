# Retrieval Strategies in the Code

| # | Retriever (factory method) | Core Idea | Main Hyper-params | Key Formulae |
|---|---------------------------|-----------|-------------------|--------------|
| 1 | **Vector Similarity**<br>`build_similarity_retriever()` | Rank chunks by **cosine similarity** in embedding space (optionally MMR for diversity). | `k` (neighbors) · `mmr?` · `λ` (MMR weight) | <br>Cosine:  \(\displaystyle \text{sim}(\mathbf q,\mathbf d)=\frac{\mathbf q\!\cdot\!\mathbf d}{\lVert\mathbf q\rVert\,\lVert\mathbf d\rVert}\)<br><br>MMR:  \(\displaystyle \arg\max_{d\in C\setminus S}\bigl[\lambda\,\text{sim}(q,d)-(1-\lambda)\max_{d'\in S}\text{sim}(d,d')\bigr]\) |
| 2 | **Contextual Compression**<br>`build_compression_retriever()` | *Late-chunking*: fetch parent docs, then split & keep only top-`n` chunks via a custom `TopNSliceCompressor`. | `chunk_size`, `chunk_overlap`, `top_n` | 1. Dense sim (as above).<br>2. Split parent \(p\) → chunks \(c_1…c_m\).<br>3. Output \(S=\{c_1,…,c_{n}\}\). |
| 3 | **Multi-Query RAG**<br>`build_multiquery_retriever()` | LLM creates \(m\) diverse queries → union of their top-`k` hits. | `n_queries=m`, `top_k` | \(Q=\{q_0,\dots,q_{m-1}\}\)    \(D=\bigcup_{q_i\in Q}\text{TopK}(q_i)\) |
| 4 | **Hybrid Dense + Sparse**<br>`build_hybrid_fusion_retriever()` | Linear fuse dense (cosine) and BM25 scores. | `α` (blend), `sparse_k`, `dense_k` | \(\displaystyle \text{score}_{\text{hyb}}(d)=\alpha\,s_{\text{dense}}(d)+(1-\alpha)\,s_{\text{BM25}}(d)\) |
| 5 | **Slice Wrapper**<br>`SliceRetriever` | Decorator truncates any retriever’s list to *k* docs (hard budget). | `k` | \(D_{\text{out}} = D_{1:k}\) |

---

## Quick Explanations

### 1. Vector Similarity  
Rank chunks by cosine similarity in embedding space

### 2. Contextual Compression (Late-Chunking)  
Retrieve full docs → split only those → optionally drop chunks after `slice_filter`. Saves tokens & speeds up generation.

### 3. Multi-Query Retriever  
LLM-generated paraphrases widen recall on synonym-heavy or ambiguous queries.

### 4. Hybrid Fusion  
Dense vectors capture semantics; BM25 keeps keyword precision. Weight \(α\) trades recall vs precision.


### 5. Slice Retriever  
Guarantees ≤ *k* chunks reach the LLM, preventing context overflow and unpredictable cost.

---

## When to Use What?

| Situation | Best Choice |
|-----------|-------------|
| Clear terms, low latency | Vector Similarity |
| Need synonyms / paraphrases | Multi-Query |
| Want *few* but *precise* chunks | Contextual Compression + Slice |
| Mixed lexical + semantic signals | Hybrid Fusion |
