import xml.etree.ElementTree as ET
from tqdm import tqdm
from src.extract_segments_from_audio import detect_speech_segments, merge_close_segments, get_silence_segments
from src.add_captions_to_fcpxml import add_captions_to_fcpxml

def process_fcpxml_with_audio_segments(input_xml_file, audio_file, output_xml_file, 
                                     min_silence_len=500, silence_thresh=-40, seek_step=1, 
                                     max_gap=0.3):
    """
    Process FCPXML file using audio segment detection to create new asset clips.
    
    Args:
        input_xml_file (str): Path to input FCPXML file
        audio_file (str): Path to audio file for audio analysis
        output_xml_file (str): Path to save output FCPXML file
        min_silence_len (int): Minimum silence length in milliseconds
        silence_thresh (int): Silence threshold in dB
        seek_step (int): Step size for silence detection in milliseconds
        max_gap (float): Maximum gap between segments to merge (in seconds)
    """
    # First, get speech segments from audio
    print("Analyzing audio segments...")
    speech_segments = detect_speech_segments(
        audio_file,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        seek_step=seek_step
    )
    speech_segments = merge_close_segments(speech_segments, max_gap=max_gap)
    silence_segments = get_silence_segments(speech_segments, 10)
    
    segments = speech_segments + silence_segments
    segments = sorted(segments, key=lambda x: x['start'])

    # Load the FCPXML file
    print("Loading FCPXML...")
    tree = ET.parse(input_xml_file)
    root = tree.getroot()
    
    # Find the timeline/sequence
    timeline = root.find(".//sequence")
    if timeline is None:
        raise ValueError("No sequence found in FCPXML file")
    
    # Store original asset clips
    original_clips = []
    for clip in timeline.findall(".//asset-clip"):
        original_clips.append({
            'element': clip,
            'offset': float(clip.get("offset", "0s")[:-1]),
            'start': eval(clip.get("start", "0s")[:-1]),
            'ref': clip.get("ref"),
            'name': clip.get("name"),
            'duration': eval(clip.get("duration", "0s")[:-1])
        })
    
    # Remove existing asset clips from spine
    spine = timeline.find(".//spine")
    if spine is not None:
        for clip in spine.findall(".//asset-clip"):
            spine.remove(clip)
    
    # Create new asset clips based on speech segments
    print("Creating new asset clips based on speech segments...")
    for segment in tqdm(segments):
        # Find the corresponding original clip that contains this segment
        for orig_clip in original_clips:
            if (orig_clip['offset'] <= segment['start'] < 
                (orig_clip['offset'] + orig_clip['duration'])):
                
                # Create new asset clip
                new_clip = ET.Element("asset-clip")
                new_clip.set("ref", orig_clip['ref'])
                new_clip.set("offset", f"{segment['start']}s")
                new_clip.set("duration", f"{segment['duration']}s")
                new_clip.set("name", f"{orig_clip['name']}")
                new_clip.set("start", f"{segment['start']}s") #TODO: correct to include multiclip timeline
                conform_rate = ET.SubElement(new_clip, "conform-rate")
                conform_rate.set("scaleEnabled", "0")
                conform_rate.set("srcFrameRate", "60")
                
                """
                # Copy relevant child elements from original clip
                for child in orig_clip['element']:
                    if child.tag in ['audio', 'video']:
                        new_child = deepcopy(child)
                        new_clip.append(new_child)
                """
                # Add the new clip to the spine
                if spine is not None:
                    spine.append(new_clip)
                break
    
    """
    # Save the modified FCPXML
    print("Saving modified FCPXML...")
    pretty_xml = prettify_xml(root)
    with open(output_xml_file, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)
    """
    # Format the XML with proper indentation
    ET.indent(tree, space="    ")
    tree.write(output_xml_file, encoding="utf-8", xml_declaration=True)
    return "Audio segments processed and FCPXML updated successfully!"

def combine_audio_processing_and_captions(audio_file, srt_file, input_xml_file, 
                                        intermediate_xml_file, output_xml_file):
    """
    Complete workflow combining audio segment processing and caption addition.
    
    Args:
        video_path (str): Path to video file
        srt_file (str): Path to SRT file
        input_xml_file (str): Path to input FCPXML
        intermediate_xml_file (str): Path for intermediate FCPXML
        output_xml_file (str): Path for final output FCPXML
    """
    # First process the audio segments
    print("Processing audio segments...")
    process_fcpxml_with_audio_segments(
        input_xml_file,
        audio_file,
        intermediate_xml_file
    )
    
    # Then add captions
    print("Adding captions...")
    add_captions_to_fcpxml(srt_file, intermediate_xml_file, output_xml_file)
    
    return "Processing complete!"

# Example usage:
if __name__ == "__main__":

    srt_file = "p2_tiktok.srt"
    audio_file = "data/p2_tiktok.m4a"
    input_xml_file = "p2_tiktok_initial.fcpxml"
    intermediate_xml_file = "p2_tiktok_out2.fcpxml"
    output_xml_file = "p2_tiktok_out2.fcpxml"
    combine_audio_processing_and_captions(audio_file, srt_file, input_xml_file, 
                                        intermediate_xml_file, output_xml_file)

    #TODO: fix the last clip
    #TODO: Add audio role to the silent clips
