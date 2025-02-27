import pyvista as pv
import numpy as np
import time

def main():
<<<<<<< HEAD
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
=======
    filepath = "/Users/Ayeeshi/Documents/DT03/"
    stl_file = filepath + "bph_mold_combined.stl"
    mesh = pv.read(stl_file)

    # Translate mesh (if necessary)
    new_origin = np.array([1.0, 1.0, 1.0])
    current_center = np.array(mesh.center)
    translation_vector = new_origin - current_center
>>>>>>> 847d0f652483d577cfdbb4a9edb4ea4da92701d0
    mesh.translate(translation_vector)

    coordinate_file = "minimap/coordinates.txt"
    f = open(coordinate_file)
    coordinates = [line.strip().split(' ') for line in f if len(line.strip().split(' ')) >= 3]
    print(coordinates)
    f.close()

<<<<<<< HEAD
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
=======
    plotter = pv.Plotter()
>>>>>>> 847d0f652483d577cfdbb4a9edb4ea4da92701d0
    plotter.show_axes()
    plotter.add_mesh(mesh, color="white", show_edges=True, opacity=0.5)
    
    # Initial marker at mesh center
    marker_position = mesh.center
    marker = pv.PolyData(np.array([marker_position]))
    marker_actor = plotter.add_mesh(marker, color="red", render_points_as_spheres=True, point_size=25)

    # Initialize frame counter
    frame = 0

    def update_position(caller, timer_id):
        nonlocal frame
        if frame < len(coordinates):
            coords = coordinates[frame]
            x, y, z = float(coords[0]), float(coords[1]), float(coords[2])
            marker.points = np.array([[x, y, z]])
            plotter.render()
            frame += 1

    # Set up the timer
    plotter.iren.add_observer('TimerEvent', update_position)
    timer_id = plotter.iren.create_timer(1000)  # 100 milliseconds
    
    # Show the plotter window
    plotter.show()

if __name__ == "__main__":
    main()