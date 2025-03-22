import streamlit as st
from modules.model import load_model, SENSITIVITY_LEVELS
from modules.redaction import redact_text, extract_text_from_file, redact_file_content, convert_to_original_format
from typing import List, Dict, Optional, Tuple

st.set_page_config(page_title="EDR Tool", layout="wide")

# Cache the model loading
@st.cache_resource
def get_model():
    """Load and cache the model for entity detection."""
    return load_model()

# Load model once at startup
model = get_model()

# Set fixed confidence threshold
CONFIDENCE_THRESHOLD = 0.1

def get_default_text() -> str:
    """
    Provide default text for the text redaction tab.

    Returns:
        str: The default text.
    """
    return """
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

def render_sidebar() -> str:
    """
    Render the sidebar with sensitivity settings and Mistral API key configuration.

    Returns:
        str: The selected sensitivity level.
    """
    with st.sidebar:
        st.title("Redaction Settings")
        
        # Mistral API Key Configuration        
        mistral_api_key = st.text_input(
            "Mistral API Key (OCR)",
            value=st.secrets.get("mistral_api_key", ""),
            type="password",
            help="Your Mistral API key is used for OCR processing of images and PDFs. Keep it secure."
        )
        
        if mistral_api_key and mistral_api_key != st.secrets.get("mistral_api_key", ""):
            st.session_state.mistral_api_key = mistral_api_key
            st.secrets["mistral_api_key"] = mistral_api_key
            st.success("Mistral API key updated and stored in secrets.")
        
        # Sensitivity Level Selection
        sensitivity = st.selectbox(
            "Select Sensitivity Level",
            ["Low", "Medium", "High"],
            help="Choose the level of Privileged Information detection sensitivity"
        )
        st.subheader("Detected Privileged Information Types")
        with st.container(height=300):
            for pii_type in SENSITIVITY_LEVELS[sensitivity]:
                st.markdown(f"✓ {pii_type}")
    return sensitivity

def clean_text_for_display(text: str) -> str:
    """
    Clean text for display by removing markdown table formatting while preserving original newlines.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text with markdown tables converted to plain text.
    """
    lines = text.split('\n')
    cleaned_lines = []
    in_table = False
    table_lines = []
    
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            in_table = True
            if not line.strip().startswith('| ---'):
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                paired_cells = []
                for i in range(0, len(cells), 2):
                    left_cell = cells[i] if i < len(cells) else ''
                    right_cell = cells[i + 1] if i + 1 < len(cells) else ''
                    if left_cell or right_cell:
                        left_cell_padded = left_cell.ljust(30)
                        paired_cells.append(f"{left_cell_padded} {right_cell}")
                if paired_cells:
                    table_lines.extend(paired_cells)
        else:
            if in_table:
                # End of table, append the table lines and a single newline
                cleaned_lines.extend(table_lines)
                table_lines = []
                in_table = False
                cleaned_lines.append('')  # Add a single newline after the table
            # Preserve the line as-is (including empty lines)
            cleaned_lines.append(line)
    
    # If the last section was a table, append its lines
    if table_lines:
        cleaned_lines.extend(table_lines)
    
    # Remove trailing empty lines
    while cleaned_lines and cleaned_lines[-1] == '':
        cleaned_lines.pop()
    
    return '\n'.join(cleaned_lines)

def display_results(original_text: str, redacted_text: str, entities: List[Dict[str, any]], key_prefix: str = "") -> None:
    """
    Display the original and redacted text side by side, along with detected entities.

    Args:
        original_text (str): The original text.
        redacted_text (str): The redacted text.
        entities (List[Dict[str, any]]): The detected entities.
        key_prefix (str): Prefix for Streamlit widget keys.
    """
    original_cleaned = clean_text_for_display(original_text)
    redacted_cleaned = clean_text_for_display(redacted_text)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Content")
        st.text_area("Original", original_cleaned, height=400, key=f"{key_prefix}original")
    with col2:
        st.subheader("Redacted Content")
        st.text_area("Redacted", redacted_cleaned, height=400, key=f"{key_prefix}redacted")
    
    # st.subheader("Detected Privileged Information Entities")
    # with st.container(height=200):
    #     if entities:
    #         for entity in entities:
    #             st.write(f"- {entity['text']} => {entity['label']} (Confidence: {entity['score']:.2f})")
    #     else:
    #         st.write("No Privileged Information entities detected with the current settings.")

def text_redaction_tab(sensitivity: str) -> None:
    """
    Render the text redaction tab.

    Args:
        sensitivity (str): The selected sensitivity level.
    """
    st.write("Enter text to detect and redact Privileged Information")
    
    input_text = st.text_area(
        "Input Text",
        value=get_default_text(),
        height=300,
        help="Paste or type the text you want to analyze"
    )
    
    if st.button("Redact Text", key="text_redact"):
        if input_text:
            entities = model.predict_entities(
                input_text,
                SENSITIVITY_LEVELS[sensitivity],
                threshold=CONFIDENCE_THRESHOLD
            )
            redacted_text = redact_text(input_text, entities)
            display_results(input_text, redacted_text, entities, "text_")
            st.download_button(
                label="Download Redacted Text",
                data=convert_to_original_format(redacted_text, "input.txt"),
                file_name="redacted_input.txt",
                mime="text/plain"
            )
        else:
            st.warning("Please enter some text to analyze.")

def file_redaction_tab(sensitivity: str) -> None:
    """
    Render the file redaction tab.

    Args:
        sensitivity (str): The selected sensitivity level.
    """
    st.write("Upload a file (txt, docx, pdf, jpg, png) to detect and redact Privileged Information")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['txt', 'docx', 'pdf', 'jpg', 'png'],
        help="Upload a text file, Word document, PDF, or image"
    )
    
    if st.button("Redact File", key="file_redact"):
        if uploaded_file:
            try:
                original_text, redacted_text, entities = redact_file_content(
                    uploaded_file,
                    model,
                    SENSITIVITY_LEVELS[sensitivity],
                    CONFIDENCE_THRESHOLD
                )
                if original_text and redacted_text:
                    display_results(original_text, redacted_text, entities, "file_")
                    
                    ext = uploaded_file.name.split('.')[-1].lower()
                    mime_types = {
                        'txt': 'text/plain',
                        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'pdf': 'application/pdf',
                        'jpg': 'image/png',
                        'png': 'image/png'
                    }
                    output_ext = '.txt' if ext == 'txt' else f'.{ext}'
                    output_mime = mime_types.get(ext, 'text/plain')
                    
                    st.download_button(
                        label="Download Redacted Content",
                        data=convert_to_original_format(redacted_text, uploaded_file.name),
                        file_name=f"redacted_{uploaded_file.name.split('.')[0]}{output_ext}",
                        mime=output_mime
                    )
                else:
                    st.error("Unable to process file content.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
        else:
            st.warning("Please upload a file to analyze.")

def main() -> None:
    """Main function to run the Streamlit app."""
    st.title("EDR Tool")
    sensitivity = render_sidebar()
    
    tab1, tab2 = st.tabs(["Text Redaction", "File Redaction"])
    
    with tab1:
        text_redaction_tab(sensitivity)
    
    with tab2:
        file_redaction_tab(sensitivity)

if __name__ == "__main__":
    main()
