import pyvista as pv
import numpy as np

def main():
    # Replace 'my_model.stl' with the path to your STL file
    # stl_file = "minimap/bph_mold_meshsolid.stl"
    stl_file = "C:/Users/reach/OneDrive/Documents/2024-25/DT/bph_mold_meshsolid.stl"

    # Load the STL file
    mesh = pv.read(stl_file)

    # new_origin = np.array([1.0, 1.0, 1.0])
    # current_center = np.array(mesh.center)
    # translation_vector = new_origin - current_center
    # mesh.translate(translation_vector)

    # Set scaling factor (adjust as needed)
    scale_factor = 1.5  
    mesh.scale([scale_factor] * 3, inplace=True)

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

    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Add the mesh to the plotter
    plotter.add_mesh(mesh, color="white", show_edges=True)
    plotter.add_mesh(marker, color="red", render_points_as_spheres=True, point_size=20)
    plotter.window_size = [1200, 900]  # Scale the render window size



    # Optional: show axes indicator in the 3D window
    plotter.show_axes()

    # Display the interactive window
    plotter.show()

if __name__ == "__main__":
    main()