import vtk

def create_marker(x, y, z, radius=1.0, color=(1.0, 0.0, 0.0)):
    """Create a sphere marker at the specified coordinates"""
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

# Create an STL reader and specify the file name
stl_reader = vtk.vtkSTLReader()
filepath = "/Users/Ayeeshi/Documents/DT03/" # Update this to your path
stl_reader.SetFileName(filepath + "bph_mold_meshsolid.stl")
stl_reader.Update()

# Get STL bounds
bounds = stl_reader.GetOutput().GetBounds()
print("STL Bounds:", bounds)

# Calculate center of STL
center_x = (bounds[0] + bounds[1]) / 2
center_y = (bounds[2] + bounds[3]) / 2
center_z = (bounds[4] + bounds[5]) / 2

# Calculate appropriate marker size based on STL dimensions
model_size = min(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
marker_radius = model_size * 0.02  # Make marker 2% of model size

# Create a mapper that will take the output of the STL reader
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stl_reader.GetOutputPort())

# Create an actor to represent the STL model
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 0.8, 0.3)
actor.GetProperty().SetOpacity(1)

# Create a renderer and add the actor to it
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)
renderer.SetLayer(0)

# Create markers at appropriate positions with scaled size
markers = [
    create_marker(center_x, center_y, center_z, radius=marker_radius, color=(1.0, 0.0, 0.0)),  # Red marker at center
]

marker_renderer = vtk.vtkRenderer()
for marker in markers:
    marker_renderer.AddActor(marker)
marker_renderer.SetBackground(0, 0, 0)
marker_renderer.SetLayer(1)

# Create a render window and add the renderers
render_window = vtk.vtkRenderWindow()
render_window.SetNumberOfLayers(2)
render_window.AddRenderer(renderer)
render_window.AddRenderer(marker_renderer)
render_window.SetSize(800, 600)

# Share the camera between renderers
marker_renderer.SetActiveCamera(renderer.GetActiveCamera())

# Set viewports
renderer.SetViewport(0, 0, 1, 1)
marker_renderer.SetViewport(0, 0, 1, 1)

# Create a render window interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Add trackball camera controls
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
render_window_interactor.SetInteractorStyle(interactor_style)

# Reset camera to fit all actors
renderer.ResetCamera()

# Initialize and start
render_window.Render()
render_window_interactor.Initialize()
render_window_interactor.Start()