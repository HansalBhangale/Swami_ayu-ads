import os
import json
import time
from google import genai
from google.genai import types
from PIL import Image as PILImage
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips

# =================CONFIGURATION=================
# TODO: REPLACE WITH YOUR PROJECT DETAILS
PROJECT_ID = "mindgate-475505" 
LOCATION = "us-central1" #Currently best for video models

# SETTINGS
TOTAL_DURATION = 48    # 8 scenes × 6 seconds for complete story
CLIP_DURATION = 6      # Veo 3.1 requires 4, 6, or 8 seconds
PRODUCT_IMAGE = "swami_soap.png" # Local path to your product image
FINAL_OUTPUT_NAME = "FINAL_SWAMI_AYURVED_AD.mp4"

# Product description for the sage to explain
PRODUCT_DESCRIPTION = """
SwamiAyurved Gandhak Druti Soap - A medicated soap bar made from only SwamiAyurved Gandhak Druti.
Purely handmade with no machines. No synthetic chemicals or fragrances - absolutely skin friendly.

Highly effective in treating:
- Different types of eczemas
- Various fungal infections (tinea pedis, tinea cruris, tinea capitis, tinea corporis)
- Psoriasis, lichen planus, lichen simplex chronicus
- Scrotal dermatitis, candidiasis
- All inflammatory skin conditions
- Acute itching of urticaria and scabies

Well tolerated on skin and safe for daily use. Perfect for prophylaxis of fungal infections in rainy seasons.
"""

# Initialize Google Generative AI client
client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

# PRODUCT BRIEF (Used by the Director Agent)
PRODUCT_DESCRIPTION = """
PRODUCT: SwamiAyurved Gandhak Druti Soap.
DETAILS: Medicated soap bar made PURELY from Gandhak Druti (Sulfur based). 
Handmade, no machines. No synthetic chemicals or fragrances. 
Highly effective for eczema, fungal infections (tinea), psoriasis, itch relief.
VIBE: Ancient Indian wisdom, Ayurvedic roots, natural healing.
VISUAL CUES: Golden hour lighting, earthy textures (stone, leaf), yellow/golden tones (due to Sulfur/Gandhak).
NOTE: Gandhak means Sulphur in Sanskrit.
"""
# ===============================================


# --- HELPER: Extract Last Frame for Chaining ---
def get_last_frame_as_pil(video_path):
    """Reads the very last frame of a video file and returns a PIL Image."""
    print(f"🖼️ Extracting reference frame from {video_path}...")
    clip = VideoFileClip(video_path)
    # Get frame at the very end (duration - 0.1s to be safe)
    last_frame_np = clip.get_frame(clip.duration - 0.1) 
    pil_image = PILImage.fromarray(last_frame_np)
    return pil_image


# --- STEP 1: THE DIRECTOR AGENT (Fixed Script) ---
def plan_shoot(total_dur, clip_dur, product_desc):
    """Returns a fixed 8-scene script with exact dialogue provided by user."""
    print(f"\n🎬 DIRECTOR: Using custom 8-scene script with dialogue...")
    
    # Fixed script with user's exact dialogue
    script = [
        {
            "scene_id": 1,
            "prompt": """Cinematic wide shot of an ancient Indian ashram at golden hour. Warm sunlight filters through trees. 
            A dignified elderly sage with white beard and saffron robes sits peacefully in meditation pose. 
            Camera slowly pushes in. Sage opens eyes and looks at camera with wisdom.
            Sage: (Calm, deep voice) "For thousands of years, Ayurveda has healed the skin through nature, not chemicals."
            SFX: Birds chirping, gentle wind, distant temple bells."""
        },
        {
            "scene_id": 2,
            "prompt": """Close-up shot of the sage's weathered hands holding a small brass bowl containing bright yellow Gandhak (sulfur) powder. 
            Golden sunlight illuminates the yellow powder. Camera focuses on the vibrant color.
            Sage: (Authoritative) "This is Gandhak Druti — purified sulfur, revered in Ayurveda for its powerful skin-healing properties."
            SFX: Soft rustling of fabric, gentle breeze."""
        },
        {
            "scene_id": 3,
            "prompt": """Medium shot of sage's hands using traditional mortar and pestle to grind herbs and yellow sulfur. 
            Slow, deliberate movements showing the handmade process. Traditional brass vessels in background.
            Sage: (Mindful tone) "This soap is purely handmade, just as our ancestors prepared medicines — slowly, mindfully, without machines."
            SFX: Grinding sounds, mortar and pestle rhythm."""
        },
        {
            "scene_id": 4,
            "prompt": """Close-up of the finished golden-yellow SwamiAyurved Gandhak Druti Soap bar on natural wooden surface. 
            Fresh herbs and leaves arranged around it. Natural lighting emphasizes the pure, chemical-free nature.
            Sage: (Gentle, reassuring) "No synthetic chemicals. No artificial fragrance. Only what the skin truly understands."
            SFX: Soft wind, leaves rustling, peaceful ambience."""
        },
        {
            "scene_id": 5,
            "prompt": """Split composition: Left side shows sage holding the soap, right side shows gentle visual metaphors of healing 
            (water droplets on skin, healthy glowing skin texture). Warm, healing golden light throughout.
            Sage: (Compassionate) "It gently treats eczema, fungal infections, psoriasis, and chronic itching at the root — not just the surface."
            SFX: Gentle water sounds, healing ambience."""
        },
        {
            "scene_id": 6,
            "prompt": """Medium shot of sage in ashram courtyard during light rain. He holds the soap confidently. 
            Rain falls gently in background, creating peaceful atmosphere. Natural monsoon setting.
            Sage: (Confident, caring) "It is safe, well-tolerated, and ideal for daily use — even during the rainy season."
            SFX: Gentle rain, water droplets, peaceful monsoon sounds."""
        },
        {
            "scene_id": 7,
            "prompt": """Wide shot of sage standing in beautiful natural setting with flowing water and lush greenery. 
            He gestures peacefully, embodying balance and harmony. Golden hour lighting creates serene atmosphere.
            Sage: (Wise, philosophical) "When the skin is cared for naturally, balance is restored effortlessly."
            SFX: Flowing water, birds, gentle breeze, nature sounds."""
        },
        {
            "scene_id": 8,
            "prompt": """Close-up of sage's kind face with soft smile, holding the SwamiAyurved Gandhak Druti Soap towards camera. 
            Product clearly visible with warm golden lighting. Sage's eyes convey trust and ancient wisdom.
            Sage: (Warm, soft smile) "SwamiAyurved Gandhak Druti Soap — ancient wisdom, in your hands."
            SFX: Peaceful ashram ambience, soft chimes, fading into silence."""
        }
    ]
    
    print(f"✅ Script ready: {len(script)} scenes, {len(script) * clip_dur} seconds total")
    return script


# --- STEP 2: THE CAMERAMAN (Imagen Video with Chaining) ---
def execute_shoot(script_plan):
    print("\n🎥 CAMERAMAN: Starting shoot with visual chaining...")
    # Using Veo 3.1 for video generation (correct model ID)
    video_model_name = "veo-3.1-generate-001"
    
    generated_files = []
    previous_clip_path = None

    for i, scene in enumerate(script_plan):
        scene_num = scene['scene_id']
        current_output_file = f"temp_scene_{scene_num}.mp4"
        print(f"\n--- Shooting Scene {scene_num}/{len(script_plan)} ---")
        print(f"📝 Prompt: {scene['prompt'][:70]}...")

        # --- REFERENCE IMAGE LOGIC ---
        # NOTE: Reference images are not yet supported in Veo 3.1 on Vertex AI
        # The product will be described in the text prompt instead
        reference_images_list = []
        
        # Disabled until Vertex AI supports reference images
        # if scene_num in [1, 4, 8]:  # Opening, product showcase, and closing scenes
        #     if os.path.exists(PRODUCT_IMAGE):
        #         print(f"📸 Using product image as visual reference for Scene {scene_num}")
        #         try:
        #             # Read the image file as bytes
        #             with open(PRODUCT_IMAGE, 'rb') as f:
        #                 image_bytes = f.read()
        #             
        #             # Create an Image object from bytes
        #             image_obj = types.Image(
        #                 image_bytes=image_bytes,
        #                 mime_type='image/png'
        #             )
        #             
        #             # Create reference image object with the Image
        #             soap_reference = types.VideoGenerationReferenceImage(
        #                 image=image_obj,
        #                 reference_type="asset"  # Use as content/subject reference
        #             )
        #             reference_images_list.append(soap_reference)
        #             print(f"✅ Product image loaded successfully")
        #         except Exception as e:
        #             print(f"⚠️ Could not load product image: {e}")
        #     else:
        #         print(f"⚠️ Product image not found: {PRODUCT_IMAGE}")

        # --- GENERATION ---
        try:
            # Build the generation config for Veo 3.1
            config = types.GenerateVideosConfig(
                aspect_ratio="9:16",  # Reel format
                duration_seconds=CLIP_DURATION,  # Must be 4, 6, or 8
                generate_audio=True,  # Required for Veo 3
            )
            
            # Add reference images if we have any
            if reference_images_list:
                config.reference_images = reference_images_list
            
            # Start video generation (returns a Long-Running Operation)
            print(f"🎬 Starting video generation for Scene {scene_num}...")
            operation = client.models.generate_videos(
                model=video_model_name,
                prompt=scene['prompt'],
                config=config
            )
            
            # Poll for completion
            print(f"⏳ Waiting for video generation to complete...")
            while not operation.done:
                time.sleep(10)  # Check every 10 seconds
                operation = client.operations.get(operation)
            
            # Check if generation was successful
            if operation.result and operation.result.generated_videos:
                generated_video = operation.result.generated_videos[0]
                
                # Debug: Print what we got
                print(f"🔍 Debug - Generated video object: {type(generated_video)}")
                print(f"🔍 Debug - Has video attr: {hasattr(generated_video, 'video')}")
                
                # Try to access the video URI or bytes
                video_uri = None
                video_bytes = None
                
                if hasattr(generated_video, 'video') and generated_video.video:
                    video_obj = generated_video.video
                    print(f"� Debug - Video object: {type(video_obj)}")
                    
                    # Check for URI
                    if hasattr(video_obj, 'uri') and video_obj.uri:
                        video_uri = video_obj.uri
                        print(f"📥 Downloading video from GCS: {video_uri}")
                        
                        # Download from GCS
                        from google.cloud import storage
                        uri_parts = video_uri.replace("gs://", "").split("/", 1)
                        bucket_name = uri_parts[0]
                        blob_path = uri_parts[1]
                        
                        storage_client = storage.Client(project=PROJECT_ID)
                        bucket = storage_client.bucket(bucket_name)
                        blob = bucket.blob(blob_path)
                        blob.download_to_filename(current_output_file)
                        
                    # Check for inline bytes
                    elif hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
                        video_bytes = video_obj.video_bytes
                        print(f"💾 Saving inline video bytes ({len(video_bytes)} bytes)")
                        with open(current_output_file, 'wb') as f:
                            f.write(video_bytes)
                    else:
                        print(f"🔍 Debug - Video object attributes: {dir(video_obj)}")
                        print(f"❌ No URI or bytes found in video object")
                        break
                else:
                    print(f"🔍 Debug - Generated video attributes: {dir(generated_video)}")
                    print(f"❌ No video attribute found")
                    break
                
                print(f"✅ Scene {scene_num} wrapped. Saved to {current_output_file}")
                generated_files.append(current_output_file)
                previous_clip_path = current_output_file
            else:
                print(f"❌ Video generation failed for scene {scene_num}")
                break

        except Exception as e:
            print(f"❌ Failed to shoot scene {scene_num}: {e}")
            import traceback
            traceback.print_exc()
            break

    return generated_files


# --- STEP 3: THE EDITOR (Stitching) ---
def edit_final_reel(video_files):
    if not video_files:
        print("❌ No video files to edit.")
        return

    print(f"\n🎞️ EDITOR: Stitching {len(video_files)} clips into final Reel...")
    
    clips = [VideoFileClip(f) for f in video_files]
    final_reel = concatenate_videoclips(clips, method="compose")
    
    final_reel.write_videofile(
        FINAL_OUTPUT_NAME, 
        fps=24, 
        codec="libx264", 
        audio_codec='aac',  # Preserve Veo-generated audio
        logger=None # Reduce terminal noise
    )
    print(f"\n✨🎉 SUCCESS! Final ad ready: {FINAL_OUTPUT_NAME}")
    print(f"Total Duration: {final_reel.duration} seconds.")

    # Optional: Clean up temp files
    # for f in video_files: os.remove(f)


# ================= MAIN EXECUTION =================
if __name__ == "__main__":
    # 1. Plan
    script = plan_shoot(TOTAL_DURATION, CLIP_DURATION, PRODUCT_DESCRIPTION)
    
    if script:
        # 2. Shoot (with chaining)
        clip_filenames = execute_shoot(script)
        
        # 3. Edit
        edit_final_reel(clip_filenames)