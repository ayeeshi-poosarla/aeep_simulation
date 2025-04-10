# main.py
import dof9_filter
import dof9_parser
from force_analysis import force_analysis
from force_reader import read_flex_data
from imu_reader import read_imu_data
import pyvista as pv
import numpy as np
import random

def main():
    # Replace with the path to your STL file
    stl_file = "bph_mold_combined.stl"

    
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
    coordinate_file = "coordinates.txt"
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
    

    def update_position(frame, coordinates, marker):
        if frame < len(coordinates):
            coords = coordinates[frame]
            x, y, z = float(coords[0]) * 1000, float(coords[1]) * 1000, float(coords[2]) * 1000
            current_position = np.array([x, y, z])
            marker.points = np.array([current_position])

            # Simulate force reading
            current_force = random.uniform(0, 20)
            return current_force
        return None
    
    def update_mesh_color(force, mesh_actor, plotter, force_threshold1, force_threshold2):
        # Update force display text
        plotter.textActor.SetText(0, f"Force: {force:.2f} N")

        if force > force_threshold2:
            intensity = min(1.0, force / 20.0)
            red_value = min(255, 150 + int(105 * intensity))
            color = (red_value/255, 0, 0)

            mesh_actor.GetProperty().SetColor(color)
            mesh_actor.GetProperty().SetOpacity(0.5 + 0.3*intensity)
            mesh_actor.GetProperty().SetAmbient(0.5 + 0.5*intensity)

        elif force > force_threshold1:
            intensity = min(1.0, force / 20.0)
            yellow_value = min(255, 150 + int(105 * intensity))
            color = (yellow_value/255, yellow_value/255, 0)

            mesh_actor.GetProperty().SetColor(color)
            mesh_actor.GetProperty().SetOpacity(0.5 + 0.3*intensity)
            mesh_actor.GetProperty().SetAmbient(0.5 + 0.5*intensity)

        else:
            mesh_actor.GetProperty().SetColor((1, 1, 1))
            mesh_actor.GetProperty().SetOpacity(0.5)
            mesh_actor.GetProperty().SetAmbient(0.0)

        mesh_actor.Modified()
        plotter.render()


    
    # Set up the timer
    plotter.iren.add_observer('TimerEvent', update_position)
    timer_id = plotter.iren.create_timer(300)  # 300 milliseconds for better visualization
    
    # Show the plotter window
    plotter.show()

    df = []
    time_above_pressure_thresh = 0
    time_threshold = 3.0
    force_threshold = 10.0
  
    x_min = -75.485
    x_max = 75.485
    y_min = -82.4505
    y_max = 82.4505
    z_min = -63.0095
    z_max = 63.0095
  
    x = 0
    y = 0
    z = 0
    dt = 0.01 

    while (
      x_min <= x <= x_max and
      y_min <= y <= y_max and
      z_min <= z <= z_max
    ):
        imu_outputs = read_imu_data()
        bend_values = read_flex_data()
        # coordinates = madgwick(imu_outputs)

        
        pressure = force_analysis(bend_values)
      
        update_position() # update point on minimap

        # force thresholding

        if pressure > force_threshold:
            time_above_pressure_thresh += dt
        else:
            time_above_pressure_thresh = 0

        if time_above_pressure_thresh > time_threshold:
            update_mesh_color(pressure, mesh_actor, plotter, force_threshold1, force_threshold2)

        N, S, E, W = force_reader()
        data = {dt, x, y, z, N, S, E, W}
        df.append(data)


if __name__ == "__main__":
    main()
