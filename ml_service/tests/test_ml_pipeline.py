import os
import sys
import unittest
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning)

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.load_data import load_processed_dataset
from src.model_utils import load_model, load_scaler
from src.predict import predict_gesture, predict_gesture_with_confidence

class TestMLServicePipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.model = load_model()
        cls.scaler = load_scaler()
        cls.expected_features = cls.scaler.n_features_in_
        cls.valid_sample = [0.5] * cls.expected_features

    def test_01_data_loading(self):
        X, y = load_processed_dataset()
        self.assertGreater(len(X), 0, "Dataset features matrix is empty.")
        self.assertEqual(len(X), len(y), "Features and labels row count mismatch.")

    def test_02_model_artifacts_loaded(self):
        self.assertIsNotNone(self.model, "SVM Model failed to load.")
        self.assertIsNotNone(self.scaler, "StandardScaler failed to load.")
        self.assertTrue(hasattr(self.model, "predict"))

    def test_03_prediction_valid_input_list(self):
        pred = predict_gesture(self.valid_sample)
        self.assertIsInstance(pred, str)
        self.assertIn(pred, self.model.classes_)

    def test_04_prediction_valid_input_numpy(self):
        np_sample = np.array(self.valid_sample)
        pred = predict_gesture(np_sample)
        self.assertIsInstance(pred, str)
        self.assertIn(pred, self.model.classes_)

    def test_05_prediction_with_confidence(self):
        pred, conf = predict_gesture_with_confidence(self.valid_sample)
        self.assertIsInstance(pred, str)
        self.assertIsInstance(conf, float)
        self.assertTrue(0.0 <= conf <= 1.0)

    def test_06_wrong_feature_count_raises_error(self):
        invalid_sample = [0.1, 0.2]
        with self.assertRaises(ValueError):
            predict_gesture(invalid_sample)

    def test_07_nan_input_raises_error(self):
        nan_sample = [np.nan] * self.expected_features
        with self.assertRaises(ValueError):
            predict_gesture(nan_sample)

    def test_08_invalid_type_raises_error(self):
        with self.assertRaises(TypeError):
            predict_gesture("invalid_string_input")

if __name__ == "__main__":
    unittest.main()
