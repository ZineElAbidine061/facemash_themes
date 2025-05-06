import streamlit as st
import random
import pandas as pd
import requests

st.set_page_config(page_title="Facemash Culturel", layout="centered")
st.title("Facemash Culturel : Duel par thème")

themes = ["Films", "Séries", "Musiques"]
selected_theme = st.selectbox("Choisis un thème :", themes)

# TMDB API
TMDB_API_KEY = "1b9c5eeeb36a9d4d72db645e9d08cb3e"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

@st.cache_data
def get_tmdb_items(category):
    endpoint = f"{TMDB_BASE_URL}/trending/{category}/week?api_key={TMDB_API_KEY}"
    response = requests.get(endpoint)
    data = response.json()
    items = data.get("results", [])[:20]
    return [{"title": i.get("title") or i.get("name"), "image": f"https://image.tmdb.org/t/p/w500{i['poster_path']}", "id": i["id"]} for i in items if i.get("poster_path")]

@st.cache_data
def get_music_items():
    url = "https://api.deezer.com/chart"
    response = requests.get(url)
    data = response.json()

    items = []
    for track in data.get("tracks", {}).get("data", []):
        title = f"{track['title']} – {track['artist']['name']}"
        image = track["album"]["cover_big"]
        if title and image:
            items.append({"title": title, "image": image})


    return items




# Choix des éléments selon thème
if selected_theme == "Films":
    items = get_tmdb_items("movie")
elif selected_theme == "Séries":
    items = get_tmdb_items("tv")
elif selected_theme == "Musiques":
    items = get_music_items()
elif selected_theme == "Jeux Vidéo":
    items = get_games_items()



# Initialisation de session
if "duel_count" not in st.session_state:
    st.session_state.duel_count = 0
    st.session_state.results = []

if st.session_state.duel_count < 10:
    # Filtrer les doublons (titre + image)
    unique_items = { (item["title"], item["image"]) : item for item in items }.values()
    unique_items = list(unique_items)

    if len(unique_items) < 2:
        st.error("Pas assez d'éléments vraiment distincts pour un duel.")
        st.stop()

    duel = random.sample(unique_items, 2)

    col1, col2 = st.columns(2)
    with col1:
        st.image(duel[0]["image"], use_container_width=True)
        if st.button(f"Je choisis : {duel[0]['title']}", key="left"):
            st.session_state.results.append({
                "winner": duel[0]["title"],
                "loser": duel[1]["title"],
                "theme": selected_theme
            })
            st.session_state.duel_count += 1
            st.experimental_rerun()

    with col2:
        st.image(duel[1]["image"], use_container_width=True)
        if st.button(f"Je choisis : {duel[1]['title']}", key="right"):
            st.session_state.results.append({
                "winner": duel[1]["title"],
                "loser": duel[0]["title"],
                "theme": selected_theme
            })
            st.session_state.duel_count += 1
            st.experimental_rerun()

else:
    st.subheader("Résultats du thème :")
    df = pd.DataFrame(st.session_state.results)
    df_counts = df["winner"].value_counts().reset_index()
    df_counts.columns = ["Titre", "Victoires"]
    st.table(df_counts.head(3))
    df.to_csv(f"votes_{selected_theme}.csv", index=False)
    st.success("Votes enregistrés dans le fichier CSV.")
