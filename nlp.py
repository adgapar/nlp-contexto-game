import streamlit as st
import gensim.downloader as api  # type: ignore
import numpy as np

@st.cache_data(show_spinner=False)
def load_model():
    return api.load('glove-wiki-gigaword-100')
    
model = load_model()

def embedding(word):
    """Get the word embedding for a given word or None if the word is not in the model."""
    try:
        return model[word]
    except KeyError:
        return None
    
def top10_most_similar(word_or_vector):
    """Get the most similar word to a given word or vector."""
    try:
        return model.most_similar(word_or_vector)
    except KeyError:
        return None
    
def similarity_score(vec1, vec2):
    """Cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def normalized_proximity(similarity, progress_scale, max_similarity):
    """Normalize the similarity to a progress scale."""
    norm_proximity = round(progress_scale * (max_similarity - similarity) / max_similarity)
    if norm_proximity == 0:
        return progress_scale * 0.05

    if norm_proximity > progress_scale:
        return progress_scale
    
    return norm_proximity

def ranking_score(guess_vec, secret_vec, progress_scale=10000):
    score = similarity_score(guess_vec, secret_vec)
    max_similarity = top10_most_similar(secret_vec)[0][1]
    ranking = normalized_proximity(score, progress_scale, max_similarity)
    return ranking