from PIL import Image, ImageDraw
import os

icon_dir = os.path.expanduser("~/calorie-tracker/frontend/public/icons")
os.makedirs(icon_dir, exist_ok=True)

for size in [(192, 192), (512, 512)]:
    img = Image.new("RGBA", size, (16, 185, 129, 255))

    draw = ImageDraw.Draw(img)
    cx, cy = size[0] // 2, size[1] // 2
    r = size[0] // 3

    # Outer plate circle
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 200), width=max(3, size[0] // 40))
    # Inner plate circle
    r2 = r - max(5, size[0] // 20)
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=(255, 255, 255, 150), width=max(2, size[0] // 50))

    # Fork/knife cross symbol
    lw = max(2, size[0] // 30)
    draw.rectangle([cx - lw, cy - r2 // 2, cx + lw, cy + r2 // 2], fill=(255, 255, 255, 220))
    draw.rectangle([cx - r2 // 2, cy - lw, cx + r2 // 2, cy + lw], fill=(255, 255, 255, 220))

    filename = f"icon-{size[0]}.png"
    filepath = os.path.join(icon_dir, filename)
    img.save(filepath, "PNG")
    print(f"Created {filepath} ({size[0]}x{size[1]})")

print("All icons done!")