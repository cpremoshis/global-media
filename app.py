import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

st.set_page_config(
    page_title="Global Media",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
    )

#Opens CSV of broadcasters with links and other info
@st.cache_data
def open_database():
    database = "Assets/broadcasters.csv"

    with open(database, 'r') as f:
        df = pd.read_csv(f)
    
    return df

#Pull Wikipedia summary for selected outlet
@st.cache_data
def wiki_summary(outlet_wiki):
    request_url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{outlet_wiki}?redirect=true'

    wiki_response = requests.get(request_url)
    wiki_data = wiki_response.json()
    summary = wiki_data['extract']

    return summary

#Pull data for selected outlet
@st.cache_data
def pull_data(outlet):
    selection_info = broadcasters_df[broadcasters_df['Name'] == outlet]
    selection_name = selection_info['Name'].iloc[0]
    selection_country = selection_info['Country'].iloc[0]
    selection_format = selection_info['Format'].iloc[0]
    selection_type = selection_info['Type'].iloc[0]
    selection_wiki = selection_info['Wiki'].iloc[0]
    selection_media_url = selection_info['Media URL'].iloc[0]
    selection_page_url = selection_info['Page URL'].iloc[0]

    return selection_name, selection_country, selection_format, selection_type, selection_wiki, selection_media_url, selection_page_url

#Generate media player.
#Fourth argument is optional and blank by default; if media player needs auto-muted on load, enter 'muted="muted"' when calling function. 
def generate_player(format, type, url, muted=""):
    if format == "M3U8" and type == "Video":
        m3u8_video_player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HLS Stream</title>
            <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
            <style>
                html, body, div, span, applet, object, iframe,
                video, audio {{
                    margin: 0;
                    padding: 0;
                    border: 0;
                    background-color: #0E1117;
                    vertical-align: baseline;
                    box-sizing: border-box; /* Include padding and border in the element's size */
                }}
            </style>
        </head>
        <body>
        <video id="video" controls autoplay {muted} style="width:100vw; height:100vh; object-fit: contain; margin:auto"></video>
        <script>
            var video = document.getElementById('video');
            if (Hls.isSupported()) {{
                var hls = new Hls();
                hls.loadSource('{url}');
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function() {{
                    video.play();
                }});
            }}
            // For browsers like Safari that support HLS natively
            else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = '{url}';
                video.addEventListener('loadedmetadata', function() {{
                    video.play();
                }});
            }}
        </script>
        </body>
        </html>
        """

        return m3u8_video_player_html, 525
    
    if format == "M3U8" and type == "Audio":
        m3u8_audio_player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HLS Stream</title>
            <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
            <style>
                html, body, div, span, applet, object, iframe,
                video, audio {{
                    margin: 0;
                    padding: 0;
                    border: 0;
                    background-color: #0E1117;
                    vertical-align: baseline;
                    box-sizing: border-box; /* Include padding and border in the element's size */
                }}
            </style>
        </head>
        <body>

        <audio id="audio" controls autoplay {muted} style="width:100vw; height:100vh;"></audio>

        <script>
            var audio = document.getElementById('audio');
            if (Hls.isSupported()) {{
                var hls = new Hls();
                hls.loadSource('{url}');
                hls.attachMedia(audio);
                hls.on(Hls.Events.MANIFEST_PARSED, function() {{
                    audio.play();
                }});
            }}
            // For browsers like Safari that support HLS natively
            else if (audio.canPlayType('application/vnd.apple.mpegurl')) {{
                audio.src = '{url}';
                audio.addEventListener('loadedmetadata', function() {{
                    audio.play();
                }});
            }}
        </script>

        </body>
        </html>
        """

        return m3u8_audio_player_html, 40
    
    if format == "MP3":
        mp3_audio_player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
            html, body {{
                margin: 0;
                padding: 0;
                border: 0;
                background-color: #0E1117; /* Set the background color */
                height: 100%; /* Full height */
                width: 100%; /* Full width */
                display: flex; /* Use flex to center the audio player */
                justify-content: center; /* Center horizontally */
                align-items: center; /* Center vertically */
                overflow: hidden; /* Hide scrollbars if the content is larger than the viewport */
            }}
            audio {{
                /* No need to set width or height here as the controls should automatically adjust to the content */
            }}
            </style>
        </head>
        <body>
            <audio id="audio" controls{muted} autoplay>
                <source src="{url}" type="audio/mpeg">
            </audio>
        </body>
        </html>
        """
        return mp3_audio_player_html, 40

    if format == "YouTube":
        player_html = st.video(url)
        return player_html, None

#Opens database to load media outlet data
broadcasters_df = open_database()

#Sidebar with user input options
with st.sidebar:
    st.title("Title TBD")

    display_type = st.radio("Display type:", ['Single', 'Multiview'], horizontal=True)

    if display_type == 'Single':

        if 'index' not in st.session_state:
            st.session_state['index'] = 0

        selection = st.selectbox("Outlet:", broadcasters_df['Name'], index=st.session_state['index'])
        record_time = st.slider("Record length (minutes):", min_value=.5, max_value=5.0, step=.5, format="m:ss")
        if st.button("Record", type="primary"):
            st.warning("Record feature not yet setup")
        
    else:
        selections = st.multiselect("Select outlets:", broadcasters_df['Name'], max_selections=4)

        selections_len = len(selections)

#Media display
if display_type == "Single":
    selection_name, selection_country, selection_format, selection_type, selection_wiki, selection_media_url, selection_page_url = pull_data(selection)

    #Metrics/info display
    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.metric("Name", selection_name)
    with middle_column:
        st.metric("Country", selection_country)

    result = generate_player(selection_format, selection_type, selection_media_url)

    if result[1] is not None:
        player_html, player_size = result
        components.html(player_html, height=player_size)
    else:
        player_html = result[0]

    st.subheader("Summary")
    st.write(wiki_summary(selection_wiki))
    st.write(selection_page_url)
    st.caption("Information from Wikipedia")
else:
    #No media
    if selections_len == 0:
        st.warning("No outlets selected")

    #Single media
    if selections_len == 1:
        #First (and only) selection
        first_selection = selections[0]
        first_selection_name, first_selection_country, first_selection_format, first_selection_type, first_selection_wiki, first_selection_media_url, first_selection_page_url = pull_data(first_selection)

        #First (and only) media player
        result = generate_player(first_selection_format, first_selection_type, first_selection_media_url)
        if result[1] is not None:
            player_html, player_size = result
            components.html(player_html, height=player_size)
        else:
            player_html = result[0]

    #Two media
    if selections_len == 2:
        column_left, column_right = st.columns(2)

        #First selection
        first_selection = selections[0]
        first_selection_name, first_selection_country, first_selection_format, first_selection_type, first_selection_wiki, first_selection_media_url, first_selection_page_url = pull_data(first_selection)

        #Second selection
        second_selection = selections[1]
        second_selection_name, second_selection_country, second_selection_format, second_selection_type, second_selection_wiki, second_selection_media_url, second_selection_page_url = pull_data(second_selection)

        #First media player
        with column_left:
            first_result = generate_player(first_selection_format, first_selection_type, first_selection_media_url)
            if first_result[1] is not None:
                player_html, player_size = first_result
                components.html(player_html, height=400)
            else:
                player_html = first_result[0]

        #Second media player
        with column_right:
            second_result = generate_player(second_selection_format, second_selection_type, second_selection_media_url, muted="muted")
            if second_result[1] is not None:
                player_html, player_size = second_result
                components.html(player_html, height=400)
            else:
                player_html = second_result[0]

    #Three media
    if selections_len == 3:
        column_left, column_right = st.columns(2)
        blank_left, column_middle, blank_right = st.columns([0.2, 0.6, 0.2])

        #First selection
        first_selection = selections[0]
        first_selection_name, first_selection_country, first_selection_format, first_selection_type, first_selection_wiki, first_selection_media_url, first_selection_page_url = pull_data(first_selection)

        #Second selection
        second_selection = selections[1]
        second_selection_name, second_selection_country, second_selection_format, second_selection_type, second_selection_wiki, second_selection_media_url, second_selection_page_url = pull_data(second_selection)

        #Third selection
        third_selection = selections[2]
        third_selection_name, third_selection_country, third_selection_format, third_selection_type, third_selection_wiki, third_selection_media_url, third_selection_page_url = pull_data(third_selection)

        with column_left:
            #First media player
            first_result = generate_player(first_selection_format, first_selection_type, first_selection_media_url)
            if first_result[1] is not None:
                player_html, player_size = first_result
                components.html(player_html, height=365)
            else:
                player_html = first_result[0]

        with column_right:
            #Second media player
            second_result = generate_player(second_selection_format, second_selection_type, second_selection_media_url, muted="muted")
            if second_result[1] is not None:
                player_html, player_size = second_result
                components.html(player_html, height=365)
            else:
                player_html = second_result[0]

        with column_middle:
            #Third media player
            third_result = generate_player(third_selection_format, third_selection_type, third_selection_media_url, muted="muted")
            if third_result[1] is not None:
                player_html, player_size = third_result
                components.html(player_html, height=365)
            else:
                player_html = third_result[0]

    #Four media
    if selections_len == 4:
        column_left, column_right = st.columns(2)

        #First selection
        first_selection = selections[0]
        first_selection_name, first_selection_country, first_selection_format, first_selection_type, first_selection_wiki, first_selection_media_url, first_selection_page_url = pull_data(first_selection)

        #Second selection
        second_selection = selections[1]
        second_selection_name, second_selection_country, second_selection_format, second_selection_type, second_selection_wiki, second_selection_media_url, second_selection_page_url = pull_data(second_selection)

        #Third selection
        third_selection = selections[2]
        third_selection_name, third_selection_country, third_selection_format, third_selection_type, third_selection_wiki, third_selection_media_url, third_selection_page_url = pull_data(third_selection)

        #Fourth selection
        fourth_selection = selections[3]
        fourth_selection_name, fourth_selection_country, fourth_selection_format, fourth_selection_type, fourth_selection_wiki, fourth_selection_media_url, fourth_selection_page_url = pull_data(fourth_selection)

        with column_left:
            #First media player
            first_result = generate_player(first_selection_format, first_selection_type, first_selection_media_url)
            if first_result[1] is not None:
                player_html, player_size = first_result
                components.html(player_html, height=365)
            else:
                player_html = first_result[0]

            #Third media player
            third_result = generate_player(third_selection_format, third_selection_type, third_selection_media_url, muted="muted")
            if third_result[1] is not None:
                player_html, player_size = third_result
                components.html(player_html, height=365)
            else:
                player_html = third_result[0]

        with column_right:
            #Second media player
            second_result = generate_player(second_selection_format, second_selection_type, second_selection_media_url, muted="muted")
            if second_result[1] is not None:
                player_html, player_size = second_result
                components.html(player_html, height=365)
            else:
                player_html = second_result[0]

            #Fourth media player
            fourth_result = generate_player(fourth_selection_format, fourth_selection_type, fourth_selection_media_url, muted="muted")
            if fourth_result[1] is not None:
                player_html, player_size = fourth_result
                components.html(player_html, height=365)
            else:
                player_html = fourth_result[0]