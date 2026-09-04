"""
API Client and Service Layer for Sign Language Translator.
Provides a mock data implementation suitable for frontend development,
structured to allow seamless swapping with real HTTP/WebSocket backend endpoints.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import frontend.config as config


class ApiClient:
    """
    Service client for communication between Frontend GUI and Backend/Hardware.
    Currently operates in Mock mode to supply realistic telemetry and translation events.
    """

    def __init__(self, base_url: str = config.API_BASE_URL, use_mock: bool = config.USE_MOCK_DATA):
        self.base_url = base_url
        self.use_mock = use_mock

        # Simulated hardware state
        self._glove_connected = True
        self._device_name = config.DEFAULT_DEVICE_NAME
        self._battery_level = config.DEFAULT_BATTERY_LEVEL
        self._detection_active = False
        self._system_state = "Ready"  # Ready, Detecting, Processing, Error

        # Simulated active translation
        self._current_translation = {
            "sign": "HELLO",
            "translation": "Hello",
            "confidence": 0.94,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

        # Simulated translation history
        self._history: List[Dict[str, Any]] = [
            {"id": 1, "time": "10:42", "sign": "HELLO", "translation": "Hello", "confidence": 0.96},
            {"id": 2, "time": "10:43", "sign": "THANK YOU", "translation": "Thank you", "confidence": 0.92},
            {"id": 3, "time": "10:44", "sign": "YES", "translation": "Yes", "confidence": 0.98},
            {"id": 4, "time": "10:46", "sign": "HELP", "translation": "Help", "confidence": 0.89},
        ]

        # Configurable sensor values (Thumb, Index, Middle, Ring, Little)
        self._sensor_data = {
            "fingers": {
                "Thumb": 82,
                "Index": 64,
                "Middle": 73,
                "Ring": 51,
                "Little": 43,
            },
            "orientation": {
                "X": 0.32,
                "Y": 0.74,
                "Z": 0.18,
            },
        }

    # --- Glove Hardware Status ---
    def get_glove_status(self) -> Dict[str, Any]:
        """Fetch current status of the sensor glove."""
        return {
            "connected": self._glove_connected,
            "device_name": self._device_name if self._glove_connected else "None",
            "battery": self._battery_level if self._glove_connected else 0,
            "port": "COM3 (Simulated)" if self._glove_connected else "Disconnected",
            "status_text": "Connected" if self._glove_connected else "Disconnected",
        }

    def connect_glove(self, device_name: Optional[str] = None) -> bool:
        """Connect to the sensor glove."""
        self._glove_connected = True
        if device_name:
            self._device_name = device_name
        self._battery_level = 87
        return True

    def disconnect_glove(self) -> bool:
        """Disconnect the sensor glove."""
        self._glove_connected = False
        self._detection_active = False
        self._system_state = "Ready"
        return True

    # --- System & Detection State ---
    def get_system_state(self) -> str:
        """Get the current system status (Ready, Detecting, Processing, Error)."""
        if not self._glove_connected:
            return "Disconnected"
        return self._system_state

    def start_detection(self) -> bool:
        """Start sign detection stream."""
        if not self._glove_connected:
            return False
        self._detection_active = True
        self._system_state = "Detecting"
        return True

    def stop_detection(self) -> bool:
        """Stop sign detection stream."""
        self._detection_active = False
        self._system_state = "Ready"
        return True

    def is_detecting(self) -> bool:
        """Return whether detection is currently active."""
        return self._detection_active

    # --- Sensor Monitoring ---
    def get_sensor_data(self) -> Dict[str, Any]:
        """Fetch real-time sensor metrics."""
        return self._sensor_data

    # --- Translation Data & Operations ---
    def get_current_translation(self) -> Dict[str, Any]:
        """Get the latest recognized sign and translation."""
        return self._current_translation

    def clear_current_translation(self) -> None:
        """Clear the active translation display."""
        self._current_translation = {
            "sign": "—",
            "translation": "Waiting for sign...",
            "confidence": 0.0,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
        }

    def save_current_translation(self) -> bool:
        """Save the current translation to history."""
        if self._current_translation["sign"] not in ("—", ""):
            new_entry = {
                "id": len(self._history) + 1,
                "time": datetime.now().strftime("%H:%M"),
                "sign": self._current_translation["sign"],
                "translation": self._current_translation["translation"],
                "confidence": self._current_translation["confidence"],
            }
            self._history.insert(0, new_entry)
            return True
        return False

    def get_history(self) -> List[Dict[str, Any]]:
        """Retrieve translation history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear all historical translation records."""
        self._history.clear()


# Default singleton instance
api_client = ApiClient()
