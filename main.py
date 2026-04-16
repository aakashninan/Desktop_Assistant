import threading
import time
import sys
from agent.core import run_agent
from voice_handler import VoiceAssistant
from voice_ui import SiriInterface
from PyQt6.QtWidgets import QApplication

def voice_thread_logic(ui):
    va = VoiceAssistant()
    print("🎙️ Agent Lurking... Ready for 'Hey Assistant'")
    
    while True:
        try:
            raw_text = va.listen(timeout=None)
            
            if raw_text and "hey assistant" in raw_text.lower():
                # Emit signals to the UI thread
                ui.update_ui("🎤 I'm listening...", state="listening")
                va.speak("Yes?")
                
                command = va.listen(timeout=5)
                if command:
                    ui.update_ui(f"Thinking...", state="thinking")
                    response = run_agent(command)
                    
                    ui.update_ui(response, state="responding")
                    va.speak(response)
                    time.sleep(5)
                else:
                    ui.update_ui("No command heard.", state="responding")
                    time.sleep(1.5)
                
                ui.update_ui("", visible=False)
                
            time.sleep(0.1)
        except Exception:
            continue

if __name__ == "__main__":
    # Create the App instance
    app = QApplication(sys.argv)
    
    # Initialize UI
    ui_overlay = SiriInterface()
    
    # Start background thread
    t = threading.Thread(target=voice_thread_logic, args=(ui_overlay,), daemon=True)
    t.start()
    
    # Start the App Loop (This blocks the main thread)
    sys.exit(app.exec())