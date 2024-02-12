import streamlit as st
import os
import time
import zipfile

path = "/mount/src/global-media/Recordings"
files = os.listdir(path)

st.write(files)

selections = st.multiselect("Select files:", files)

def zip_files(selections):

    files_to_zip = [item for item in selections if item != "None"]

    now = str(time.time())
    zip_folder_name = f"./Recordings/download_{now}.zip"

    with zipfile.ZipFile(zip_folder_name, 'w') as zipf:
        for file in files_to_zip:
            file_name = file
            file_path = f"./Recordings/{file_name}"
            zipf.write(file_path, arcname=file_name)

    return zip_folder_name

if st.button("Zip for download"):
    zip_folder = zip_files(files)
    file_name = os.path.basename(zip_folder)

    dwnbtn = st.download_button("Download", data=zip_folder, file_name=file_name, mime="applicatioin/zip")