import speech_recognition as sr
import pyttsx3
import json
import re

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0
        self._init_engine()

    def _init_engine(self):
        """Initializes the speech engine with a fresh instance."""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
            self.engine.setProperty('rate', 180)
        except Exception as e:
            print(f"Speech Engine Init Error: {e}")

    def speak(self, text):
        """Extracts content and speaks it, then resets the engine."""
        try:
            # Handle JSON if the agent returns it
            try:
                data = json.loads(text)
                text = data.get('content', text)
            except:
                pass
            
            # Clean technical tags
            clean_text = re.sub(r'\[.*?\]:?', '', text).strip()
            
            if clean_text:
                self.engine.say(clean_text)
                self.engine.runAndWait()
            
            # Reset to ensure the audio driver is released properly
            self._init_engine()
        except Exception:
            self._init_engine()

    def listen(self, timeout=None):
        """Captures audio and converts to text via Google STT."""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                return self.recognizer.recognize_google(audio)
            except:
                return None