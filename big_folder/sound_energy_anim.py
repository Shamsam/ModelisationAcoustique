import numpy as np
import pyroomacoustics as pra
import matplotlib.pyplot as plt
import matplotlib.animation as animation

room_dim = [5, 4, 3]
absorption = 0.5
fs = 16000
time_step = 0.01  # time step in seconds

src_positions = np.array([
    [1, 1, 1.5],
    [3, 1, 1.5],
    [2, 1, 1.5]
])

x = np.linspace(0, room_dim[0], 11)
y = np.linspace(0, room_dim[1], 11)
z = np.linspace(0, room_dim[2], 11)
X, Y, Z = np.meshgrid(x, y, z, indexing='ij')

n_time_frames = int(fs * time_step)

sound_level_time = np.zeros((len(x), len(y), len(z), n_time_frames))

for i, xi in enumerate(x):
    for j, yj in enumerate(y):
        for k, zk in enumerate(z):
            room = pra.ShoeBox(room_dim, fs=fs, absorption=absorption, max_order=3)
            mic_pos = np.array([xi, yj, zk])
            room.add_microphone(mic_pos)

            for src_pos in src_positions:
                room.add_source(src_pos)

            room.compute_rir()

            for src_idx in range(len(src_positions)):
                rir = room.rir[0][src_idx]
                for t in range(n_time_frames):
                    sound_level_time[i, j, k, t] += rir[t] ** 2

sound_level_time /= np.max(sound_level_time)

fig, axs = plt.subplots(1, len(z), figsize=(10 * len(z), 10), sharey=True)

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

def update(frame):
    for k, zk in enumerate(z):
        axs[k].clear()
        im = plot_2d_slice(axs[k], sound_level_time[:, :, k, frame].T, 'XY', zk, src_positions, room_dim, cmap='viridis')
        axs[k].set_title(f'Z = {zk:.1f} | Frame: {frame}')


ani = animation.FuncAnimation(fig, update, frames=n_time_frames, interval=50, repeat=True)

plt.show()
