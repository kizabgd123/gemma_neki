import subprocess
import os
import sys

PIPER_PATH = os.path.expanduser("~/.local/bin/piper")
VOICE_MODEL = os.path.expanduser("~/.local/share/piper-voices/sr_RS-serbski_institut-medium.onnx")

def speak(text):
    if not text: return
    try:
        piper_proc = subprocess.Popen(
            [PIPER_PATH, "--model", VOICE_MODEL, "--output_raw"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        aplay_proc = subprocess.Popen(
            ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
            stdin=piper_proc.stdout, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        piper_proc.stdin.write(text.encode('utf-8'))
        piper_proc.stdin.close()
        aplay_proc.wait()
    except Exception as e:
        print(f"TTS Error: {e}")

if __name__ == "__main__":
    speak(" ".join(sys.argv[1:]))
