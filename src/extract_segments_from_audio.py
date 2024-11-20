from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import numpy as np

def detect_speech_segments(audio_path, 
                         min_silence_len=700,  # minimum silence length in ms
                         silence_thresh=-40,     # silence threshold in dB
                         seek_step=50,          # step size for silence detection in ms
                         padding_ms=400):          # step size for silence detection in ms
    """
    Detect speech segments in an audio file using pydub
    
    Parameters:
    -----------
    audio_path : str
        Path to the audio file
    min_silence_len : int
        Minimum length of silence in milliseconds
    silence_thresh : int
        Silence threshold in dB
    seek_step : int
        Step size for silence detection in milliseconds
    
    Returns:
    --------
    list of tuples
        List of (start_time, end_time) in milliseconds for speech segments
    """
    
    # Load the audio file
    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        print(f"Error loading audio file: {e}")
        return []
    
    # Detect non-silent chunks
    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=seek_step
    )
    
    # Convert to seconds and create segments
    speech_segments = []
    for start, end in nonsilent_ranges:

        padded_start = (start - padding_ms) / 1000.0  # Convert to seconds
        padded_end = (end + padding_ms) / 1000.0
        segment = {
            'start': round(padded_start, 3),  # Convert to seconds
            'end': round(padded_end, 3),
            'duration': round(padded_end - padded_start, 3),
            'type': 'speech'
        }
        speech_segments.append(segment)
    
    return speech_segments


def infer_silence_segments(speech_segments, total_duration):
    """
    Convert speech segments to silence segments
    
    Parameters:
    -----------
    speech_segments : list
        List of speech segments
    total_duration : float
        Total duration of the audio in seconds
    """
    silence_segments = []
    
    # Handle the beginning
    if speech_segments[0]['start'] > 0:
        silence_segments.append({
            'start': 0,
            'end': speech_segments[0]['start'],
            'duration': round(speech_segments[0]['start'], 3),
            'type': 'silence'
        })
    
    # Handle gaps between speech segments
    for i in range(len(speech_segments)-1):
        silence_start = speech_segments[i]['end']
        silence_end = speech_segments[i+1]['start']
        
        if silence_end - silence_start > 0:
            silence_segments.append({
                'start': silence_start,
                'end': silence_end,
                'duration': round(silence_end - silence_start, 3),
                'type': 'silence'
            })
    
    # Handle the end
    if speech_segments[-1]['end'] < total_duration:
        silence_segments.append({
            'start': speech_segments[-1]['end'],
            'end': total_duration,
            'duration': round(total_duration - speech_segments[-1]['end'], 3),
            'type': 'silence'
        })
    
    return silence_segments

# Example usage:
def segment_audio(audio_file):
    """
    Process video to detect speech and silence segments
    """
    total_duration = len(AudioSegment.from_file(audio_file)) / 1000.0
    # Detect speech segments
    speech_segments = detect_speech_segments(audio_file)
    
    # Get silence segments
    silence_segments = infer_silence_segments(speech_segments, total_duration)

    segments = speech_segments + silence_segments
    segments = sorted(segments, key=lambda x: x['start'])
    
    return segments

if __name__ == "__main__":
    audio_file = "data/p2_tiktok.m4a"
    segments = segment_audio(audio_file)
    print(segments)