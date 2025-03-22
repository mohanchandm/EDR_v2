from gliner import GLiNER

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

# Sensitivity levels configuration
SENSITIVITY_LEVELS = {
    "Low": [
        "person", "date of birth", "medical condition", "medication",
        "organization", "address", "email", "phone number", "mobile phone number",
        "landline phone number", "social media handle", "username",
        "medical condition", "blood type", "reservation number",
        "flight number", "train ticket number", "postal code",
        "insurance company", "registration number", "student id number",
        "vehicle registration number", "license plate number", "serial number",
        "fax number", "ip address", "digital signature"
    ],
    "Medium": [
        "person", "date of birth", "medical condition", "medication",
        "organization", "address", "email", "phone number", "mobile phone number",
        "landline phone number", "social media handle", "username",
        "medical condition", "blood type", "reservation number",
        "flight number", "train ticket number", "postal code",
        "insurance company", "registration number", "student id number",
        "vehicle registration number", "license plate number", "serial number",
        "fax number", "ip address", "digital signature",
        "social security number", "health insurance id number", "health insurance number",
        "insurance number", "national health insurance number",
        "tax identification number", "cpf", "cnpj",
        "email address", "iban", "bank account number",
        "driver's license number", "identity card number", "national id number",
        "identity document number", "visa number"
    ],
    "High": ALL_LABELS
}

def load_model():
    """Load and return the GLiNER model."""
    return GLiNER.from_pretrained("mohanchandm/edr_v2")
