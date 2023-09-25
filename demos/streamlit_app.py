import streamlit as st
from owl.utils.io import get_weed_detector, setup_and_run_detector, load_config
from owl.utils import FrameReader
import cv2
import tempfile

import numpy as np

def get_file_type(file):
    if file.type in ['image/png', 'image/jpg', 'image/JPG', 'image/png', 'image/jpeg']:
        return 'image'
    elif file.type in ['video/mp4', 'video/avi', 'video/mov']:
        return 'video'
    else:
        raise ValueError("Unsupported file type")


def main():
    st.set_page_config(layout="wide", page_title="Interactive owl-tools")
    st.title("Interactive owl-tools")
    st.write("Test out the owl-tools package on your own images and videos. Simply select the algorithm, model and image files below.")
    st.write("This WebApp is part of the OpenWeedLocator (OWL) project developed by Guy Coleman. "
             "To build your own OWL device find the code, guide and 3D model files [here](https://github.com/geezacoleman/OpenWeedLocator).")

    st.sidebar.write("# Select Media Files")

    # Select Algorithm
    algorithm = st.sidebar.selectbox("Select Algorithm", ["ExG + HSV", "Green-On-Green"])

    # If 'gog' is selected, allow user to upload YOLO model
    model_path = 'models/yolov8n.pt'  # Default Model Path
    if algorithm == 'Green-On-Green':
        uploaded_model = st.sidebar.file_uploader("Upload YOLO Model", type=['pt'])
        if uploaded_model is not None:
            print(uploaded_model, 'HERE')
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_model.read())
            model_path = tfile.name
            print(model_path)

    # Upload Video
    uploaded_files = st.sidebar.file_uploader("Upload Files", type=['mp4', 'avi', 'mov', 'jpg', 'JPG', 'png', 'jpeg'], accept_multiple_files=True)

    st_frame = st.empty()
    placeholder = np.ones((600, 600), dtype=np.uint8) * 255
    st_frame.image(placeholder)
    CONFIG_NAME = st.sidebar.selectbox("Select Config", ["CONFIG_DAY_SENSITIVITY_1"])

    if uploaded_files:
        config = load_config(CONFIG_NAME)

        current_file_idx = st.session_state.get("current_file_idx", 0)
        file_type = get_file_type(uploaded_files[current_file_idx])

        if file_type == 'video':
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_files[current_file_idx].read())
            media_path = tfile.name

            weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path)
            frame_reader = FrameReader(path=media_path, resolution=config.get('resolution'))

            play = st.button('Play')
            stop = st.button('Stop')
            is_playing = False

            while True:
                if play:
                    is_playing = True
                if stop or not is_playing:
                    break

                frame = frame_reader.read()
                if frame is None:
                    break

                _, _, _, image = setup_and_run_detector(weed_detector=weed_detector, frame=frame.copy(), config=config)
                st.image(image, caption='Processed Frame', use_column_width=True)

        if st.button("Back"):
            if current_file_idx > 0:
                current_file_idx -= 1
                st.session_state.current_file_idx = current_file_idx
        if st.button("Next"):
            if current_file_idx < len(uploaded_files) - 1:
                current_file_idx += 1
                st.session_state.current_file_idx = current_file_idx

if __name__ == "__main__":
    main()
