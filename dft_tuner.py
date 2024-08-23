from time import sleep
import sounddevice as sd
import numpy as np
import scipy.fftpack as fftpack
import os

SAMPLE_FREQ = 44100
WINDOW_SIZE = 44100
WINDOW_STEP = 21050
WINDOW_T_LEN = WINDOW_SIZE / SAMPLE_FREQ
SAMPLE_T_LENGTH = 1 / SAMPLE_FREQ
window_samples = [0 for _ in range(WINDOW_SIZE)]

CONCERT_PITCH = 440
ALL_NOTES = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
def find_closest_note(pitch):
    i = int(np.round(np.log2(pitch / CONCERT_PITCH) *12))
    closest_note = ALL_NOTES[i % 12] + str(4 + (i + 9) // 12)
    closest_pitch = CONCERT_PITCH * 2 ** (i / 12)
    return closest_note, closest_pitch

def callback(input_data, frames, time, status):
    global window_samples
    if status:
        print(status)
    if any(input_data):
        window_samples = np.concatenate((window_samples, input_data[:, 0]))
        window_samples = window_samples[len(input_data[:, 0]):]
        magnitude_spectrum = abs(
            fftpack.fft(window_samples)[:len(window_samples) // 2])
        
        for i in range(int(62 / SAMPLE_FREQ / WINDOW_SIZE)):
            magnitude_spectrum[i] = 0
            
        max_ind = np.argmax(magnitude_spectrum)
        max_freq = max_ind * (SAMPLE_FREQ / WINDOW_SIZE)
        closest_note, closest_pitch = find_closest_note(max_freq)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f'Closest note: {closest_note} {max_freq:.1f} / {closest_pitch:.1f}')
    else:
        print('no input')

# my microphone = 1
# my audio interface = 2
def get_selected_device():
    devices = sd.query_devices()
    request = 'Enter index of input device\n'
    print('Printing list of available input devices:')
    sleep(1)
    for device in devices:
        print(f"{device['name']} | Index: {device['index']} | hostapi: {device['hostapi']}")
        sleep(0.3)
    print('')
    selected_device = int(input(request))
    while selected_device not in range(0, len(devices)):
        selected_device = int(input(request))
        
    return int(selected_device)

sd.default.device = get_selected_device()
try:
    with sd.InputStream(channels=1,
                        callback=callback,
                        blocksize=WINDOW_STEP,
                        samplerate=SAMPLE_FREQ):
        while True:
            pass
except Exception as e:
    print(str(e))
    