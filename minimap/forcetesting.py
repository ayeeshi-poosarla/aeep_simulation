import pyvista as pv
import numpy as np
import random

def main():
    # Replace with the path to your STL file
    stl_file = "/Users/bennettye/Documents/DT03/bph_mold_combined.stl"
    
    # Load the STL file
    mesh = pv.read(stl_file)
    
    # Set scaling factor
    sf = 1.5
    mesh.scale([sf] * 3, inplace=True)
    
    # Move mesh origin to the bottom-left-front corner
    min_x, max_x, min_y, max_y, min_z, max_z = mesh.bounds
    translation_vector = np.array([min_x, min_y, min_z])  # Move min bounds to (0,0,0)
    mesh.translate(translation_vector)
    
    desired_marker_position = translation_vector
    
    # Create a bounding box around the mesh
    box_corners = np.array([[min_x, min_y, min_z], [max_x, min_y, min_z], [max_x, max_y, min_z], 
                           [min_x, max_y, min_z], [min_x, min_y, max_z], [max_x, min_y, max_z], 
                           [max_x, max_y, max_z], [min_x, max_y, max_z]])
    
    # Define the edges of the bounding box
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],  # Bottom edges
        [4, 5], [5, 6], [6, 7], [7, 4],  # Top edges
        [0, 4], [1, 5], [2, 6], [3, 7]   # Vertical edges
    ]
    
    # Create a PolyData object for the border lines
    border_lines = pv.PolyData()
    
    # Read coordinates from file
    coordinate_file = "minimap/coordinates.txt"
    with open(coordinate_file) as f:
        coordinates = [
            line.strip().replace('[','').replace(']','').replace(',','').split() 
            for line in f if len(line.strip().replace('[','').replace(']','').replace(',','').split()) >= 3
        ]
    
    # Loop through edges to create the lines
    for edge in edges:
        start_point = box_corners[edge[0]]
        end_point = box_corners[edge[1]]
        line = pv.Line(start_point, end_point)
        border_lines += line
    
    # Create a PyVista plotter
    plotter = pv.Plotter()
    
    # Add the mesh to the plotter with initial settings
    mesh_actor = plotter.add_mesh(mesh, color="white", show_edges=True, opacity=0.25)
    
    # Add marker at the center initially
    marker_position = mesh.center
    marker = pv.PolyData(np.array([marker_position]))
    plotter.add_mesh(marker, color="cyan", render_points_as_spheres=True, point_size=20)
    
    # Set window size
    plotter.window_size = [1200, 900]
    
    # Add the border edges
    plotter.add_mesh(border_lines, color="blue", line_width=2)
    
    # Show axes indicator
    plotter.show_axes()
    
    # Add text display for force value
    force_text = plotter.add_text("Force: 0.0 N", position="upper_left", font_size=12)
    
    frame = 0
    
    # Define the threshold force that triggers the red glow (5N)
    force_threshold1 = 5.0
    force_threshold2 = 10.0
    
    def update_position(caller, timer_id):
        nonlocal frame
        if frame < len(coordinates):
            coords = coordinates[frame]
            x, y, z = float(coords[0]) * 1000, float(coords[1]) * 1000, float(coords[2]) * 1000
            current_position = np.array([x, y, z])
            marker.points = np.array([current_position])
            
            # Generate random force value between 0 and 10N for testing
            current_force = random.uniform(0, 20)
            
            # Update force display text
            plotter.textActor.SetText(0, f"Force: {current_force:.2f} N")
            
            # Check if force exceeds threshold
            if current_force > force_threshold2:
                # Make the mesh glow red with intensity proportional to force
                intensity = min(1.0, current_force / 20.0)  # Normalize to 0-1 range
                # Brighter red for higher forces
                red_value = min(255, 150 + int(105 * intensity))
                color = (red_value/255, 0, 0)
                
                # Increase opacity and ambient lighting for glow effect
                mesh_actor.GetProperty().SetColor(color)
                mesh_actor.GetProperty().SetOpacity(0.5 + 0.3*intensity)
                mesh_actor.GetProperty().SetAmbient(0.5 + 0.5*intensity)
            elif current_force > force_threshold1:
                intensity = min(1.0, current_force / 20.0)  # Normalize to 0-1 range
                # Brighter yellow for higher forces
                yellow_value = min(255, 150 + int(105 * intensity))
                color = (yellow_value/255, yellow_value/255, 0)  # Yellow is (R,G,0)
    
    # Increase opacity and ambient lighting for glow effect
                mesh_actor.GetProperty().SetColor(color)
                mesh_actor.GetProperty().SetOpacity(0.5 + 0.3*intensity)
                mesh_actor.GetProperty().SetAmbient(0.5 + 0.5*intensity)

            else:
                # Return to normal appearance
                mesh_actor.GetProperty().SetColor((1, 1, 1))
                mesh_actor.GetProperty().SetOpacity(0.5)
                mesh_actor.GetProperty().SetAmbient(0.0)
            
            mesh_actor.Modified()
            plotter.render()
            frame += 1
        else:
            # Reset to start when all frames are processed
            frame = 0
    
    # Set up the timer
    plotter.iren.add_observer('TimerEvent', update_position)
    timer_id = plotter.iren.create_timer(300)  # 300 milliseconds for better visualization
    
    # Show the plotter window
    plotter.show()

if __name__ == "__main__":
    main()