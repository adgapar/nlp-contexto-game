import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity # type: ignore
import gensim.downloader as api  # type: ignore

@st.cache(allow_output_mutation=True)
def load_model():
    return api.load('glove-wiki-gigaword-100')

def similarity_score(vec1, vec2):
    return cosine_similarity(vec1.reshape(1, -1), vec2.reshape(1, -1))[0][0]

def embedding(word):
    try:
        return model[word]
    except KeyError:
        return None

SECRET_WORD = "apple"

model = load_model()

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
        st.write(f"Similarity score: {score}")



