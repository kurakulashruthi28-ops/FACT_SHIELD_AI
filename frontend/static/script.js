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

    // Remove active state from all buttons
    document.querySelectorAll(".type-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    // Add active state
    if (button) {
        button.classList.add("active");
    }

    const textInput = document.getElementById("textInput");

    const placeholders = {
        news: "Paste the news, claim or information you want to verify...",
        internship: "Paste the internship offer or message you want to check...",
        email: "Paste the email or message you want to analyze...",
        pdf: "Upload a PDF document to analyze...",
        image: "Upload an image to analyze...",
        url: "Paste a website URL to analyze..."
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
    const fileInput = event.target;
    const fileName = document.getElementById("fileName");

    selectedFile = fileInput.files[0] || null;

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

    const textInput = document.getElementById("textInput");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    const text = textInput.value.trim();

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

            const formData = new FormData();

            formData.append("file", selectedFile);

            // Important:
            // Send selected analysis type to backend
            formData.append("analysis_type", selectedType);

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
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify({
                        text: text,
                        analysis_type: selectedType
                    })
                }
            );
        }


        // ======================================
        // READ RESPONSE
        // ======================================

        const data = await response.json();

        console.log(
            "FACT SHIELD AI BACKEND RESPONSE:",
            data
        );


        // Backend error
        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.message ||
                "The server returned an error."
            );
        }


        // Display result
        displayResult(data);

    }

    catch (error) {

        console.error(
            "FACT SHIELD AI ERROR:",
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
                    Make sure your FastAPI backend is running at:
                </p>

                <strong>
                    http://127.0.0.1:8000
                </strong>

            </div>
        `;
    }

    finally {

        loading.style.display = "none";
    }
}


// ==========================================
// DISPLAY RESULT
// ==========================================

function displayResult(data) {

    const result = document.getElementById("result");

    console.log(
        "Displaying backend data:",
        data
    );


    // ======================================
    // IMPORTANT FIX
    // ======================================
    // Your backend returns:
    //
    // {
    //     "success": true,
    //     "analysis_id": 1,
    //     "analysis_type": "news",
    //     "result": {
    //         "assessment": "...",
    //         "confidence": 85,
    //         "explanation": "...",
    //         "warning_indicators": [...]
    //     }
    // }
    //
    // Therefore we must use data.result.

    const payload = data.result ?? data;


    // ======================================
    // FORMAT VALUES SAFELY
    // ======================================

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
                .map(item => {

                    if (
                        typeof item === "object" &&
                        item !== null
                    ) {
                        return `
                            <div style="
                                margin:8px 0;
                                padding:10px;
                                border-radius:10px;
                                background:rgba(255,255,255,0.7);
                            ">
                                ${formatValue(item)}
                            </div>
                        `;
                    }

                    return `
                        <div style="
                            margin:6px 0;
                        ">
                            ${escapeHTML(String(item))}
                        </div>
                    `;
                })
                .join("");
        }


        // Object
        if (
            typeof value === "object" &&
            value !== null
        ) {

            return Object.entries(value)
                .map(([key, val]) => {

                    return `
                        <div style="
                            margin:8px 0;
                            padding:10px;
                            border-radius:10px;
                            background:rgba(255,255,255,0.65);
                        ">

                            <strong>
                                ${formatKey(key)}:
                            </strong>

                            <div style="
                                margin-top:5px;
                            ">
                                ${formatValue(val)}
                            </div>

                        </div>
                    `;
                })
                .join("");
        }


        // Normal text/number
        return escapeHTML(
            String(value)
        );
    }


    // ======================================
    // FORMAT KEY
    // ======================================

    function formatKey(key) {

        return String(key)
            .replace(/_/g, " ")
            .replace(/\b\w/g, letter =>
                letter.toUpperCase()
            );
    }


    // ======================================
    // GET RESULT VALUES
    // ======================================

    const assessment =
        payload.assessment ??
        payload.verdict ??
        payload.status ??
        "Analysis Complete";


    const confidence =
        payload.confidence ??
        payload.score ??
        null;


    const explanation =
        payload.explanation ??
        payload.message ??
        payload.reason ??
        "The information has been analyzed.";


    const warnings =
        payload.warning_indicators ??
        payload.warnings ??
        payload.risk_indicators ??
        [];


    // ======================================
    // WARNING HTML
    // ======================================

    let warningHTML = "";


    if (
        Array.isArray(warnings) &&
        warnings.length > 0
    ) {

        warningHTML = warnings
            .map(item => {

                return `
                    <li style="
                        margin:10px 0;
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
                margin:10px 0;
            ">
                ⚠️ ${formatValue(warnings)}
            </li>
        `;

    }

    else {

        warningHTML = `
            <li style="
                margin:10px 0;
            ">
                ✅ No warning indicators returned.
            </li>
        `;
    }


    // ======================================
    // CONFIDENCE
    // ======================================

    let confidenceHTML = "";


    if (confidence !== null) {

        let confidenceValue =
            formatValue(confidence);

        // Avoid adding % twice
        let confidenceText =
            String(confidence).includes("%")
                ? confidenceValue
                : confidenceValue + "%";


        confidenceHTML = `
            <div style="
                margin-top:20px;
                padding:18px;
                border-radius:18px;
                background:
                    linear-gradient(
                        135deg,
                        #dbeafe,
                        #ede9fe,
                        #fce7f3
                    );
            ">

                <h3>
                    📊 Confidence
                </h3>

                <p style="
                    font-size:24px;
                    font-weight:800;
                    margin-top:8px;
                ">
                    ${confidenceText}
                </p>

            </div>
        `;
    }


    // ======================================
    // EXTRA INFORMATION
    // ======================================

    let extraHTML = "";


    if (payload.risk_score !== undefined) {

        extraHTML += `
            <div style="
                margin-top:15px;
                padding:15px;
                border-radius:15px;
                background:#fef3c7;
            ">

                <strong>
                    🎯 Risk Score:
                </strong>

                ${formatValue(
                    payload.risk_score
                )}

            </div>
        `;
    }


    if (payload.detected_categories !== undefined) {

        extraHTML += `
            <div style="
                margin-top:15px;
                padding:15px;
                border-radius:15px;
                background:#ecfeff;
            ">

                <strong>
                    🔎 Detected Categories:
                </strong>

                <div style="
                    margin-top:8px;
                ">
                    ${formatValue(
                        payload.detected_categories
                    )}
                </div>

            </div>
        `;
    }


    if (
        payload.verification_required !== undefined
    ) {

        extraHTML += `
            <div style="
                margin-top:15px;
                padding:15px;
                border-radius:15px;
                background:#f3e8ff;
            ">

                <strong>
                    🔍 Verification Required:
                </strong>

                ${formatValue(
                    payload.verification_required
                )}

            </div>
        `;
    }


    // ======================================
    // FINAL RESULT
    // ======================================

    result.innerHTML = `

        <div class="result-card">

            <h2>
                🔍 Analysis Result
            </h2>


            <!-- ASSESSMENT -->

            <div style="
                margin-top:20px;
                padding:22px;
                border-radius:20px;

                background:
                    linear-gradient(
                        135deg,
                        #ede9fe,
                        #fce7f3,
                        #cffafe
                    );

                border-left:
                    7px solid #7c3aed;
            ">

                <h3>
                    📌 Assessment
                </h3>

                <div style="
                    margin-top:12px;
                    font-size:22px;
                    font-weight:800;
                ">

                    ${formatValue(
                        assessment
                    )}

                </div>

            </div>


            <!-- CONFIDENCE -->

            ${confidenceHTML}


            <!-- EXPLANATION -->

            <div style="
                margin-top:20px;
                padding:20px;
                border-radius:18px;
                background:#f8fafc;
            ">

                <h3>
                    🧠 Explanation
                </h3>

                <p style="
                    margin-top:10px;
                    line-height:1.8;
                ">

                    ${formatValue(
                        explanation
                    )}

                </p>

            </div>


            <!-- WARNING INDICATORS -->

            <div style="
                margin-top:20px;
                padding:20px;
                border-radius:18px;
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


            <!-- EXTRA DATA -->

            ${extraHTML}

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


    if (textInput) {
        textInput.value = "";
    }


    if (fileInput) {
        fileInput.value = "";
    }


    if (fileName) {
        fileName.textContent = "";
    }


    if (result) {
        result.innerHTML = "";
    }


    selectedFile = null;
    selectedType = "news";


    // Reset active button
    const buttons =
        document.querySelectorAll(".type-btn");

    buttons.forEach(btn => {
        btn.classList.remove("active");
    });

    if (buttons.length > 0) {
        buttons[0].classList.add("active");
    }
}


// ==========================================
// ESCAPE HTML
// ==========================================

function escapeHTML(value) {

    return String(value)

        .replace(/&/g, "&amp;")

        .replace(/</g, "&lt;")

        .replace(/>/g, "&gt;")

        .replace(/"/g, "&quot;")

        .replace(/'/g, "&#039;");
}


// ==========================================
// INITIALIZE
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const firstButton =
            document.querySelector(".type-btn");

        if (firstButton) {
            firstButton.classList.add("active");
        }

        selectType(
            "news",
            firstButton
        );
    }
);