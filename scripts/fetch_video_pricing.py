#!/usr/bin/env python3
"""
Fetch video models with pricing from Venice API.
This script fetches all video models and gets pricing quotes for each one.
"""
import json
import pathlib
import requests
import time

# API Configuration
API_BASE = "https://api.venice.ai/api/v1"
MODELS_ENDPOINT = f"{API_BASE}/models?type=video"
QUOTE_ENDPOINT = f"{API_BASE}/video/quote"

# Paths
BASE_DIR = pathlib.Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"
OUTPUT_FILE = DATA_DIR / "venice_models_video_with_pricing.json"

def get_default_quote_params(model):
    """
    Generate default quote parameters for a model based on its constraints.
    """
    model_id = model['id']
    constraints = model.get('model_spec', {}).get('constraints', {})
    model_type = constraints.get('model_type', 'text-to-video')
    
    # Base parameters
    params = {
        'model': model_id,
        'prompt': 'quote'
    }
    
    # Add resolution if available
    resolutions = constraints.get('resolutions', [])
    if resolutions:
        # Use the lowest resolution for quote
        params['resolution'] = resolutions[-1]  # Usually 480p or 720p
    
    # Add duration
    durations = constraints.get('durations', [])
    if durations:
        # Use the shortest duration
        params['duration'] = durations[0]
    
    # Add aspect ratio if available
    aspect_ratios = constraints.get('aspect_ratios', [])
    if aspect_ratios:
        params['aspect_ratio'] = aspect_ratios[0]
    
    # Add image_url for image-to-video models
    if 'image-to-video' in model_type:
        params['image_url'] = 'https://venice.ai/favicon.ico'
    
    # Add audio parameter if configurable
    if constraints.get('audio_configurable'):
        params['audio'] = constraints.get('audio', False)
    
    return params

def fetch_video_models():
    """Fetch all video models from the API."""
    print(f"Fetching video models from {MODELS_ENDPOINT}...")
    try:
        response = requests.get(MODELS_ENDPOINT)
        response.raise_for_status()
        response_data = response.json()
        # Extract models from the 'data' field
        models = response_data.get('data', response_data)
        if isinstance(models, list):
            print(f"✅ Fetched {len(models)} video models")
            return models
        else:
            print(f"❌ Unexpected response format")
            return []
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def get_model_quote(model):
    """Get pricing quote for a specific model."""
    model_id = model['id']
    params = get_default_quote_params(model)
    
    try:
        response = requests.post(QUOTE_ENDPOINT, json=params)
        response.raise_for_status()
        quote_data = response.json()
        price = quote_data.get('quote')
        print(f"  💰 {model_id}: ${price}")
        return price
    except Exception as e:
        print(f"  ⚠️  {model_id}: Failed to get quote - {e}")
        return None

def main():
    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)
    
    # Fetch models
    models = fetch_video_models()
    if not models:
        print("No models found. Exiting.")
        return
    
    # Get pricing for each model
    print(f"\n📊 Fetching pricing for {len(models)} models...")
    enriched_models = []
    
    for i, model in enumerate(models, 1):
        model_name = model.get('model_spec', {}).get('name', model['id'])
        print(f"\n[{i}/{len(models)}] {model_name}")
        
        # Get quote
        price = get_model_quote(model)
        
        # Add pricing info to model
        model_with_pricing = model.copy()
        if price is not None:
            model_with_pricing['pricing'] = {
                'base_price_usd': price,
                'quote_params': get_default_quote_params(model)
            }
        
        enriched_models.append(model_with_pricing)
        
        # Rate limiting - be nice to the API
        if i < len(models):
            time.sleep(0.5)
    
    # Save enriched data
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(enriched_models, f, indent=2)
    
    print(f"\n✅ Saved {len(enriched_models)} models with pricing to {OUTPUT_FILE}")
    
    # Print summary
    models_with_pricing = [m for m in enriched_models if 'pricing' in m]
    print(f"\n📈 Summary:")
    print(f"  Total models: {len(enriched_models)}")
    print(f"  Models with pricing: {len(models_with_pricing)}")
    print(f"  Models without pricing: {len(enriched_models) - len(models_with_pricing)}")
    
    # Show price range
    if models_with_pricing:
        prices = [m['pricing']['base_price_usd'] for m in models_with_pricing]
        print(f"\n💵 Price range: ${min(prices):.2f} - ${max(prices):.2f}")

if __name__ == '__main__':
    main()
