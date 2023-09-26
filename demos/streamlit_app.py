import time

import streamlit as st
from owl.utils.io import get_weed_detector, setup_and_run_detector, load_config
from owl.utils import FrameReader
from PIL import Image
from io import BytesIO
import requests
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

def update_value():
    config = st.session_state.config
    config_list = ["conf", "iou", "exgMin", "exgMax", "hueMin", "hueMax", "saturationMin",
                   "saturationMax", "brightnessMin", "brightnessMax", "minArea"]
    for slider in config_list:
        config.update({slider: st.session_state[slider]})


def main():
    st.set_page_config(layout="wide", page_title="Interactive owl-tools")
    col_main, col_config = st.columns([5, 2])
    st.sidebar.write("## Select Parameters")
    with col_main:
        st.title("Interactive owl-tools")
        st.write("Test out the owl-tools package on your own images and videos. Simply select the algorithm, model (if using"
                 "Green-on-Green and image files below. Use the Configuration Panel to set algorithm parameters. Click"
                 "'Update Config' to test out the new config.")
        st.write("This WebApp is part of the OpenWeedLocator (OWL) project. "
                 "To build your own OWL device find the code, guide and 3D model files [here](https://github.com/geezacoleman/OpenWeedLocator).")


    # select algo
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

    with st.sidebar.form("File Upload", clear_on_submit=True):
        uploaded_files = st.file_uploader("Select Files", accept_multiple_files=True, type=['mp4', 'avi', 'mov', 'jpg', 'JPG', 'png', 'jpeg'])
        submitted = st.form_submit_button("Upload")

    st_frame = col_main.empty()
    message_box = col_config.empty()

    if "logo" not in st.session_state:
        response = requests.get(
            'https://user-images.githubusercontent.com/51358498/152991504-005a1daa-2900-4f48-8bec-d163d6336ed2.png')
        if response.status_code == 200:
            logo = Image.open(BytesIO(response.content))
            st.session_state['logo'] = logo

        if 'last_frame' not in st.session_state:
            st.session_state['last_frame'] = st.session_state.logo

    if len(uploaded_files) == 0:
        st.warning("Please upload media files.")
        response = requests.get(
            'https://user-images.githubusercontent.com/51358498/152991504-005a1daa-2900-4f48-8bec-d163d6336ed2.png')
        if response.status_code == 200:
            logo = Image.open(BytesIO(response.content))
            st.session_state['logo'] = st.session_state['last_frame'] = logo

    st_frame.image(st.session_state.last_frame, width=800)
    with col_config:
        st.write("## Configuration Panel")
        CONFIG_NAME = st.selectbox("Select Config", ["CONFIG_DAY_SENSITIVITY_1"])
        if 'config' not in st.session_state or CONFIG_NAME != st.session_state.config_name:
            config = load_config(CONFIG_NAME)
            st.session_state['config'] = config
            st.session_state['config_name'] = CONFIG_NAME

        else:
            config = st.session_state.config
        with st.expander("### Green on Green Config"):
            st.slider('Confidence', min_value=0.0, max_value=1.0, value=config.get('conf', 0.6), key='conf',
                      on_change=update_value)
            st.slider('IOU', min_value=0.0, max_value=1.0, value=config.get('iou', 0.7), key='iou',
                      on_change=update_value)

        with st.expander("### Green on Brown Config"):
            st.slider('ExG Min', min_value=0, max_value=255, value=config.get('exgMin', 25), key='exgMin',
                      on_change=update_value)
            st.slider('ExG Max', min_value=0, max_value=255, value=config.get('exgMax', 200), key='exgMax',
                      on_change=update_value)
            st.slider('Hue Min', min_value=0, max_value=128, value=config.get('hueMin', 39), key='hueMin',
                      on_change=update_value)
            st.slider('Hue Max', min_value=0, max_value=128, value=config.get('hueMax', 83), key='hueMax',
                      on_change=update_value)
            st.slider('Saturation Min', min_value=0, max_value=255, value=config.get('saturationMin', 50), key='saturationMin',
                      on_change=update_value)
            st.slider('Saturation Max', min_value=0, max_value=255, value=config.get('saturationMax', 220), key='saturationMax',
                      on_change=update_value)
            st.slider('Brightness Min', min_value=0, max_value=255, value=config.get('brightnessMin', 60), key='brightnessMin',
                      on_change=update_value)
            st.slider('Brightness Max', min_value=0, max_value=255, value=config.get('brightnessMax', 190), key='brightnessMax',
                      on_change=update_value)
            st.slider('Min Area', min_value=0, max_value=255, value=config.get('minArea', 10), key='minArea',
                      on_change=update_value)

    if current_file_idx >= len(uploaded_files) and current_file_idx != 0:
        st.session_state.current_file_idx = (len(uploaded_files) - 1)
    elif current_file_idx < 0:
        st.session_state.current_file_idx = 0
    else:
        st.session_state.current_file_idx = current_file_idx

    if uploaded_files and 0 <= current_file_idx:
        current_file_idx = st.session_state.get("current_file_idx", 0)
        file_type = get_file_type(uploaded_files[current_file_idx])

        if 'weed_detector' not in st.session_state or 'model_used' in st.session_state and st.session_state.model_used != model_path:
            try:
                message_box.info('Loading algorithm...')
                weed_detector = get_weed_detector(algorithm=algorithm_dict[algorithm_key], model_path=model_path)
                st.session_state.weed_detector = weed_detector
                message_box.success('Algorithm ready.')

                st.session_state.model_used = model_path
            except Exception:
                st.error('Please upload model or change algorithm')

        else:
            if config.get('algorithm') != algorithm_dict[algorithm_key]:
                try:
                    message_box.info('Loading algorithm...')
                    weed_detector = get_weed_detector(algorithm=algorithm_dict[algorithm_key], model_path=st.session_state.model_path)
                    st.session_state.weed_detector = weed_detector
                    message_box.success('Algorithm ready.')

                except Exception:
                    st.warning('Please upload model or change algorithm')

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
                st_frame.image(st.session_state.last_frame, caption='Processed Frame', use_column_width=False, width=800)

            while True:
                if play:
                    is_playing = True
                if stop or not is_playing:
                    st_frame.image(st.session_state.last_frame, caption='Processed Frame', use_column_width=False, width=800)
                    break

                frame = frame_reader.read()

                if frame is None:
                    break
                try:
                    _, _, _, image = setup_and_run_detector(weed_detector=weed_detector, frame=frame.copy(), config=config)
                    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    st_frame.image(rgb, caption='Processed Frame', use_column_width=False, width=800)
                    st.session_state.last_frame = rgb
                    time.sleep(0.03)
                except Exception:
                    st.error('Please upload model or change algorithm.')

        elif file_type == 'image':
            uploaded_file = uploaded_files[current_file_idx]
            uploaded_file.seek(0)
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, 1)
            try:
                _, _, _, image = setup_and_run_detector(weed_detector=weed_detector, frame=image.copy(), config=config)
                rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                st_frame.image(rgb, width=800)
                st.session_state['last_frame'] = rgb
            except Exception:
                st.error('Please upload model or change algorithm.')

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
    col_main.write('## Try it yourself!')
    col_main.code('''from owl.viz import webcam, images_and_video
    # run using your webcam
    webcam(algorithm='gog', model_path='models/yolov8n.pt) # add your own model path as required
    
    # run on images, videos or directories
    images_and_video(media_path='path/to/your/media_files''')

if __name__ == "__main__":
    main()
