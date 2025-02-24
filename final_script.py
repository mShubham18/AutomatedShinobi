from PIL import Image
import os
import tempfile
import cv2
import numpy as np
import whisperx
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips,
    CompositeVideoClip, TextClip
)
from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.config import change_settings

# Set ImageMagick binary path (Windows users)
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


def load_images(folder="downloaded_images"):
    image_files = sorted(os.listdir(folder))  # Sort to maintain order
    loaded_images = [Image.open(os.path.join(folder, img)) for img in image_files]
    print(f"Loaded {len(loaded_images)} images")
    return loaded_images  # Returns a list of PIL objects


def process_images(image_list, voiceover_duration, max_duration_per_image=4):
    """
    Selects images to fit the duration of the voiceover and applies zoom-out effect.
    Handles PIL images by saving them as temporary files.
    """
    num_images = min(len(image_list), int(voiceover_duration / max_duration_per_image))
    selected_images = image_list[:num_images]

    clips = []
    temp_files = []

    for img_index, img in enumerate(selected_images):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        img.save(temp_file, format="JPEG")
        temp_file.close()
        temp_files.append(temp_file.name)

        cv_img = cv2.imread(temp_file.name)
        if cv_img is None:
            print(f"Error: Unable to read {temp_file.name}")
            continue

        clip = ImageClip(temp_file.name).set_duration(max_duration_per_image).resize(lambda t: 1 + 0.05 * t)
        clips.append(clip)

    return clips


def process_audio(voiceover_path, bgm_path):
    """
    Load the voiceover and background music and mix them properly.
    """
    voiceover = AudioFileClip(voiceover_path)
    bgm = AudioFileClip(bgm_path).subclip(0, voiceover.duration).volumex(0.4)  # Reduce BGM volume
    return CompositeAudioClip([voiceover, bgm])


def generate_subtitles(voiceover_path, video_height):
    """
    Generates subtitles using WhisperX, synchronizing them with the voiceover.
    - Subtitles are placed at the bottom center.
    - Uses 'Arial-Bold' font with a black outline for visibility.
    - Ensures correct timing and display.
    """
    model = whisperx.load_model("base", device="cpu", compute_type="float32")
    audio = whisperx.load_audio(voiceover_path)
    result = model.transcribe(audio)

    # Extract subtitle segments with timestamps
    subs = [((segment['start'], segment['end']), segment['text']) for segment in result['segments']]

    subtitle_clips = []

    for (start, end), text in subs:
        subtitle_clip = (
            TextClip(
                text,
                fontsize=50,
                color="white",
                font="Arial-Bold",
                stroke_color="black",
                stroke_width=3,  # Ensures better contrast
            )
            .set_position(("center", video_height - 100))  # 100px from the bottom
            .set_start(start)  # Sync start time with audio
            .set_duration(end - start)  # Sync duration
        )
        subtitle_clips.append(subtitle_clip)

    if not subtitle_clips:
        print("No subtitles generated! Check WhisperX output.")

    return CompositeVideoClip(subtitle_clips)




def create_final_video(images, voiceover_path, bgm_path, output_path="shorts/final_video.mp4"):
    """
    Combines images, voiceover, background music, and subtitles into a final video.
    """
    voiceover = AudioFileClip(voiceover_path)
    clips = process_images(images, voiceover.duration)

    # Get video height
    video_height = clips[0].size[1]

    # Concatenate video clips
    video = concatenate_videoclips(clips, method="compose")
    video = video.set_audio(process_audio(voiceover_path, bgm_path))

    # Generate and add subtitles
    subtitles = generate_subtitles(voiceover_path, video_height)
    final_video = CompositeVideoClip([video, subtitles])

    # Save output
    os.makedirs("shorts", exist_ok=True)
    final_video.write_videofile(output_path, fps=24, codec="libx264")


# Run the pipeline
if __name__ == "__main__":
    img_list = load_images()
    create_final_video(images=img_list, voiceover_path="outputs/output.mp3", bgm_path="Resources/bgm.mp3")
