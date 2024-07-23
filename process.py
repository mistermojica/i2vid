import threading
from ig_uploader import upload_video_thread

def main():
    video_url = "https://videos.pexels.com/video-files/10780729/10780729-hd_1080_1920_30fps.mp4"
    video_type = "REELS"
    caption = "Follow @luxuryroamers for more!!!"
    share_to_feed = True

    def callback(response):
        print(response)
    
    # Crear y empezar el hilo
    thread = threading.Thread(target=upload_video_thread, args=(video_url, video_type, caption, share_to_feed, callback))
    thread.start()

if __name__ == "__main__":
    main()