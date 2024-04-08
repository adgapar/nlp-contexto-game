import streamlit as st
import pandas as pd
import numpy as np
from nlp import embedding, top10_most_similar, ranking_score
from word_generator import generate_secret_word

buttons_panel = st.columns(2)

with buttons_panel[0]:
    with st.popover("Game controls", use_container_width=True):
        new_game_button = st.empty()
        reset_game_button = st.empty()
        end_game_button = st.empty()

with buttons_panel[1]:
    hint_button = st.empty()

st.title("Word Guessing Game")
msg = st.empty()
msg.write("Try to guess the secret word. The closer your word is to the secret word, the higher your score.")  

hint1 = st.empty()
hint2 = st.empty()
hint3 = st.empty()
hint4 = st.empty()

def new_game(initial=False):
    secret_word = generate_secret_word()
    st.session_state["last_secret_word"] = secret_word
    st.session_state["input_value"] = ""
    st.session_state["hints_count"] = 0
    st.session_state["hinted_word"] = None
    st.session_state["game_is_finished"] = False
    st.session_state["submissions"] = pd.DataFrame({
        "label": [],
        "guess": [],
        "proximity": []
    })
    if not initial:
        st.info("New game started!", icon="🆕")

def reset_game():
    if st.session_state["game_is_finished"]:
        st.warning("Game is finished. Start new game", icon="🚫")
    else:
        st.session_state["submissions"] = pd.DataFrame({
            "label": [],
            "guess": [],
            "proximity": []
        })
        st.session_state["input_value"] = ""
        st.warning("Game is reset: same word, attempts are removed", icon="🔄")

def end_game(reason="lose"):
    st.session_state["game_is_finished"] = True
    submissions_df = st.session_state["submissions"]

    if reason == "lose":
        st.error(f"You gave up :(. The secret word was `{SECRET_WORD}`. Do you want to try again?")
        last_label = f"Correct word: {SECRET_WORD}"
    elif reason == "win":
        hints_count = st.session_state["hints_count"]
        st.success(f"Congratulations! You guessed the secret word `{SECRET_WORD}` with {hints_count} hints.")
        last_label = f"Correct attempt #{submissions_df.shape[0] + 1}: {SECRET_WORD}"
    
    correct_df = pd.DataFrame({
        "label": last_label,
        "guess": SECRET_WORD,
        "proximity": 0
    }, index=[0])

    submissions_df = pd.concat([submissions_df, correct_df], ignore_index=True)
    st.session_state["submissions"] = submissions_df

def get_hint():
    if st.session_state["game_is_finished"]:
        st.warning("Game is finished. Start new game", icon="🚫")
    else:
        hints_count = st.session_state["hints_count"]
        if hints_count > 3:
            st.error("No more hints available", icon="🚫")
        else:
            st.session_state["hints_count"] = hints_count + 1

def has_been_guessed(guess):
    submissions_df = st.session_state["submissions"]
    return guess in submissions_df["guess"].values

def display_progress():
    submissions_df = st.session_state["submissions"]
    if submissions_df.shape[0] == 0:
        return
    
    submissions_df = submissions_df.drop_duplicates()

    sorted_submissions = submissions_df.sort_values("proximity", ascending=True)
    for _, row in sorted_submissions.iterrows():
        proximity = row["proximity"]
        label = row["label"]
        progress = (PROGRESS_SCALE - proximity) / PROGRESS_SCALE
        st.progress(progress, label)

if "last_secret_word" not in st.session_state:
    new_game(initial=True)

SECRET_WORD = st.session_state["last_secret_word"]
SECRET_VEC = embedding(SECRET_WORD)
PROGRESS_SCALE = 10000
submissions_df = st.session_state["submissions"]
hints_count = st.session_state["hints_count"]

if hints_count > 0:
    hint1.write(f"Hint #1: the secret word starts with `{SECRET_WORD[0]}`")
if hints_count > 1:
    hint2.write(f"Hint #2: the secret word ends with `{SECRET_WORD[-1]}`")
if hints_count > 2:
    hint3.write(f"Hint #3: the secret word has {len(SECRET_WORD)} letters")
if hints_count > 3:
    hinted_word = st.session_state["hinted_word"]
    if hinted_word is None:
        closest_words = top10_most_similar(SECRET_WORD)
        closest_words = [word for word, _ in closest_words]
        hint_word = np.random.choice(closest_words)
        st.session_state["hinted_word"] = hint_word
    
    hint_word = st.session_state["hinted_word"]
    hint4.write(f"Hint #4 (final): try `{hint_word}`")


with st.form("guess_form"):
    col1, col2 = st.columns([3, 1])
    with col1:
        guess_word = st.text_input("Your guess", label_visibility="collapsed", placeholder="Your guess", value=st.session_state["input_value"])

    with col2:
        submitted = st.form_submit_button("Submit", help="Submit your guess", use_container_width=True)

    if submitted:
        st.session_state["input_value"] = guess_word

guess_word = st.session_state["input_value"]

if guess_word and guess_word != "":
    st.session_state["input_value"] = ""
    guess_word = guess_word.lower().strip()
    guess_vec = embedding(guess_word)
    if guess_vec is None:
        st.write(":red[I don't know that word.]")
    elif guess_word == SECRET_WORD:
        end_game(reason="win")
    elif has_been_guessed(guess_word):
        st.write(":red[You've already tried that word.]")
    else:
        score = ranking_score(guess_vec, SECRET_VEC, PROGRESS_SCALE)
        guess_df = pd.DataFrame({
            "label": f"Attempt #{submissions_df.shape[0] + 1}: {guess_word}",
            "guess": guess_word,
            "proximity": score
        }, index=[0])
        submissions_df = pd.concat([submissions_df, guess_df], ignore_index=True)
        st.session_state["submissions"] = submissions_df

to_show = submissions_df.shape[0] > 0

if to_show:
    display_progress()

if st.session_state["game_is_finished"]:
    msg.write("Game is finished. Start a new game.")

new_game_button.button("New Game", on_click=new_game, use_container_width=True)
reset_game_button.button("Reset Game", on_click=reset_game, use_container_width=True)
end_game_button.button("End Game", on_click=end_game, use_container_width=True)
hint_button.button('Hint', on_click=get_hint, use_container_width=True)