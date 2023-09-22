import pytest
import numpy as np
from owl.detection import GreenOnBrown, GreenOnGreen

class TestGreenOnBrown:
    resolutions = [(123, 456), (789, 101), (112, 134), (563, 289)]
    algorithms = ['exgr', 'exg', 'exg_standardised_hue', 'hsv']

    @pytest.mark.parametrize("resolution", resolutions)
    def test_non_standard_resolutions(self, resolution):
        weed_detector = GreenOnBrown()
        width, height = resolution

        # Create a dummy image with the specified resolution
        test_image = np.zeros((height, width, 3), dtype=np.uint8)

        try:
            # Process the image with GreenOnBrown module and check for any errors
            weed_detector.find(test_image)
        except Exception as e:
            pytest.fail(f"Processing failed for resolution {resolution} with error {str(e)}")

    @pytest.mark.parametrize("algorithm", algorithms)
    def test_algorithms(self, algorithm):
        test_image = np.zeros((320, 416, 3), dtype=np.uint8)  # Create a black image with default resolution
        weed_detector = GreenOnBrown()

        try:
            # Process the image with GreenOnBrown module and check for any errors
            weed_detector.find(image=test_image, algorithm=algorithm)
        except Exception as e:
            pytest.fail(f"Processing failed for algorithm {algorithm} with error {str(e)}")

    def test_invalid_algorithm(self):
        test_image = np.zeros((320, 416, 3), dtype=np.uint8)
        weed_detector = GreenOnBrown()

        with pytest.warns(UserWarning, match=r".*Defaulting to ExG"):
            weed_detector.find(image=test_image, algorithm='invalid', show_display=False)


class TestGreenonGreen:
    resolutions = [(123, 456), (789, 101), (112, 134), (563, 289)]

    @pytest.mark.parametrize("resolution", resolutions)
    def test_non_standard_resolutions(self, resolution):
        weed_detector = GreenOnGreen()
        width, height = resolution

        # Create a dummy image with the specified resolution
        test_image = np.zeros((height, width, 3), dtype=np.uint8)

        try:
            # Process the image with GreenOnBrown module and check for any errors
            weed_detector.find(test_image)
        except Exception as e:
            pytest.fail(f"Processing failed for resolution {resolution} with error {str(e)}")

    def test_invalid_model_path(self):
        test_image = np.zeros((320, 416, 3), dtype=np.uint8)

        with pytest.raises(ValueError):
            weed_detector = GreenOnGreen(model_path='invalid_path')
            weed_detector.find(image=test_image, algorithm='gog')

    def test_invalid_platform(self):
        test_image = np.zeros((320, 416, 3), dtype=np.uint8)

        with pytest.raises(NotImplementedError):
            weed_detector = GreenOnGreen(platform='invalid_platform')
            weed_detector.find(image=test_image, algorithm='gog')
