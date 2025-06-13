import os
import logging
import threading
import queue
import time
from typing import Dict, Any, Optional, Callable

# Import conditionally to avoid hard dependency
try:
    import pyaudio
    import numpy as np
    
    # Try to import vosk for wake word detection
    try:
        from vosk import Model, KaldiRecognizer
        VOSK_AVAILABLE = True
    except ImportError:
        VOSK_AVAILABLE = False
    
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    VOSK_AVAILABLE = False

logger = logging.getLogger(__name__)

class WakeWordDetector:
    """Detects wake words or phrases to activate the voice assistant."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the wake word detector with configuration.
        
        Args:
            config: Dictionary containing wake word configuration
        """
        self.listening = False
        self.config = config
        self.engine = config.get('engine', 'vosk').lower()
        self.model_path = config.get('model_path', 'model\vosk-model-small-en-us-0.15')
        self.trigger_phrase = config.get('trigger_phrase', 'hey assistant').lower()
        self.sensitivity = config.get('sensitivity', 0.7)  # Higher = more sensitive
        self.sample_rate = 16000
        
        # Verify dependencies
        if not AUDIO_AVAILABLE:
            logger.error("PyAudio or NumPy not available. Wake word detection will be disabled.")
            raise ImportError("Required audio processing libraries not installed")
        
        # Initialize the detection engine
        self._initialize_engine()
        
        # Audio recording variables
        self.audio_queue = queue.Queue()
        self.listen_thread = None
        self.stream = None
        self.audio = None
    
    def _initialize_engine(self) -> None:
        """Initialize the appropriate wake word detection engine."""
        if self.engine == 'vosk':
            if not VOSK_AVAILABLE:
                raise ImportError("Vosk is not installed. Please install it using 'pip install vosk'")
            
            # Check if model exists
            if not os.path.isdir(self.model_path):
                logger.error(f"Vosk model not found at {self.model_path}")
                raise FileNotFoundError(f"Vosk model not found at {self.model_path}")
            
            try:
                self.model = Model(self.model_path)
                self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
                logger.info(f"Initialized Vosk model for wake word detection from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to initialize Vosk model for wake word detection: {e}")
                raise
        else:
            logger.error(f"Unsupported wake word engine: {self.engine}")
            raise ValueError(f"Unsupported wake word engine: {self.engine}")
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
    
    def start_detection(self, callback: Callable[[], None]) -> None:
        """
        Start listening for wake word.
        
        Args:
            callback: Function to call when wake word is detected
        """
        if self.listening:
            logger.warning("Already listening for wake word")
            return
        
        # Start listening in a separate thread
        self.listening = True
        self.listen_thread = threading.Thread(
            target=self._detect_wake_word,
            args=(callback,),
            daemon=True
        )
        self.listen_thread.start()
        logger.debug("Started listening for wake word")
    
    def stop_detection(self) -> None:
        """Stop listening for wake word."""
        if not self.listening:
            return
        
        self.listening = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        
        # Clear the audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.debug("Stopped listening for wake word")
    
    def _detect_wake_word(self, callback: Callable[[], None]) -> None:
        """
        Listen for and detect wake word.
        
        Args:
            callback: Function to call when wake word is detected
        """
        # Open audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=2048,
            stream_callback=self._audio_callback
        )
        
        self.stream.start_stream()
        
        # Wake word detection loop
        while self.listening:
            try:
                audio_chunk = self.audio_queue.get(timeout=0.5)
                
                if self.engine == 'vosk':
                    # Process audio with Vosk
                    if self.recognizer.AcceptWaveform(audio_chunk):
                        result_json = self.recognizer.Result()
                        detected_text = self._parse_vosk_result(result_json)
                        
                        # Check if wake word is in detected text
                        if detected_text and self.trigger_phrase in detected_text.lower():
                            logger.info(f"Wake word detected: {detected_text}")
                            callback()
                            
                            # Reset recognizer after detection
                            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in wake word detection: {e}")
                break
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """PyAudio callback function for streaming audio data."""
        if self.listening:
            self.audio_queue.put(in_data)
        return (in_data, pyaudio.paContinue)
    
    def _parse_vosk_result(self, result_json: str) -> Optional[str]:
        """
        Parse Vosk recognition result.
        
        Args:
            result_json: JSON result string from Vosk
            
        Returns:
            Optional[str]: Recognized text or None
        """
        import json
        result = json.loads(result_json)
        
        if 'text' in result and result['text'].strip():
            return result['text'].strip()
        
        return None
    
    def __del__(self):
        """Clean up resources when the object is garbage collected."""
        self.stop_detection()
        if self.audio:
            self.audio.terminate()