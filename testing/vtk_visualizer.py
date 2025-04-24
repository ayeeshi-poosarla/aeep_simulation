import vtk
import numpy as np

# Dummy data: generate a few random positions
dummy_positions = [np.random.rand(3) * 100 for _ in range(50)]
frame = 0

def update(obj, event):
    global frame
    if frame >= len(dummy_positions):
        return
    x, y, z = dummy_positions[frame]
    marker.SetCenter(x, y, z)
    render_window.Render()
    frame += 1

# Custom interactor style that disables camera interaction
class NoRotateInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def OnMouseMove(self): pass
    def OnLeftButtonDown(self): pass
    def OnLeftButtonUp(self): pass
    def OnRightButtonDown(self): pass
    def OnRightButtonUp(self): pass
    def OnMiddleButtonDown(self): pass
    def OnMiddleButtonUp(self): pass

# Load STL
stl_reader = vtk.vtkSTLReader()
stl_reader.SetFileName("C:/Users/kayla/.spyder-py3/DT3_Local/bph_mold_combined.stl")
stl_reader.Update()
stl_output = stl_reader.GetOutput()

# Make the STL mesh semi-transparent
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(stl_output)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetOpacity(0.3)  # Set transparency (0=fully transparent, 1=fully opaque)
actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # White

# Create a moving marker (sphere)
marker = vtk.vtkSphereSource()
marker.SetRadius(5.0)
marker.SetCenter(dummy_positions[0])

marker_mapper = vtk.vtkPolyDataMapper()
marker_mapper.SetInputConnection(marker.GetOutputPort())

marker_actor = vtk.vtkActor()
marker_actor.SetMapper(marker_mapper)
marker_actor.GetProperty().SetColor(0, 1, 1)  # Cyan

# Renderer
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.AddActor(marker_actor)
renderer.SetBackground(0.1, 0.1, 0.1)

# Window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(1200, 900)

# Interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Set the no-rotation interactor style
interactor.SetInteractorStyle(NoRotateInteractorStyle())

# Add timer to update marker
interactor.AddObserver('TimerEvent', update)
interactor.CreateRepeatingTimer(200)  # update every 200 ms

# Start
interactor.Initialize()
render_window.Render()
interactor.Start()
