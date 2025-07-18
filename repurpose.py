import os
from dotenv import load_dotenv
from openai import OpenAI

# ✅ Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def transcribe_video(file_path):
    print("[1/4] Transcribing video...")
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcript.text

def generate_content(transcript):
    print("[2/4] Generating content...")
    prompt = f"""
    You are an expert content repurposer.
    From the following transcript, create:

    ### Twitter/X Thread
    Write a 5-7 post Twitter/X thread (under 280 chars, numbered 1/, 2/).

    ### LinkedIn Blog-Style Summary
    Write a professional blog-style summary (LinkedIn tone).

    ### Instagram Caption
    Write a catchy Instagram caption with 5 relevant hashtags.

    Transcript:
    {transcript}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    return response.choices[0].message.content

def save_split_outputs(content):
    print("[3/4] Splitting and saving outputs...")
    os.makedirs("outputs", exist_ok=True)

    sections = {"twitter_thread": "", "blog_summary": "", "instagram_caption": ""}
    current = None

    for line in content.splitlines():
        line = line.strip()
        if "Twitter/X Thread" in line:
            current = "twitter_thread"
            continue
        elif "LinkedIn Blog-Style Summary" in line:
            current = "blog_summary"
            continue
        elif "Instagram Caption" in line:
            current = "instagram_caption"
            continue
        if current and line:
            sections[current] += line + "\n"

    with open("outputs/twitter_thread.txt", "w", encoding="utf-8") as f:
        f.write(sections["twitter_thread"].strip())
    with open("outputs/blog_summary.txt", "w", encoding="utf-8") as f:
        f.write(sections["blog_summary"].strip())
    with open("outputs/instagram_caption.txt", "w", encoding="utf-8") as f:
        f.write(sections["instagram_caption"].strip())
    with open("outputs/full_result.txt", "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Files saved in outputs/: twitter_thread.txt, blog_summary.txt, instagram_caption.txt")

if __name__ == "__main__":

    video_path = input("Enter your video file path (e.g., video.mp4): ")
    transcript = transcribe_video(video_path)
    print("Transcript captured ✅")
    content = generate_content(transcript)
    save_split_outputs(content)
    print("[4/4] ✅ Done! Check the outputs folder.")
