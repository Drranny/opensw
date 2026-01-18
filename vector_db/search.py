import faiss
import numpy as np

def search(index, query_vector, k=3):
    D, I = index.search(np.array([query_vector]), k)
    return I[0]
