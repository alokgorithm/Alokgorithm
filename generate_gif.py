import base64
from PIL import Image, ImageDraw
import io
import math
import random
import sys

def main():
    print("Loading image...")
    try:
        img = Image.open('ChatGPT Image Jul 27, 2026, 08_51_15 PM.png').convert('RGB')
    except Exception as e:
        print(f"Error loading image: {e}")
        sys.exit(1)

    COLS, ROWS = 80, 100
    PIXEL_SIZE = 3
    WIDTH = COLS * PIXEL_SIZE
    HEIGHT = ROWS * PIXEL_SIZE

    print(f"Resizing to {COLS}x{ROWS}...")
    img_small = img.resize((COLS, ROWS), resample=Image.NEAREST)
    pixels = img_small.load()

    print("Calculating animation sequence...")
    indices = []
    cx, cy = COLS / 2, ROWS / 2
    for y in range(ROWS):
        for x in range(COLS):
            dist = math.sqrt((x - cx)**2 + (y - cy)**2)
            priority = dist + random.uniform(0, 4)
            indices.append({'x': x, 'y': y, 'p': priority})

    indices.sort(key=lambda item: item['p'])

    frames = []
    BG_COLOR = (13, 17, 23)  # GitHub dark mode background match

    current_frame = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(current_frame)

    batch_size = 120
    total_pixels = COLS * ROWS

    # Add a few blank frames at start
    for _ in range(5):
        frames.append(current_frame.copy())

    print("Rendering frames...")
    for i in range(0, total_pixels, batch_size):
        batch = indices[i:i+batch_size]
        for p in batch:
            x, y = p['x'], p['y']
            color = pixels[x, y]
            px_x = x * PIXEL_SIZE
            px_y = y * PIXEL_SIZE
            draw.rectangle([px_x, px_y, px_x + PIXEL_SIZE - 1, px_y + PIXEL_SIZE - 1], fill=color)
        
        # We append a frame for every batch
        frames.append(current_frame.copy())

    # Add pause frames at the end
    print("Adding end pause...")
    for _ in range(40):
        frames.append(current_frame.copy())

    print(f"Saving portrait.gif with {len(frames)} frames...")
    frames[0].save('portrait.gif', save_all=True, append_images=frames[1:], optimize=False, duration=30, loop=0)
    print("Saved portrait.gif successfully!")

if __name__ == "__main__":
    main()
