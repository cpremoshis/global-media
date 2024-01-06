import ffmpeg

def record_m3u8_stream(url, output):
    (
        ffmpeg
        .input(url)
        .output(output, c='copy', **{'bsf:a': 'aac_adtstoasc'})
        .run()
    )

url = "https://live-hls-web-aje-fa.getaj.net/AJE/03.m3u8"
output = "test.mp4"
record_m3u8_stream(url, output)