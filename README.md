# Venice Pricing & Model List

This project fetches model data from the Venice.ai API and generates interactive HTML tables for comparing pricing, capabilities, and constraints of Text, Image, and Video models.

## Usage

### 1. Update Data & Generate Lists
Run the automation script to fetch the latest data and rebuild the HTML files:

```bash
./scripts/update_all.sh
```

### 2. View Results
Open `output/index.html` in your web browser to navigate the generated lists:
- **Text Models**: Pricing, context window, capabilities (Reasoning, Code, etc.)
- **Image Models**: Generation costs, upscale pricing, constraints.
- **Video Models**: Resolution, duration, and audio support.

## Project Structure

- `data/`: JSON data fetched from the API.
- `output/`: Generated HTML files.
- `scripts/`: Python scripts for fetching data and generating HTML.

## Requirements
- Python 3
