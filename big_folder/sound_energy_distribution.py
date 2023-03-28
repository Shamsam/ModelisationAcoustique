import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

room_dim = [5, 4, 3]
absorption = 0.5

src_positions = np.array([
    [1, 1, 1.5],
    [3, 1, 1.5],
    [2, 1, 1.5]
])

# Define a grid for the room
x = np.linspace(0, room_dim[0], 11)
y = np.linspace(0, room_dim[1], 11)
z = np.linspace(0, room_dim[2], 11)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

# Calculate the sound level at each point in the grid
sound_level = np.zeros_like(X)

for i, xi in enumerate(x):
    for j, yj in enumerate(y):
        for k, zk in enumerate(z):
            room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3)
            mic_pos = np.array([xi, yj, zk])
            room.add_microphone(mic_pos)

            for src_pos in src_positions:
                room.add_source(src_pos)

            room.compute_rir()
            for src_idx in range(len(src_positions)):
                rir = room.rir[0][src_idx]
                sound_level[i, j, k] += np.sum(np.square(rir))

# Normalize sound level
sound_level /= np.max(sound_level)

# Create a 3D scatter plot
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

for src_pos in src_positions:
    ax.scatter(*src_pos, color='red', marker='x', s=100)

scatter = ax.scatter(X, Y, Z, c=sound_level.flatten(), cmap='viridis', alpha=0.5)

ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Scatter Plot of Sound Level in the Room')

cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Normalized Sound Level')

plt.show()

