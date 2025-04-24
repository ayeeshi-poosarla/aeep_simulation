import open3d as o3d
import numpy as np
import time
import threading

def main():
    # Load the STL mesh
    stl_file = "C:/Users/kayla/.spyder-py3/DT3_Local/bph_mold_combined.stl"  # Update this path!
    mesh = o3d.io.read_triangle_mesh(stl_file)
    mesh.compute_vertex_normals()

    # Scale the mesh
    sf = 1.5
    mesh.scale(sf, center=mesh.get_center())

    # Translate to origin (move minimum bounds to (0,0,0))
    bounds = mesh.get_axis_aligned_bounding_box()
    min_bound = bounds.get_min_bound()
    mesh.translate(-min_bound)

    # Create a marker point
    marker = o3d.geometry.TriangleMesh.create_sphere(radius=5.0)
    marker.paint_uniform_color([0.0, 1.0, 1.0])  # Cyan
    marker.translate(mesh.get_center())

    # Create a bounding box
    bounding_box = bounds.translate(-min_bound)
    bounding_box.color = (0, 0, 1)  # Blue

    # Load coordinates from file
    coordinate_file = "minimap/coordinates.txt"
    coordinates = []
    with open(coordinate_file, "r") as f:
        for line in f:
            parts = line.strip().replace('[','').replace(']','').replace(',','').split()
            if len(parts) >= 3:
                coordinates.append([float(parts[0])*1000, float(parts[1])*1000, float(parts[2])*1000])

    # Create visualizer
    mesh.paint_uniform_color([1, 1, 1])  # Set the mesh color to white
    vis = o3d.visualization.Visualizer()
    vis.create_window(window_name="STL Viewer", width=1200, height=900)
    vis.add_geometry(mesh)
    mesh.paint_uniform_color([1, 1, 1, 0.5])
    vis.add_geometry(marker)
    vis.add_geometry(bounding_box)

    def update():
        for coord in coordinates:
            time.sleep(1)  # Delay between frames (1000 ms)
            marker.translate(np.array(coord) - marker.get_center(), relative=False)
            vis.update_geometry(marker)
            vis.poll_events()
            vis.update_renderer()

    # Run animation in separate thread so it doesn't block
    threading.Thread(target=update).start()

    vis.run()
    vis.destroy_window()

if __name__ == "__main__":
    main()
