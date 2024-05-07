import subprocess

def quadbox(first, second, third, fourth, output_path):

    command = [
        'ffmpeg',
        '-i', first,
        '-i', second,
        '-i', third,
        '-i', fourth,
        '-filter_complex',
        'nullsrc=size=1920x1080 [base];'
        '[0:v] setpts=PTS-STARTPTS, scale=960x540 [upperleft];'
        '[1:v] setpts=PTS-STARTPTS, scale=960x540 [upperright];'
        '[2:v] setpts=PTS-STARTPTS, scale=960x540 [lowerleft];'
        '[3:v] setpts=PTS-STARTPTS, scale=960x540 [lowerright];'
        '[base][upperleft] overlay=shortest=1 [tmp1];'
        '[tmp1][upperright] overlay=shortest=1:x=960 [tmp2];'
        '[tmp2][lowerleft] overlay=shortest=1:y=540 [tmp3];'
        '[tmp3][lowerright] overlay=shortest=1:x=960:y=540',
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-f', 'hls',
        '-hls_time', '4',
        '-hls_list_size', '6',
        output_path
    ]

    return command

first = 'https://live-hls-web-aje-fa.getaj.net/AJE/index.m3u8'
second = 'https://epg.provider.plex.tv/library/parts/5e20b730f2f8d5003d739db7-646fab0e43d6d6838db81a6a.m3u8?X-Plex-Session-Identifier=y5kimltbbz1wd2bebe0frh42&X-Plex-Product=Plex%20Web&X-Plex-Version=4.126.1&X-Plex-Client-Identifier=ailqbujzrt691c866g32cugy&X-Plex-Platform=Chrome&X-Plex-Platform-Version=123.0&X-Plex-Features=external-media%2Cindirect-media%2Chub-style-list&X-Plex-Model=hosted&X-Plex-Device=OSX&X-Plex-Device-Name=Chrome&X-Plex-Device-Screen-Resolution=1440x792%2C1447x795&X-Plex-Token=V7Jq9k79kyS3ufx7MzmJ&X-Plex-Language=en&Accept-Language=en&X-Plex-Session-Id=a6931f62-66e9-49f0-8421-9af3c2981362'
third = 'https://news.cgtn.com/resource/live/english/cgtn-news.m3u8'
fourth = 'https://tv-trtworld.live.trt.com.tr/master.m3u8'
output = '/home/casey/Videos/playlist.m3u8'

command = quadbox(first, second, third, fourth, output)

subprocess.run(command)