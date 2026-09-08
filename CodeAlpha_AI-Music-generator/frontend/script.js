
const generateBtn = document.getElementById("generateBtn");
const statusText = document.getElementById("status");

let generatedNotes = [];
let isPlaying = false;
let stopPlayback = false;


generateBtn.addEventListener("click", async () => {

    const genre = document.getElementById("genre").value;
    const mood = document.getElementById("mood").value;
    const length = document.getElementById("length").value;

    generateBtn.disabled = true;
    generateBtn.innerHTML = "✦ Creating your music...";

    statusText.innerHTML =
        "MuseAI is composing something special...";

    try {

        const response = await fetch("/api/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                genre: genre,
                mood: mood,
                length: length
            })
        });

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || "Something went wrong.");
        }

        generatedNotes = result.notes;

        statusText.innerHTML = `
            <div class="music-result">

                <div class="result-icon">♫</div>

                <div class="result-content">

                    <h3>Your track is ready ✨</h3>

                    <p>
                        ${result.genre} ·
                        ${result.mood} ·
                        ${result.length}
                    </p>

                    <div class="result-actions">

                        <button
                            class="preview-button"
                            id="previewBtn"
                        >
                            ▶ Play Preview
                        </button>

                        <a
                            href="${result.download_url}"
                            class="download-link"
                        >
                            <span>↓</span>
                            Download MIDI
                        </a>

                    </div>

                </div>

            </div>
        `;

        const previewBtn =
            document.getElementById("previewBtn");

        previewBtn.addEventListener(
            "click",
            playPreview
        );

    } catch (error) {

        console.error(error);

        statusText.innerHTML = `
            <div class="error-message">
                Something went wrong while creating your music.
            </div>
        `;

    } finally {

        generateBtn.disabled = false;
        generateBtn.innerHTML =
            `<span class="sparkle">✦</span>
             Generate Music
             <span class="arrow">→</span>`;

    }
});


async function playPreview() {

    const previewBtn =
        document.getElementById("previewBtn");

    if (isPlaying) {

        stopPlayback = true;
        isPlaying = false;

        previewBtn.innerHTML =
            "▶ Play Preview";

        return;
    }

    if (!generatedNotes.length) {
        return;
    }

    isPlaying = true;
    stopPlayback = false;

    previewBtn.innerHTML =
        "■ Stop Preview";

    const AudioContext =
        window.AudioContext ||
        window.webkitAudioContext;

    const audioContext =
        new AudioContext();

    /*
       Common General MIDI drum sounds:
       36 = Kick
       38 = Snare
       42 = Closed Hi-Hat
       46 = Open Hi-Hat
    */

    const drumNotes = [
        36, 38, 42, 46, 49, 51
    ];

    for (
        let i = 0;
        i < generatedNotes.length;
        i++
    ) {

        if (stopPlayback) {
            break;
        }

        const note =
            generatedNotes[i];

        playDrumSound(
            audioContext,
            note
        );

        await sleep(130);
    }

    await audioContext.close();

    isPlaying = false;
    stopPlayback = false;

    if (previewBtn) {
        previewBtn.innerHTML =
            "▶ Play Preview";
    }
}


function playDrumSound(
    audioContext,
    midiNote
) {

    const oscillator =
        audioContext.createOscillator();

    const gain =
        audioContext.createGain();

    oscillator.connect(gain);
    gain.connect(audioContext.destination);

    /*
       Map generated MIDI values
       to a small percussion palette.
    */

    const soundType =
        midiNote % 6;

    let frequency;

    if (soundType === 0) {
        // Kick
        frequency = 100;
    }
    else if (soundType === 1) {
        // Snare
        frequency = 180;
    }
    else if (soundType === 2) {
        // Hi-hat
        frequency = 420;
    }
    else if (soundType === 3) {
        // Open hat
        frequency = 520;
    }
    else if (soundType === 4) {
        // Percussion
        frequency = 260;
    }
    else {
        // Higher percussion
        frequency = 340;
    }

    oscillator.frequency.setValueAtTime(
        frequency,
        audioContext.currentTime
    );

    gain.gain.setValueAtTime(
        0.0001,
        audioContext.currentTime
    );

    gain.gain.exponentialRampToValueAtTime(
        0.35,
        audioContext.currentTime + 0.01
    );

    gain.gain.exponentialRampToValueAtTime(
        0.0001,
        audioContext.currentTime + 0.12
    );

    oscillator.start();

    oscillator.stop(
        audioContext.currentTime + 0.13
    );
}


function sleep(milliseconds) {
    return new Promise(
        resolve =>
            setTimeout(resolve, milliseconds)
    );
}