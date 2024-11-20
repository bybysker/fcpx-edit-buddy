import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import pysrt
from tqdm import tqdm

def parse_srt(srt_path: str):
    subtitles = pysrt.open(srt_path)
    segments = []
    for subtitle in subtitles:
        start = (subtitle.start.hours * 3600) + (subtitle.start.minutes * 60) + subtitle.start.seconds
        end = (subtitle.end.hours * 3600) + (subtitle.end.minutes * 60) + subtitle.end.seconds
        duration = end - start
        segments.append({
            'start': start,
            'end': end,
            'duration': duration,
            'text': subtitle.text
        })
    return segments

# Load the .fcpxml file, parse it, and keep <resources> intact
def load_fcpxml(fcpxml_path: str):
    tree = ET.parse(fcpxml_path)
    root = tree.getroot()
    return tree, root

def add_captions_to_fcpxml(srt_file, input_xml_file, output_xml_file):
    """
    Add captions from an SRT file to an FCPXML file and save to a new file.
    
    Args:
        srt_file (str): Path to input SRT file
        input_xml_file (str): Path to input FCPXML file 
        output_xml_file (str): Path to save output FCPXML file
    """
    segments = parse_srt(srt_file)

    tree, root = load_fcpxml(input_xml_file)

    timeline = root.find(".//sequence")

    asset_clips = timeline.findall(".//asset-clip")
    len(asset_clips)

    for asset_clip in tqdm(asset_clips):
        for i, segment in tqdm(enumerate(segments)):
            if eval(asset_clip.get("offset")[:-1]) <= segment['start'] and segment['start'] <= eval(asset_clip.get("offset")[:-1]) + eval(asset_clip.get("duration")[:-1]):
                # add the segment to the asset_clip as a title
                title = ET.SubElement(asset_clip, "title")
                title.set("ref", "title_effect")
                title.set("offset", str(segment['start'])+"s")
                title.set("duration", str(segment['duration'])+"s")
                title.set("name", segment['text'][:30])
                title.set("lane", "3")

                caption_position = ET.SubElement(title, "param")
                caption_position.set("name", "Position")
                caption_position.set("key", "9999/999166631/999166633/1/100/101")
                caption_position.set("value", "0 -450")

                text = ET.SubElement(title, "text")
                text_style = ET.SubElement(text, "text-style")
                text_style.set("ref", "ts" + str(i))
                text_style.text = segment['text']

                text_style_def = ET.SubElement(title, "text-style-def")
                text_style_def.set("id", "ts" + str(i))

                text_style_in_style_def = ET.SubElement(text_style_def, "text-style")
                text_style_in_style_def.set("font", "Noteworthy")
                text_style_in_style_def.set("fontSize", "30")
                text_style_in_style_def.set("fontColor", "1 0.7 0 1")
                text_style_in_style_def.set("bold", "1")
                text_style_in_style_def.set("shadowColor", "0 0 0 0.75")
                text_style_in_style_def.set("shadowOffset", "5 315")
                text_style_in_style_def.set("alignment", "center")

    # Format the XML with proper indentation
    ET.indent(tree, space="    ")
    tree.write(output_xml_file, encoding="utf-8", xml_declaration=True)

    return print("Captions added successfully!")



if __name__ == "__main__":
    srt_file = "p2_tiktok.srt"
    input_xml_file = "p2_tiktok_initial.fcpxml"
    output_xml_file = "p2_tiktok_out.fcpxml"
    add_captions_to_fcpxml(srt_file, input_xml_file, output_xml_file)