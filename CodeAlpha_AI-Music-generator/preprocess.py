
import os
import pickle
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

DATA_FILE = "data/processed/drum_sequences.pkl"
MODEL_FILE = "models/music_model.keras"

print("=" * 60)
print("🎵 MuseAI - LSTM MUSIC MODEL TRAINING")
print("=" * 60)

# Load processed sequences
with open(DATA_FILE, "rb") as file:
    sequences = pickle.load(file)

print(f"📂 Loaded sequences: {len(sequences)}")

# Prepare training data
X = []
y = []

SEQ_LENGTH = 32

for sequence in sequences:
    if len(sequence) <= SEQ_LENGTH:
        continue

    for i in range(len(sequence) - SEQ_LENGTH):
        X.append(sequence[i:i + SEQ_LENGTH])
        y.append(sequence[i + SEQ_LENGTH])

if not X:
    print("❌ Not enough data to train.")
    exit()

X = np.array(X)
y = np.array(y)

print(f"🎼 Training samples: {len(X)}")

# Normalize MIDI notes
X = X / 127.0
y = y / 127.0

# Reshape for LSTM
X = X.reshape((X.shape[0], X.shape[1], 1))

print(f"📐 Input shape: {X.shape}")

# Build model
model = Sequential([
    LSTM(128, input_shape=(SEQ_LENGTH, 1), return_sequences=True),
    Dropout(0.2),

    LSTM(128),
    Dropout(0.2),

    Dense(64, activation="relu"),
    Dense(128, activation="softmax")
])

model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam"
)

print()
print("🚀 Starting training...")
print()

# Convert target back to integer MIDI values
y = np.clip(y * 127, 0, 127).astype(np.int32)

model.fit(
    X,
    y,
    epochs=20,
    batch_size=32,
    verbose=1
)

# Save model
os.makedirs("models", exist_ok=True)
model.save(MODEL_FILE)

print()
print("=" * 60)
print("✅ TRAINING COMPLETE")
print("=" * 60)
print(f"💾 Model saved to: {MODEL_FILE}")
print("=" * 60)