import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt

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

room_dim = [5, 4, 3]
absorption = 0.5

src_positions = np.array([
    [1, 1, 1.5],
    [3, 1, 1.5],
    [2, 1, 1.5]
])

x = np.linspace(0, room_dim[0], 11)
y = np.linspace(0, room_dim[1], 11)
z = np.linspace(0, room_dim[2], 11)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

sound_level_sources = [np.zeros_like(X) for _ in range(len(src_positions))]

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
                sound_level_sources[src_idx][i, j, k] = np.sum(np.square(rir))

for src_idx, sound_level in enumerate(sound_level_sources):
    sound_level /= np.max(sound_level)

    fig, axs = plt.subplots(1, len(z), figsize=(10 * len(z), 10), sharey=True)

    for k, zk in enumerate(z):
        im = plot_2d_slice(axs[k], sound_level[:, :, k].T, 'XY', zk, [src_positions[src_idx]], room_dim)
        if k > 0:
            axs[k].set_ylabel("")
        if k > 0:
            axs[k].set_title(f'{zk:.1f}')

    fig.subplots_adjust(right=0.8, wspace=0.5)
    cbar_ax = fig.add_axes([0.85, 0.15, 0.05, 0.7])
    cbar = plt.colorbar(im, cax=cbar_ax)
    cbar.set_label('Normalized Sound Level')

    plt.suptitle(f'Sound Level Distribution for Source {src_idx+1}', fontsize=16, y=1.05)
    plt.show()
