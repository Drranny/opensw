import faiss
from ingest.embed import embed_chunks

def build_index(chunks):
    vectors = embed_chunks(chunks)
    dim = vectors.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(vectors)

    return index
