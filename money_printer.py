import os
import time
from datetime import datetime
from openai import OpenAI
from gtts import gTTS
import subprocess

# ====================== CONFIG ======================
GROK_API_KEY = os.getenv("GROK_API_KEY")
NICHE = "naval maritime small business compliance life hacks puget sound shipyard"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

def generate_short_script():
    prompt = f"""Create a short, engaging 25-30 second YouTube Shorts script about {NICHE}.
    - Start with a strong hook
    - Give 2-3 practical tips for shipyard workers or maritime small business owners in Puget Sound
    - End with a clear CTA and affiliate placeholder
    Keep the entire spoken text under 70 words. Make it conversational and useful."""
    
    response = client.chat.completions.create(
        model="grok-4.20-non-reasoning",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=250
    )
    return response.choices[0].message.content.strip()

def create_video(script_text, video_id):
    try:
        audio_path = f"{OUTPUT_DIR}/{video_id}.mp3"
        final_path = f"{OUTPUT_DIR}/{video_id}.mp4"
        
        # Generate audio
        tts = gTTS(script_text, lang='en')
        tts.save(audio_path)
        
        # Create simple video with ffmpeg (very low memory)
        # Black background with white text overlay + gentle zoom
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", "color=c=0x001428:s=1080x1920:d=30",  # Navy background, 30 seconds
            "-i", audio_path,
            "-vf", "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:fontsize=50:fontcolor=white:borderw=4:bordercolor=black:x=(w-text_w)/2:y=(h-text_h)/2:text='" + script_text.replace("'", "'\\''") + "':enable='between(t,0,30)'",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-shortest",
            final_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Stable Short with sound generated: {final_path}")
            return final_path
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Video creation error: {e}")
        return None

def ai_watchdog():
    print(f"[{datetime.now()}] 🚀 Generating new maritime Short...")
    script = generate_short_script()
    print("📝 Script:", script)
    create_video(script, f"short_{int(time.time())}")

# Scheduler + immediate run
scheduler = BackgroundScheduler()
scheduler.add_job(ai_watchdog, 'interval', hours=12)
scheduler.start()

print("🚀 Maritime Money Printer (ultra-light) started!")
ai_watchdog()  # Generate one right away

try:
    while True:
        time.sleep(3600)
except:
    scheduler.shutdown()