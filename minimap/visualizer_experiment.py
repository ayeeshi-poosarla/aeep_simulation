import pyvista as pv
import numpy as np

def main():
    # Path to your STL file
    stl_file = "/Users/bennettye/Documents/DT03/bph_mold_combined.stl"
    
    # Load the STL file (this is assumed to be a closed, manifold surface)
    mesh = pv.read(stl_file)

    # (Optional) Translate the mesh so its center is at a known location.
    new_origin = np.array([1.0, 1.0, 1.0])
    current_center = np.array(mesh.center)
    translation_vector = new_origin - current_center
    mesh.translate(translation_vector)

    # Create an inner mesh by scaling the original mesh slightly down.
    # The scaling factor controls the wall thickness of the shell.
    inner_mesh = mesh.copy()
    scale_factor = 0.95  # Adjust this factor as needed (closer to 1.0 = thinner walls)
    inner_mesh.scale(scale_factor)
    
    # Use a boolean difference to subtract the inner mesh from the outer mesh.
    # This operation should leave you with a hollow shell that has both an outer and an inner surface.
    try:
        shell = mesh.boolean_difference(inner_mesh)
    except Exception as e:
        print("Boolean difference failed:", e)
        return

    # Now, to place a marker on the inside surface, we can use the inner_mesh.
    # Define the desired marker position (this is your guess or target point inside the cavity)
    desired_marker_position = [0, -0.005, 0.006]
    closest_point_idx = inner_mesh.find_closest_point(np.array(desired_marker_position))
    marker_position = inner_mesh.points[closest_point_idx]
    marker = pv.PolyData(np.array([marker_position]))

    # Create a PyVista plotter
    plotter = pv.Plotter()

    # Add the hollow shell to the plotter.
    # Using partial opacity so you can see both the outer and inner surfaces.
    plotter.add_mesh(shell, color="white", show_edges=True, opacity=0.5)
    
    # (Optional) Also add the inner surface in a different color.
    plotter.add_mesh(inner_mesh, color="lightblue", opacity=0.5)
    
    # Add the marker as a red sphere to indicate the chosen point on the inside surface.
    plotter.add_mesh(marker, color="red", render_points_as_spheres=True, point_size=25)
    
    # Show axes and then display the interactive window.
    plotter.show_axes()
    plotter.show()

if __name__ == "__main__":
    main()