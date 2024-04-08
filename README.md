# nlp-contexto-game
My implementation of game contexto (e.g. contexto.me) using embeddings. 

The goal of the game is to find secret word. The player submits the guess word and receives feedback in the form of proximity to the secret word. The proximity is calculated using GloVe embeddings.
The secret words are generated randomly from current week top news headlines.

Hints that you can expect:
1. First letter
2. Last letter
3. Length of the secret word
4. One of the top 10 most similar words (chosen randomly)

You can play it at https://adgapar-contexto-game.streamlit.app
