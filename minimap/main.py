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

# ---------------------------
# Create the STL Actor (Layer 0)
# ---------------------------
stl_reader = vtk.vtkSTLReader()
stl_reader.SetFileName("/Users/Ayeeshi/Documents/DT03/bph_mold_meshsolid.stl")
stl_reader.Update()

mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stl_reader.GetOutputPort())

stl_actor = vtk.vtkActor()
stl_actor.SetMapper(mapper)
stl_actor.GetProperty().SetColor(1.0, 0.8, 0.3)
stl_actor.GetProperty().SetOpacity(0.7)  # Make the model slightly transparent

# ---------------------------
# Create Marker Actor (Layer 1)
# ---------------------------
marker = create_marker(10, 10, 10, radius=0.5, color=(1.0, 0.0, 0.0))

# Renderer for the STL model (Layer 0)
renderer = vtk.vtkRenderer()
renderer.AddActor(stl_actor)
renderer.SetBackground(0.1, 0.2, 0.4)
renderer.SetLayer(0)

# Renderer for the marker (Layer 1)
marker_renderer = vtk.vtkRenderer()
marker_renderer.AddActor(marker)
marker_renderer.SetBackground(0, 0, 0)
marker_renderer.SetLayer(1)

# ---------------------------
# Setup Render Window and Interactor with Multiple Layers
# ---------------------------
render_window = vtk.vtkRenderWindow()
render_window.SetNumberOfLayers(2)
render_window.AddRenderer(renderer)
render_window.AddRenderer(marker_renderer)
render_window.SetSize(800, 600)

render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)
interactor_style = vtk.vtkInteractorStyleTrackballCamera()
render_window_interactor.SetInteractorStyle(interactor_style)

# ---------------------------
# Timer Callback for Updating Coordinates (for Marker)
# ---------------------------
class TimerCallback:
    def __init__(self, filename, actor):
        self.file = open(filename, "r")
        self.actor = actor
        self.timer_id = None

    def execute(self, obj, event):
        line = self.file.readline()
        if not line:
            print("End of coordinate file reached. Stopping timer.")
            self.file.close()
            # Stop the timer when end-of-file is reached.
            obj.DestroyTimer(self.timer_id)
            return

        line = line.strip()
        if not line:
            return  # Skip empty lines

        try:
            parts = line.split()
            if len(parts) != 3:
                print("Invalid coordinate line:", line)
                return
            x, y, z = map(float, parts)
        except ValueError:
            print("Could not convert line to floats:", line)
            return

        # Update the marker's position
        self.actor.SetPosition(x, y, z)
        print(f"Moving marker to: ({x}, {y}, {z})")
        obj.GetRenderWindow().Render()

# Create an instance of the callback with the coordinates file and the marker actor to update.
callback = TimerCallback("/Users/Ayeeshi/Documents/DT03/aeep_simulation/minimap/coordinates.txt", marker)

# Add the timer callback observer.
render_window_interactor.AddObserver('TimerEvent', callback.execute)
# Create a repeating timer event (every 1000 milliseconds in this example)
timer_id = render_window_interactor.CreateRepeatingTimer(1000)
callback.timer_id = timer_id

# ---------------------------
# Start the Render Window Interactor
# ---------------------------
render_window.Render()
render_window_interactor.Start()