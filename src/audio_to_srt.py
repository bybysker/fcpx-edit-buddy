import mlx_whisper

def create_srt_from_transcription(transcription_dict, output_file="output.srt"):
    """
    Convert a transcription dictionary to SRT format and save to file
    
    Args:
        transcription_dict (dict): Dictionary containing transcription data
        output_file (str): Path to save the SRT file
    """
    def format_timestamp(seconds):
        """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    # Extract segments from the transcription
    segments = transcription_dict.get('segments', [])
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            # Get start and end times
            start_time = segment.get('start', 0)
            end_time = segment.get('end', 0)
            
            # Get text
            text = segment.get('text', '').strip()
            
            # Format in SRT
            srt_segment = (
                f"{i}\n"
                f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n"
                f"{text}\n\n"
            )
            
            f.write(srt_segment)

# Example usage:
speech_file = "./data/vlog_rotter.m4a"
transcription = mlx_whisper.transcribe(speech_file)
create_srt_from_transcription(transcription)