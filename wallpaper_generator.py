"""
Generative Art Wallpaper Generator
===================================
Creates beautiful algorithmic wallpapers using flow fields,
fractals, and procedural patterns.

Usage:
    python wallpaper_generator.py [--style STYLE] [--width W] [--height H] [--output FILE]

Styles available:
    - flow_field (default)
    - plasma
    - voronoi
    - nebula
"""

import argparse
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image


def create_color_palette(seed: int | None = None) -> list[tuple[int, int, int]]:
    """Generate a harmonious color palette."""
    if seed:
        random.seed(seed)
    
    # Base hue with analogous colors
    base_hue = random.random()
    palette = []
    
    for i in range(5):
        hue = (base_hue + i * 0.1) % 1.0
        saturation = 0.6 + random.random() * 0.4
        lightness = 0.3 + random.random() * 0.4
        
        # HSL to RGB conversion
        rgb = hsl_to_rgb(hue, saturation, lightness)
        palette.append(rgb)
    
    return palette


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """Convert HSL to RGB color."""
    if s == 0:
        r = g = b = l
    else:
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return (int(r * 255), int(g * 255), int(b * 255))


def generate_flow_field(width: int, height: int, seed: int | None = None) -> np.ndarray:
    """
    Generate a flow field wallpaper using Perlin-like noise.
    Creates organic, flowing patterns reminiscent of wind or water.
    """
    if seed:
        np.random.seed(seed)
        random.seed(seed)
    
    # Create image array
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    palette = create_color_palette(seed)
    
    # Background gradient
    for y in range(height):
        t = y / height
        bg_color = interpolate_color(palette[0], palette[1], t)
        img_array[y, :] = bg_color
    
    # Flow field parameters
    scale = 0.005 + random.random() * 0.01
    num_particles = 3000
    steps_per_particle = 100
    
    # Generate flow field angles using simplex-like noise
    angles = np.zeros((height // 10 + 1, width // 10 + 1))
    for gy in range(angles.shape[0]):
        for gx in range(angles.shape[1]):
            angles[gy, gx] = noise_2d(gx * scale * 50, gy * scale * 50) * math.pi * 4
    
    # Draw flow lines
    for _ in range(num_particles):
        x = random.random() * width
        y = random.random() * height
        color_idx = random.randint(2, 4)
        color = palette[color_idx]
        
        for step in range(steps_per_particle):
            gx = int(x / 10) % angles.shape[1]
            gy = int(y / 10) % angles.shape[0]
            angle = angles[gy, gx]
            
            # Move particle
            x += math.cos(angle) * 2
            y += math.sin(angle) * 2
            
            # Draw with fading alpha
            if 0 <= x < width and 0 <= y < height:
                alpha = 1 - (step / steps_per_particle) * 0.7
                px, py = int(x), int(y)
                existing = img_array[py, px]
                blended = tuple(int(existing[i] * (1 - alpha * 0.3) + color[i] * alpha * 0.3) for i in range(3))
                img_array[py, px] = blended
            else:
                break
    
    return img_array


def generate_plasma(width: int, height: int, seed: int | None = None) -> np.ndarray:
    """
    Generate a plasma/lava lamp style wallpaper.
    Uses overlapping sine waves to create psychedelic patterns.
    """
    if seed:
        np.random.seed(seed)
        random.seed(seed)
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    palette = create_color_palette(seed)
    
    # Plasma generation using sine wave interference
    freq1 = 0.02 + random.random() * 0.03
    freq2 = 0.03 + random.random() * 0.02
    freq3 = 0.01 + random.random() * 0.02
    phase = random.random() * math.pi * 2
    
    for y in range(height):
        for x in range(width):
            # Multiple overlapping waves
            v1 = math.sin(x * freq1 + phase)
            v2 = math.sin(y * freq2)
            v3 = math.sin((x + y) * freq3)
            v4 = math.sin(math.sqrt((x - width/2)**2 + (y - height/2)**2) * 0.02)
            
            # Combine waves
            value = (v1 + v2 + v3 + v4) / 4
            
            # Map to color palette
            t = (value + 1) / 2  # Normalize to 0-1
            color_idx = t * (len(palette) - 1)
            idx1 = int(color_idx)
            idx2 = min(idx1 + 1, len(palette) - 1)
            frac = color_idx - idx1
            
            color = interpolate_color(palette[idx1], palette[idx2], frac)
            img_array[y, x] = color
    
    return img_array


def generate_voronoi(width: int, height: int, seed: int | None = None) -> np.ndarray:
    """
    Generate a Voronoi diagram wallpaper.
    Creates a cellular/crystalline pattern.
    """
    if seed:
        np.random.seed(seed)
        random.seed(seed)
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    palette = create_color_palette(seed)
    
    # Generate random points
    num_points = 50 + random.randint(0, 50)
    points = [(random.randint(0, width), random.randint(0, height)) for _ in range(num_points)]
    point_colors = [palette[i % len(palette)] for i in range(num_points)]
    
    # For each pixel, find closest point
    for y in range(height):
        for x in range(width):
            min_dist = float('inf')
            closest_idx = 0
            
            for i, (px, py) in enumerate(points):
                dist = (x - px) ** 2 + (y - py) ** 2
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = i
            
            # Color based on distance for gradient effect
            base_color = point_colors[closest_idx]
            dist_factor = min(1.0, math.sqrt(min_dist) / 150)
            
            # Darken towards edges
            color = tuple(int(c * (1 - dist_factor * 0.3)) for c in base_color)
            img_array[y, x] = color
    
    return img_array


def generate_nebula(width: int, height: int, seed: int | None = None) -> np.ndarray:
    """
    Generate a cosmic nebula wallpaper.
    Creates a space-like atmosphere with stars and gas clouds.
    """
    if seed:
        np.random.seed(seed)
        random.seed(seed)
    
    img_array = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Dark space background
    for y in range(height):
        for x in range(width):
            noise_val = noise_2d(x * 0.003, y * 0.003)
            dark = int(5 + noise_val * 10)
            img_array[y, x] = (dark, dark, int(dark * 1.2))
    
    # Create nebula clouds
    nebula_colors = [
        (180, 100, 200),  # Purple
        (100, 150, 220),  # Blue
        (220, 120, 150),  # Pink
        (100, 200, 180),  # Teal
    ]
    
    for _ in range(3):
        cx, cy = random.randint(0, width), random.randint(0, height)
        radius = random.randint(200, 500)
        color = random.choice(nebula_colors)
        
        for y in range(max(0, cy - radius), min(height, cy + radius)):
            for x in range(max(0, cx - radius), min(width, cx + radius)):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if dist < radius:
                    noise_val = noise_2d(x * 0.01, y * 0.01)
                    alpha = (1 - dist / radius) * 0.4 * (0.5 + noise_val * 0.5)
                    existing = img_array[y, x]
                    blended = tuple(int(existing[i] + color[i] * alpha) for i in range(3))
                    img_array[y, x] = tuple(min(255, c) for c in blended)
    
    # Add stars
    for _ in range(500):
        x, y = random.randint(0, width - 1), random.randint(0, height - 1)
        brightness = random.randint(150, 255)
        size = random.choice([1, 1, 1, 2])
        
        for dy in range(-size, size + 1):
            for dx in range(-size, size + 1):
                if 0 <= x + dx < width and 0 <= y + dy < height:
                    dist = abs(dx) + abs(dy)
                    star_bright = max(0, brightness - dist * 50)
                    existing = img_array[y + dy, x + dx]
                    img_array[y + dy, x + dx] = tuple(min(255, existing[i] + star_bright) for i in range(3))
    
    return img_array


def noise_2d(x: float, y: float) -> float:
    """Simple 2D noise function using sine combinations."""
    return (math.sin(x * 1.5 + y * 2.3) * 
            math.cos(x * 0.7 - y * 1.8) * 
            math.sin(x * 0.3 + y * 0.9) + 1) / 2


def interpolate_color(c1: tuple, c2: tuple, t: float) -> tuple:
    """Linearly interpolate between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


STYLE_GENERATORS = {
    'flow_field': generate_flow_field,
    'plasma': generate_plasma,
    'voronoi': generate_voronoi,
    'nebula': generate_nebula,
}


def main():
    parser = argparse.ArgumentParser(
        description='Generate beautiful algorithmic wallpapers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python wallpaper_generator.py
    python wallpaper_generator.py --style plasma --width 2560 --height 1440
    python wallpaper_generator.py --style nebula --seed 42 --output cosmic.png
        """
    )
    parser.add_argument('--style', choices=STYLE_GENERATORS.keys(), 
                        default='flow_field', help='Art style to generate')
    parser.add_argument('--width', type=int, default=1920, help='Image width')
    parser.add_argument('--height', type=int, default=1080, help='Image height')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    parser.add_argument('--output', type=str, default=None, help='Output filename')
    
    args = parser.parse_args()
    
    # Generate the wallpaper
    print(f"🎨 Generating {args.style} wallpaper ({args.width}x{args.height})...")
    
    generator = STYLE_GENERATORS[args.style]
    img_array = generator(args.width, args.height, args.seed)
    
    # Create and save image
    img = Image.fromarray(img_array, 'RGB')
    
    output_path = args.output or f"wallpaper_{args.style}_{args.width}x{args.height}.png"
    img.save(output_path, 'PNG')
    
    print(f"✅ Saved to: {output_path}")
    print(f"   File size: {Path(output_path).stat().st_size / 1024:.1f} KB")


if __name__ == '__main__':
    main()
