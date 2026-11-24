"""Sound Atlas - a no-login music explorer built with Streamlit.

Data: iTunes Search API (no key needed), MusicBrainz + Open-Meteo (map, no key needed).
Run:  pip install -r requirements.txt   then   streamlit run spotify_app.py
"""
import time

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Sound Atlas", page_icon="🎧", layout="wide")

ITUNES = "https://itunes.apple.com"
USER_AGENT = "SoundAtlas/1.0 (student project)"


# ---------------------------------------------------------------- API layer
class ApiError(Exception):
    """Friendly, user-facing API error."""


def fetch(url, params):
    try:
        r = requests.get(url, params=params, headers={"User-Agent": USER_AGENT}, timeout=15)
    except requests.RequestException:
        raise ApiError("Could not reach the music service. Check your internet connection.")
    if r.status_code in (403, 429):
        raise ApiError("Too many requests. Wait a minute and try again.")
    if r.status_code != 200:
        raise ApiError(f"The music service returned an error ({r.status_code}).")
    try:
        return r.json()
    except ValueError:
        raise ApiError("The music service sent back something unreadable. Try again.")


@st.cache_data(ttl=600, show_spinner=False)
def search_artists(term):
    data = fetch(f"{ITUNES}/search", {"term": term, "entity": "musicArtist", "limit": 10})
    return [r for r in data.get("results", []) if r.get("artistId")]


def release_type(name):
    if name.endswith("- Single"):
        return "Single"
    if name.endswith("- EP"):
        return "EP"
    return "Album"


@st.cache_data(ttl=600, show_spinner=False)
def load_albums(artist_id):
    data = fetch(f"{ITUNES}/lookup", {"id": artist_id, "entity": "album", "limit": 200})
    rows = [
        {
            "Release": a["collectionName"],
            "Type": release_type(a["collectionName"]),
            "Released": a.get("releaseDate", "")[:10],
            "Year": int(a["releaseDate"][:4]) if a.get("releaseDate") else 0,
            "Tracks": a.get("trackCount", 0),
            "Genre": a.get("primaryGenreName", ""),
            "id": a["collectionId"],
        }
        for a in data.get("results", [])
        if a.get("wrapperType") == "collection"
    ]
    return pd.DataFrame(rows)


@st.cache_data(ttl=600, show_spinner=False)
def load_tracks(collection_id):
    data = fetch(f"{ITUNES}/lookup", {"id": collection_id, "entity": "song"})
    rows = [
        {
            "#": t.get("trackNumber", 0),
            "Track": t["trackName"],
            "Minutes": round(t.get("trackTimeMillis", 0) / 60000, 2),
            "Explicit": t.get("trackExplicitness") == "explicit",
        }
        for t in data.get("results", [])
        if t.get("wrapperType") == "track"
    ]
    return pd.DataFrame(rows)


@st.cache_data(ttl=86400, show_spinner=False)
def artist_origin(name):
    """MusicBrainz (artist origin) + Open-Meteo geocoding -> (place, lat, lon)."""
    time.sleep(1.1)  # MusicBrainz asks for max 1 request/second (runs only on cache miss)
    try:
        mb = requests.get(
            "https://musicbrainz.org/ws/2/artist/",
            params={"query": f'artist:"{name}"', "fmt": "json", "limit": 1},
            headers={"User-Agent": USER_AGENT},
            timeout=15,
        ).json()
        match = mb["artists"][0]
        place = (match.get("begin-area") or match.get("area") or {}).get("name")
        if not place:
            return None
        geo = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": place, "count": 1},
            timeout=15,
        ).json()["results"][0]
        return place, geo["latitude"], geo["longitude"]
    except (requests.RequestException, KeyError, IndexError, ValueError):
        return None


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.title("🎧 Sound Atlas")
    st.caption("Find an artist. See their catalog. Map where they come from.")

    st.header("Filters")
    release_types = st.multiselect(
        "Release types", ["Album", "EP", "Single"], default=["Album", "EP", "Single"]
    )
    max_releases = st.slider("Max releases to show", 5, 50, 20, step=5)
    hide_explicit = st.checkbox("Hide explicit tracks", value=False)
    sort_order = st.radio("Sort releases by", ["Newest first", "Oldest first", "Most tracks"])

# --------------------------------------------------------------------- main
st.title("Sound Atlas")
st.caption("Pick an artist ➜ explore their releases ➜ see where the music started.")

# 1 · search -------------------------------------------------------------
st.header("1 · Find an artist")
c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
search_text = c1.text_input("Artist name", placeholder="e.g. Bad Bunny, Daft Punk, Celia Cruz")
go = c2.button("Search", type="primary", use_container_width=True)

if go:
    if not search_text.strip():
        st.warning("Type an artist name first.")
    else:
        try:
            with st.spinner("Searching..."):
                st.session_state["artists"] = search_artists(search_text.strip())
            if st.session_state["artists"]:
                st.success(f"Found {len(st.session_state['artists'])} artists.")
            else:
                st.warning("No artists matched. Check the spelling or try fewer words.")
        except ApiError as e:
            st.error(str(e))

artists = st.session_state.get("artists", [])
if not artists:
    st.info("Search for an artist to unlock charts, tables and the map.")
    st.stop()

# 2 · pick + overview ----------------------------------------------------
labels = {f"{a['artistName']}  ·  {a.get('primaryGenreName', 'no genre listed')}": a for a in artists}
choice = st.selectbox("Which artist did you mean?", list(labels))
selected = labels[choice]

st.header(f"2 · {selected['artistName']}")

if not release_types:
    st.warning("Select at least one release type in the sidebar.")
    st.stop()

try:
    with st.spinner("Loading releases..."):
        albums = load_albums(selected["artistId"])
except ApiError as e:
    st.error(str(e))
    st.stop()

albums = albums[albums["Type"].isin(release_types)] if not albums.empty else albums
if albums.empty:
    st.info("No releases found for those filters.")
    st.stop()

m1, m2, m3 = st.columns(3)
m1.metric("Releases shown", min(len(albums), max_releases))
m2.metric("Main genre", selected.get("primaryGenreName", "n/a"))
m3.metric("First release", int(albums[albums["Year"] > 0]["Year"].min()))

sorters = {
    "Newest first": ("Released", False),
    "Oldest first": ("Released", True),
    "Most tracks": ("Tracks", False),
}
sort_col, ascending = sorters[sort_order]
albums = albums.sort_values(sort_col, ascending=ascending).head(max_releases).reset_index(drop=True)

left, right = st.columns([3, 2])
with left:
    st.subheader("Release catalog")
    st.dataframe(albums.drop(columns=["id", "Year"]), use_container_width=True, hide_index=True)
with right:
    st.subheader("Releases per year")
    st.bar_chart(albums[albums["Year"] > 0].groupby("Year").size().rename("Releases"))
    st.caption("Bar chart: count of the releases shown on the left, grouped by year.")

# 3 · tracks ------------------------------------------------------------
st.header("3 · Inside a release")
release_name = st.selectbox("Choose a release", albums["Release"])
release_id = albums.loc[albums["Release"] == release_name, "id"].iloc[0]

try:
    tracks = load_tracks(release_id)
except ApiError as e:
    st.error(str(e))
    tracks = pd.DataFrame()

if not tracks.empty:
    if hide_explicit:
        hidden = int(tracks["Explicit"].sum())
        tracks = tracks[~tracks["Explicit"]]
        if hidden:
            st.info(f"Hid {hidden} explicit track(s).")
    if tracks.empty:
        st.warning("Every track on this release is explicit. Turn off the filter to see them.")
    else:
        t1, t2 = st.columns(2)
        t1.dataframe(tracks, use_container_width=True, hide_index=True)
        t2.line_chart(tracks.set_index("Track")["Minutes"])
        t2.caption("Track length in minutes, in album order.")
        st.success(f"{len(tracks)} tracks · {tracks['Minutes'].sum():.1f} minutes total.")

# 4 · map ---------------------------------------------------------------
st.header("4 · Where do they come from?")
st.caption("Uses MusicBrainz for each artist's origin and Open-Meteo to place it on the map.")

if st.button("Map all search results"):
    rows = []
    bar = st.progress(0, text="Looking up origins...")
    for i, a in enumerate(artists, start=1):
        origin = artist_origin(a["artistName"])
        if origin:
            rows.append({"Artist": a["artistName"], "Place": origin[0], "lat": origin[1], "lon": origin[2]})
        bar.progress(i / len(artists), text=f"Checked {a['artistName']}")
    bar.empty()
    st.session_state["origins"] = pd.DataFrame(rows)

origins = st.session_state.get("origins")
if origins is not None:
    if origins.empty:
        st.warning("No origins found for these artists.")
    else:
        st.map(origins, latitude="lat", longitude="lon", size=60000)
        with st.expander("See the places as a table"):
            st.dataframe(origins[["Artist", "Place"]], hide_index=True, use_container_width=True)
else:
    st.info("Press the button to plot your search results on the map. It takes a few seconds.")