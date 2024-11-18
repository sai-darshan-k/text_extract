import os
from flask import Flask, send_file, render_template_string, jsonify
from PIL import ImageGrab, Image
import easyocr
import hashlib

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])  # ['en'] is for English

# Initialize Flask
app = Flask(__name__)

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
    extracted_text = " ".join([text[1] for text in result])
    return extracted_text

def hash_image(image_path):
    """Generate a hash for the image."""
    with open(image_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

@app.route('/')
def home():
    """Root route to guide users."""
    capture_screen()
    return render_template_string(""" 
        <h1>Screen Capture Service</h1>
        <h3>Here's the latest screenshot:</h3>
        <img src="{{ url_for('get_screen') }}" alt="Screenshot" style="max-width: 100%; height: auto;">
        <p><a href="/get_text">Click here to extract text from the screenshot</a></p>
    """)

@app.route('/screen', methods=['GET'])
def get_screen():
    """API to serve the screenshot image."""
    capture_screen()
    return send_file(screenshot_path, mimetype='image/png')

@app.route('/get_text', methods=['GET'])
def get_text():
    """API to capture the screen, extract text, and return as JSON."""
    image_path = capture_screen()
    text_result = extract_text_easyocr(image_path)
    return render_template_string(""" 
        <h1>Extracted Text from Screenshot</h1>
        <h3>Here's the latest screenshot:</h3>
        <img src="{{ url_for('get_screen') }}" alt="Screenshot" style="max-width: 100%; height: auto;">
        <p>Extracted Text: {{ text }}</p>
    """, text=text_result)

if __name__ == "__main__":
    capture_screen()
    app.run(debug=True)
