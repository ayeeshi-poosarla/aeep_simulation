import pyvista as pv
import numpy as np

def main():
    # Replace 'my_model.stl' with the path to your STL file
    stl_file = "/Users/bennettye/Documents/DT03/bph_mold_combined.stl"

    # Load the STL file
    mesh = pv.read(stl_file)

    new_origin = np.array([1.0, 1.0, 1.0])
    current_center = np.array(mesh.center)
    translation_vector = new_origin - current_center
    mesh.translate(translation_vector)


    # Translate the mesh so that its geometric center is at the origin
    #mesh.translate(-np.array(mesh.center))

    desired_marker_position = [0.08, -0.12, -0.08]
    marker = pv.PolyData(np.array([desired_marker_position]))
    #marker_position = mesh.center
    #marker = pv.PolyData(np.array([marker_position]))

    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Add the mesh to the plotter
    plotter.add_mesh(mesh, color="white", show_edges=True, opacity=0.5)
    plotter.add_mesh(marker, color="red", render_points_as_spheres=True, point_size=25)

    # Optional: show axes indicator in the 3D window
    plotter.show_axes()

    # Display the interactive window
    plotter.show()

if __name__ == "__main__":
    main()