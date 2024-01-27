import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests
from recording import record_m3u8, record_youtube, record_mp3, multi_record
import zipfile
import time

st.set_page_config(
    page_title="GlobalBroadcastHub",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
    )

custom_html = open('extra_html.html', 'r').read()
st.markdown(custom_html, unsafe_allow_html=True)

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
@st.cache_resource
class Outlet:
    def __init__(self, outlet, broadcasters_df):
        outlet_info = broadcasters_df[broadcasters_df['Name'] == outlet].iloc[0]
        self.name = outlet_info['Name']
        self.country = outlet_info['Country']
        self.language = outlet_info['Language']
        self.format = outlet_info['Format']
        self.type = outlet_info['Type']
        self.wiki = outlet_info['Wiki']
        self.playback_url = outlet_info['Playback M3U8']
        self.recording_url = outlet_info['Recording M3U8']
        self.root_url = outlet_info['Root URL']
        self.page_url = outlet_info['Page URL']

####CONSIDER ADDING FILE ZIPPING TO RECORDING.PY. GETTING TOO MESSY####
#Zip files for download
def zip_single_recording(recording, translation, audio):
    
    files_to_zip = [recording, translation, audio]

    zip_folder_name = recording.split(".mp4")[0] + ".zip"

    with zipfile.ZipFile(zip_folder_name, 'w') as zipf:
        for file in files_to_zip:
            file_name = file.split("/")[2]
            zipf.write(file, arcname=file_name)

    return zip_folder_name

def zip_multiple_recordings(video_dict, savetime):
    
    values = [value for key in video_dict for value in video_dict[key].values()]

    files_to_zip = [item for item in values if item != "None"]

    zip_folder_name = f"./Recordings/Multi_record_{savetime}.zip"

    with zipfile.ZipFile(zip_folder_name, 'w') as zipf:
        for file in files_to_zip:
            file_name = file.split("/")[2]
            zipf.write(file, arcname=file_name)

    return zip_folder_name

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

        if display_type == "Single":
            return m3u8_video_player_html, 525
        elif display_type == "Multiview":
            return m3u8_video_player_html, 475
    
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

#Opens .csv database to load media outlet data
broadcasters_df = open_database()

#Sets a default index to keep track of recordings for the session
if 'recordings' not in st.session_state:
    st.session_state['recordings'] = []

#Sidebar with user input options
with st.sidebar:
    st.title("GlobalBroadcastHub")

    display_type = st.radio("Display type:", ['Single', 'Multiview', 'Live Translation'], horizontal=True)

    #Reformats the full file name into just the ending (ex: "Outlet_time.mp4")
    def format_file_names(option):
        option = option.split("/")[2]
        return option

    if display_type == 'Single':

        #----->User input<-----
        #Filters list of outlets based on selected languages
        #If no language is selected, defaults to all languages

        languages = st.multiselect("Select languages:", broadcasters_df['Language'].unique(), placeholder="All languages")

        broadcasters_filtered_by_lang = []

        if len(languages) == 0:
            for row in broadcasters_df.itertuples():
                broadcasters_filtered_by_lang.append(row.Name)
        else:
            for row in broadcasters_df.itertuples():
                if row.Language in languages:
                    broadcasters_filtered_by_lang.append(row.Name)

        st.session_state['selection'] = st.selectbox("Outlet:", broadcasters_filtered_by_lang)

        outlet = Outlet(st.session_state['selection'], broadcasters_df)

        record_time = st.slider("Record length (minutes):", min_value=.5, max_value=5.0, step=.5)
        record_time = record_time * 60

        translate = st.checkbox("Translate/transcribe")

        #----->Recording and download functions<-----
        if st.button("Record", type="primary"):

            with st.spinner("Recording in progress. Do not change any settings."):

                if outlet.format == "M3U8" and translate == True:
                    status, name, recording, translation, audio = record_m3u8(outlet.name, record_time, outlet.recording_url, outlet.root_url, translate)
                    zipped_files = zip_single_recording(recording, translation, audio)
                elif outlet.format == "M3U8":
                    status, name, recording = record_m3u8(outlet.name, record_time, outlet.recording_url, outlet.root_url, translate)

                elif outlet.format == "MP3" and translate == True:
                    status, recording, translation, audio = record_mp3(outlet.name, record_time, outlet.recording_url, translate)
                    zipped_files = zip_single_recording(recording, translation, audio)
                elif outlet.format == "MP3":
                    status, recording = record_mp3(outlet.name, record_time, outlet.recording_url, translate)

                elif outlet.format == "YouTube" and translate == True:
                    status, recording, translation, audio = record_youtube(outlet.name, record_time, outlet.recording_url, translate)
                    zipped_files = zip_single_recording(recording, translation, audio)
                elif outlet.format == "YouTube":
                    status, recording = record_youtube(outlet.name, record_time, outlet.recording_url)

            if status == True and 'zipped_files' in locals():
                st.session_state['recordings'].append(zipped_files)
            elif status == True:
                st.session_state['recordings'].append(recording)
            else:
                st.error("Error.")

        #Displays selection box if the 'recordings' list contains items
        if len(st.session_state['recordings']) != 0:

            download_select = st.selectbox("Recordings:", st.session_state['recordings'], format_func=format_file_names ,index=len(st.session_state['recordings'])-1)

            #Download option for MP3s
            if download_select.endswith(".mp3"):
                with open(download_select, 'rb') as f:
                    file_name = download_select.split("/")[2]
                    dwnbtn = st.download_button("Download", data=f, file_name=file_name, mime="audio/mpeg")
            
            elif download_select.endswith(".zip"):
                with open(download_select, 'rb') as f:
                    file_name = download_select.split("/")[2]
                    dwnbtn = st.download_button("Download", data=f, file_name=file_name, mime="applicatioin/zip")

            #Download option for videos
            else:                        
                with open(download_select, 'rb') as f:
                    file_name = download_select.split("/")[2]
                    dwnbtn = st.download_button("Download", data=f, file_name=file_name, mime="video/mp4")

    if display_type == "Multiview":

        #Filters list of outlets based on selected languages
        #If no language is selected, defaults to all languages

        languages = st.multiselect("Select languages:", broadcasters_df['Language'].unique(), placeholder="All languages")

        broadcasters_filtered_by_lang = []

        if len(languages) == 0:
            for row in broadcasters_df.itertuples():
                if row.Type == "Video":
                    broadcasters_filtered_by_lang.append(row.Name)
        else:
            for row in broadcasters_df.itertuples():
                if row.Language in languages and row.Type == "Video":
                    broadcasters_filtered_by_lang.append(row.Name)

        selections = st.multiselect("Select outlets:", broadcasters_filtered_by_lang, max_selections=4)
        selections_len = len(selections)

        record_time = st.slider("Record length (minutes):", min_value=.5, max_value=5.0, step=.5)
        record_time = record_time * 60

        translate = st.checkbox("Translate/transcribe")

        #Recording and processing
        record_multiple = st.button("Record Multiple", type="primary")

        if record_multiple:

            with st.spinner("Recording in progress. Do not change any settings."):

                if selections_len == 2:

                    #First selection
                    first_selection = selections[0]
                    first_outlet = Outlet(first_selection, broadcasters_df)

                    #Second selection
                    second_selection = selections[1]
                    second_outlet = Outlet(second_selection, broadcasters_df)

                    status, video_dict, savetime = multi_record(first_outlet, second_outlet, seconds=record_time, translate=translate)

                    if status == True:
                        zipped_files = zip_multiple_recordings(video_dict, savetime)
                    else:
                        st.error("Unspecified error.")
                    
                    if 'zipped_files' in locals():
                        st.session_state['recordings'].append(zipped_files)

                if selections_len == 3:

                    #First selection
                    first_selection = selections[0]
                    first_outlet = Outlet(first_selection, broadcasters_df)

                    #Second selection
                    second_selection = selections[1]
                    second_outlet = Outlet(second_selection, broadcasters_df)

                    #Third selection
                    third_selection = selections[2]
                    third_outlet = Outlet(third_selection, broadcasters_df)

                    status, video_dict, savetime = multi_record(first_outlet, second_outlet, third_outlet, seconds=record_time, translate=translate)

                    if status == True:
                        zipped_files = zip_multiple_recordings(video_dict, savetime)
                    else:
                        st.error("Unspecified error.")
                    
                    if 'zipped_files' in locals():
                        st.session_state['recordings'].append(zipped_files)                

                if selections_len == 4:

                    #First selection
                    first_selection = selections[0]
                    first_outlet = Outlet(first_selection, broadcasters_df)

                    #Second selection
                    second_selection = selections[1]
                    second_outlet = Outlet(second_selection, broadcasters_df)

                    #Third selection
                    third_selection = selections[2]
                    third_outlet = Outlet(third_selection, broadcasters_df)

                    #Fourth selection
                    fourth_selection = selections[3]
                    fourth_outlet = Outlet(fourth_selection, broadcasters_df)

                    status, video_dict, savetime = multi_record(first_outlet, second_outlet, third_outlet, fourth_outlet, seconds=record_time, translate=translate)

                    if status == True:
                        zipped_files = zip_multiple_recordings(video_dict, savetime)
                    else:
                        st.error("Unspecified error.")
                    
                    if 'zipped_files' in locals():
                        st.session_state['recordings'].append(zipped_files)  

        #Displays selection box if the 'recordings' list contains items
        if len(st.session_state['recordings']) != 0:

            download_select = st.selectbox("Recordings:", st.session_state['recordings'], format_func=format_file_names ,index=len(st.session_state['recordings'])-1)

            #Download option for MP3s
            if download_select.endswith(".mp3"):
                with open(download_select, 'rb') as f:
                    file_name = download_select.split("/")[2]
                    dwnbtn = st.download_button("Download", data=f, file_name=file_name, mime="audio/mpeg")
            
            elif download_select.endswith(".zip"):
                with open(download_select, 'rb') as f:
                    file_name = download_select.split("/")[2]
                    dwnbtn = st.download_button("Download", data=f, file_name=file_name, mime="applicatioin/zip")

            #Download option for videos
            else:                        
                with open(download_select, 'rb') as f:
                    file_name = download_select.split("/")[2]
                    dwnbtn = st.download_button("Download", data=f, file_name=file_name, mime="video/mp4")

#Media display
if display_type == "Single":

    #Metrics/info display
    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.metric("Name", outlet.name)
    with middle_column:
        st.metric("Country", outlet.country)
    with right_column:
        st.metric("Language", outlet.language)

    result = generate_player(outlet.format, outlet.type, outlet.playback_url)

    if result[1] is not None:
        player_html, player_size = result
        components.html(player_html, height=player_size)
    else:
        #For YouTube streams
        player_html = result[0]

    st.subheader("Summary")
    st.write(wiki_summary(outlet.wiki))
    st.write(outlet.page_url)
    st.caption("Information from Wikipedia")
elif display_type == "Multiview":
    #No media
    if selections_len == 0:
        st.warning("No outlets selected")

    #Single media
    if selections_len == 1:
        #First (and only) selection
        first_selection = selections[0]
        first_outlet = Outlet(first_selection, broadcasters_df)

        #First (and only) media player
        result = generate_player(first_outlet.format, first_outlet.type, first_outlet.playback_url)
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
        first_outlet = Outlet(first_selection, broadcasters_df)

        #Second selection
        second_selection = selections[1]
        second_outlet = Outlet(second_selection, broadcasters_df)

        #First media player
        with column_left:
            first_result = generate_player(first_outlet.format, first_outlet.type, first_outlet.playback_url)
            if first_result[1] is not None:
                player_html, player_size = first_result
                components.html(player_html, height=400)
            else:
                player_html = first_result[0]

        #Second media player
        with column_right:
            second_result = generate_player(second_outlet.format, second_outlet.type, second_outlet.playback_url, muted="muted")
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
        first_outlet = Outlet(first_selection, broadcasters_df)

        #Second selection
        second_selection = selections[1]
        second_outlet = Outlet(second_selection, broadcasters_df)

        #Third selection
        third_selection = selections[2]
        third_outlet = Outlet(third_selection, broadcasters_df)

        with column_left:
            #First media player
            first_result = generate_player(first_outlet.format, first_outlet.type, first_outlet.playback_url)
            if first_result[1] is not None:
                player_html, player_size = first_result
                components.html(player_html, height=365)
            else:
                player_html = first_result[0]

        with column_right:
            #Second media player
            second_result = generate_player(second_outlet.format, second_outlet.type, second_outlet.playback_url, muted="muted")
            if second_result[1] is not None:
                player_html, player_size = second_result
                components.html(player_html, height=365)
            else:
                player_html = second_result[0]

        with column_middle:
            #Third media player
            third_result = generate_player(third_outlet.format, third_outlet.type, third_outlet.playback_url, muted="muted")
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
        first_outlet = Outlet(first_selection, broadcasters_df)

        #Second selection
        second_selection = selections[1]
        second_outlet = Outlet(second_selection, broadcasters_df)

        #Third selection
        third_selection = selections[2]
        third_outlet = Outlet(third_selection, broadcasters_df)

        #Fourth selection
        fourth_selection = selections[3]
        fourth_outlet = Outlet(fourth_selection, broadcasters_df)

        with column_left:
            #First media player
            first_result = generate_player(first_outlet.format, first_outlet.type, first_outlet.playback_url)
            if first_result[1] is not None:
                player_html, player_size = first_result
                components.html(player_html, height=365)
            else:
                player_html = first_result[0]

            #Third media player
            third_result = generate_player(third_outlet.format, third_outlet.type, third_outlet.playback_url, muted="muted")
            if third_result[1] is not None:
                player_html, player_size = third_result
                components.html(player_html, height=365)
            else:
                player_html = third_result[0]

        with column_right:
            #Second media player
            second_result = generate_player(second_outlet.format, second_outlet.type, second_outlet.playback_url, muted="muted")
            if second_result[1] is not None:
                player_html, player_size = second_result
                components.html(player_html, height=365)
            else:
                player_html = second_result[0]

            #Fourth media player
            fourth_result = generate_player(fourth_outlet.format, fourth_outlet.type, fourth_outlet.playback_url, muted="muted")
            if fourth_result[1] is not None:
                player_html, player_size = fourth_result
                components.html(player_html, height=365)
            else:
                player_html = fourth_result[0]
elif display_type == "Live Translation":
    st.warning("Under construction.")

    #m3u8_live_url = "https://35.222.235.96/playlist.m3u8"
    m3u8_live_url = "https://globalbroadcasthub.net/playlist.m3u8"
    dash_url = "https://globalbroadcasthub.net/dash_1/stream.mpd"

    st.video("https://globalbroadcasthub.net/playlist.m3u8")

    hls_player_html = f"""
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
        <video id="video" controls autoplay style="width:100vw; height:100vh; object-fit: contain; margin:auto"></video>
        <script>
            var video = document.getElementById('video');
            if (Hls.isSupported()) {{
                var hls = new Hls();
                hls.loadSource('{m3u8_live_url}');
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function() {{
                    video.play();
                }});

                hls.on(Hls.Events.MANIFEST_LOADED, function () {{
                    var subtitleTracks = hls.subtitleTracks;
                    if (subtitleTracks.length > 0) {{
                        hls.subtitleTrack = 0; // Select the first subtitle track
                    }}

            }}
            // For browsers like Safari that support HLS natively
            else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = '{m3u8_live_url}';
                video.addEventListener('loadedmetadata', function() {{
                    video.play();
                }});
            }}
        </script>
        </body>
        </html>
        """
    
    #components.html(hls_player_html, height=525)

    dash_player_html = ash_video_player_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DASH Stream</title>
            <script src="https://cdn.dashjs.org/latest/dash.all.min.js"></script>
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
        <video id="video" controls autoplay style="width:100vw; height:100vh; object-fit: contain; margin:auto"></video>
        <script>
            var video = document.getElementById('video');
            var player = dashjs.MediaPlayer().create();
            player.initialize(video, '{dash_url}', true);
        </script>
        </body>
        </html>
        """
    
    #components.html(dash_player_html, height=525)