#!/usr/bin/env python3
"""
Flask REST API for generating PNG from GraphViz DOT files
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import graphviz
import os
import tempfile
import uuid
from pathlib import Path
import logging
import shutil
import subprocess

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
ALLOWED_EXTENSIONS = {'dot', 'gv'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def configure_graphviz():
    """Configure Graphviz executable paths"""
    try:
        # Try to find dot executable
        dot_path = shutil.which('dot')
        if dot_path:
            logger.info(f"Found Graphviz dot executable at: {dot_path}")
            # Test if it works
            result = subprocess.run(['dot', '-V'], capture_output=True, text=True)
            logger.info(f"Graphviz version: {result.stderr}")
            return True
        else:
            logger.error("Graphviz dot executable not found in PATH")
            # Try common installation paths
            common_paths = [
                '/usr/bin/dot',
                '/usr/local/bin/dot', 
                '/opt/homebrew/bin/dot',
                '/usr/bin/graphviz/dot'
            ]
            for path in common_paths:
                if os.path.exists(path):
                    logger.info(f"Found Graphviz at: {path}")
                    os.environ['PATH'] = f"{os.path.dirname(path)}:{os.environ.get('PATH', '')}"
                    return True
            return False
    except Exception as e:
        logger.error(f"Error configuring Graphviz: {str(e)}")
        return False

# Configure Graphviz on startup
graphviz_available = configure_graphviz()
if not graphviz_available:
    logger.warning("Graphviz not properly configured. PNG generation may fail.")

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint"""
    return jsonify({
        "message": "GraphViz PNG Generator API",
        "endpoints": {
            "/": "GET - This documentation",
            "/generate": "POST - Generate PNG from uploaded DOT file",
            "/generate_from_existing": "POST - Generate PNG from existing DOT file in folder",
            "/list_dot_files": "GET - List available DOT files",
            "/list_signal_generator_images": "GET - List available signal generator images",
            "/health": "GET - Health check",
            "/image/<filename>": "GET - Serve PNG image for web display",
            "/download/<filename>": "GET - Download PNG file"
        },
        "example_usage": {
            "upload_file": "POST /generate with 'file' in form-data and optional 'signal_generator_image'",
            "use_existing": "POST /generate_from_existing with {'filename': 'your_file.dot', 'signal_generator_image': 'signal_generator2.png'}",
            "display_image": "GET /image/<filename> - Use this URL in <img> tags"
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "GraphViz PNG API is running"})

@app.route('/list_signal_generator_images', methods=['GET'])
def list_signal_generator_images():
    """List all available signal generator images"""
    try:
        signal_gen_images = []
        current_dir = Path('.')
        
        # Find all signal generator images
        for file_path in current_dir.glob('signal_generator*.png'):
            signal_gen_images.append(file_path.name)
            
        return jsonify({
            "signal_generator_images": signal_gen_images,
            "count": len(signal_gen_images)
        })
    except Exception as e:
        logger.error(f"Error listing signal generator images: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/list_dot_files', methods=['GET'])
def list_dot_files():
    """List all DOT files in the current directory"""
    try:
        dot_files = []
        current_dir = Path('.')
        
        # Find all .dot and .gv files
        for file_path in current_dir.glob('*.dot'):
            dot_files.append(file_path.name)
        for file_path in current_dir.glob('*.gv'):
            dot_files.append(file_path.name)
            
        return jsonify({
            "dot_files": dot_files,
            "count": len(dot_files)
        })
    except Exception as e:
        logger.error(f"Error listing DOT files: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_png_from_upload():
    """Generate PNG from uploaded DOT file"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Only .dot and .gv files allowed"}), 400
        
        # Save uploaded file temporarily
        file_id = str(uuid.uuid4())
        temp_filename = f"{file_id}.dot"
        temp_filepath = os.path.join(UPLOAD_FOLDER, temp_filename)
        file.save(temp_filepath)
        
        # Get optional signal generator image parameter
        signal_generator_image = request.form.get('signal_generator_image', 'signal_generator.png')
        
        # Generate PNG
        png_data = generate_png_from_dot_file(temp_filepath, signal_generator_image)
        
        # Clean up temp file
        os.remove(temp_filepath)
        
        # Save PNG output
        output_filename = f"{file_id}.png"
        output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)
        
        with open(output_filepath, 'wb') as f:
            f.write(png_data)
        
        return jsonify({
            "message": "PNG generated successfully",
            "output_file": output_filename
        })
        
    except Exception as e:
        logger.error(f"Error generating PNG from upload: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate_from_existing', methods=['POST'])
def generate_png_from_existing():
    """Generate PNG from existing DOT file in the folder"""
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({"error": "No filename provided. Send JSON with 'filename' field"}), 400
        
        filename = data['filename']
        signal_generator_image = data.get('signal_generator_image', 'signal_generator.png')  # Default to signal_generator.png
        spectrum_analyzer_image = data.get('spectrum_analyzer_image', 'spectrum_analyzer.png')  # Default to spectrum_analyzer.png
        filepath = Path(filename)
        
        if not filepath.exists():
            return jsonify({"error": f"File '{filename}' not found"}), 404
        
        if not allowed_file(filename):
            return jsonify({"error": "Invalid file type. Only .dot and .gv files allowed"}), 400
        
        # Generate PNG with optional signal generator image selection
        png_data = generate_png_from_dot_file(str(filepath), signal_generator_image, spectrum_analyzer_image)
        
        # Save PNG output
        file_id = str(uuid.uuid4())
        output_filename = f"{filepath.stem}_{file_id}.png"
        output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)
        
        with open(output_filepath, 'wb') as f:
            f.write(png_data)
        
        return jsonify({
            "message": "PNG generated successfully",
            "source_file": filename,
            "output_file": output_filename,
            "signal_generator_image": signal_generator_image
        })
        
    except Exception as e:
        logger.error(f"Error generating PNG from existing file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download generated PNG file"""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(filepath, as_attachment=True)
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/image/<filename>', methods=['GET'])
def serve_image(filename):
    """Serve PNG image for web display"""
    try:
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found"}), 404
        
        return send_file(filepath, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error serving image: {str(e)}")
        return jsonify({"error": str(e)}), 500

def generate_png_from_dot_file(dot_filepath, signal_generator_image='signal_generator.png', spectrum_analyzer_image='spectrum_analyzer.png'):
    """Generate PNG data from DOT file with optional signal generator image selection"""
    try:
        # Read DOT file content
        with open(dot_filepath, 'r') as f:
            dot_content = f.read()
        
        if 'harmonic_distortion_test_setup.dot' in dot_filepath:
            if 'image="signal_generator.png"' in dot_content and signal_generator_image != 'signal_generator.png':
                if not os.path.exists(signal_generator_image):
                    logger.warning(f"Signal generator image '{signal_generator_image}' not found, using default.")
                    signal_generator_image = 'signal_generator.png'
                dot_content = dot_content.replace('image="signal_generator.png"', f'image="{signal_generator_image}"')
                signal_generator_image_label = signal_generator_image.replace('.png', '')
                dot_content = dot_content.replace('label="Signal Generator"', f'label="Keysight Technologies {signal_generator_image_label}"')
            if 'image="spectrum_analyzer.png"' in dot_content and spectrum_analyzer_image != 'spectrum_analyzer.png':
                if not os.path.exists(spectrum_analyzer_image):
                    logger.warning(f"Spectrum analyzer image '{spectrum_analyzer_image}' not found, using default.")
                    spectrum_analyzer_image = 'spectrum_analyzer.png'
                dot_content = dot_content.replace('image="spectrum_analyzer.png"', f'image="{spectrum_analyzer_image}"')
                spectrum_analyzer_image_label = spectrum_analyzer_image.replace('.png', '')
                dot_content = dot_content.replace('label="Spectrum Analyzer"', f'label="Keysight Technologies {spectrum_analyzer_image_label}"')
        elif 'voltage_accuracy_test_setup.dot' in dot_filepath:
            # Similar logic for voltage_accuracy_test_setup.dot if needed
            if 'image="signal_generator.png"' in dot_content and signal_generator_image != 'signal_generator.png':
                if not os.path.exists(signal_generator_image):
                    raise Exception(f"Signal generator image '{signal_generator_image}' not found")
                
                dot_content = dot_content.replace('image="signal_generator.png"', f'image="{signal_generator_image}"')
                logger.info(f"Replaced signal generator image with: {signal_generator_image}")
        
        # Create graphviz Source object
        src = graphviz.Source(dot_content)
        
        # Generate PNG
        png_data = src.pipe(format='png')
        
        return png_data
        
    except Exception as e:
        logger.error(f"Error in generate_png_from_dot_file: {str(e)}")
        raise Exception(f"Failed to generate PNG: {str(e)}")

if __name__ == '__main__':
    # Get port from environment variable for Render deployment
    port = int(os.environ.get('PORT', 5000))
    
    print("Starting GraphViz PNG Generator API...")
    print("Available endpoints:")
    print("  GET  /                     - API documentation")
    print("  GET  /health               - Health check")
    print("  GET  /list_dot_files       - List available DOT files")
    print("  POST /generate             - Generate PNG from uploaded file")
    print("  POST /generate_from_existing - Generate PNG from existing file")
    print("  GET  /image/<filename>     - Serve PNG image for web display")
    print("  GET  /download/<filename>  - Download generated PNG")
    print()
    
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=True, host='0.0.0.0', port=5000)
