import os

downloaded_path = "/home/casey/Videos/CCTV_13/"
downloaded = os.listdir(downloaded_path)
downloaded_ts = [item for item in downloaded if ".ts" in item]
for item in downloaded_ts:
    os.remove(downloaded_path + item)
    print(f"Removed: {item}")