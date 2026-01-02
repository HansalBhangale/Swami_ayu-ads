# AI Video Ad Generator

Automated video advertisement generator using Google's Veo 3.1 AI model with native dialogue generation.

## Overview

This script generates cinematic video advertisements by:
1. Creating a scene-by-scene script with dialogue
2. Generating videos for each scene using Veo 3.1
3. Stitching scenes together with preserved audio

## Features

- ✅ **AI-Generated Videos**: Uses Veo 3.1 for cinematic video generation
- ✅ **Native Dialogue**: Veo generates spoken dialogue from text prompts
- ✅ **Sound Effects**: Ambient sounds and SFX automatically generated
- ✅ **Multi-Scene Support**: Creates longer ads by stitching multiple scenes
- ✅ **Audio Preservation**: Maintains dialogue and sound effects in final video

## Requirements

- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Vertex AI API credentials configured

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Google Cloud credentials:
   ```bash
   gcloud auth application-default login
   ```

4. Update `main.py` with your project details:
   ```python
   PROJECT_ID = "your-project-id"
   LOCATION = "us-central1"
   ```

## Usage

### Basic Usage

Run the script to generate a video ad:

```bash
python main.py
```

### Configuration

Edit these settings in `main.py`:

```python
TOTAL_DURATION = 48    # Total video length in seconds
CLIP_DURATION = 6      # Duration per scene (4, 6, or 8 seconds)
PRODUCT_IMAGE = "your_product.png"  # Product image path
```

### Custom Script

The script uses a fixed 8-scene structure. To customize dialogue, edit the `plan_shoot()` function:

```python
{
    "scene_id": 1,
    "prompt": """
    Cinematic description of the scene.
    Character: "Dialogue in quotes for Veo to generate speech."
    SFX: Sound effects description.
    """
}
```

## How It Works

### 1. Script Planning

The `plan_shoot()` function returns a structured script with:
- Scene descriptions
- Dialogue (in quotation marks)
- Sound effects (SFX)

### 2. Video Generation

For each scene, the `execute_shoot()` function:
- Sends the prompt to Veo 3.1
- Polls for completion (takes 5-10 minutes per scene)
- Downloads the generated video with audio

### 3. Video Stitching

The `edit_final_reel()` function:
- Concatenates all scene videos
- Preserves audio tracks using AAC codec
- Outputs final video file

## Dialogue Generation

Veo 3.1 generates dialogue natively from text prompts. Use this format:

```
Character: (Tone) "Spoken dialogue here."
```

**Example:**
```
Sage: (Calm, wise voice) "This soap is purely handmade."
```

Veo will:
- Generate the voice audio
- Sync lip movements
- Add appropriate tone and emotion

## Output Files

- `temp_scene_1.mp4` through `temp_scene_N.mp4` - Individual scene videos
- `FINAL_[PROJECT_NAME]_AD.mp4` - Final stitched video with audio

## Limitations

- **Reference Images**: Not currently supported in Veo 3.1 on Vertex AI
  - Product appearance relies on text descriptions
  - Use detailed visual descriptions in prompts

- **Generation Time**: 5-10 minutes per 6-second scene
  - 8 scenes = 40-80 minutes total

- **Clip Duration**: Must be 4, 6, or 8 seconds (Veo 3.1 requirement)

## Troubleshooting

### "This method is only supported in the Gemini Developer client"
- You're using Vertex AI, not Gemini Developer API
- Reference images feature is disabled (expected behavior)

### "The requested feature is not supported by this model"
- Ensure you're using `veo-3.1-generate-001` model
- Check that your project has Veo 3.1 access enabled

### No audio in final video
- Verify `audio_codec='aac'` is set in `write_videofile()`
- Check individual scene files have audio before stitching

## Project Structure

```
.
├── main.py                          # Main script
├── requirements.txt                 # Python dependencies
├── swami_soap.png                  # Product image (optional)
├── temp_scene_*.mp4                # Generated scene videos
└── FINAL_SWAMI_AYURVED_AD.mp4     # Final output video
```

## Dependencies

- `google-genai` - Google Generative AI SDK
- `google-cloud-aiplatform` - Vertex AI client
- `moviepy` - Video editing and stitching
- `pillow` - Image processing
- `numpy` - Numerical operations

## License

MIT License - Feel free to modify and use for your projects.

## Credits

- **Veo 3.1**: Google's video generation model
- **Vertex AI**: Google Cloud's AI platform
- **MoviePy**: Video editing library

---

**Note**: This is a template. Customize the script, dialogue, and scenes for your specific product or service.
