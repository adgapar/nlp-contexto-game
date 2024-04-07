import numpy as np
import streamlit as st
from nlp import embedding, top10_most_similar
from news import get_today_news

def generate_secret_word():
    word = None
    try:
        words = get_today_news()
        words = list(words.keys())
        st.toast(f"Found {len(words)} words in the news this week.", icon="📰")
        while word is None:
            random_word = np.random.choice(words)
            vector = embedding(random_word)
            if vector is not None and random_word.isalpha() and len(random_word) > 3:
                word = random_word
    except:
        st.toast("No news available.", icon='😞')

    if word is None:
        st.toast("Generating a random word.", icon='🤖')
        word = backup_word_generator()
    
    return word

def backup_word_generator():
    secret_word = None
    while secret_word is None:
        random_vector = np.random.rand(100)
        top_word, top_similarity = top10_most_similar(random_vector)[0]
        if top_similarity > 0.3 and top_word.isalpha():
            secret_word = top_word
    
    return secret_word