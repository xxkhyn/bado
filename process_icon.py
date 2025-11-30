from PIL import Image, ImageDraw

def process_image():
    try:
        # Open and convert to RGBA
        img = Image.open('static/images/icon.jpg').convert("RGBA")
        
        # Use ImageDraw.floodfill to fill the background starting from corners
        # We fill with a fully transparent color (0, 0, 0, 0)
        # thresh=50 handles JPEG compression artifacts (near-white pixels)
        
        width, height = img.size
        corners = [(0, 0), (width-1, 0), (0, height-1), (width-1, height-1)]
        
        for corner in corners:
            try:
                ImageDraw.floodfill(img, xy=corner, value=(0, 0, 0, 0), thresh=50)
            except Exception:
                pass

        # Now trim the transparent area (crop to content)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        
        # Resize to standard icon size
        img = img.resize((512, 512), Image.Resampling.LANCZOS)
        
        img.save('static/images/icon.png', "PNG")
        print("Successfully processed icon.png with flood-fill transparency")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    process_image()
