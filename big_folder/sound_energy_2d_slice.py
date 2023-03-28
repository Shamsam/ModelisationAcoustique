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
x = np.linspace(0, room_dim[0], 11) # 11 points in the x-direction
y = np.linspace(0, room_dim[1], 11)
z = np.linspace(0, room_dim[2], 11)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij') # Create a 3D grid of points

# Calculate the sound level at each point in the grid
sound_level = np.zeros_like(X)

for i, xi in enumerate(x):
    for j, yj in enumerate(y):
        for k, zk in enumerate(z):
            room = pra.ShoeBox(room_dim, fs=16000, absorption=absorption, max_order=3) 
            mic_pos = np.array([xi, yj, zk]) # The microphone position is the current grid point
            room.add_microphone(mic_pos)

            for src_pos in src_positions:
                room.add_source(src_pos)

            room.compute_rir()
            for src_idx in range(len(src_positions)): # Sum the sound level from each source
                rir = room.rir[0][src_idx]
                sound_level[i, j, k] += np.sum(np.square(rir))

# Normalize sound level
sound_level /= np.max(sound_level)

def plot_2d_slice(ax, plane_data, plane, fixed_axis_val, src_positions, room_dim, cmap='viridis'): 
    # Plot the 2D slice of the sound level
    im = ax.imshow(plane_data, cmap=cmap, origin='lower',
                   extent=[0, room_dim[0], 0, room_dim[1]]) 
    ax.set_xlabel('X')
    ax.set_ylabel('Y')

    for src_pos in src_positions: # Plot the source positions
        ax.scatter(src_pos[0], src_pos[1], color='red', marker='x', s=10)

    ax.set_title(f'{plane}-plane at {fixed_axis_val}')
    return im # Return the image so we can add a colorbar

fig, axs = plt.subplots(1, len(z), figsize=(5 * len(z), 5), sharey=True) # Create a figure with a subplot for each z-slice

for k, zk in enumerate(z): # Plot each z-slice
    im = plot_2d_slice(axs[k], sound_level[:, :, k].T, 'XY', zk, src_positions, room_dim)
    if k > 0: # Hide the y-axis label for all but the first subplot
        axs[k].set_ylabel("")
    if k > 0: # Hide the y-axis ticks for all but the first subplot
        axs[k].set_title(f'{zk:.1f}')

fig.subplots_adjust(right=0.8, wspace=1) # Adjust the spacing between subplots
cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7]) # Create an axes for the colorbar
cbar = plt.colorbar(im, cax=cbar_ax) # Add a colorbar
cbar.set_label('Normalized Sound Level')

plt.show()


