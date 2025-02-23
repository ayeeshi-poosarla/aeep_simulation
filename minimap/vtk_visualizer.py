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
stl_reader.SetFileName("minimap/bph_mold_combined.stl")
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
actor.GetProperty().SetOpacity(0.7)

# Create a single renderer
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.1, 0.2, 0.4)

# Add the STL actor first
renderer.AddActor(actor)

# Create and add marker
marker = create_marker(center_x, center_y, center_z, radius=marker_radius, color=(1.0, 0.0, 0.0))
renderer.AddActor(marker)

# Create render window
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)

# Enable transparency options
render_window.SetAlphaBitPlanes(1)
render_window.SetMultiSamples(0)
renderer.SetUseDepthPeeling(1)
renderer.SetMaximumNumberOfPeels(100)
renderer.SetOcclusionRatio(0.0)

# Create interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Add trackball camera controls
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
render_window_interactor.SetInteractorStyle(interactor_style)

# Reset camera
renderer.ResetCamera()

# Initialize and start
render_window.Render()
render_window_interactor.Initialize()
render_window_interactor.Start()