import os
import time
from datetime import datetime
from openai import OpenAI
from gtts import gTTS
import subprocess
from PIL import Image, ImageDraw, ImageFont
from apscheduler.schedulers.background import BackgroundScheduler

# ====================== CONFIG ======================
GROK_API_KEY = os.getenv("GROK_API_KEY")
NICHE = "naval maritime small business compliance life hacks puget sound shipyard"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

def generate_short_script():
    prompt = f"""Write a engaging 30-second YouTube Shorts script for this niche: {NICHE}.
    Structure:
    - Strong hook (first 3-5 seconds)
    - 2-3 useful tips or life hacks
    - Strong CTA with affiliate placeholder
    Keep total spoken text under 75 words. Make it conversational and valuable for shipyard workers/vets in Puget Sound area."""
    
    response = client.chat.completions.create(
        model="grok-4.20-non-reasoning",  # or whatever current model works
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

def create_video(script_text, video_id):
    try:
        # Simple background
        width, height = 1080, 1920
        bg_color = (0, 20, 40)  # Navy blue
        
        # Create text image with PIL (lower memory)
        text_img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(text_img)
        
        # Use available Linux font with smaller size and wrapping
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
        except:
            font = ImageFont.load_default()
        
        # Simple word wrap
        lines = []
        words = script_text.split()
        current_line = []
        for word in words:
            current_line.append(word)
            if len(" ".join(current_line)) > 40:  # rough wrap
                lines.append(" ".join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))
        
        y = 300
        for line in lines:
            draw.text((100, y), line, font=font, fill=(255, 255, 255))
            y += 80
        
        # Save text frame
        text_path = f"{OUTPUT_DIR}/{video_id}_text.png"
        text_img.save(text_path)
        
        # TTS audio
        tts = gTTS(script_text, lang='en')
        audio_path = f"{OUTPUT_DIR}/{video_id}.mp3"
        tts.save(audio_path)
        
        # Create simple video with ffmpeg (much lower memory)
        final_path = f"{OUTPUT_DIR}/{video_id}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", text_path,
            "-i", audio_path,
            "-c:v", "libx264", "-tune", "stillimage",
            "-c:a", "aac",
            "-shortest",
            "-vf", "scale=1080:1920",
            final_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        
        print(f"✅ Stable Short with sound generated: {final_path}")
        return final_path
        
    except Exception as e:
        print(f"❌ Video creation error: {e}")
        return None

def ai_watchdog():
    print(f"[{datetime.now()}] 🚀 Generating new maritime Short...")
    script = generate_short_script()
    print("📝 Generated script:", script[:200] + "..." if len(script) > 200 else script)
    create_video(script, f"short_{int(time.time())}")

# Scheduler (runs every 12 hours)
scheduler = BackgroundScheduler()
scheduler.add_job(ai_watchdog, 'interval', hours=12)
scheduler.start()

print("🚀 Maritime Money Printer started with AI watchdog!")
ai_watchdog()  # Generate one immediately

# Keep running
try:
    while True:
        time.sleep(3600)
except KeyboardInterrupt:
    scheduler.shutdown()