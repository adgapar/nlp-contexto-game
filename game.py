import streamlit as st
import gensim.downloader as api  # type: ignore
import numpy as np
import pandas as pd
from typing import List


@st.cache_data(show_spinner=False)
def load_model():
    return api.load('glove-wiki-gigaword-100')

def similarity_score(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def ranking(max_similarity, similarity):
    return round(10000 * (max_similarity - similarity) / max_similarity)

def embedding(word):
    try:
        return model[word]
    except KeyError:
        return None
    
model = load_model()

SECRET_WORD = "apple"
MAX_SIMILARITY = model.most_similar(SECRET_WORD)[0][1]

st.title("Word Guessing Game")
st.write("I'm thinking of a word. Can you guess it?")

key = f"{SECRET_WORD}_submissions"

if key in st.session_state:
    submissions_df = st.session_state[key]
else:
    submissions_df = pd.DataFrame({
        "guess": [],
        "is_close": [],
        "similarity": []
    })
    st.session_state[key] = submissions_df

guess_bars: List[str] = []

guess_word = st.text_input("Your guess")

if guess_word:
    guess_vec = embedding(guess_word)
    if guess_vec is None:
        st.write("I don't know that word.")
    else:
        if guess_word.lower() == SECRET_WORD:
            st.write("You win!")
            st.write(f"The secret word was {SECRET_WORD}")

        secret_vec = embedding(SECRET_WORD)
        score = similarity_score(guess_vec, secret_vec)
        score = 0 if score < 0 else score
        ranking_score = ranking(MAX_SIMILARITY, score)
        guess_df = pd.DataFrame({
            "guess": guess_word,
            "is_close": score > 0.5,
            "similarity": score
        }, index=[0])

        submissions_df = pd.concat([submissions_df, guess_df], ignore_index=True)
        st.session_state[key] = submissions_df


to_show = guess_df.shape[0] > 0

if to_show:
    st.write("Previous guesses:")
    st.write(guess_df)
    st.write("Guess similarity:")
    st.write(guess_bars)



