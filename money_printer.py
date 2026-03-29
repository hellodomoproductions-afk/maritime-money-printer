import os
import time
from datetime import datetime
from openai import OpenAI
from gtts import gTTS
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

GROK_API_KEY = os.getenv("GROK_API_KEY")
NICHE = "naval maritime small business compliance life hacks puget sound shipyard"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

def generate_short_script():
    print(f"[{datetime.now()}] 🤖 Calling Grok to generate script...")
    prompt = f"Create a 25-30 second YouTube Shorts script about {NICHE}. Strong hook, 2-3 tips for shipyard workers in Puget Sound, clear CTA. Under 70 words."
    response = client.chat.completions.create(
        model="grok-4.20-non-reasoning",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=250
    )
    script = response.choices[0].message.content.strip()
    print(f"✅ Script ready: {script[:150]}...")
    return script

def create_video(script_text, video_id):
    print(f"[{datetime.now()}] 🎥 Creating video...")
    try:
        audio_path = f"{OUTPUT_DIR}/{video_id}.mp3"
        final_path = f"{OUTPUT_DIR}/{video_id}.mp4"
        
        tts = gTTS(script_text, lang='en')
        tts.save(audio_path)
        
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x001428:s=1080x1920:d=30",
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            final_path
        ]
        
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Stable Short with sound generated: {final_path}")
        return final_path
    except Exception as e:
        print(f"❌ Video error: {e}")
        return None

def ai_watchdog():
    print(f"\n[{datetime.now()}] 🚀 Generating new maritime Short...")
    script = generate_short_script()
    create_video(script, f"short_{int(time.time())}")

# Run immediately and schedule
scheduler = BackgroundScheduler()
scheduler.add_job(ai_watchdog, 'interval', hours=12)
scheduler.start()

print("🚀 Maritime Money Printer started!")
ai_watchdog()   # <--- This forces generation right now

try:
    while True:
        time.sleep(3600)
except:
    scheduler.shutdown()