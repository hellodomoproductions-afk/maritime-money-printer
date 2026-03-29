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

def generate_short():
    print(f"\n[{datetime.now()}] 🚀 Generating new maritime Short on startup...")
    try:
        prompt = f"Create a short engaging YouTube Shorts script about {NICHE}. Strong hook, 2-3 practical tips for shipyard workers or maritime small business owners in Puget Sound, clear CTA with Amazon affiliate placeholder. Keep spoken text under 70 words. Make it conversational."
        
        response = client.chat.completions.create(
            model="grok-4.20-non-reasoning",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=250
        )
        script = response.choices[0].message.content.strip()
        print("📝 Script generated:", script)

        # Generate audio
        audio_path = f"{OUTPUT_DIR}/short_{int(time.time())}.mp3"
        tts = gTTS(script, lang='en')
        tts.save(audio_path)

        # Generate video (navy background + audio)
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
        
        return video_path
    except Exception as e:
        print(f"❌ Error generating Short: {e}")
        return None

# Force generation on every startup
print("🚀 Maritime Money Printer started - generating Short now...")
generate_short()

# Optional scheduler for future (every 12 hours)
scheduler = BackgroundScheduler()
scheduler.add_job(generate_short, 'interval', hours=12)
scheduler.start()

print("✅ Generation cycle started. Next one in 12 hours.")

try:
    while True:
        time.sleep(3600)
except:
    scheduler.shutdown()