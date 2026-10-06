// ==========================================
// FACT SHIELD AI - FRONTEND JAVASCRIPT
// ==========================================

let selectedType = "news";
let selectedFile = null;


// ==========================================
// SELECT ANALYSIS TYPE
// ==========================================

function selectType(type, button) {

    selectedType = type;

    // Remove active state
    document.querySelectorAll(".type-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    // Add active state
    if (button) {
        button.classList.add("active");
    }

    const textInput = document.getElementById("textInput");

    const placeholders = {

        news:
            "Paste the news, claim or information you want to verify...",

        internship:
            "Paste the internship offer or message you want to check...",

        email:
            "Paste the email or message you want to analyze...",

        pdf:
            "Upload a PDF document to analyze...",

        image:
            "Upload an image to analyze...",

        url:
            "Paste a website URL to analyze..."
    };

    if (textInput) {
        textInput.placeholder =
            placeholders[type] || placeholders.news;
    }
}


// ==========================================
// FILE SELECTION
// ==========================================

function handleFileSelect(event) {

    selectedFile = event.target.files[0];

    const fileName =
        document.getElementById("fileName");

    if (selectedFile) {

        fileName.textContent =
            "📎 Selected: " + selectedFile.name;

    } else {

        fileName.textContent = "";
    }
}


// ==========================================
// ANALYZE CONTENT
// ==========================================

async function analyzeContent() {

    const textInput =
        document.getElementById("textInput");

    const loading =
        document.getElementById("loading");

    const result =
        document.getElementById("result");

    const text =
        textInput.value.trim();


    // Check input
    if (!text && !selectedFile) {

        result.innerHTML = `
            <div class="result-card">

                <h2>⚠️ Nothing to Analyze</h2>

                <p>
                    Please enter a claim, news article,
                    internship offer or upload a file.
                </p>

            </div>
        `;

        return;
    }


    // Show loading
    loading.style.display = "block";

    result.innerHTML = "";


    try {

        let response;


        // ======================================
        // FILE ANALYSIS
        // ======================================

        if (selectedFile) {

            const formData =
                new FormData();

            formData.append(
                "file",
                selectedFile
            );


            response = await fetch(
                "http://127.0.0.1:8000/analyze-file",
                {
                    method: "POST",
                    body: formData
                }
            );
        }


        // ======================================
        // TEXT ANALYSIS
        // ======================================

        else {

            response = await fetch(
                "http://127.0.0.1:8000/analyze",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        text: text
                    })
                }
            );
        }


        // ======================================
        // READ RESPONSE
        // ======================================

        const data =
            await response.json();


        console.log(
            "FACT SHIELD BACKEND RESPONSE:",
            data
        );


        // Server error
        if (!response.ok) {

            throw new Error(
                data.detail ||
                "The server returned an error."
            );
        }


        // Display result
        displayResult(data);


    } catch (error) {

        console.error(
            "FACT SHIELD ERROR:",
            error
        );


        result.innerHTML = `

            <div class="result-card">

                <h2>❌ Analysis Failed</h2>

                <p>
                    ${escapeHTML(error.message)}
                </p>

                <br>

                <p>
                    Make sure your FastAPI backend
                    is running at:
                </p>

                <strong>
                    http://127.0.0.1:8000
                </strong>

            </div>

        `;

    } finally {

        // Hide loading
        loading.style.display = "none";
    }
}


// ==========================================
// DISPLAY RESULT
// ==========================================

function displayResult(data) {

    const result =
        document.getElementById("result");


    console.log(
        "Displaying:",
        data
    );


    // ------------------------------------------
    // Helper: convert objects to readable text
    // ------------------------------------------

    function formatValue(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }


        // Array
        if (Array.isArray(value)) {

            if (value.length === 0) {
                return "None";
            }

            return value
                .map(item =>
                    `<div style="margin:6px 0;">
                        ${formatValue(item)}
                    </div>`
                )
                .join("");
        }


        // Object
        if (typeof value === "object") {

            return Object.entries(value)
                .map(([key, val]) => {

                    return `
                        <div style="
                            margin:8px 0;
                            padding:8px;
                            border-radius:8px;
                            background:rgba(255,255,255,0.6);
                        ">

                            <strong>
                                ${formatKey(key)}:
                            </strong>

                            ${formatValue(val)}

                        </div>
                    `;
                })
                .join("");
        }


        // Normal value
        return escapeHTML(
            String(value)
        );
    }


    // ------------------------------------------
    // Helper: format key names
    // ------------------------------------------

    function formatKey(key) {

        return String(key)
            .replace(/_/g, " ")
            .replace(/\b\w/g, letter =>
                letter.toUpperCase()
            );
    }


    // ------------------------------------------
    // Get backend fields
    // ------------------------------------------

    const assessment =
        data.assessment ??
        data.result ??
        data.verdict ??
        data.status ??
        "Analysis Complete";


    const confidence =
        data.confidence ??
        data.score ??
        null;


    const explanation =
        data.explanation ??
        data.message ??
        data.reason ??
        "The information has been analyzed.";


    const warnings =
        data.warning_indicators ??
        data.warnings ??
        data.risk_indicators ??
        [];


    // ------------------------------------------
    // Warning display
    // ------------------------------------------

    let warningHTML = "";


    if (
        Array.isArray(warnings) &&
        warnings.length > 0
    ) {

        warningHTML = warnings
            .map(item => {

                return `
                    <li style="
                        margin:8px 0;
                    ">
                        ⚠️ ${formatValue(item)}
                    </li>
                `;
            })
            .join("");

    }

    else if (
        typeof warnings === "object" &&
        warnings !== null
    ) {

        warningHTML = `
            <li style="
                margin:8px 0;
            ">
                ⚠️ ${formatValue(warnings)}
            </li>
        `;

    }

    else {

        warningHTML = `
            <li style="
                margin:8px 0;
            ">
                ✅ No warning indicators returned.
            </li>
        `;
    }


    // ------------------------------------------
    // Confidence
    // ------------------------------------------

    let confidenceHTML = "";

    if (confidence !== null) {

        confidenceHTML = `

            <div style="
                margin-top:20px;
                padding:16px;
                border-radius:15px;
                background:linear-gradient(
                    135deg,
                    #e0f2fe,
                    #ede9fe
                );
            ">

                <h3>📊 Confidence</h3>

                <p style="
                    font-size:20px;
                    font-weight:700;
                    margin-top:8px;
                ">
                    ${formatValue(confidence)}%
                </p>

            </div>

        `;
    }


    // ------------------------------------------
    // Final result UI
    // ------------------------------------------

    result.innerHTML = `

        <div class="result-card">

            <h2>
                🔍 Analysis Result
            </h2>


            <div style="
                margin-top:20px;
                padding:20px;
                border-radius:18px;

                background:
                    linear-gradient(
                        135deg,
                        #ede9fe,
                        #fce7f3,
                        #cffafe
                    );

                border-left:
                    6px solid #7c3aed;
            ">

                <h3>
                    📌 Assessment
                </h3>

                <div style="
                    margin-top:12px;
                    font-size:18px;
                    font-weight:600;
                ">

                    ${formatValue(assessment)}

                </div>

            </div>


            ${confidenceHTML}


            <div style="
                margin-top:20px;
                padding:18px;
                border-radius:15px;
                background:#f8fafc;
            ">

                <h3>
                    🧠 Explanation
                </h3>

                <p style="
                    margin-top:10px;
                    line-height:1.7;
                ">

                    ${formatValue(explanation)}

                </p>

            </div>


            <div style="
                margin-top:20px;
                padding:18px;
                border-radius:15px;
                background:#fff7ed;
            ">

                <h3>
                    ⚠️ Warning Indicators
                </h3>

                <ul style="
                    margin-top:10px;
                    padding-left:25px;
                ">

                    ${warningHTML}

                </ul>

            </div>

        </div>

    `;
}


// ==========================================
// CLEAR INPUT
// ==========================================

function clearInput() {

    const textInput =
        document.getElementById("textInput");

    const fileInput =
        document.getElementById("fileInput");

    const fileName =
        document.getElementById("fileName");

    const result =
        document.getElementById("result");


    textInput.value = "";

    fileInput.value = "";

    fileName.textContent = "";

    result.innerHTML = "";

    selectedFile = null;
}


// ==========================================
// SECURITY HELPER
// ==========================================

function escapeHTML(value) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}