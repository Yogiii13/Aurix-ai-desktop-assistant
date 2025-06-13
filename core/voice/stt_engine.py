import json
from vosk import Model, KaldiRecognizer
import pyaudio
import logging
import os

logger = logging.getLogger(__name__)

class STTEngine:
    def __init__(self, config):
        self.config = config
        self.engine_type = config['engine']
        self.language = config['language']
        self.sample_rate = config['sample_rate']
        self.timeout = config['timeout']
        self.model_path = config['model_path']
        self.model = None
        self.recognizer = None
        self.audio = None
        
        # Add caching for better performance
        self.result_cache = {}
        self.max_cache_size = 100
        
        # Add option for smaller model for faster processing
        self.use_fast_model = config.get('use_fast_model', False)
        if self.use_fast_model and 'fast_model_path' in config:
            self.model_path = config['fast_model_path']
    
        try:
            self._initialize_engine()
        except Exception as e:
            logger.error(f"Failed to initialize STT engine: {e}")

    def _initialize_engine(self):
        if self.engine_type == 'vosk':
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model path not found: {self.model_path}")
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            self.audio = pyaudio.PyAudio()
            logger.info("Initialized Vosk Speech Recognition")
        elif self.engine_type == 'google':
            # Initialize Google Speech Recognition
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.audio = pyaudio.PyAudio()
            logger.info("Initialized Google Speech Recognition")
        else:
            raise ValueError(f"Unsupported STT engine: {self.engine_type}")

    def recognize(self, audio_data):
        if self.recognizer is None:
            logger.error("Recognizer not initialized")
            return ""
        
        try:
            if self.engine_type == 'vosk':
                if self.recognizer.AcceptWaveform(audio_data):
                    result = json.loads(self.recognizer.Result())
                    return result['text']
                else:
                    return ""
            elif self.engine_type == 'google':
                # Google Speech Recognition implementation
                import speech_recognition as sr
                audio = sr.AudioData(audio_data, self.sample_rate, 2)
                return self.recognizer.recognize_google(audio, language=self.language)
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return ""

    def listen(self):
        if self.audio is None:
            logger.error("Audio not initialized")
            return ""
        stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=self.sample_rate, input=True, frames_per_buffer=8000)
        stream.start_stream()

        logger.info("Listening...")
        for _ in range(0, int(self.sample_rate / 1024 * self.timeout)):
            data = stream.read(1024)
            if len(data) == 0:
                break
            if self.recognizer.AcceptWaveform(data):
                result = json.loads(self.recognizer.Result())
                stream.stop_stream()
                stream.close()
                return result['text']

        stream.stop_stream()
        stream.close()
        result = json.loads(self.recognizer.FinalResult())
        return result['text']

    def __del__(self):
        if hasattr(self, 'audio') and self.audio:
            self.audio.terminate()