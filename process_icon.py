from PIL import Image, ImageChops

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)
    return im

try:
    img = Image.open('static/images/icon.jpg')
    trimmed_img = trim(img)
    # Resize to standard icon size if needed, e.g., 512x512
    trimmed_img = trimmed_img.resize((512, 512), Image.Resampling.LANCZOS)
    trimmed_img.save('static/images/icon.png')
    print("Successfully processed icon.png")
except Exception as e:
    print(f"Error processing image: {e}")
