from flask import Flask, send_file, jsonify, render_template_string
from PIL import ImageGrab, Image
import easyocr
import hashlib
import os

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])  # ['en'] is for English

# Initialize Flask
app = Flask(__name__)

# Global variables for caching
text_result = None
last_image_hash = None
screenshot_path = "static/screenshot.png"  # Save in static folder to serve it easily

def capture_screen():
    """Capture the screen and save as an image."""
    screenshot = ImageGrab.grab()  # Capture the entire screen
    screenshot.save(screenshot_path)  # Save it to the static folder
    return screenshot_path

def preprocess_image(image_path):
    """Preprocess the image for better OCR performance."""
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img = img.resize((img.width // 2, img.height // 2))  # Reduce size by half
    img.save(image_path)  # Overwrite the image file
    return image_path

def extract_text_easyocr(image_path):
    """Extract text using EasyOCR."""
    image_path = preprocess_image(image_path)
    # Using EasyOCR reader to extract text from the image
    result = reader.readtext(image_path)
    
    # Combine all text into a single string
    extracted_text = " ".join([text[1] for text in result])
    return extracted_text

def hash_image(image_path):
    """Generate a hash for the image."""
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

@app.route('/')
def home():
    """Root route to guide users."""
    # Capture the screen
    capture_screen()

    # HTML template with the image embedded
    return render_template_string(""" 
        <h1>Screen Capture Service</h1>
        <h3>Here's the latest screenshot:</h3>
        <img src="{{ url_for('get_screen') }}" alt="Screenshot" style="max-width: 100%; height: auto;">
        <p><a href="/get_text">Click here to extract text from the screenshot</a></p>
    """)

@app.route('/screen', methods=['GET'])
def get_screen():
    """API to serve the screenshot image."""
    # Ensure the image is captured before serving
    capture_screen()

    # Serve the image file directly
    return send_file(screenshot_path, mimetype='image/png')

@app.route('/get_text', methods=['GET'])
def get_text():
    """API to capture the screen, extract text, and return as JSON."""
    global text_result, last_image_hash

    # Capture the screen
    image_path = capture_screen()

    # Compute hash of the new image
    current_hash = hash_image(image_path)

    # If the hash matches the previous one, return cached result
    if current_hash == last_image_hash:
        return render_template_string("""
            <h1>Extracted Text from Screenshot</h1>
            <h3>Here's the latest screenshot:</h3>
            <img src="{{ url_for('get_screen') }}" alt="Screenshot" style="max-width: 100%; height: auto;">
            <p>Extracted Text: {{ text }}</p>
        """, text=text_result)

    # Otherwise, run OCR and update cache
    text_result = extract_text_easyocr(image_path)
    last_image_hash = current_hash  # Update the hash

    return render_template_string("""
        <h1>Extracted Text from Screenshot</h1>
        <h3>Here's the latest screenshot:</h3>
        <img src="{{ url_for('get_screen') }}" alt="Screenshot" style="max-width: 100%; height: auto;">
        <p>Extracted Text: {{ text }}</p>
    """, text=text_result)

if __name__ == '__main__':
    # Ensure the 'static' directory exists for the screenshot to be saved
    if not os.path.exists('static'):
        os.makedirs('static')

    # Capture the screen immediately when the app starts
    capture_screen()

    # Run the Flask server
    app.run(host='0.0.0.0', port=5000)
