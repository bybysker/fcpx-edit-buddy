# FCPX Edit Buddy

FCPX Edit Buddy is a tool designed to streamline the video editing workflow by automating the transcription of audio to subtitles and integrating these subtitles seamlessly into Final Cut Pro X (FCPX) projects. Leveraging machine learning for accurate transcription and robust scripting for XML manipulation, FCPX Edit Buddy ensures efficient and precise subtitle integration, enhancing the overall editing experience.

## Features

- **Automatic Transcription**: Converts audio files to text using `mlx-whisper`.
- **Subtitle Generation**: Transforms transcriptions into SRT (SubRip Subtitle) format, ensuring each subtitle segment represents a complete sentence for better readability.
- **FCPXML Integration**: Inserts generated subtitles into FCPX projects by modifying FCPXML files.
- **Customizable Output**: Allows customization of subtitle formatting and placement.
- **Easy Installation**: Simple setup with all dependencies managed via `requirements.txt`.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Transcribe Audio to SRT](#transcribe-audio-to-srt)
  - [Integrate SRT into FCPX](#integrate-srt-into-fcpx)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/fcpx-edit-buddy.git
   cd fcpx-edit-buddy
   ```

2. **Set Up a Virtual Environment**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   **Note**: Ensure that `pip` is up to date. You can upgrade `pip` using:

   ```bash
   pip install --upgrade pip
   ```

## Usage

### Transcribe Audio to SRT

The `audio_to_srt.py` script handles the transcription of audio files into SRT format.

1. **Prepare Your Audio File**

   Place your audio file (e.g., `vlog_rotter.m4a`) in the `data/` directory.

2. **Run the Transcription Script**

   ```bash
   python src/audio_to_srt.py
   ```

   This will generate an `output.srt` file in the project root, with each subtitle segment corresponding to a complete sentence for improved clarity.

### Integrate SRT into FCPX

The `srt_to_fcpxxml.py` script integrates the generated SRT subtitles into an FCPX project.

1. **Prepare Your FCPXML Template**

   Ensure you have a template FCPXML file (`template.fcpxml`) in the project directory.

2. **Run the Integration Script**

   ```bash
   python src/srt_to_fcpxxml.py
   ```

   This will generate a `generated_output.fcpxml` file with the integrated subtitles.

3. **Import into Final Cut Pro X**

   - Open Final Cut Pro X.
   - Import the `generated_output.fcpxml` file to apply the subtitles to your project.

## Project Structure
