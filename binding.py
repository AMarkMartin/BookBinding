import drawsvg as draw

def generate_pro_binding_template(
    book_w, book_h, book_t, 
    board_thickness=2.0, 
    turn_in=20.0, 
    hinge_gap=7.0,
    square=3.0,
    num_hubs=5,
    design_elements_data=None
):
    """
    book_w/h/t: Textblock dimensions (mm)
    board_thickness: Thickness of the greyboard/cardboard
    turn_in: Amount of leather folded over the edge
    hinge_gap: Space between spine and board
    square: Overhang of the cover past the pages
    num_hubs: Number of raised bands on the spine
    design_elements_data: Dict {'border_inset': float, 'elements': List} or just List (legacy)
    """
    if design_elements_data is None:
        design_elements_data = {}

    # 1. Component Dimensions
    board_w = book_w - 1.0 # Standard offset for the joint
    board_h = book_h + (2 * square)
    spine_w = book_t + (board_thickness)
    
    total_w = (2 * board_w) + spine_w + (2 * hinge_gap) + (2 * turn_in)
    total_h = board_h + (2 * turn_in)
    
    d = draw.Drawing(total_w, total_h, displayInline=False)

    # 2. Draw Leather Outline with Mitered Corners
    # Miter offset is usually ~1.5x board thickness to cover the corner
    miter = board_thickness * 1.5
    pts = [
        turn_in - miter, 0,                      # Top left 1
        total_w - (turn_in - miter), 0,          # Top right 1
        total_w, turn_in - miter,                # Top right 2
        total_w, total_h - (turn_in - miter),    # Bottom right 1
        total_w - (turn_in - miter), total_h,    # Bottom right 2
        turn_in - miter, total_h,                # Bottom left 1
        0, total_h - (turn_in - miter),          # Bottom left 2
        0, turn_in - miter                       # Top left 2
    ]
    d.append(draw.Lines(*pts, close=True, fill='none', stroke='black', stroke_width=1))

    # 3. Draw Board Placement Guides
    # Front Board
    d.append(draw.Rectangle(turn_in, turn_in, board_w, board_h, 
                            fill='none', stroke='blue', stroke_dasharray='3,3'))
    
    # Spine Stiffener
    spine_x = turn_in + board_w + hinge_gap
    d.append(draw.Rectangle(spine_x, turn_in, spine_w, board_h, 
                            fill='none', stroke='blue', stroke_dasharray='3,3'))
    
    # Back Board
    back_x = spine_x + spine_w + hinge_gap
    d.append(draw.Rectangle(back_x, turn_in, board_w, board_h, 
                            fill='none', stroke='blue', stroke_dasharray='3,3'))

    # 4. Spine Hub (Raised Band) Calculator
    # Divide the board height into (num_hubs + 1) spaces, but the bottom (tail) is often larger.
    # We will use equal spacing for this version.
    panel_height = board_h / (num_hubs + 1)
    
    # Calculate Material Usage
    leather_area_mm2 = total_w * total_h
    # Two boards plus spine piece (spine stiffener usually bristol or thinner board, but we'll include it for now or just the main boards)
    # Typically greyboard is just the two covers. Spine stiffener is often separate material.
    # We will calculate the 2 boards area.
    boards_area_mm2 = 2 * (board_w * board_h)
    
    measurements = {
        "width": f"{total_w:.1f}",
        "height": f"{total_h:.1f}",
        "hubs": [],
        "materials": {
            "leather_area_cm2": f"{leather_area_mm2 / 100:.1f}",
            "leather_area_sqft": f"{leather_area_mm2 / 92903:.2f}",
            "boards_area_cm2": f"{boards_area_mm2 / 100:.1f}"
        }
    }

    print(f"--- Measurements ---")
    print(f"Leather Cut: {total_w:.1f} x {total_h:.1f} mm")
    print(f"Spine Hub Positions (from top of board):")
    
    for i in range(1, num_hubs + 1):
        hub_y = turn_in + (i * panel_height)
        # Draw a line on the spine to indicate hub placement
        d.append(draw.Line(spine_x, hub_y, spine_x + spine_w, hub_y, stroke='red', stroke_width=0.5))
        measurements["hubs"].append({
            "index": i,
            "position": f"{i * panel_height:.1f}"
        })
        print(f"  Hub {i}: {i * panel_height:.1f} mm")

    # 5. Add 100mm Calibration Scale
    # Draw logic: Line 100mm long, with ticks at 0, 10, ... 100
    scale_x = turn_in
    scale_y = total_h - (turn_in / 2) # Position in the bottom margin
    d.append(draw.Line(scale_x, scale_y, scale_x + 100, scale_y, stroke='black', stroke_width=1))
    
    d.append(draw.Text("100mm Scale", 8, scale_x, scale_y - 2, fill='black'))
    
    for i in range(0, 101, 10):
        tick_x = scale_x + i
        d.append(draw.Line(tick_x, scale_y, tick_x, scale_y + 3, stroke='black', stroke_width=1))

    # Motifs Library (Simple SVG paths)
    motif_paths = {
        'acorn': 'M12,2 C6,2 2,6 2,12 C2,18 6,22 12,22 C18,22 22,18 22,12 C22,6 18,2 12,2 Z M12,4 C16,4 19,7 19,12 C19,17 16,20 12,20 C8,20 5,17 5,12 C5,7 8,4 12,4 Z', 
        'fleuron': 'M12,2 L15,10 L24,10 L17,16 L20,24 L12,19 L4,24 L7,16 L0,10 L9,10 Z',
        'corner': 'M2,2 L20,2 L20,5 L5,5 L5,20 L2,20 Z'
    }

    # 6. Process Design Elements
    # Custom Border Tool
    border_inset = float(design_elements_data.get('border_inset', 0)) if isinstance(design_elements_data, dict) else 0
    if border_inset > 0:
        # Draw tooling border on front and back boards
        # Front
        b_x = turn_in + border_inset
        b_y = turn_in + border_inset
        b_w = board_w - (2 * border_inset)
        b_h = board_h - (2 * border_inset)
        d.append(draw.Rectangle(b_x, b_y, b_w, b_h, fill='none', stroke='goldenrod', stroke_width=2))
        
        # Back
        bb_x = back_x + border_inset
        d.append(draw.Rectangle(bb_x, b_y, b_w, b_h, fill='none', stroke='goldenrod', stroke_width=2))

    elements_list = design_elements_data.get('elements', []) if isinstance(design_elements_data, dict) else design_elements_data
    
    # Handle list if it was passed directly (legacy support)
    if isinstance(elements_list, list):
        for elem in elements_list:
            etype = elem.get('type')
            x = float(elem.get('x', 0))
            y = float(elem.get('y', 0))
            
            if etype == 'text':
                content = elem.get('content', '')
                font_size = float(elem.get('font_size', 12))
                d.append(draw.Text(content, font_size, x, y, fill='black'))
            
            elif etype == 'stamp':
                motif_name = elem.get('motif', 'acorn')
                scale = float(elem.get('scale', 1.0))
                path_d = motif_paths.get(motif_name, '')
                if path_d:
                    # Create a group to handle translation and scaling
                    g = draw.Group(transform=f'translate({x},{y}) scale({scale})')
                    g.append(draw.Path(d=path_d, fill='black'))
                    d.append(g)

    return d, measurements

if __name__ == "__main__":
    # Run the generator
    layout, meas = generate_pro_binding_template(152, 229, 25, num_hubs=5)
    layout.save_svg("pro_binding_template.svg")


