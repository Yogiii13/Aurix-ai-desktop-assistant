import os
import logging
import threading
from typing import Dict, Any, Optional
import pyttsx3

logger = logging.getLogger(__name__)

class TTSEngine:
    """Text-to-Speech Engine for converting text to speech."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine_type = config.get('engine', 'pyttsx3').lower()
        self.voice = config.get('voice', 'default')
        self.rate = config.get('rate', 175)
        self.volume = config.get('volume', 1.0)

        # Security fix: Get API key from environment only
        self.api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_id = os.getenv('ELEVENLABS_VOICE_ID', config.get('voice_id', ''))

        self.engine = None
        self.speaking = False
        self.speech_thread = None
        self.elevenlabs_client = None

        self._initialize_engine()

    def _initialize_engine(self) -> None:
        """Initialize the appropriate TTS engine."""
        if self.engine_type == 'pyttsx3':
            self._initialize_pyttsx3()
        elif self.engine_type == 'elevenlabs':
            self._initialize_elevenlabs()
        else:
            logger.warning(f"Unsupported TTS engine: {self.engine_type}, falling back to pyttsx3")
            self.engine_type = 'pyttsx3'
            self._initialize_pyttsx3()

    def _initialize_pyttsx3(self) -> None:
        """Initialize pyttsx3 TTS engine."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            self.engine.setProperty('volume', self.volume)

            if self.voice != 'default':
                voices = self.engine.getProperty('voices')
                for v in voices:
                    if v and self.voice.lower() in v.name.lower():
                        self.engine.setProperty('voice', v.id)
                        break

            logger.info("Initialized pyttsx3 TTS engine")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self.engine = None

    def _initialize_elevenlabs(self) -> None:
        """Initialize ElevenLabs TTS engine."""
        try:
            if not self.api_key:
                raise ValueError("ElevenLabs API key not found in environment variables")
    
            # Import ElevenLabs client - using the latest API structure
            try:
                import elevenlabs
                
                # Set API key - different ways to set it based on version
                # First try direct attribute assignment
                elevenlabs.api_key = self.api_key
                
                self.elevenlabs_client = elevenlabs
                logger.info("Using ElevenLabs API")
            except ImportError:
                logger.error("ElevenLabs library not installed. Please install it with: pip install elevenlabs")
                raise
            except Exception as e:
                logger.error(f"Error initializing ElevenLabs: {e}")
                raise
    
            # Validate voice ID
            if not self.voice_id:
                try:
                    available_voices = elevenlabs.voices()
                    if available_voices:
                        # Handle different return types
                        if hasattr(available_voices[0], 'voice_id'):
                            self.voice_id = available_voices[0].voice_id
                            voice_name = getattr(available_voices[0], 'name', 'Unknown')
                        else:
                            # Might be a dict or other structure
                            self.voice_id = available_voices[0].get('voice_id', available_voices[0].get('id', ''))
                            voice_name = available_voices[0].get('name', 'Unknown')
                        
                        logger.info(f"Using default voice: {voice_name}")
                    else:
                        raise ValueError("No voices available from ElevenLabs")
                except Exception as e:
                    logger.error(f"Failed to get ElevenLabs voices: {e}")
                    raise
    
            logger.info(f"Initialized ElevenLabs TTS engine with voice_id: {self.voice_id}")
    
        except Exception as e:
            logger.error(f"Failed to initialize ElevenLabs: {e}")
            logger.info("Falling back to pyttsx3")
            self.engine_type = 'pyttsx3'
            self._initialize_pyttsx3()
    
    def speak(self, text: str) -> None:
        """
        Speak the given text.
        
        Args:
            text: Text to speak
        """
        if not text or not text.strip():
            return

        # Stop any current speech
        self.stop()

        self.speaking = True
        self.speech_thread = threading.Thread(
            target=self._speak_thread, 
            args=(text.strip(),), 
            daemon=True
        )
        self.speech_thread.start()

    def _speak_thread(self, text: str) -> None:
        """Thread function for speaking text."""
        try:
            if self.engine_type == 'pyttsx3' and self.engine:
                self._speak_pyttsx3(text)
            elif self.engine_type == 'elevenlabs' and self.elevenlabs_client:
                self._speak_elevenlabs(text)
            else:
                logger.error("No TTS engine available")

        except Exception as e:
            logger.error(f"Error during speech synthesis: {e}")
        finally:
            self.speaking = False

    def _speak_pyttsx3(self, text: str) -> None:
        """Speak using pyttsx3."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error with pyttsx3 speech: {e}")

    def _speak_elevenlabs(self, text: str) -> None:
        """Speak using ElevenLabs."""
        try:
            # Use the elevenlabs client directly
            # Try different API patterns
            try:
                # First try the generate function directly
                audio = self.elevenlabs_client.generate(
                    text=text,
                    voice=self.voice_id
                )
            except (AttributeError, TypeError):
                # Try alternative API patterns
                try:
                    # Try using the Voice class if available
                    from elevenlabs import Voice, generate
                    voice = Voice(voice_id=self.voice_id)
                    audio = generate(text=text, voice=voice)
                except:
                    # Last resort - try the most basic form
                    audio = self.elevenlabs_client.generate(text, self.voice_id)
            
            # Play audio
            self._play_audio_data(audio)
            
        except ImportError as e:
            logger.error(f"ElevenLabs library error: {e}")
            logger.info("Falling back to pyttsx3")
            self.engine_type = 'pyttsx3'
            self._initialize_pyttsx3()
            self._speak_pyttsx3(text)
        except Exception as e:
            logger.error(f"Error with ElevenLabs speech: {e}")
            # Try fallback to pyttsx3 if ElevenLabs fails
            if self.engine_type == 'elevenlabs':
                logger.info("Temporarily falling back to pyttsx3 for this request")
                if not self.engine:
                    self._initialize_pyttsx3()
                self._speak_pyttsx3(text)

    def _play_audio_data(self, audio_data) -> None:
        """Play audio data using pygame or other available method."""
        try:
            # Try to use pygame for audio playback
            import pygame
            import io
            
            pygame.mixer.init()
            pygame.mixer.music.load(io.BytesIO(audio_data))
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
                
        except ImportError:
            # Fallback to saving and playing file
            import tempfile
            import subprocess
            
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Try to play with system default player
                if os.name == 'nt':  # Windows
                    os.system(f'start /B /WAIT {temp_file_path}')
                else:  # Unix-like
                    subprocess.run(['play', temp_file_path], check=True)
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except OSError:
                    pass

    def stop(self) -> None:
        """Stop current speech."""
        if not self.speaking:
            return

        self.speaking = False

        try:
            if self.engine_type == 'pyttsx3' and self.engine:
                self.engine.stop()
            elif self.engine_type == 'elevenlabs':
                # Stop pygame mixer if it's running
                try:
                    import pygame
                    pygame.mixer.music.stop()
                except ImportError:
                    pass
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")

        # Wait for speech thread to finish
        if self.speech_thread and self.speech_thread.is_alive():
            self.speech_thread.join(timeout=1.0)

    def save_to_file(self, text: str, file_path: str) -> bool:
        """
        Save speech to an audio file.
        
        Args:
            text: Text to convert to speech
            file_path: Path where to save the audio file
            
        Returns:
            bool: True if successful
        """
        if not text or not text.strip():
            return False
    
        try:
            if self.engine_type == 'pyttsx3' and self.engine:
                self.engine.save_to_file(text, file_path)
                self.engine.runAndWait()
                return os.path.exists(file_path)
    
            elif self.engine_type == 'elevenlabs' and self.elevenlabs_client:
                # Try different API patterns
                try:
                    # First try the generate function directly
                    audio = self.elevenlabs_client.generate(
                        text=text,
                        voice=self.voice_id
                    )
                except (AttributeError, TypeError):
                    # Try alternative API patterns
                    try:
                        # Try using the Voice class if available
                        from elevenlabs import Voice, generate
                        voice = Voice(voice_id=self.voice_id)
                        audio = generate(text=text, voice=voice)
                    except:
                        # Last resort - try the most basic form
                        audio = self.elevenlabs_client.generate(text, self.voice_id)
                
                with open(file_path, 'wb') as f:
                    f.write(audio)
                
                return os.path.exists(file_path)
    
        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
            return False
    
        return False

    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self.speaking

    def get_available_voices(self) -> list:
        """Get list of available voices for the current engine."""
        voices = []
        
        try:
            if self.engine_type == 'pyttsx3' and self.engine:
                pyttsx3_voices = self.engine.getProperty('voices')
                for voice in pyttsx3_voices:
                    if voice:
                        voices.append({
                            'id': voice.id,
                            'name': voice.name,
                            'language': getattr(voice, 'languages', ['unknown'])
                        })
            
            elif self.engine_type == 'elevenlabs' and self.elevenlabs_client:
                elevenlabs_voices = self.elevenlabs_client.voices()
                for voice in elevenlabs_voices:
                    voices.append({
                        'id': voice.voice_id,
                        'name': voice.name,
                        'language': getattr(voice, 'category', 'unknown')
                    })
                    
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
        
        return voices

    def __del__(self):
        """Clean up resources when object is destroyed."""
        try:
            self.stop()
        except Exception as e:
            logger.error(f"Error during TTSEngine cleanup: {e}")