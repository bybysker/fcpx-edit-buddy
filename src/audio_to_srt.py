import mlx_whisper

def create_srt_from_transcription(transcription_dict, output_file="output.srt"):
    """
    Convert a transcription dictionary to SRT format and save to file.
    
    Args:
        transcription_dict (dict): Dictionary containing transcription data
        output_file (str): Path to save the SRT file
    """
    def format_timestamp(seconds):
        """Convert seconds to SRT timestamp format: HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        milliseconds = int(round((seconds - int(seconds)) * 1000))
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

    # Extract and sort segments
    segments = transcription_dict.get('segments', [])
    segments.sort(key=lambda x: x.get('start', 0))

    # Process segments to fix overlaps
    processed_segments = []
    previous_end = 0
    
    for segment in segments:
        start_time = segment.get('start', 0)
        end_time = segment.get('end', 0)
        
        # Adjust start_time if it overlaps with previous segment
        if start_time <= previous_end:
            start_time = previous_end + 0.001  # Add 1ms gap
        
        # Ensure end_time is after start_time
        if end_time <= start_time:
            end_time = start_time + 0.001  # Minimum duration of 1ms
            
        # Update previous_end for next iteration
        previous_end = end_time
        
        processed_segments.append({
            'start': start_time,
            'end': end_time,
            'text': segment.get('text', '').strip()
        })

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        empty=0
        for i, segment in enumerate(processed_segments, 1):
            text = segment['text']
            if not text:  # Skip empty segments
                empty+=1
                continue
                
            srt_segment = (
                f"{i-empty}\n"
                f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n"
                f"{text}\n\n"
            )
            f.write(srt_segment)
    
    print(f"SRT file '{output_file}' created successfully.")

speech_file = "./data/vlog_rotter_audio.m4a"
transcription = mlx_whisper.transcribe(speech_file, path_or_hf_repo="mlx-community/whisper-large-v3-mlx", initial_prompt="Mes péripéties à rotterdam: mon accueil, recherche de logement et de taff, mon état mental")
create_srt_from_transcription(transcription, output_file="vlog_rotter2.srt")