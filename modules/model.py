from gliner import GLiNER
import os

# Define all possible PII labels supported by the model (based on documentation)
ALL_PII_LABELS = [
    "person", "organization", "phone number", "address", "passport number", "email",
    "credit card number", "social security number", "health insurance id number",
    "date of birth", "mobile phone number", "bank account number", "medication",
    "cpf", "driver's license number", "tax identification number", "medical condition",
    "identity card number", "national id number", "ip address", "email address",
    "iban", "credit card expiration date", "username", "health insurance number",
    "registration number", "student id number", "insurance number", "flight number",
    "landline phone number", "blood type", "cvv", "reservation number",
    "digital signature", "social media handle", "license plate number", "cnpj",
    "postal code", "serial number", "vehicle registration number", "credit card brand",
    "fax number", "visa number", "insurance company", "identity document number",
    "transaction number", "national health insurance number", "cvc",
    "birth certificate number", "train ticket number", "passport expiration date"
]

# Map PII labels to sensitivity levels based on your original SENSITIVITY_LEVELS
SENSITIVITY_LEVELS = {
    "Low": {
        "credit card number", "social security number", "passport number",
        "driver's license number", "tax identification number", "bank account number",
        "identity card number", "national id number", "cnpj"
    },
    "Medium": {
        "credit card number", "social security number", "passport number",
        "driver's license number", "tax identification number", "bank account number",
        "identity card number", "national id number", "cnpj", "email", "person",
        "phone number", "mobile phone number", "landline phone number", "username",
        "email address"
    },
    "High": set(ALL_PII_LABELS)  # All PII labels, including privileged info like medical data
}

def load_model():
    """Load the GLiNER model for PII detection."""
    try:
        model = GLiNER.from_pretrained("E3-JSI/gliner-multi-pii-domains-v1")
        print("GLiNER model loaded successfully!")
        return model
    except Exception as e:
        raise Exception(f"Failed to load GLiNER model: {str(e)}")

def predict_entities(model, text, sensitivity="Medium"):
    """Predict entities based on the selected sensitivity level."""
    allowed_labels = SENSITIVITY_LEVELS.get(sensitivity.lower(), SENSITIVITY_LEVELS["Medium"])
    entities = model.predict_entities(text, labels=allowed_labels, threshold=0.5)
    return entities