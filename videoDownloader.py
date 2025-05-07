
import os
import subprocess
import requests
from bs4 import BeautifulSoup
import yt_dlp

# Function to update yt-dlp automatically
def update_yt_dlp():
    try:
        subprocess.run(['pip', 'install', '--upgrade', 'yt-dlp'], check=True)
        print("✅ yt-dlp has been updated to the latest version.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to update yt-dlp: {e}")

# Function to download videos using yt-dlp
def download_video_with_ytdlp(video_url, output_path):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'bestvideo+bestaudio/best',
            'noplaylist': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"▶️ Downloading: {video_url}")
            ydl.download([video_url])
            print(f"✅ Done: {video_url}")
            return True
    except Exception as e:
        print(f"❌ Error downloading with yt-dlp: {e}")
        return False

# Fallback for TikTok videos
def download_tiktok_fallback(video_url, output_path):
    try:
        response = requests.get(video_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        video_tag = soup.find('video')

        if video_tag:
            video_src = video_tag.get('src')
            video_content = requests.get(video_src).content

            output_file = os.path.join(output_path, 'tiktok_video.mp4')
            with open(output_file, 'wb') as f:
                f.write(video_content)
            print(f"✅ Fallback TikTok saved: {output_file}")
            return True
        else:
            print("⚠️ No <video> tag found.")
            return False
    except Exception as e:
        print(f"❌ Error in fallback: {e}")
        return False

# Master function
def download_video(video_url, output_path):
    if "youtube.com" in video_url or "youtu.be" in video_url:
        return download_video_with_ytdlp(video_url, output_path)
    elif "tiktok.com" in video_url:
        if download_video_with_ytdlp(video_url, output_path):
            return True
        else:
            print("⏪ Trying fallback method for TikTok...")
            return download_tiktok_fallback(video_url, output_path)
    else:
        return download_video_with_ytdlp(video_url, output_path)

# === Main ===
if __name__ == "__main__":
    update_yt_dlp()
    
    input_txt = input("📄 Enter the path to the .txt file with URLs: ").strip()

    if not os.path.isfile(input_txt):
        print("❌ File does not exist.")
        exit()

    # Read and clean URLs
    with open(input_txt, 'r') as f:
        urls = [line.strip().strip('"').strip("'") for line in f.readlines() if line.strip()]

    output_path = "/home/phonemyint-kyaw/Videos/testing"
    os.makedirs(output_path, exist_ok=True)

    successfully_downloaded = []
    failed_downloads = []

    for url in urls:
        result = download_video(url, output_path)
        if result:
            successfully_downloaded.append(url)
        else:
            failed_downloads.append(url)

    # Write results to file
    with open("all_results.txt", "w") as f:
        f.write("✅ Successfully Downloaded:\n")
        for s in successfully_downloaded:
            f.write(s + ",\n")  # comma at the end of each line
        f.write("\n❌ Failed Downloads:\n")
        for f_url in failed_downloads:
            f.write(f_url + ",\n")  # comma at the end of each line

    print("\n📊 === SUMMARY ===")
    print(f"✅ {len(successfully_downloaded)} Success")
    print(f"❌ {len(failed_downloads)} Failed")
    print("📁 All results saved to 'all_results.txt'")

