# Lesson 08 — Building Search Applications (Embeddings)

> Source: `08-building-search-applications` · Retargeted to `gemini-embedding-001`.

## 🎯 Goal
Build semantic search over a corpus using embeddings + cosine similarity.

---

## 1. Semantic vs keyword search
Search "my dream car" →
- **Keyword search** returns documents about *dreaming*. ❌
- **Semantic search** understands you mean your *ideal* car. ✅

## 2. What is a text embedding?
A **vector** — a list of floats — that numerically represents the *meaning* of text. Similar meanings
land close together in that space.

```python
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

r = client.models.embed_content(
    model="gemini-embedding-001",
    contents=["Today we are going to learn about Azure Machine Learning."],
)
vec = r.embeddings[0].values
print(len(vec), vec[:6])
# 3072 [-0.0066, 0.0026, 0.0087, -0.0244, -0.0085, 0.0220]
```
> ✅ Verified: `gemini-embedding-001` returns **3072-dimensional** vectors and accepts a batch list of strings.

## 3. Building an embedding index — the pipeline

The course's YouTube-transcript index was built by a Python pipeline. The shape is universal:

1. **Download** the source content (transcripts).
2. **Extract metadata** with an LLM (e.g. the speaker's name from the first 3 minutes) — function calling, lesson 11.
3. **Chunk** into segments (3-minute windows, ~20 words of **overlap** so meaning isn't cut mid-thought and context is preserved).
4. **Summarize** each chunk (~60 words) with the model — stored alongside.
5. **Embed** each chunk → vector → store chunk + vector + metadata in the index.

```python
import json, numpy as np
from google import genai

client = genai.Client()
EMBED = "gemini-embedding-001"

def embed(texts: list[str]) -> np.ndarray:
    r = client.models.embed_content(model=EMBED, contents=texts)
    return np.array([e.values for e in r.embeddings])

chunks = ["...segment 1...", "...segment 2...", "...segment 3..."]
index = [{"text": c, "embedding": v.tolist()} for c, v in zip(chunks, embed(chunks))]

with open("embedding_index.json", "w") as f:
    json.dump(index, f)
```

> For the lesson, the index is a **JSON file loaded into a pandas DataFrame**. In production use a
> **vector database**: Chroma, FAISS, Pinecone, Weaviate, Qdrant, Redis, Azure AI Search.

## 4. Cosine similarity (a.k.a. nearest-neighbour search)

Measures the **cosine of the angle** between two vectors. Better than Euclidean distance for text:
two documents of very different lengths can still point the same direction, so the angle is small
even when the straight-line distance is large.

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

Vectorized over the whole index:

```python
def search(query: str, index, top_k: int = 5):
    q = embed([query])[0]
    M = np.array([item["embedding"] for item in index])
    # normalize once, then a single matrix product gives all similarities
    sims = (M @ q) / (np.linalg.norm(M, axis=1) * np.linalg.norm(q))
    order = np.argsort(sims)[::-1][:top_k]
    return [(float(sims[i]), index[i]["text"]) for i in order]

for score, text in search("can you use rstudio with azure ml?"):
    print(f"{score:.3f}  {text[:90]}")
```

## 5. The full search app

```python
import json, numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()
EMBED = "gemini-embedding-001"

index = json.load(open("embedding_index.json"))
M = np.array([i["embedding"] for i in index])
M_norm = M / np.linalg.norm(M, axis=1, keepdims=True)

while True:
    q = input("\nSearch (or 'quit'): ")
    if q.strip().lower() == "quit":
        break
    qv = np.array(client.models.embed_content(model=EMBED, contents=[q]).embeddings[0].values)
    sims = M_norm @ (qv / np.linalg.norm(qv))
    for i in np.argsort(sims)[::-1][:5]:
        item = index[i]
        print(f"{sims[i]:.3f}  {item.get('title','')}  {item.get('url','')}")
        print(f"        {item['text'][:120]}...")
```

Because each chunk carries a timestamp, the result URL can deep-link to the exact moment in the
video that answers the question — the real payoff of chunk-level indexing.

---

## 🧠 Crux Notes
- **Embed once, search many.** Building the index is the expensive step; queries are cheap matrix math.
- **Chunking with overlap** is what makes retrieval good — no overlap means answers cut in half.
- **Cosine similarity ignores magnitude**, which is why it beats Euclidean distance for text of varying length.
- Normalize your matrix once up front; then similarity is a single dot product.
- JSON + numpy is fine for learning; move to a **vector DB** when the index outgrows memory.
- Store **metadata alongside vectors** (title, url, timestamp) — the vector alone can't link a user anywhere.

---

## ✅ Test Your Knowledge

**1.** Someone searches "my dream car". What does keyword search return versus semantic search?
<details><summary>Answer</summary>

Keyword search returns documents about *dreaming*. Semantic search understands the intent — your *ideal* car — and returns car-buying content.
</details>

**2.** Why cosine similarity rather than Euclidean distance for text?
<details><summary>Answer</summary>

Cosine measures the **angle**, ignoring magnitude. Two documents of very different lengths can point the same direction — small angle, large Euclidean distance. Cosine gets the semantics right.
</details>

**3.** Why do chunks overlap by ~20 words?
<details><summary>Answer</summary>

So meaning is not severed at a chunk boundary, and each chunk carries a little context from its neighbour — which improves both the embedding and the retrieved result.
</details>

**4.** Your index has 3072-dim vectors for 10,000 chunks. Why normalise the matrix once at startup?
<details><summary>Answer</summary>

Then each query is a single dot product instead of recomputing norms for every row on every search — the same maths, far faster.
</details>

**5.** You store only vectors, no metadata. What breaks?
<details><summary>Answer</summary>

You can find the most similar vector but cannot show the user anything — no title, URL or timestamp. A vector alone links nowhere.
</details>

---

## 🛠️ Practical Task

**Build:** `practice/08_search.py` — semantic search over a real corpus.

### Corpus
Use the lesson notes themselves — `lessons/*.md` — as your documents. Self-contained and you know the ground truth.

### Requirements
1. Read all `lessons/*.md`, chunk each to ~800 chars **with ~100 chars overlap**.
2. Embed with `gemini-embedding-001` (batch — do not loop one call per chunk).
3. Cache the index to `practice/08_index.json` and **reuse it** if the file exists.
4. Search loop: query → top-5 results with similarity score and source filename.
5. Normalise the matrix once at load.

### Passing criteria

| # | Criterion | Expected |
|---|---|---|
| 1 | Index builds and caches | Second run is visibly faster; no re-embedding |
| 2 | Chunks overlap | Verify two consecutive chunks share text |
| 3 | Batched embedding | One call per batch, not per chunk |
| 4 | Scores descend | Top-5 sorted high → low |
| 5 | **Relevance** | See test cases |

### Test cases

| Query | Top result must come from |
|---|---|
| "how do I stop the model making things up" | lesson 03 or 04 |
| "what is cosine similarity" | lesson 08 or 15 |
| "the model wants to call my python function" | lesson 11 |
| "running a model on my own laptop offline" | lesson 16 or 19 |
| "purple elephant tax law" | **all scores low** — nothing relevant exists |

### Verify
```bash
time python practice/08_search.py   # run 1: builds index
time python practice/08_search.py   # run 2: must be much faster
```
**PASS:** 4 of 5 relevance cases hit the expected lesson, and the nonsense query scores visibly lower than the others.

**Key insight from case 5:** the retriever *always* returns its best 5, however bad they are. That is why lesson 15 adds a **relevance threshold**.
