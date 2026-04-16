import threading
import time
import sys
from PyQt6.QtWidgets import QApplication
from agent.core import run_agent
from voice_handler import VoiceAssistant
from voice_ui import SiriInterface

def voice_thread_logic(ui):
    va = VoiceAssistant()
    print("🎙️ Agent Lurking... Ready for 'Hey Assistant'")
    
    while True:
        try:
            # 1. Listen for the Wake Word
            raw_text = va.listen(timeout=None)
            
            if raw_text and "hey assistant" in raw_text.lower():
                # 2. Trigger UI & Audio feedback
                ui.update_ui("🎤 I'm listening...", state="listening")
                va.speak("Yes?")
                
                # 3. Capture Command
                command = va.listen(timeout=5)
                if command:
                    ui.update_ui(f"Thinking...", state="thinking")
                    
                    # 4. Call Agentic Logic
                    response = run_agent(command)
                    
                    # 5. Show and Speak Response
                    ui.update_ui(response, state="responding")
                    va.speak(response)
                    time.sleep(5) # Reading time
                else:
                    ui.update_ui("No command detected.", state="responding")
                    time.sleep(1.5)
                
                # 6. Smooth Fade Out
                ui.update_ui("", visible=False)
                
                # Buffer to let audio drivers settle
                time.sleep(1.0)
                
            time.sleep(0.1)
        except Exception as e:
            # Silently keep the loop alive
            continue

if __name__ == "__main__":
    # Initialize the High-Performance App Loop
    app = QApplication(sys.argv)
    
    # Initialize UI
    ui_overlay = SiriInterface()
    
    # Start background voice thread
    t = threading.Thread(target=voice_thread_logic, args=(ui_overlay,), daemon=True)
    t.start()
    
    # Execute App
    try:
        sys.exit(app.exec())
    except SystemExit:
        pass