# 🎨 Generative Wallpapers

Create beautiful algorithmic desktop wallpapers using Python.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Features

Generate stunning wallpapers in 4 unique styles:

| Style | Description |
|-------|-------------|
| **Flow Field** | Organic, flowing patterns like wind or water currents |
| **Plasma** | Psychedelic lava-lamp style color waves |
| **Voronoi** | Cellular/crystalline geometric patterns |
| **Nebula** | Cosmic space scenes with stars and gas clouds |

## Installation

```bash
pip install numpy pillow
```

## Usage

```bash
# Generate default flow field wallpaper (1920x1080)
python wallpaper_generator.py

# Generate plasma style at 4K resolution
python wallpaper_generator.py --style plasma --width 3840 --height 2160

# Generate reproducible nebula with seed
python wallpaper_generator.py --style nebula --seed 42 --output cosmic.png

# Quick voronoi wallpaper
python wallpaper_generator.py --style voronoi
```

## Options

| Argument | Default | Description |
|----------|---------|-------------|
| `--style` | `flow_field` | Art style (`flow_field`, `plasma`, `voronoi`, `nebula`) |
| `--width` | `1920` | Output image width in pixels |
| `--height` | `1080` | Output image height in pixels |
| `--seed` | Random | Seed for reproducible results |
| `--output` | Auto | Custom output filename |

## Examples

```bash
# 1080p wallpaper collection
python wallpaper_generator.py --style flow_field --seed 1
python wallpaper_generator.py --style plasma --seed 2
python wallpaper_generator.py --style voronoi --seed 3
python wallpaper_generator.py --style nebula --seed 4
```

## License

MIT License - feel free to use these wallpapers however you like!
