import streamlit as st
from owl.utils.io import get_weed_detector, setup_and_run_detector, load_config
from owl.utils import FrameReader
import cv2
import tempfile


def main():
    st.title('OpenWeedLocator Tool')

    # Select Algorithm
    algorithm = st.selectbox("Select Algorithm", ["exhsv", "gog"])

    # If 'gog' is selected, allow user to upload YOLO model
    model_path = 'models/yolov8n.pt'  # Default Model Path
    if algorithm == 'gog':
        uploaded_file = st.file_uploader("Upload YOLO Model", type=['pt'])
        if uploaded_file is not None:
            tfile = tempfile.NamedTemporaryFile(delete=False)
            tfile.write(uploaded_file.read())
            model_path = tfile.name

    # Upload Video
    video_file = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov'])

    if video_file is not None:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_file.read())
        video_path = tfile.name

        CONFIG_NAME = st.selectbox("Select Config", ["CONFIG_DAY_SENSITIVITY_1", "CONFIG_DAY_SENSITIVITY_2"])
        config = load_config(CONFIG_NAME)

        weed_detector = get_weed_detector(algorithm=algorithm, model_path=model_path)
        frame_reader = FrameReader(path=video_path, resolution=config.get('resolution'))

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

            if cv2.waitKey(1) == 27:
                break


if __name__ == "__main__":
    main()
