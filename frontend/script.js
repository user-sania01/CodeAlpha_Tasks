console.log("SCRIPT.JS IS WORKING");

// Getting elements from HTML

const inputText = document.getElementById("inputText");

const sourceLanguage =
    document.getElementById("sourceLanguage");

const targetLanguage =
    document.getElementById("targetLanguage");

const translateButton =
    document.getElementById("translateButton");

const translationResult =
    document.getElementById("translationResult");

const copyButton =
    document.getElementById("copyButton");

const speakButton =
    document.getElementById("speakButton");

const clearButton =
    document.getElementById("clearButton");

const characterCount =
    document.getElementById("characterCount");


// ------------------------------------
// CHARACTER COUNTER
// ------------------------------------

inputText.addEventListener("input", function () {

    const count = inputText.value.length;

    characterCount.textContent =
        `${count} / 5000`;

});


// ------------------------------------
// TRANSLATE BUTTON
// ------------------------------------

translateButton.addEventListener("click", async function () {

    console.log("TRANSLATE BUTTON CLICKED");

    const text = inputText.value.trim();

    const source = sourceLanguage.value;

    const target = targetLanguage.value;


    // Check if text is empty

    if (text === "") {

        translationResult.textContent =
            "Please enter some text to translate.";

        return;
    }


    // Show loading message

    translationResult.textContent =
        "Translating...";


    // Disable button

    translateButton.disabled = true;


    try {

        console.log("Sending translation request...");


        const response = await fetch(
            "http://localhost:5000/api/translate",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    text: text,

                    sourceLanguage: source,

                    targetLanguage: target

                })

            }
        );


        console.log(
            "Server response:",
            response.status
        );


        // Convert response to JSON

        const data = await response.json();


        // Check for error

        if (!response.ok) {

            throw new Error(
                data.error ||
                "Translation failed."
            );

        }


        // Display translation

        translationResult.textContent =
            data.translation;


        console.log("Translation displayed!");


    } catch (error) {

        console.error(
            "Translation error:",
            error
        );

        translationResult.textContent =
            "Unable to translate. Please try again.";

    }


    // Enable button again

    translateButton.disabled = false;

});


// ------------------------------------
// COPY BUTTON
// ------------------------------------

copyButton.addEventListener("click", async function () {

    const text =
        translationResult.textContent.trim();


    if (
        text === "" ||
        text === "Your translated text will appear here."
    ) {
        return;
    }


    try {

        await navigator.clipboard.writeText(text);

        copyButton.textContent =
            "✓ Copied!";


        setTimeout(function () {

            copyButton.textContent =
                "📋 Copy";

        }, 1500);


    } catch (error) {

        console.error(
            "Copy error:",
            error
        );

    }

});


// ------------------------------------
// SPEAK BUTTON
// ------------------------------------

speakButton.addEventListener("click", function () {

    const text =
        translationResult.textContent.trim();


    if (
        text === "" ||
        text === "Your translated text will appear here."
    ) {
        return;
    }


    // Stop previous speech

    window.speechSynthesis.cancel();


    const speech =
        new SpeechSynthesisUtterance(text);


    // Set language

    speech.lang =
        targetLanguage.value;


    // Speak

    window.speechSynthesis.speak(speech);

});


// ------------------------------------
// CLEAR BUTTON
// ------------------------------------

clearButton.addEventListener("click", function () {

    inputText.value = "";

    translationResult.textContent =
        "Your translated text will appear here.";

    characterCount.textContent =
        "0 / 5000";

});