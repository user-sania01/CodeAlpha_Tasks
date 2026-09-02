
const express = require("express");
const cors = require("cors");

const app = express();

const PORT = 5000;


// ------------------------------------
// Middleware
// ------------------------------------

app.use(cors());

app.use(express.json());


// ------------------------------------
// Test Route
// ------------------------------------

app.get("/", (req, res) => {

    res.json({
        message: "AI Translation Server is running!"
    });

});


// ------------------------------------
// Translation Route
// ------------------------------------

app.post("/api/translate", async (req, res) => {

    console.log("Translation request received!");

    try {

        const {
            text,
            sourceLanguage,
            targetLanguage
        } = req.body;


        console.log("Text:", text);
        console.log("From:", sourceLanguage);
        console.log("To:", targetLanguage);


        // ------------------------------------
        // Validate input
        // ------------------------------------

        if (!text || !targetLanguage) {

            return res.status(400).json({

                error:
                    "Text and target language are required."

            });

        }


        // ------------------------------------
        // MyMemory uses normal language codes
        // ------------------------------------

        let source = sourceLanguage;

        if (source === "auto") {

            source = "en";

        }


        // ------------------------------------
        // Create API URL
        // ------------------------------------

        const url =
            "https://api.mymemory.translated.net/get?" +
            "q=" + encodeURIComponent(text) +
            "&langpair=" +
            encodeURIComponent(source) +
            "|" +
            encodeURIComponent(targetLanguage);


        console.log("Calling MyMemory API...");


        // ------------------------------------
        // Send request
        // ------------------------------------

        const response =
            await fetch(url);


        const data =
            await response.json();


        // ------------------------------------
        // Check API response
        // ------------------------------------

        if (!response.ok) {

            throw new Error(
                "Translation service returned an error."
            );

        }


        // ------------------------------------
        // Get translation
        // ------------------------------------

        const translation =
            data.responseData &&
            data.responseData.translatedText;


        if (!translation) {

            throw new Error(
                "No translation was returned."
            );

        }


        console.log(
            "Translation completed:",
            translation
        );


        // ------------------------------------
        // Send translation to frontend
        // ------------------------------------

        res.json({

            translation: translation

        });


    } catch (error) {

        console.error(
            "Translation error:",
            error
        );


        res.status(500).json({

            error:
                error.message ||
                "Translation failed."

        });

    }

});


// ------------------------------------
// Start Server
// ------------------------------------

app.listen(PORT, () => {

    console.log(
        `Server running on http://localhost:${PORT}`
    );

});