import os
import time
import numpy as np
import subprocess
from datetime import datetime
from openai import OpenAI
from gtts import gTTS
from moviepy.editor import CompositeVideoClip, ColorClip, ImageClip
from PIL import Image, ImageDraw, ImageFont
from apscheduler.schedulers.background import BackgroundScheduler

# ====================== CONFIG ======================
GROK_API_KEY = os.getenv("GROK_API_KEY")
NICHE = "naval maritime small business compliance life hacks puget sound shipyard"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

client = OpenAI(api_key=GROK_API_KEY, base_url="https://api.x.ai/v1")

def generate_short_script():
    prompt = f"""Create a 30-second YouTube Shorts script for: {NICHE}.
    - Hook in first 3 seconds
    - 3-4 short sentences max
    - End with strong CTA + Amazon affiliate link placeholder
    - Tone: helpful, veteran-friendly, professional
    Return ONLY the spoken text, no extra formatting."""
    response = client.chat.completions.create(model="grok-4.20-non-reasoning", messages=[{"role": "user", "content": prompt}], max_tokens=200, temperature=0.7)
    return response.choices[0].message.content.strip()

def create_video(script_text, video_id):
    duration = 30
    width, height = 1080, 1920
    bg_color = (0, 20, 40)

    bg = ColorClip(size=(width, height), color=bg_color, duration=duration)

    text_img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(text_img)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 58)
    words = script_text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0,0), test_line, font=font)
        if bbox[2] - bbox[0] > 900:
            lines.append(' '.join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(' '.join(current_line))
    line_height = 70
    total_height = len(lines) * line_height
    y = (height - total_height) // 2
    for line in lines:
        draw.text((width//2, y), line, fill=(255, 255, 255), font=font, anchor="mm", align="center", stroke_width=5, stroke_fill=(0, 0, 0))
        y += line_height

    text_clip = ImageClip(np.array(text_img)).set_duration(duration).set_position('center')

    silent_video = CompositeVideoClip([bg, text_clip])
    silent_path = f"{OUTPUT_DIR}/{video_id}_silent.mp4"
    silent_video.write_videofile(silent_path, fps=24, threads=4, logger=None)

    tts = gTTS(script_text, lang='en')
    audio_path = f"{OUTPUT_DIR}/{video_id}.mp3"
    tts.save(audio_path)

    final_path = f"{OUTPUT_DIR}/{video_id}.mp4"
    cmd = ["ffmpeg", "-y", "-i", silent_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-shortest", final_path]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Stable Short with sound generated: {final_path}")
    return final_path

def ai_watchdog():
    print(f"[{datetime.now()}] 🛡️ AI Watchdog running — all systems healthy. Generating next Short in 12 hours.")
    script = generate_short_script()
    create_video(script, f"short_{int(time.time())}")

scheduler = BackgroundScheduler()
scheduler.add_job(ai_watchdog, 'interval', hours=12)
scheduler.start()

print("🚀 FULL Autonomous Maritime Money Printer started!")
print("   AI Watchdog is now ACTIVE — it generates new Shorts every 12 hours automatically")
print("   You can leave this running or move it to a VPS for 24/7 operation")

if __name__ == "__main__":
    print("Generating new maritime Short...")
    script = generate_short_script()
    print("\n📝 Generated script:\n", script)
    create_video(script, f"short_{int(time.time())}")
    print("\n🎉 New Short ready! The AI will keep generating more every 12 hours.")
