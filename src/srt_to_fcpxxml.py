import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
import pysrt

def parse_srt(srt_path):
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

def format_duration(seconds):
    return f"{int(seconds * 1000)}/3000s"

def create_caption_element(caption_id, subtitle, ts_id):
    caption = ET.Element('caption', {
        'lane': "1",
        'offset': "0s",
        'name': subtitle['text'],
        'start': f"{subtitle['start']}s",
        'duration': format_duration(subtitle['duration']),
        'role': "SRT?captionFormat=SRT.fr-FR"
    })
    
    text = ET.SubElement(caption, 'text', {'placement': "bottom"})
    text_style = ET.SubElement(text, 'text-style', {'ref': ts_id})
    text_style.text = subtitle['text']
    
    text_style_def = ET.SubElement(caption, 'text-style-def', {'id': ts_id})
    ET.SubElement(text_style_def, 'text-style', {
        'font': ".AppleSystemUIFont",
        'fontSize': "10",
        'fontFace': "Regular",
        'fontColor': "1 0.843 0 1",
        'backgroundColor': "0 0 0 0"
    })
    
    return caption

def create_asset_clip_element(clip_id, subtitle, ts_id):
    asset_clip = ET.Element('asset-clip', {
        'ref': "r2",
        'offset': "0s",
        'name': f"Subtitle Clip {clip_id}",
        'start': f"{subtitle['start']}s",
        'duration': format_duration(subtitle['duration']),
        'format': "r1",
        'tcFormat': "NDF",
        'audioRole': "dialogue"
    })
    
    ET.SubElement(asset_clip, 'conform-rate', {'scaleEnabled': "0"})
    
    caption = create_caption_element(clip_id, subtitle, f"ts{clip_id}")
    asset_clip.append(caption)
    
    return asset_clip

def prettify_xml(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def generate_fcpxml(srt_file, output_xml):
    subtitles = parse_srt(srt_file)
    
    fcpxml = ET.Element('fcpxml', {'version': "1.10"})
    resources = ET.SubElement(fcpxml, 'resources')
    
    library = ET.SubElement(fcpxml, 'library', {'location': "file:///Users/byby/Movies/Bybysker%20TV.fcpbundle/"})
    event = ET.SubElement(library, 'event', {'name': "youtube", 'uid': "D3A94D22-5900-4F79-BF7E-FEEF9E5EE92D"})
    project = ET.SubElement(event, 'project', {'name': "vlog_rotter", 'uid': "419AF4A1-84A0-4B0F-891E-354234E5DA57", 'modDate': "2024-11-11 18:34:39 +0100"})
    sequence = ET.SubElement(project, 'sequence', {
        'format': "r1",
        'duration': "3142200/3000s",
        'tcStart': "0s",
        'tcFormat': "NDF",
        'audioLayout': "stereo",
        'audioRate': "48k"
    })
    spine = ET.SubElement(sequence, 'spine')
    
    for idx, subtitle in enumerate(subtitles, start=1):
        asset_clip = create_asset_clip_element(idx, subtitle, f"ts{idx}")
        spine.append(asset_clip)
    
    pretty_xml = prettify_xml(fcpxml)
    with open(output_xml, 'w', encoding='utf-8') as f:
        f.write(pretty_xml)

if __name__ == "__main__":
    srt_input = "output.srt"
    xml_output = "generated_output.fcpxml"
    generate_fcpxml(srt_input, xml_output)