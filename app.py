import streamlit as st
from gliner import GLiNER
import random

st.set_page_config(page_title="EDR Tool", layout="wide")

# Initialize the GLiNER model
@st.cache_resource
def load_model():
    return GLiNER.from_pretrained("mohanchandm/edr_v2")

model = load_model()

# Comprehensive list of Privileged Information labels
ALL_LABELS = [
    "person", "organization", "phone number", "address", "passport number",
    "email", "credit card number", "social security number", "health insurance id number",
    "date of birth", "mobile phone number", "bank account number", "medication", "cpf",
    "driver's license number", "tax identification number", "medical condition",
    "identity card number", "national id number", "ip address", "email address", "iban",
    "credit card expiration date", "username", "health insurance number", "registration number",
    "student id number", "insurance number", "flight number", "landline phone number",
    "blood type", "cvv", "reservation number", "digital signature", "social media handle",
    "license plate number", "cnpj", "postal code", "serial number", "vehicle registration number",
    "credit card brand", "fax number", "visa number", "insurance company",
    "identity document number", "transaction number", "national health insurance number",
    "cvc", "birth certificate number", "train ticket number", "passport expiration date"
]

# Sensitivity levels and their corresponding Privileged Information types with redaction percentages
# Comprehensive list of Privileged Information labels
ALL_LABELS = [
    "person", "organization", "phone number", "address", "passport number",
    "email", "credit card number", "social security number", "health insurance id number",
    "date of birth", "mobile phone number", "bank account number", "medication", "cpf",
    "driver's license number", "tax identification number", "medical condition",
    "identity card number", "national id number", "ip address", "email address", "iban",
    "credit card expiration date", "username", "health insurance number", "registration number",
    "student id number", "insurance number", "flight number", "landline phone number",
    "blood type", "cvv", "reservation number", "digital signature", "social media handle",
    "license plate number", "cnpj", "postal code", "serial number", "vehicle registration number",
    "credit card brand", "fax number", "visa number", "insurance company",
    "identity document number", "transaction number", "national health insurance number",
    "cvc", "birth certificate number", "train ticket number", "passport expiration date"
]

# Sensitivity levels with manually selected Privileged Information types
SENSITIVITY_LEVELS = {
    "Low": [
        "person", "date of birth", "medical condition", "medication",  # Basic personal/health info
        "organization", "address", "email", "phone number", "mobile phone number",  # Contact info
        "landline phone number", "social media handle", "username",  # Public-facing identifiers
        "medical condition", "blood type", "reservation number",  # Less critical identifiers
        "flight number", "train ticket number", "postal code",  # Travel and location
        "insurance company", "registration number", "student id number",  # General identifiers
        "vehicle registration number", "license plate number", "serial number",  # Vehicle-related
        "fax number", "ip address", "digital signature"  # Tech-related, less critical
    ],  # 27 labels (50%)
    
    "Medium": [
        "person", "date of birth", "medical condition", "medication",  # Basic personal/health info
        "organization", "address", "email", "phone number", "mobile phone number",  # Contact info
        "landline phone number", "social media handle", "username",  # Public-facing identifiers
        "medical condition", "blood type", "reservation number",  # Less critical identifiers
        "flight number", "train ticket number", "postal code",  # Travel and location
        "insurance company", "registration number", "student id number",  # General identifiers
        "vehicle registration number", "license plate number", "serial number",  # Vehicle-related
        "fax number", "ip address", "digital signature",  # Tech-related
        # Add more sensitive identifiers
        "social security number", "health insurance id number", "health insurance number",  # Health/legal IDs
        "insurance number", "national health insurance number",  # Insurance-related
        "tax identification number", "cpf", "cnpj",  # Tax-related
        "email address", "iban", "bank account number",  # Financial/contact
        "driver's license number", "identity card number", "national id number",  # Legal IDs
        "identity document number", "visa number"  # Additional legal IDs
    ],  # 42 labels (80%)
    
    "High": ALL_LABELS  # 53 labels (100%)
}

def redact_text(text, entities):
    redacted_text = text
    for entity in sorted(entities, key=lambda x: x["start"], reverse=True):
        redacted_text = (
            redacted_text[:entity["start"]] + 
            "[REDACTED " + entity["label"].upper() + "]" + 
            redacted_text[entity["end"]:]
        )
    return redacted_text

def main():
    # Streamlit UI configuration
    
    # Sidebar
    st.sidebar.title("Redaction Settings")
    
    # Confidence threshold slider (moved above Privileged Information types)
    threshold = st.sidebar.slider(
        "Confidence Threshold",
        min_value=0.1,
        max_value=0.9,
        value=0.5,
        step=0.1,
        help="Adjust the confidence level for Privileged Information detection"
    )
    
    # Sensitivity level selection
    sensitivity = st.sidebar.selectbox(
        "Select Sensitivity Level",
        ["Low", "Medium", "High"],
        help="Choose the level of Privileged Information detection sensitivity"
    )
    
    # Display selected Privileged Information types
    st.sidebar.subheader("Detected Privileged Information Types")
    for pii_type in SENSITIVITY_LEVELS[sensitivity]:
        st.sidebar.markdown(f"✓ {pii_type}")
    
    # Main content
    st.title("EDR Tool")
    st.write("Enter text to detect and redact Privileged Information")
    
    # Text input
    default_text = """
Medical Record

Patient Name: John Doe
Date of Birth: 15-01-1985
Date of Examination: 20-05-2024
Social Security Number: 123-45-6789

Examination Procedure:
John Doe underwent a routine physical examination. The procedure included measuring vital signs (blood pressure, heart rate, temperature), a comprehensive blood panel, and a cardiovascular stress test. The patient also reported occasional headaches and dizziness, prompting a neurological assessment and an MRI scan to rule out any underlying issues.

Medication Prescribed:
Ibuprofen 200 mg: Take one tablet every 6-8 hours as needed for headache and pain relief.
Lisinopril 10 mg: Take one tablet daily to manage high blood pressure.
Next Examination Date:
15-11-2024
My name is Mohan Chand Mandava i take 50 mg of caffeine everyday
"""
    
    input_text = st.text_area(
        "Input Text",
        value=default_text,
        height=300,
        help="Paste or type the text you want to analyze"
    )
    
    if st.button("Redact Privileged Information"):
        if input_text:
            # Perform entity extraction
            entities = model.predict_entities(
                input_text,
                SENSITIVITY_LEVELS[sensitivity],
                threshold=threshold
            )
            
            # Create two columns for side-by-side display
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Original Text")
                st.text_area("Original", input_text, height=400, key="original")
            
            with col2:
                st.subheader("Redacted Text")
                redacted_text = redact_text(input_text, entities)
                st.text_area("Redacted", redacted_text, height=400, key="redacted")
            
            # Display detected entities
            st.subheader("Detected Privileged Information Entities")
            if entities:
                for entity in entities:
                    st.write(f"- {entity['text']} => {entity['label']} (Confidence: {entity['score']:.2f})")
            else:
                st.write("No Privileged Information entities detected with the current settings.")
        else:
            st.warning("Please enter some text to analyze.")

if __name__ == "__main__":
    main()


# import sys
# import streamlit as st

# st.write(sys.executable)
