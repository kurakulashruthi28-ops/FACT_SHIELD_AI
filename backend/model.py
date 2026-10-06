"""
FACT SHIELD AI
Risk Analysis Model

This module analyzes text and returns:
- assessment
- confidence
- explanation
- warning indicators
- risk score
"""

import re


# ============================================================
# SUSPICIOUS PATTERNS
# ============================================================

HIGH_RISK_PATTERNS = {
    "payment_request": [
        r"\bpay\b",
        r"\bpayment\b",
        r"\bprocessing fee\b",
        r"\bregistration fee\b",
        r"\bdeposit\b",
        r"\btransfer money\b",
        r"\bpay ₹?\s*\d+",
        r"\b₹\s*\d+\s*(fee|payment|registration)?"
    ],

    "guaranteed_result": [
        r"\bguaranteed job\b",
        r"\bguaranteed internship\b",
        r"\bguaranteed placement\b",
        r"\b100% job\b",
        r"\b100% placement\b",
        r"\bguaranteed income\b",
        r"\bguaranteed return\b"
    ],

    "urgency": [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\btoday only\b",
        r"\bwithin \d+ hours\b",
        r"\blimited time\b",
        r"\bexpires today\b",
        r"\blast chance\b",
        r"\bact now\b"
    ],

    "limited_availability": [
        r"\bonly \d+ seats?\b",
        r"\bonly \d+ spots?\b",
        r"\blimited seats?\b",
        r"\blimited availability\b"
    ],

    "personal_information": [
        r"\bsubmit your personal details\b",
        r"\bprovide your aadhaar\b",
        r"\bprovide your password\b",
        r"\bprovide your otp\b",
        r"\bshare your otp\b",
        r"\bshare your bank details\b",
        r"\baccount details\b"
    ],

    "prize_claim": [
        r"\byou have won\b",
        r"\byou won\b",
        r"\bclaim your prize\b",
        r"\bfree prize\b",
        r"\bcash reward\b"
    ],

    "suspicious_links": [
        r"\bclick this link\b",
        r"\bclick here\b",
        r"\bverify your account\b",
        r"\bverification link\b"
    ]
}


# ============================================================
# LOWER-RISK / NORMAL PATTERNS
# ============================================================

NORMAL_PATTERNS = [
    r"\bresearch\b",
    r"\bstudy\b",
    r"\buniversity\b",
    r"\bgovernment report\b",
    r"\bofficial website\b",
    r"\baccording to\b",
    r"\bpublished\b",
    r"\breport\b"
]


# ============================================================
# HELPER
# ============================================================

def clean_text(text: str) -> str:
    """
    Clean and normalize input text.
    """

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# MAIN ANALYSIS FUNCTION
# ============================================================

def analyze_text(text: str) -> dict:
    """
    Analyze supplied text.

    Returns a structured dictionary that can be
    directly returned by FastAPI.
    """

    text = clean_text(text)

    if not text:

        return {
            "assessment": "UNCERTAIN",
            "confidence": 0,
            "risk_score": 0,
            "explanation": "No information was provided for analysis.",
            "warning_indicators": []
        }


    warnings = []

    matched_categories = []

    risk_score = 0


    # ========================================================
    # CHECK HIGH-RISK PATTERNS
    # ========================================================

    for category, patterns in HIGH_RISK_PATTERNS.items():

        category_found = False

        for pattern in patterns:

            try:
                match = re.search(
                    pattern,
                    text,
                    re.IGNORECASE
                )

            except re.error:
                match = None


            if match:

                category_found = True

                break


        if category_found:

            matched_categories.append(category)

            warnings.append(
                format_warning(category)
            )


    # ========================================================
    # CALCULATE RISK SCORE
    # ========================================================

    weights = {

        "payment_request": 25,

        "guaranteed_result": 25,

        "urgency": 15,

        "limited_availability": 10,

        "personal_information": 20,

        "prize_claim": 20,

        "suspicious_links": 15
    }


    for category in matched_categories:

        risk_score += weights.get(
            category,
            5
        )


    # Prevent score above 100

    risk_score = min(
        risk_score,
        100
    )


    # ========================================================
    # CHECK NORMAL INFORMATION SIGNALS
    # ========================================================

    normal_matches = 0

    for pattern in NORMAL_PATTERNS:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            normal_matches += 1


    # ========================================================
    # DETERMINE ASSESSMENT
    # ========================================================

    if risk_score >= 60:

        assessment = "HIGH CAUTION"

        confidence = min(
            70 + (risk_score - 60),
            95
        )

        explanation = (
            "Several strong warning indicators were "
            "detected in the submitted content. "
            "These indicators do not independently "
            "prove that the information is fraudulent "
            "or false, so independent verification "
            "is recommended before taking action."
        )


    elif risk_score >= 35:

        assessment = "CAUTION"

        confidence = min(
            55 + (risk_score - 35),
            85
        )

        explanation = (
            "The content contains multiple indicators "
            "that require caution. The available text "
            "alone is not sufficient to establish "
            "whether the claim is true or false."
        )


    elif risk_score >= 15:

        assessment = "UNCERTAIN"

        confidence = 45 + risk_score // 2

        explanation = (
            "Some potentially important indicators "
            "were detected, but there is not enough "
            "evidence in the submitted text to determine "
            "whether the information is reliable."
        )


    else:

        assessment = "LOW RISK"

        confidence = 60

        explanation = (
            "No major warning indicators were detected "
            "in the submitted text. However, the absence "
            "of warning indicators does not prove that "
            "the information is true."
        )


    # ========================================================
    # REMOVE DUPLICATE WARNINGS
    # ========================================================

    warnings = list(
        dict.fromkeys(warnings)
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "assessment": assessment,

        "confidence": confidence,

        "risk_score": risk_score,

        "explanation": explanation,

        "warning_indicators": warnings,

        "detected_categories": matched_categories,

        "verification_required": (
            assessment != "LOW RISK"
        )
    }


# ============================================================
# WARNING TEXT
# ============================================================

def format_warning(category: str) -> str:

    messages = {

        "payment_request":
            "A payment, registration fee, processing fee, or money transfer is requested.",

        "guaranteed_result":
            "The content makes a strong guarantee about a job, internship, placement, income, or result.",

        "urgency":
            "The message uses urgency or time pressure to encourage immediate action.",

        "limited_availability":
            "The message claims that availability is extremely limited.",

        "personal_information":
            "The message requests sensitive or personal information.",

        "prize_claim":
            "The content claims that the recipient has won a prize or reward.",

        "suspicious_links":
            "The content encourages clicking a verification or other potentially suspicious link."
    }

    return messages.get(
        category,
        "A potentially suspicious indicator was detected."
    )


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    test_text = """
    Congratulations! You have been selected
    for a guaranteed AI internship.

    Pay ₹999 as a registration fee today
    to confirm your seat.

    Only 10 seats are left!
    """

    result = analyze_text(
        test_text
    )

    print("\nFACT SHIELD AI RESULT")
    print("=====================")

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )