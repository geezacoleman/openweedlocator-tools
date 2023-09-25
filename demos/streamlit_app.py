import streamlit as st
from owl.utils.io import get_weed_detector, setup_and_run_detector, load_config
from owl.utils import FrameReader
from PIL import Image
from io import BytesIO
import requests
import cv2
import tempfile
import imutils
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
    col_main, col_config = st.columns([5, 2])
    st.sidebar.write("## Select Parameters")
    with col_main:
        st.title("Interactive owl-tools")
        st.write("Test out the owl-tools package on your own images and videos. Simply select the algorithm, model and image files below.")
        st.write("This WebApp is part of the OpenWeedLocator (OWL) project developed by Guy Coleman. "
                 "To build your own OWL device find the code, guide and 3D model files [here](https://github.com/geezacoleman/OpenWeedLocator).")

    # Select Algorithm
    algorithm_key = st.sidebar.selectbox("Select Algorithm", ["ExG", "ExG + HSV", "HSV", "Green-On-Green"])

    algorithm_dict = {
        "ExG + HSV": 'exhsv',
        "ExG": 'exg',
        "HSV": 'hsv',
        "Green-On-Green": 'gog'
    }

    current_file_idx = st.session_state.get("current_file_idx", 0)

    model_path = None
    if algorithm_key == 'Green-On-Green':
        uploaded_model = st.sidebar.file_uploader("Upload YOLO Model", type=['pt'])
        if uploaded_model is not None:
            if 'model_path' in st.session_state:
                model_path = st.session_state.model_path
            else:
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.pt')
                tfile.write(uploaded_model.read())
                model_path = tfile.name
                # store model_path in st.session_state to avoid reloading
                st.session_state['model_path'] = model_path

        elif uploaded_model is None and 'model_path' not in st.session_state:
            st.error('Please upload model.')

    uploaded_files = st.sidebar.file_uploader("Upload Files", type=['mp4', 'avi', 'mov', 'jpg', 'JPG', 'png', 'jpeg'], accept_multiple_files=True)

    st_frame = col_main.empty()

    if "logo" not in st.session_state:
        response = requests.get('https://user-images.githubusercontent.com/51358498/152991504-005a1daa-2900-4f48-8bec-d163d6336ed2.png')
        if response.status_code == 200:
            logo = Image.open(BytesIO(response.content))
            st.session_state['logo'] = logo

        if 'last_frame' not in st.session_state:
            st.session_state['last_frame'] = st.session_state.logo

    st_frame.image(st.session_state.last_frame, width=500)
    CONFIG_NAME = st.sidebar.selectbox("Select Config", ["CONFIG_DAY_SENSITIVITY_1"])
    config = load_config(CONFIG_NAME)

    with col_config:
        st.write("## Configuration Panel")
        with st.form(key='config_form'):
            submitted = st.form_submit_button("Update Config")

            with st.expander("### Green on Green Config"):
                conf = st.slider('Confidence', min_value=0.0, max_value=1.0, value=config.get('conf', 0.6))
                iou = st.slider('IOU', min_value=0.0, max_value=1.0, value=config.get('iou', 0.7))

            with st.expander("### Green on Brown Config"):
                exg_min = st.slider('ExG Min', min_value=0, max_value=255, value=config.get('exgMin', 25))
                exg_max = st.slider('ExG Max', min_value=0, max_value=255, value=config.get('exgMax', 200))
                hue_min = st.slider('Hue Min', min_value=0, max_value=128, value=config.get('hueMin', 39))
                hue_max = st.slider('Hue Max', min_value=0, max_value=128, value=config.get('hueMax', 83))
                saturation_min = st.slider('Saturation Min', min_value=0, max_value=255, value=config.get('saturationMin', 50))
                saturation_max = st.slider('Saturation Max', min_value=0, max_value=255, value=config.get('saturationMax', 220))
                brightness_min = st.slider('Brightness Min', min_value=0, max_value=255, value=config.get('brightnessMin', 60))
                brightness_max = st.slider('Brightness Max', min_value=0, max_value=255, value=config.get('brightnessMax', 190))
                min_area = st.slider('Min Area', min_value=0, max_value=255, value=config.get('minArea', 10))

            if submitted:
                updated_config = {
                    "conf": conf,
                    "iou": iou,
                    "exgMin": exg_min,
                    "exgMax": exg_max,
                    "hueMin": hue_min,
                    "hueMax": hue_max,
                    "saturationMin": saturation_min,
                    "saturationMax": saturation_max,
                    "brightnessMin": brightness_min,
                    "brightnessMax": brightness_max,
                    "minArea": min_area
                }
                config.update(updated_config)

    if uploaded_files and 0 <= current_file_idx < len(uploaded_files):
        current_file_idx = st.session_state.get("current_file_idx", 0)
        file_type = get_file_type(uploaded_files[current_file_idx])

        if 'weed_detector' not in st.session_state or 'model_used' in st.session_state and st.session_state.model_used != model_path:
            try:
                weed_detector = get_weed_detector(algorithm=algorithm_dict[algorithm_key], model_path=model_path)
                st.session_state.weed_detector = weed_detector

                st.session_state.model_used = model_path
            except Exception:
                st.error('Please upload model.')

        else:
            if config.get('algorithm') != algorithm_dict[algorithm_key]:
                try:
                    weed_detector = get_weed_detector(algorithm=algorithm_dict[algorithm_key], model_path=st.session_state.model_path)
                    st.session_state.weed_detector = weed_detector

                except Exception:
                    st.warning('Please upload model.')

            else:
                weed_detector = st.session_state.weed_detector

        config.update({"algorithm": f"{algorithm_dict[algorithm_key]}"})

        if file_type == 'video':
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_files[current_file_idx].read())
            media_path = tfile.name
            frame_reader = FrameReader(path=media_path, resolution=config.get('resolution'))

            col1, col2 = col_main.columns(2)
            play = col1.button('Play')
            stop = col2.button('Stop')

            is_playing = False

            if 'last_frame' in st.session_state:
                st_frame.image(st.session_state.last_frame, caption='Processed Frame', use_column_width=False, width=500)

            while True:
                if play:
                    is_playing = True
                if stop or not is_playing:
                    st_frame.image(st.session_state.last_frame, caption='Processed Frame', use_column_width=False, width=500)
                    break

                frame = frame_reader.read()

                if frame is None:
                    break

                _, _, _, image = setup_and_run_detector(weed_detector=weed_detector, frame=frame.copy(), config=config)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                st_frame.image(rgb, caption='Processed Frame', use_column_width=False, width=500)
                st.session_state.last_frame = rgb

        elif file_type == 'image':
            uploaded_file = uploaded_files[current_file_idx]
            uploaded_file.seek(0)
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)

            _, _, _, image = setup_and_run_detector(weed_detector=weed_detector, frame=image.copy(), config=config)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            st_frame.image(rgb)

        else:
            print('File type not supported.')

        col1, col2 = st.sidebar.columns(2)
        try:
            if col1.button("Previous File"):
                current_file_idx = max(current_file_idx - 1, 0)
                st.session_state.current_file_idx = current_file_idx

            if col2.button("Next File"):
                current_file_idx = min(current_file_idx + 1, len(uploaded_files) - 1)
                st.session_state.current_file_idx = current_file_idx
        except IndexError:
            st.warning('There is an issue with the file index. Please re-upload the files.')

if __name__ == "__main__":
    main()
