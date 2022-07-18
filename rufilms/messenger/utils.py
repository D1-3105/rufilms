from moviepy.editor import VideoFileClip


def get_video_len(filepath):
    vid=VideoFileClip(filepath)
    dur=vid.duration
    vid.close()
    return dur
