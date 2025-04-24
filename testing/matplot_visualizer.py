import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from stl import mesh

# ===== CONFIGURATION =====
stl_path = "C:/Users/kayla/.spyder-py3/DT3_Local/bph_mold_combined.stl"
scale_factor = 1.5

# ===== LOAD STL FILE =====
your_mesh = mesh.Mesh.from_file(stl_path)

# Apply scaling
your_mesh.vectors *= scale_factor

# Translate so origin is at (0, 0, 0)
min_bounds = your_mesh.vectors.min(axis=(0, 1))
your_mesh.vectors -= min_bounds

# ===== SETUP PLOT =====
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_box_aspect([1, 1, 1])  # Equal aspect ratio

# Create a Poly3DCollection and set alpha (opacity) for transparency
collection = Poly3DCollection(your_mesh.vectors, alpha=0.1, edgecolor='gray', facecolor='white')
ax.add_collection3d(collection)

# Set limits based on mesh size
mesh_max = your_mesh.vectors.max(axis=(0, 1))
ax.set_xlim(0, mesh_max[0])
ax.set_ylim(0, mesh_max[1])
ax.set_zlim(0, mesh_max[2])

# Show plot
plt.show()
