from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pickle
import numpy as np
import tensorflow as tf
from mido import MidiFile, MidiTrack, Message


# ==========================================
# MUSEAI - FLASK APPLICATION
# ==========================================

app = Flask(
    __name__,
    static_folder="frontend",
    static_url_path=""
)

CORS(app)


# ==========================================
# FILE PATHS
# ==========================================

MODEL_FILE = "models/music_model.keras"
DATA_FILE = "data/processed/drum_sequences.pkl"
OUTPUT_FILE = "generated_music.mid"

SEQ_LENGTH = 32


# ==========================================
# LOAD AI MODEL + DATA
# ==========================================

print("🎵 Loading MuseAI model...")

model = tf.keras.models.load_model(MODEL_FILE)

with open(DATA_FILE, "rb") as file:
    sequences = pickle.load(file)

print("✅ Model loaded")
print(f"✅ {len(sequences)} music sequences loaded")


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return send_from_directory(
        "frontend",
        "index.html"
    )


# ==========================================
# AI MUSIC GENERATION
# ==========================================

@app.route("/api/generate", methods=["POST"])
def generate_music():

    try:

        data = request.get_json() or {}

        genre = data.get("genre", "Lo-Fi")
        mood = data.get("mood", "Calm")
        length = data.get("length", "Medium")


        # --------------------------------------
        # LENGTH SETTINGS
        # --------------------------------------

        length_map = {
            "Short": 50,
            "Medium": 100,
            "Long": 160
        }

        generated_notes_count = length_map.get(
            length,
            100
        )


        # --------------------------------------
        # GENRE SETTINGS
        # Controls rhythm variation
        # --------------------------------------

        genre_settings = {

            "Lo-Fi": {
                "density": 0.55,
                "temperature": 0.08
            },

            "Pop": {
                "density": 0.70,
                "temperature": 0.10
            },

            "Hip-Hop": {
                "density": 0.80,
                "temperature": 0.12
            },

            "Rock": {
                "density": 0.90,
                "temperature": 0.08
            },

            "Electronic": {
                "density": 0.85,
                "temperature": 0.14
            }
        }

        settings = genre_settings.get(
            genre,
            {
                "density": 0.65,
                "temperature": 0.10
            }
        )

        density = settings["density"]
        temperature = settings["temperature"]


        # --------------------------------------
        # MOOD SETTINGS
        # Controls tempo
        # --------------------------------------

        mood_tempo = {

            "Calm": 70,

            "Dreamy": 78,

            "Happy": 105,

            "Energetic": 135,

            "Dark": 82,

            "Focused": 95
        }

        tempo = mood_tempo.get(
            mood,
            90
        )


        # --------------------------------------
        # SELECT RANDOM TRAINING SEQUENCE
        # --------------------------------------

        seed = list(
            sequences[
                np.random.randint(
                    len(sequences)
                )
            ]
        )


        if len(seed) < SEQ_LENGTH:

            return jsonify({
                "success": False,
                "error": "Selected sequence is too short."
            }), 400


        seed = seed[:SEQ_LENGTH]

        generated = seed.copy()


        # --------------------------------------
        # LSTM GENERATION
        # --------------------------------------

        for _ in range(generated_notes_count):

            input_sequence = np.array(
                generated[-SEQ_LENGTH:],
                dtype=np.float32
            )


            input_sequence = (
                input_sequence / 127.0
            )


            input_sequence = input_sequence.reshape(
                1,
                SEQ_LENGTH,
                1
            )


            prediction = model.predict(
                input_sequence,
                verbose=0
            )


            probabilities = prediction[0].copy()


            # ----------------------------------
            # CONTROL RANDOMNESS
            # ----------------------------------

            probabilities = (
                probabilities
                + (
                    np.random.random(
                        len(probabilities)
                    ) * temperature
                )
            )


            # ----------------------------------
            # GENRE-BASED RHYTHMIC VARIATION
            # ----------------------------------

            if np.random.random() > density:

                probabilities *= 0.65


            next_note = int(
                np.argmax(probabilities)
            )


            # Keep MIDI value valid

            next_note = max(
                0,
                min(127, next_note)
            )


            generated.append(
                next_note
            )


        # ======================================
        # CREATE MIDI FILE
        # ======================================

        midi = MidiFile(
            ticks_per_beat=480
        )

        track = MidiTrack()

        midi.tracks.append(track)


        # MIDI channel 9 = percussion

        step_time = max(
            60,
            int(
                60000 / tempo / 4
            )
        )


        for note in generated:

            note = max(
                0,
                min(127, int(note))
            )


            track.append(
                Message(
                    "note_on",
                    channel=9,
                    note=note,
                    velocity=80,
                    time=0
                )
            )


            track.append(
                Message(
                    "note_off",
                    channel=9,
                    note=note,
                    velocity=0,
                    time=step_time
                )
            )


        midi.save(
            OUTPUT_FILE
        )


        print(
            f"🎼 Generated: "
            f"{genre} | "
            f"{mood} | "
            f"{length}"
        )


        # ======================================
        # SEND RESULT TO WEBSITE
        # ======================================

        return jsonify({

            "success": True,

            "message":
                "Music generated successfully!",

            "genre":
                genre,

            "mood":
                mood,

            "length":
                length,

            "tempo":
                tempo,

            "download_url":
                "/api/download",

            "notes":
                generated
        })


    except Exception as e:

        print(
            "❌ Generation error:",
            e
        )


        return jsonify({

            "success": False,

            "error":
                str(e)

        }), 500


# ==========================================
# DOWNLOAD MIDI
# ==========================================

@app.route("/api/download")
def download_music():

    if not os.path.exists(
        OUTPUT_FILE
    ):

        return jsonify({

            "error":
                "No generated music found."

        }), 404


    return send_from_directory(

        ".",

        OUTPUT_FILE,

        as_attachment=True
    )


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    print()

    print("=" * 55)

    print(
        "🎵 MUSEAI — AI MUSIC GENERATOR"
    )

    print("=" * 55)

    print(
        "🌐 Website: "
        "http://127.0.0.1:5000"
    )

    print("=" * 55)

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True
    )