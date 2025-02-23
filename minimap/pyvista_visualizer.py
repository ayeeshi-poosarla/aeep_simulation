import pyvista as pv
import numpy as np

def main():
    # Replace 'my_model.stl' with the path to your STL file
    stl_file = "/Users/bennettye/Documents/DT03/bph_mold_combined.stl"

    # Load the STL file
    mesh = pv.read(stl_file)

    #idk if this is necessary but don't touch it 
    new_origin = np.array([1.0, 1.0, 1.0])
    current_center = np.array(mesh.center)
    translation_vector = new_origin - current_center
    mesh.translate(translation_vector)




    #set marker to specified location
    desired_marker_position = [0.08, -0.12, -0.08]
    marker = pv.PolyData(np.array([desired_marker_position]))
    #the block below moves the marker position to the center 
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