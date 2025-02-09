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
stl_reader.SetFileName("bph_mold_meshsolid.stl")
stl_reader.Update()

# Create a mapper that will take the output of the STL reader
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stl_reader.GetOutputPort())

# Create an actor to represent the STL model
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 0.8, 0.3)
actor.GetProperty().SetOpacity(0.7)  # Make the model slightly transparent

# Create a renderer and add the actor to it
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)

# Example: Add multiple markers at different coordinates
# You can add more markers by calling create_marker with different coordinates
markers = [
    create_marker(10, 10, 10, radius=0.5, color=(1.0, 0.0, 0.0)),  # Red marker
    create_marker(20, 20, 20, radius=0.5, color=(0.0, 1.0, 0.0)),  # Green marker
    create_marker(30, 30, 30, radius=0.5, color=(0.0, 0.0, 1.0))   # Blue marker
]

# Add all markers to the renderer
for marker in markers:
    renderer.AddActor(marker)

# Create a render window and add the renderer
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)

# Create a render window interactor to handle user input
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Add trackball camera controls
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
render_window_interactor.SetInteractorStyle(interactor_style)

# Initialize and start the render loop
render_window.Render()
render_window_interactor.Initialize()
render_window_interactor.Start()