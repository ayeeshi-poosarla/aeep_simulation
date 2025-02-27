import pyvista as pv
import numpy as np

def main():
    # Replace 'my_model.stl' with the path to your STL file
    # stl_file = "minimap/bph_mold_meshsolid.stl"
    stl_file = "/Users/bennettye/Documents/DT03/bph_mold_combined.stl"

    # Load the STL file
    mesh = pv.read(stl_file)

    # new_origin = np.array([1.0, 1.0, 1.0])
    # current_center = np.array(mesh.center)
    # translation_vector = new_origin - current_center
    # mesh.translate(translation_vector)

    # Set scaling factor (adjust as needed)
    sf = 1.5  
    mesh.scale([sf] * 3, inplace=True)

    # Move mesh origin to the bottom-left-front corner
    min_x, max_x, min_y, max_y, min_z, max_z = mesh.bounds
    translation_vector = np.array([min_x, min_y, min_z])  # Move min bounds to (0,0,0)
    mesh.translate(translation_vector)


    # Translate the mesh so that its geometric center is at the origin
    #mesh.translate(-np.array(mesh.center))

    desired_marker_position = translation_vector
    # closest_point_idx = mesh.find_closest_point(np.array(desired_marker_position))
    # marker_position = mesh.points[closest_point_idx]
    marker = pv.PolyData(np.array([desired_marker_position]))

    # Create a bounding box around the mesh
    box_corners = np.array([[min_x, min_y, min_z], [max_x, min_y, min_z],
                             [max_x, max_y, min_z], [min_x, max_y, min_z],
                             [min_x, min_y, max_z], [max_x, min_y, max_z],
                             [max_x, max_y, max_z], [min_x, max_y, max_z]])
    
    # Define the edges of the bounding box correctly
    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],   # Bottom edges
        [4, 5], [5, 6], [6, 7], [7, 4],   # Top edges
        [0, 4], [1, 5], [2, 6], [3, 7]    # Vertical edges
    ]

    # Create a PolyData object for the border lines
    border_lines = pv.PolyData()

    # Loop through edges to create the lines
    for edge in edges:
        start_point = box_corners[edge[0]]
        end_point = box_corners[edge[1]]
        line = pv.Line(start_point, end_point)
        border_lines += line  # Add the line to the border lines PolyData

    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Add the mesh to the plotter
    plotter.add_mesh(mesh, color="white", show_edges=True, opacity = 0.25)
    plotter.add_mesh(marker, color="cyan", render_points_as_spheres=True, point_size=20)
    plotter.window_size = [1200, 900]  # Scale the render window size

    # Add the border edges to the plotter with a specific color and width
    plotter.add_mesh(border_lines, color="blue", line_width=2)

    # Optional: show axes indicator in the 3D window
    plotter.show_axes()

    # Display the interactive window
    plotter.show()

if __name__ == "__main__":
    main()