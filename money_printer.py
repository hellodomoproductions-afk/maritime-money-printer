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

def ai_watchdog():
    print(f"\n[{datetime.now()}] 🚀 Generating new maritime Short...")
    try:
        prompt = f"Create a short engaging YouTube Shorts script about {NICHE}. Strong hook, 2-3 tips for shipyard workers in Puget Sound, clear CTA with affiliate link placeholder. Under 70 words."
        response = client.chat.completions.create(
            model="grok-4.20-non-reasoning",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250
        )
        script = response.choices[0].message.content.strip()
        print("📝 Script:", script)

        audio_path = f"{OUTPUT_DIR}/short_{int(time.time())}.mp3"
        tts = gTTS(script, lang='en')
        tts.save(audio_path)

        video_path = f"{OUTPUT_DIR}/short_{int(time.time())}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x001428:s=1080x1920:d=30",
            "-i", audio_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            video_path
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"✅ Stable Short with sound generated: {video_path}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Force generation on startup and schedule every 12 hours
scheduler = BackgroundScheduler()
scheduler.add_job(ai_watchdog, 'interval', hours=12)
scheduler.start()

print("🚀 Maritime Money Printer started!")
ai_watchdog()  # Force one now

try:
    while True:
        time.sleep(3600)
except:
    scheduler.shutdown()