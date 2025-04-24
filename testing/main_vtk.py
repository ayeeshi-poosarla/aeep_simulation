# main.py
from force_analysis import update_mesh_color
from force_analysis import force_analysis
from force_reader import read_flex_data
from imu_reader import read_imu_data
from dof9_filter import MadgwickFilter
import vtk
import numpy as np
import random
import time

# Custom interactor style that disables camera interaction
class NoRotateInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def OnMouseMove(self): pass
    def OnLeftButtonDown(self): pass
    def OnLeftButtonUp(self): pass
    def OnRightButtonDown(self): pass
    def OnRightButtonUp(self): pass
    def OnMiddleButtonDown(self): pass
    def OnMiddleButtonUp(self): pass

def main():

    # --- Load and transform STL ---
    stl_file = r"C:\Users\kayla\.spyder-py3\DT3_Local\bph_mold_combined.stl"
    stl_reader = vtk.vtkSTLReader()
    stl_reader.SetFileName(stl_file)
    stl_reader.Update()
    mesh = stl_reader.GetOutput()

    # Get bounds and compute translation to origin
    bounds = mesh.GetBounds()
    min_x, max_x = bounds[0], bounds[1]
    min_y, max_y = bounds[2], bounds[3]
    min_z, max_z = bounds[4], bounds[5]
    translation_vector = [-min_x, -min_y, -min_z]

    transform = vtk.vtkTransform()
    transform.Translate(*translation_vector)

    transform_filter = vtk.vtkTransformPolyDataFilter()
    transform_filter.SetInputData(mesh)
    transform_filter.SetTransform(transform)
    transform_filter.Update()
    translated_mesh = transform_filter.GetOutput()

    # --- Create STL actor with transparency ---
    stl_mapper = vtk.vtkPolyDataMapper()
    stl_mapper.SetInputData(translated_mesh)

    stl_actor = vtk.vtkActor()
    stl_actor.SetMapper(stl_mapper)
    stl_actor.GetProperty().SetOpacity(0.25)
    stl_actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # white

    # --- Create marker at center ---
    center = translated_mesh.GetCenter()
    sphere = vtk.vtkSphereSource()
    sphere.SetCenter(center)
    sphere.SetRadius(5.0)

    sphere_mapper = vtk.vtkPolyDataMapper()
    sphere_mapper.SetInputConnection(sphere.GetOutputPort())

    sphere_actor = vtk.vtkActor()
    sphere_actor.SetMapper(sphere_mapper)
    sphere_actor.GetProperty().SetColor(0.0, 1.0, 1.0)  # cyan

    # --- Create box outline from corners ---
    box_corners = np.array([
        [min_x, min_y, min_z], [max_x, min_y, min_z], [max_x, max_y, min_z], [min_x, max_y, min_z],
        [min_x, min_y, max_z], [max_x, min_y, max_z], [max_x, max_y, max_z], [min_x, max_y, max_z]
    ]) + translation_vector

    edges = [
        [0, 1], [1, 2], [2, 3], [3, 0],
        [4, 5], [5, 6], [6, 7], [7, 4],
        [0, 4], [1, 5], [2, 6], [3, 7]
    ]

    append_lines = vtk.vtkAppendPolyData()
    for edge in edges:
        p1 = box_corners[edge[0]]
        p2 = box_corners[edge[1]]
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(p1)
        line_source.SetPoint2(p2)
        line_source.Update()
        append_lines.AddInputData(line_source.GetOutput())
    append_lines.Update()

    line_mapper = vtk.vtkPolyDataMapper()
    line_mapper.SetInputData(append_lines.GetOutput())

    line_actor = vtk.vtkActor()
    line_actor.SetMapper(line_mapper)
    line_actor.GetProperty().SetColor(0.0, 0.0, 1.0)  # blue
    line_actor.GetProperty().SetLineWidth(2)

    # --- Setup Renderer, RenderWindow, Interactor ---
    renderer = vtk.vtkRenderer()
    renderer.AddActor(stl_actor)
    renderer.AddActor(sphere_actor)
    renderer.AddActor(line_actor)
    renderer.SetBackground(0.1, 0.1, 0.1)

    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(1200, 900)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    # Disable camera rotation
    style = NoRotateInteractorStyle()
    style.SetDefaultRenderer(renderer)
    interactor.SetInteractorStyle(style)

    # Start render loop
    render_window.Render()
    interactor.Start()

    
    
    
    # force_text = plotter.add_text("Force: 0.0 N", position="upper_left", font_size=12)

    # Define the threshold force that triggers the red glow (5N)
    # force_threshold1 = 5.0
    # force_threshold2 = 10.0
    
    def update_position(obj, event):
        global sphere, render_window, start_time, madgwick

        # Timing logic
        current_time = time.time()
        dt = current_time - start_time
        start_time = current_time

        # Get data from IMU
        ax, ay, az, gx, gy, gz, mx, my, mz = read_imu_data()

        # Compute new position using Madgwick filter
        position = madgwick.compute_position(
            [dt, ax, ay, az, gx, gy, gz, mx, my, mz],
            beta=0.1,
            L=0.1
        )

        # Update marker (sphere) position
        sphere.SetCenter(position)
        sphere.Update()

        # Refresh render window
        render_window.Render()

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

    start_time = time.time()
    interactor.AddObserver('TimerEvent', update_position)
    interactor.CreateRepeatingTimer(300)
    interactor.Start()

    while (
      x_min <= x <= x_max and
      y_min <= y <= y_max and
      z_min <= z <= z_max
    ):
        print("meowmeowmeowmeow")
        current_time = time.time()
        dt = current_time - start_time
        start_time = current_time

        ax, ay, az, gx, gy, gz, mx, my, mz = read_imu_data()
        N, S, E, W = read_flex_data()

        madgwick = MadgwickFilter(sample_period=dt, beta=0.1)
        position = madgwick.compute_position([dt, ax, ay, az, gx, gy, gz, mx, my, mz], beta=0.1, L=0.1)
        
        # pressure = force_analysis(bend_values)

        
      
        update_position(position) # update point on minimap

        
        # 300 milliseconds for better visualization
        # Show the plotter window
        

        # force thresholding

        # if pressure > force_threshold:
        #     time_above_pressure_thresh += dt
        # else:
        #     time_above_pressure_thresh = 0

        # if time_above_pressure_thresh > time_threshold:
        #     update_mesh_color(pressure, mesh_actor, plotter, force_threshold1, force_threshold2)

        # Set up the timer
    

    N, S, E, W = read_flex_data()
    data = {dt, position, N, S, E, W}
    df.append(data)

if __name__ == "__main__":
    main()
