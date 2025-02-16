import vtk

def create_marker(x, y, z, radius=1.0, color=(1.0, 0.0, 0.0)):
    """Create a sphere marker at the specified coordinates."""
    marker = vtk.vtkSphereSource()
    marker.SetRadius(radius)
    marker.SetCenter(x, y, z)
    
    marker_mapper = vtk.vtkPolyDataMapper()
    marker_mapper.SetInputConnection(marker.GetOutputPort())
    
    marker_actor = vtk.vtkActor()
    marker_actor.SetMapper(marker_mapper)
    marker_actor.GetProperty().SetColor(color)
    marker_actor.ForceOpaqueOn()
    marker_actor.GetProperty().SetAmbient(1.0)
    
    return marker_actor

# -----------------------------
# Create the STL Actor (Layer 0)
# -----------------------------
stl_reader = vtk.vtkSTLReader()
stl_reader.SetFileName("/Users/Ayeeshi/Documents/DT03/bph_mold_meshsolid.stl")
stl_reader.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stl_reader.GetOutputPort())

stl_actor = vtk.vtkActor()
stl_actor.SetMapper(mapper)
stl_actor.GetProperty().SetColor(1.0, 0.8, 0.3)
stl_actor.GetProperty().SetOpacity(0.7)  # Slightly transparent

# -----------------------------
# Create Marker Actors (Layer 1)
# -----------------------------
marker = create_marker(10, 10, 10, radius=0.1, color=(1.0, 0.0, 0.0))

# -----------------------------
# Create Renderers for Each Layer
# -----------------------------
# Renderer for the STL model (Layer 0)
renderer0 = vtk.vtkRenderer()
renderer0.AddActor(stl_actor)
renderer0.SetLayer(0)
renderer0.SetBackground(0.1, 0.2, 0.4)

# Renderer for the markers (Layer 1)
renderer1 = vtk.vtkRenderer()
renderer1.AddActor(marker)
renderer1.SetLayer(1)
# Set a transparent background so that the underlying layer remains visible.
renderer1.SetBackground(0.0, 0.0, 0.0)
renderer1.SetBackgroundAlpha(0)

# -----------------------------
# Share a Common Camera
# -----------------------------
shared_camera = vtk.vtkCamera()
renderer0.SetActiveCamera(shared_camera)
renderer1.SetActiveCamera(shared_camera)

# Optionally, reset the camera to include all actors.
renderer0.ResetCamera()

# -----------------------------
# Setup Render Window with Multiple Layers
# -----------------------------
render_window = vtk.vtkRenderWindow()
render_window.SetNumberOfLayers(2)
render_window.AddRenderer(renderer0)
render_window.AddRenderer(renderer1)
render_window.SetSize(800, 600)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

interactor_style = vtk.vtkInteractorStyleTrackballCamera()
render_window_interactor.SetInteractorStyle(interactor_style)

# -----------------------------
# Start Rendering
# -----------------------------
render_window.Render()
render_window_interactor.Initialize()
render_window_interactor.Start()