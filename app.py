import streamlit as st
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# -------------------------------
# Buzzwords
# -------------------------------
buzzwords = [
    "eco-friendly", "natural", "green", "organic",
    "sustainable", "non-toxic", "biodegradable"
]

# -------------------------------
# Extract text from URL
# -------------------------------
def get_text_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    except:
        return ""

# -------------------------------
# Detect buzzwords
# -------------------------------
def detect_buzzwords(text):
    return [word for word in buzzwords if word in text.lower()]

# -------------------------------
# Check proof
# -------------------------------
def has_proof(text):
    proof_keywords = [
        "certified", "ISO", "GOTS", "FSC",
        "%", "recycled", "carbon neutral"
    ]
    return any(word.lower() in text.lower() for word in proof_keywords)

# -------------------------------
# Numbers detection
# -------------------------------
def has_numbers(text):
    return bool(re.search(r'\d', text))

# -------------------------------
# Advanced classification logic
# -------------------------------
def classify_claim(found_buzz, proof):
    if proof and not found_buzz:
        return "✅ Genuine"
    elif proof and found_buzz:
        return "⚠️ Mixed Claim"
    elif found_buzz and not proof:
        return "❌ Greenwashing"
    else:
        return "⚠️ Unclear"

# -------------------------------
# Reason generator
# -------------------------------
def generate_reason(found_buzz, proof):
    if proof and not found_buzz:
        return "Contains verified certifications and avoids vague claims."
    elif proof and found_buzz:
        return f"Includes some proof, but also uses buzzwords ({', '.join(found_buzz)})."
    elif found_buzz:
        return f"Uses buzzwords ({', '.join(found_buzz)}) without evidence."
    else:
        return "No clear sustainability information provided."

# -------------------------------
# UI
# -------------------------------
st.title("🌱 Green-Truth Auditor")
st.markdown("### 🧠 AI-powered Sustainability Checker")

# Inputs
user_input = st.text_area("Enter product description:")
url = st.text_input("Or paste product URL")
brand = st.text_input("Enter brand (optional)")

# Button
if st.button("Analyze"):

    text = user_input

    # URL extraction
    if url:
        extracted = get_text_from_url(url)
        if extracted:
            text += " " + extracted
            st.info("Text extracted from URL")
        else:
            st.warning("Could not extract data from URL")

    # Empty check
    if text.strip() == "":
        st.warning("Please enter text or URL")

    else:
        # Processing
        found_buzz = detect_buzzwords(text)
        proof = has_proof(text)
        numbers = has_numbers(text)

        # -------------------------------
        # Improved scoring
        # -------------------------------
        score = 100

        if found_buzz:
            score -= 30

        if len(found_buzz) > 2:
            score -= 20

        if not proof:
            score -= 30

        if numbers:
            score += 10

        # Clamp score
        score = max(0, min(score, 100))

        # -------------------------------
        # Classification
        # -------------------------------
        result = classify_claim(found_buzz, proof)

        reason = generate_reason(found_buzz, proof)

        # -------------------------------
        # OUTPUT
        # -------------------------------
        st.subheader("🔍 Result")

        if "Greenwashing" in result:
            st.error(result)
        elif "Genuine" in result:
            st.success(result)
        else:
            st.warning(result)

        st.write(f"🌍 Sustainability Score: {score}/100")
        st.progress(score / 100)

        st.write(f"💡 Reason: {reason}")

        # Verdict (NEW 🔥)
        if score >= 70:
            st.success("🌟 Verdict: Trustable")
        elif score >= 40:
            st.warning("⚠️ Verdict: Needs Verification")
        else:
            st.error("❌ Verdict: High Greenwashing Risk")

        if found_buzz:
            st.write("⚠️ Buzzwords:", ", ".join(found_buzz))

        # -------------------------------
        # Brand Check (RAG)
        # -------------------------------
        try:
            df = pd.read_csv("brands.csv")
            if brand:
                match = df[df["brand"].str.lower() == brand.lower()]
                if not match.empty:
                    st.info(f"Brand Certification: {match.iloc[0]['certified']}")
                else:
                    st.warning("Brand not found in database")
        except:
            st.warning("Brand database not found")

        # Debug View
        with st.expander("🔎 What we detected"):
            st.write("Buzzwords:", found_buzz if found_buzz else "None")
            st.write("Has proof:", proof)
            st.write("Has numbers:", numbers)
