import pyttsx3
import speech_recognition as sr
import json
import re

class VoiceAssistant:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0
        self._init_engine()

    def _init_engine(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)

    def speak(self, text):
        try:
            # Final text cleanup for speech
            try:
                data = json.loads(text)
                text = data.get('content', text)
            except:
                pass
            clean_text = re.sub(r'\[.*?\]:?', '', text).strip()
            
            self.engine.say(clean_text)
            self.engine.runAndWait()
            # Reset engine to prevent audio driver deadlock
            self.engine.stop()
            self._init_engine()
        except:
            self._init_engine()

    def listen(self, timeout=None):
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
            try:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                return self.recognizer.recognize_google(audio)
            except:
                return None