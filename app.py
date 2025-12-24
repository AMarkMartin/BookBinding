from flask import Flask, render_template, request, jsonify, send_file
from binding import generate_pro_binding_template
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        print("Received data:", data) # Debugging
        
        # Extract and convert parameters
        # Default values matching the function signature in binding.py
        book_w = float(data.get('book_w', 152))
        book_h = float(data.get('book_h', 229))
        book_t = float(data.get('book_t', 25))
        
        board_thickness = float(data.get('board_thickness', 2.0))
        turn_in = float(data.get('turn_in', 20.0))
        hinge_gap = float(data.get('hinge_gap', 7.0))
        square = float(data.get('square', 3.0))
        num_hubs = int(data.get('num_hubs', 5))
        
        # design_elements represents the whole design payload now (border + items)
        design_payload = {
            'border_inset': float(data.get('border_inset', 0)),
            'elements': data.get('design_elements', [])
        }
        
        # Generate the drawing
        drawing, measurements = generate_pro_binding_template(
            book_w, book_h, book_t,
            board_thickness=board_thickness,
            turn_in=turn_in,
            hinge_gap=hinge_gap,
            square=square,
            num_hubs=num_hubs,
            design_elements_data=design_payload
        )
        
        # Convert SVG to string
        svg_string = drawing.as_svg()
        
        return jsonify({
            'status': 'success',
            'svg': svg_string,
            'measurements': measurements
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
