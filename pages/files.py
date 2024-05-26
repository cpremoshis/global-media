import streamlit as st
import os
import time
import zipfile

path = "/mount/src/global-media/Recordings"
files = os.listdir(path)

#st.write(files)

selections = st.multiselect("Select files:", files)

def zip_files(selections):

    files_to_zip = [f"/mount/src/global-media/Recordings/{item}" for item in selections if item != "None"]
    print(f"Files to zip: {files_to_zip}")

    now = str(time.time()).split(".")[0]    
    zip_folder_name = f"/mount/src/global-media/Recordings/download_{now}.zip"
    print(f"Zip folder: {zip_folder_name}")

    with zipfile.ZipFile(zip_folder_name, 'w') as zipf:
        for file in files_to_zip:
            file_name = file.split("/")[-1]
            zipf.write(file, arcname=file_name)

    return zip_folder_name

if st.button("Zip for download"):
    zip_folder = zip_files(selections)
    st.write(f"Zip folder: {zip_folder}")

    file_name = os.path.basename(zip_folder)
    st.write(f"Zip file name: {file_name}")

    with open(zip_folder, 'rb') as f:
        zip_bytes = f.read()

    dwnbtn = st.download_button("Download", data=zip_bytes, file_name=file_name, mime="application/zip")

if st.button("Delete files"):
    confirmation = st.button("Confirm deletion", type='primary')

    if confirmation:
        for file in selections:
            os.remove(file)

        st.text("Deleted:")
        st.write(selections)