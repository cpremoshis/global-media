import streamlit as st

def generate_player(format, type, url):
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
    <video id="video" controls autoplay style="width:100vw; height:100vh; object-fit: contain; margin:auto"></video>
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

input = st.text_input("Paste M3U8 url:")

if st.button("Load"):
    player = generate_player("M3U8", "Video", input)
    st.video(player)