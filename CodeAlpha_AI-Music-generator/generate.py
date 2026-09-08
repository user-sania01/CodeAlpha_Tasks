
import os
import pickle
import numpy as np
import tensorflow as tf
from mido import MidiFile, MidiTrack, Message

MODEL_FILE = "models/music_model.keras"
DATA_FILE = "data/processed/drum_sequences.pkl"
OUTPUT_FILE = "generated_music.mid"

SEQUENCE_LENGTH = 32
GENERATED_NOTES = 100

print("=" * 60)
print("🎵 MuseAI - AI MUSIC GENERATOR")
print("=" * 60)

# Load model
print("🤖 Loading trained model...")
model = tf.keras.models.load_model(MODEL_FILE)

# Load training data
with open(DATA_FILE, "rb") as file:
    sequences = pickle.load(file)

# Pick a random starting sequence
seed = list(sequences[np.random.randint(len(sequences))])
seed = seed[:SEQUENCE_LENGTH]

generated = seed.copy()

print("🎼 Generating new music...")

for _ in range(GENERATED_NOTES):
    input_sequence = np.array(generated[-SEQUENCE_LENGTH:])
    input_sequence = input_sequence / 127.0
    input_sequence = input_sequence.reshape(1, SEQUENCE_LENGTH, 1)

    prediction = model.predict(input_sequence, verbose=0)

    next_note = int(np.argmax(prediction[0]))

    generated.append(next_note)

# Create MIDI file
print("🎹 Creating MIDI file...")

midi = MidiFile(ticks_per_beat=480)
track = MidiTrack()
midi.tracks.append(track)

track.append(Message("program_change", program=0, time=0))

for note in generated:
    note = max(0, min(127, note))

    track.append(
        Message(
            "note_on",
            note=note,
            velocity=80,
            time=0
        )
    )

    track.append(
        Message(
            "note_off",
            note=note,
            velocity=0,
            time=240
        )
    )

midi.save(OUTPUT_FILE)

print()
print("=" * 60)
print("✅ MUSIC GENERATED!")
print("=" * 60)
print(f"🎵 Output file: {OUTPUT_FILE}")
print("=" * 60)