import sqlite3
import json
import subprocess
import os
import sys

# Konfiguracija putanja
PIPER_PATH = os.path.expanduser("~/.local/bin/piper")
VOICE_MODEL = os.path.expanduser("~/.local/share/piper-voices/sr_RS-serbski_institut-medium.onnx")
DB_PATH = "storage/memory.db"

def speak(text, lang="sr"):
    """Pokreće Piper TTS i strimuje direktno na aplay."""
    if not text:
        return
    
    # Za sada koristimo srpski glas za sve, ali možemo proširiti
    model = VOICE_MODEL
    
    print(f"Speaking: {text[:50]}...")
    
    try:
        # Piper proces
        piper_proc = subprocess.Popen(
            [PIPER_PATH, "--model", model, "--output_raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL
        )
        
        # Aplay proces
        aplay_proc = subprocess.Popen(
            ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
            stdin=piper_proc.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Pošalji tekst piperu
        piper_proc.stdin.write(text.encode('utf-8'))
        piper_proc.stdin.close()
        
        # Sačekaj da završi
        aplay_proc.wait()
        
    except Exception as e:
        print(f"TTS Error: {e}")

def get_latest_debate():
    """Izvlači poslednju debatu iz baze."""
    if not os.path.exists(DB_PATH):
        print("Baza podataka nije pronađena.")
        return None
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Uzmi poslednji debate_id
        cursor.execute("SELECT debate_id, final_consensus FROM debates ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        
        if not row:
            print("Nema pronađenih debata u bazi.")
            return None
        
        debate_id, consensus_raw = row
        consensus_data = json.loads(consensus_raw)
        
        # Uzmi argumente agenata
        cursor.execute("SELECT agent_name, argument FROM arguments WHERE debate_id = ? ORDER BY id ASC", (debate_id,))
        args_rows = cursor.fetchall()
        
        conn.close()
        return {
            "id": debate_id,
            "consensus": consensus_data.get("consensus_decision", ""),
            "arguments": args_rows
        }
    except Exception as e:
        print(f"Database Error: {e}")
        return None

def run_audio_summary():
    debate = get_latest_debate()
    if not debate:
        return

    print(f"\n--- Generisanje Audio Izveštaja za Debatu: {debate['id']} ---")
    
    # 1. Uvod
    intro = "Evo izveštaja sa poslednje debate agenata."
    speak(intro)
    
    # 2. Argumenti agenata (Skraćeno za audio)
    for agent, arg_json in debate['arguments']:
        try:
            arg_data = json.loads(arg_json)
            # Različiti agenti imaju različite strukture outputa
            content = ""
            if agent == "Analyst":
                content = f"Analitičar predlaže: {arg_data.get('proposal', '')[:100]}"
            elif agent == "Solution":
                content = f"Rešenje fokusira na: {arg_data.get('solution', '')[:100]}"
            elif agent == "Critic":
                flaws = arg_data.get('logical_flaws', [])
                content = f"Kritičar primećuje {len(flaws)} potencijalnih grešaka."
            elif agent == "Security":
                risks = arg_data.get('security_risks', [])
                content = f"Bezbednosni agent je identifikovao {len(risks)} rizika."
            elif agent == "Optimizer":
                content = "Optimizator je predložio poboljšanja performansi."
            
            if content:
                speak(content)
        except:
            continue

    # 3. Finalna Odluka
    speak("Finalna odluka orkestratora je sledeća.")
    speak(debate['consensus'])
    
    speak("Kraj izveštaja.")

if __name__ == "__main__":
    run_audio_summary()
