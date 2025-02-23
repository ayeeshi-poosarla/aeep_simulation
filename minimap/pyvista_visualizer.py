import pyvista as pv
import numpy as np
import time

def main():
    filepath = "/Users/Ayeeshi/Documents/DT03/"
    stl_file = filepath + "bph_mold_combined.stl"
    mesh = pv.read(stl_file)

    # Translate mesh (if necessary)
    new_origin = np.array([1.0, 1.0, 1.0])
    current_center = np.array(mesh.center)
    translation_vector = new_origin - current_center
    mesh.translate(translation_vector)

    coordinate_file = "minimap/coordinates.txt"
    f = open(coordinate_file)
    coordinates = [line.strip().split(' ') for line in f if len(line.strip().split(' ')) >= 3]
    print(coordinates)
    f.close()

    plotter = pv.Plotter()
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