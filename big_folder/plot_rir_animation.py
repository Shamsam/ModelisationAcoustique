import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def plot_rir_animation(room, mics):
    if mics is None:
        mics = np.arange(room.mic_array.R.shape[1])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    if len(room.rir) == 0 or len(room.rir[0]) == 0:
        print("RIR is not calculated for the room.")
        return

    n_frames = len(room.rir[0][0])

    if n_frames == 0:
        print("RIR is not calculated for any microphone.")
        return

    def animate(i):
        if not isinstance(i, np.ndarray):
            i = np.array([i])
        ax.cla()
        ax.set_xlim3d([-10, 10])
        ax.set_ylim3d([-10, 10])
        ax.set_zlim3d([-0.5, 1.5])
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Amplitude')
        ax.set_title(f'Room Impulse Response - Time Frame {i}')

        for mic in mics:
            if mic >= room.mic_array.R.shape[1]:
                print(f"Microphone {mic} does not exist.")
                continue

            if mic >= len(room.rir):
                print(f"No RIR found for microphone {mic}.")
                continue

            rir = room.rir[mic][0]
            if rir is None or len(rir) == 0:
                print(f"RIR is not calculated for microphone {mic}.")
                continue

            if len(rir) <= i.max():
                print(f"Frame {i} is out of range for microphone {mic}.")
                continue

            if rir is not None and np.any(rir) and len(rir) > i.max():
                x = np.full((len(rir[:i.max()+1]),), room.mic_array.R[0, mic])
                y = np.full((len(rir[:i.max()+1]),), room.mic_array.R[1, mic])
                z = rir[:i.max()+1]
                ax.plot(x, y, z, 'r')
                sources = room.sources
                if sources is not None and len(sources) > 0:
                    xs, ys = sources[0].position[:2]
                    zs = 0
                    ax.plot(xs, ys, zs, 'bo')

    ani = animation.FuncAnimation(fig, animate, frames=n_frames, interval=50, blit=False)
    plt.show()