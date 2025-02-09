import vtk

# Create an STL reader and specify the file name
stl_reader = vtk.vtkSTLReader()
stl_reader.SetFileName("bph_mold_meshsolid.stl")
stl_reader.Update()  # Optional: forces the reader to update immediately

# Create a mapper that will take the output of the STL reader
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(stl_reader.GetOutputPort())

# Create an actor to represent the STL model
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Optionally, adjust the actor's properties (color, opacity, etc.)
actor.GetProperty().SetColor(1.0, 0.8, 0.3)  # Example: set a custom color

# Create a renderer and add the actor to it
renderer = vtk.vtkRenderer()
renderer.AddActor(actor)
renderer.SetBackground(0.1, 0.2, 0.4)  # Set a background color

# Create a render window and add the renderer
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)

# Create a render window interactor to handle user input
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Initialize and start the render loop
render_window.Render()
render_window_interactor.Initialize()
render_window_interactor.Start()