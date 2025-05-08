import os
from PIL import Image
from pillow_heif import register_heif_opener

# Register HEIF opener
register_heif_opener()

def convert_heic_to_png():
    """Convert HEIC images to PNG format"""
    input_folder = "heic_images"
    output_folder = "png_images"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Get all HEIC files
    heic_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.heic')]
    
    if not heic_files:
        print("No HEIC files found in the input directory")
        return
    
    print(f"Found {len(heic_files)} HEIC files to convert")
    
    # Convert each file
    for filename in heic_files:
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + '.png'
        output_path = os.path.join(output_folder, output_filename)
        
        try:
            # Open and convert HEIC image
            with Image.open(input_path) as img:
                # Save as PNG
                img.save(output_path, 'PNG')
            print(f"Converted {filename} to PNG")
        except Exception as e:
            print(f"Error converting {filename}: {e}")

if __name__ == "__main__":
    convert_heic_to_png()
