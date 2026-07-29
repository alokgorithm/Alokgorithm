"""
prep_photo.py — Prepare a portrait photo for ASCII conversion.
1. Remove background with rembg
2. Boost local contrast with CLAHE
3. Composite onto pure white
4. Save as grayscale source-prepped.png
"""
import sys
import numpy as np
from PIL import Image
from pathlib import Path

def main():
    if len(sys.argv) < 2:
        print("Usage: python prep_photo.py <source-photo>")
        sys.exit(1)

    src_path = sys.argv[1]
    print(f"Loading {src_path}...")
    img = Image.open(src_path).convert("RGBA")

    # Step 1: Remove background
    print("Removing background...")
    try:
        from rembg import remove
        img_nobg = remove(img)
    except ImportError:
        print("  rembg not available, skipping bg removal")
        img_nobg = img

    # Step 2: Composite onto white
    print("Compositing onto white background...")
    white_bg = Image.new("RGBA", img_nobg.size, (255, 255, 255, 255))
    composite = Image.alpha_composite(white_bg, img_nobg)
    gray = composite.convert("L")

    # Step 3: CLAHE contrast boost
    print("Applying CLAHE contrast enhancement...")
    try:
        import cv2
        arr = np.array(gray)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        arr = clahe.apply(arr)
        gray = Image.fromarray(arr)
    except ImportError:
        print("  cv2 not available, skipping CLAHE")

    # Save
    out_path = Path(src_path).parent / "source-prepped.png"
    gray.save(out_path)
    print(f"Saved {out_path} ({gray.size[0]}x{gray.size[1]})")

if __name__ == "__main__":
    main()
