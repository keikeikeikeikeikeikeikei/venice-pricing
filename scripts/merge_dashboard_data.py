#!/usr/bin/env python3
"""
Merge all model data JSONs into a single JS file for the dashboard.
Prioritizes enriched data (like video with pricing) if available.
"""
import json
import pathlib

# Paths
BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"

def load_json(filename):
    path = DATA_DIR / filename
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def main():
    print("🔄 Merging data for dashboard...")
    
    # Load data
    text_models = load_json("venice_models_text.json")
    image_models = load_json("venice_models_image.json")
    
    # Try to load enriched video details first
    video_models = load_json("venice_models_video_with_pricing.json")
    if not video_models:
        print("⚠️  Enriched video data not found, falling back to basic data.")
        video_models = load_json("venice_models_video.json")
    
    # Other types
    audio_models = load_json("venice_models_audio.json") # Should assume exist or empty
    if not audio_models: audio_models = []
    
    # Combine (reusing the structure from fetch_venice_pricing.py)
    models_by_type = {
        "text": text_models,
        "image": image_models,
        "video": video_models,
        # Add others if needed, though dashboard primarily uses these 3
    }
    
    # Save to JS
    js_filename = DATA_DIR / "all_models.js"
    with open(js_filename, 'w', encoding='utf-8') as f:
        f.write("window.veniceModels = ")
        json.dump(models_by_type, f, indent=2, ensure_ascii=False)
        f.write(";")
        
    print(f"✅ Generated {js_filename} with:")
    print(f"  - {len(text_models)} text models")
    print(f"  - {len(image_models)} image models")
    print(f"  - {len(video_models)} video models (Pricing included: {any('pricing' in m for m in video_models)})")

if __name__ == "__main__":
    main()
