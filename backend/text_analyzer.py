"""
FACT SHIELD AI
TEXT ANALYZER

Purpose:
- Analyze submitted text
- Detect suspicious/risk indicators
- Identify important categories
- Return a structured result
- Does NOT claim that something is true/false without evidence
"""

import re


# ============================================================
# SUSPICIOUS PATTERNS
# ============================================================

RISK_PATTERNS = {

    "payment_request": [
        r"\bpay\b",
        r"\bpayment\b",
        r"\bregistration fee\b",
        r"\bprocessing fee\b",
        r"\bapplication fee\b",
        r"\bjoining fee\b",
        r"\bdeposit\b",
        r"\btransfer money\b",
        r"\bsend money\b",
        r"₹\s*\d+",
        r"\b\d+\s*(rupees|rs)\b"
    ],

    "guaranteed_job_or_internship": [
        r"\bguaranteed job\b",
        r"\bguaranteed internship\b",
        r"\bguaranteed placement\b",
        r"\b100%\s*job\b",
        r"\b100%\s*placement\b",
        r"\bguaranteed salary\b",
        r"\bguaranteed income\b"
    ],

    "urgency": [
        r"\burgent\b",
        r"\bimmediately\b",
        r"\bact now\b",
        r"\bact immediately\b",
        r"\btoday only\b",
        r"\blast chance\b",
        r"\blimited time\b",
        r"\bexpires today\b",
        r"\bwithin \d+ hours\b"
    ],

    "limited_availability": [
        r"\bonly \d+ seats?\b",
        r"\bonly \d+ spots?\b",
        r"\blimited seats?\b",
        r"\blimited spots?\b",
        r"\blimited availability\b"
    ],

    "sensitive_information": [
        r"\bshare your otp\b",
        r"\bprovide your otp\b",
        r"\benter your otp\b",
        r"\bshare your password\b",
        r"\bprovide your password\b",
        r"\bshare your aadhaar\b",
        r"\bprovide your aadhaar\b",
        r"\bshare your bank details\b",
        r"\bprovide your bank details\b",
        r"\baccount details\b",
        r"\bcard details\b"
    ],

    "prize_or_reward": [
        r"\byou have won\b",
        r"\byou won\b",
        r"\bcongratulations.*winner\b",
        r"\bclaim your prize\b",
        r"\bclaim your reward\b",
        r"\bfree prize\b",
        r"\bcash reward\b"
    ],

    "suspicious_link_action": [
        r"\bclick here\b",
        r"\bclick this link\b",
        r"\bclick the link\b",
        r"\bverify your account\b",
        r"\bverification link\b",
        r"\blogin immediately\b"
    ],

    "investment_claim": [
        r"\bguaranteed return\b",
        r"\bguaranteed profit\b",
        r"\bdouble your money\b",
        r"\bquick profit\b",
        r"\bno risk\b",
        r"\brisk[- ]free investment\b"
    ]
}


# ============================================================
# NORMAL / CONTEXT SIGNALS
# ============================================================

NORMAL_PATTERNS = [
    r"\bofficial website\b",
    r"\bgovernment website\b",
    r"\bgovernment report\b",
    r"\buniversity\b",
    r"\bresearch\b",
    r"\bstudy\b",
    r"\bpublished\b",
    r"\baccording to\b",
    r"\bofficial source\b",
    r"\bsource\b",
    r"\breport\b"
]


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text: str) -> str:
    """
    Normalize text before analysis.
    """

    if not text:
        return ""

    text = str(text)

    # Convert to lowercase
    text = text.lower()

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# WARNING MESSAGES
# ============================================================

WARNING_MESSAGES = {

    "payment_request":
        "A payment, fee, deposit, or money transfer is requested.",

    "guaranteed_job_or_internship":
        "The content makes a strong guarantee about a job, internship, placement, salary, or income.",

    "urgency":
        "The message uses urgency or time pressure to encourage immediate action.",

    "limited_availability":
        "The message claims that availability is very limited.",

    "sensitive_information":
        "The content requests sensitive personal, account, or authentication information.",

    "prize_or_reward":
        "The content claims that the recipient has won a prize or reward.",

    "suspicious_link_action":
        "The content asks the user to click a link or perform an account-verification action.",

    "investment_claim":
        "The content makes unusually strong investment or profit claims."
}


# ============================================================
# FIND MATCHES
# ============================================================

def find_matches(text: str):
    """
    Find risk categories and the matching phrases.
    """

    detected_categories = []
    matched_phrases = {}

    for category, patterns in RISK_PATTERNS.items():

        category_matches = []

        for pattern in patterns:

            try:
                matches = re.findall(
                    pattern,
                    text,
                    re.IGNORECASE
                )

            except re.error:
                matches = []

            if matches:

                for match in matches:

                    if isinstance(match, tuple):
                        match = " ".join(match)

                    match = str(match).strip()

                    if match and match not in category_matches:
                        category_matches.append(match)

        if category_matches:

            detected_categories.append(category)

            matched_phrases[category] = category_matches

    return detected_categories, matched_phrases


# ============================================================
# CALCULATE RISK SCORE
# ============================================================

def calculate_risk_score(categories):

    weights = {

        "payment_request": 25,

        "guaranteed_job_or_internship": 25,

        "urgency": 15,

        "limited_availability": 10,

        "sensitive_information": 25,

        "prize_or_reward": 20,

        "suspicious_link_action": 15,

        "investment_claim": 25
    }

    score = 0

    for category in categories:

        score += weights.get(
            category,
            5
        )

    return min(score, 100)


# ============================================================
# DETECT NORMAL SIGNALS
# ============================================================

def detect_normal_signals(text):

    matches = []

    for pattern in NORMAL_PATTERNS:

        try:
            if re.search(
                pattern,
                text,
                re.IGNORECASE
            ):
                matches.append(pattern)

        except re.error:
            pass

    return len(matches)


# ============================================================
# CREATE EXPLANATION
# ============================================================

def create_explanation(
    assessment,
    categories,
    normal_signal_count
):

    if assessment == "HIGH CAUTION":

        return (
            "Several strong risk indicators were detected. "
            "The content should be independently verified "
            "before you take action, send money, or provide "
            "sensitive information."
        )

    if assessment == "CAUTION":

        return (
            "The content contains multiple indicators that "
            "may require caution. The text alone is not "
            "enough to establish whether the information "
            "is true or false."
        )

    if assessment == "UNCERTAIN":

        if normal_signal_count > 0:

            return (
                "Some normal information signals were detected, "
                "but there is not enough evidence in the submitted "
                "text to determine whether the claim is reliable."
            )

        return (
            "The submitted text does not contain enough evidence "
            "to determine whether the information is reliable. "
            "Independent verification is recommended."
        )

    return (
        "No major risk indicators were detected in the submitted "
        "text. This does not prove that the information is true."
    )


# ============================================================
# MAIN TEXT ANALYZER
# ============================================================

def analyze_text(text: str) -> dict:

    text = clean_text(text)

    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    if not text:

        return {

            "assessment": "UNCERTAIN",

            "confidence": 0,

            "risk_score": 0,

            "explanation":
                "No information was provided for analysis.",

            "warning_indicators": [],

            "detected_categories": [],

            "matched_phrases": {},

            "verification_required": True
        }


    # --------------------------------------------------------
    # Find risk indicators
    # --------------------------------------------------------

    categories, matched_phrases = find_matches(text)


    # --------------------------------------------------------
    # Calculate score
    # --------------------------------------------------------

    risk_score = calculate_risk_score(
        categories
    )


    # --------------------------------------------------------
    # Normal signals
    # --------------------------------------------------------

    normal_signal_count = detect_normal_signals(
        text
    )


    # --------------------------------------------------------
    # Assessment
    # --------------------------------------------------------

    if risk_score >= 60:

        assessment = "HIGH CAUTION"

        confidence = min(
            70 + (risk_score - 60),
            95
        )

    elif risk_score >= 35:

        assessment = "CAUTION"

        confidence = min(
            55 + (risk_score - 35),
            85
        )

    elif risk_score >= 15:

        assessment = "UNCERTAIN"

        confidence = min(
            45 + (risk_score // 2),
            75
        )

    else:

        assessment = "LOW RISK"

        confidence = 60


    # --------------------------------------------------------
    # Warning indicators
    # --------------------------------------------------------

    warning_indicators = []

    for category in categories:

        message = WARNING_MESSAGES.get(
            category
        )

        if message:
            warning_indicators.append(
                message
            )


    # Remove duplicates
    warning_indicators = list(
        dict.fromkeys(
            warning_indicators
        )
    )


    # --------------------------------------------------------
    # Explanation
    # --------------------------------------------------------

    explanation = create_explanation(
        assessment,
        categories,
        normal_signal_count
    )


    # --------------------------------------------------------
    # Return structured result
    # --------------------------------------------------------

    return {

        "assessment": assessment,

        "confidence": confidence,

        "risk_score": risk_score,

        "explanation": explanation,

        "warning_indicators":
            warning_indicators,

        "detected_categories":
            categories,

        "matched_phrases":
            matched_phrases,

        "verification_required":
            assessment != "LOW RISK"
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_text = """
    Congratulations!

    You have been selected for a guaranteed AI internship.

    Pay ₹999 as a registration fee today
    to confirm your seat.

    Only 10 seats are left!
    """

    result = analyze_text(
        test_text
    )

    print()
    print("FACT SHIELD AI - TEXT ANALYZER")
    print("=" * 40)

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )