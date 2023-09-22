import pytest
from unittest import mock

from owl.viz import webcam, images_and_video
from owl.utils import FrameReader

import numpy as np
import os

class TestViz:
    @mock.patch('cv2.VideoCapture')
    @mock.patch('cv2.imshow')
    @mock.patch('cv2.waitKey', return_value=27)
    def test_webcam(self, mock_key_press, mock_show, mock_capture):
        mock_capture_instance = mock.Mock()
        mock_capture_instance.isOpened.return_value = True
        mock_frame = np.zeros((320, 416, 3), dtype=np.uint8)
        mock_capture_instance.read.return_value = (True, mock_frame)
        mock_capture.return_value = mock_capture_instance

        try:
            webcam()
        except Exception as e:
            pytest.fail(f"webcam() failed with error {str(e)}")

        # Then
        mock_capture_instance.isOpened.assert_called_once()
        mock_capture_instance.read.assert_called()

        # Asserting that 'imshow' was called with ('Video Feed', any frame) at least once
        for call in mock_show.call_args_list:
            call_name, call_frame = call[0]
            if call_name == 'Video Feed':
                break
        else:
            pytest.fail("cv2.imshow was never called with 'Video Feed'")

    @mock.patch('cv2.imshow')
    @mock.patch('cv2.waitKey', return_value=27)
    @mock.patch.object(FrameReader, 'read')
    def test_images_and_video(self, mock_frame_read, mock_key_press, mock_show):
        mock_frame = np.zeros((320, 416, 3), dtype=np.uint8)
        mock_frame_read.return_value = mock_frame

        try:
            images_and_video(media_path='media/OWL - frame 3.jpg')
        except Exception as e:
            pytest.fail(f"images_and_video() failed with error {str(e)}")

    def test_unsupported_file_type_and_non_existent_file(self):
        non_existing_file_path = 'media/non_existent_unsupported_file.txt'

        with pytest.raises(FileNotFoundError) as excinfo:
            FrameReader(path=non_existing_file_path)
        assert '[ERROR] The provided path does not exist:' in str(excinfo.value)

        unsupported_file_path = 'media/non_existent_unsupported_file.txt'
        with open(unsupported_file_path, 'w') as f:
            f.write('Test content')

        with pytest.raises(ValueError) as excinfo:
            FrameReader(path=unsupported_file_path)
        assert '[ERROR] Unsupported file type:' in str(excinfo.value)

        os.remove(unsupported_file_path)