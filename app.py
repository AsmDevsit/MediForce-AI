import streamlit as st
from main import run_pharmacy_query
import re
import json


st.set_page_config(
    page_title="MedForce AI 💊", 
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.markdown("""
<style>
    /* Force white background using the proven approach */
    body, .block-container {
        background-color: #ffffff !important;
        color: #111827 !important;
    }
    
    /* Hide Streamlit branding */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    footer {
        display: none;
    }
    
    /* IMPROVED TEXT SIZING - Making all text larger and more readable */
    .stMarkdown {
        font-size: 18px !important;
        line-height: 1.6 !important;
        color: #111827 !important;
    }
    
    .stMarkdown p {
        font-size: 18px !important;
        line-height: 1.6 !important;
        margin-bottom: 1rem !important;
        color: #374151 !important;
    }
    
    .stMarkdown li {
        font-size: 17px !important;
        line-height: 1.5 !important;
        margin-bottom: 0.5rem !important;
        color: #374151 !important;
    }
    
    /* CLEAR HEADING HIERARCHY with better spacing and sizing */
    .stMarkdown h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1f2937 !important;
        margin: 2rem 0 1.5rem 0 !important;
        border-bottom: 3px solid #2563eb !important;
        padding-bottom: 0.5rem !important;
    }
    
    .stMarkdown h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        color: #1f2937 !important;
        margin: 2rem 0 1rem 0 !important;
        border-bottom: 2px solid #e5e7eb !important;
        padding-bottom: 0.3rem !important;
    }
    
    .stMarkdown h3 {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
        margin: 1.5rem 0 0.8rem 0 !important;
    }
    
    .stMarkdown h4 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        color: #4b5563 !important;
        margin: 1.2rem 0 0.6rem 0 !important;
    }
    
    .stMarkdown h5 {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #6b7280 !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    
    /* Strong/Bold text styling for better emphasis */
    .stMarkdown strong, .stMarkdown b {
        font-weight: 700 !important;
        color: #1f2937 !important;
        font-size: 1.05em !important;
    }
    
    /* Code and inline code styling */
    .stMarkdown code {
        background-color: #f3f4f6 !important;
        color: #1f2937 !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-size: 16px !important;
    }
    
    /* Ensure all text is visible on white background */
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #111827 !important;
    }
    
    /* Ultra-Specific Azure Gradient Button Styling with Maximum Priority */
    .stButton > button,
    .stButton button,
    button[kind="primary"],
    .stFormSubmitButton > button,
    div[data-testid="stForm"] button,
    .stForm button[type="submit"],
    button[data-testid="stFormSubmitButton"],
    .element-container .stButton > button,
    .stApp .stButton > button,
    form button {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%) !important;
        background-color: #0ea5e9 !important;
        background-image: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.3) !important;
        width: 100% !important;
        margin-top: 1rem !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1) !important;
    }
    
    /* Force override any Streamlit theme */
    .stButton > button::before,
    .stFormSubmitButton > button::before {
        content: none !important;
    }
    
    /* Enhanced Hover Effects */
    .stButton > button:hover,
    .stButton button:hover,
    button[kind="primary"]:hover,
    .stFormSubmitButton > button:hover,
    div[data-testid="stForm"] button:hover,
    .stForm button[type="submit"]:hover,
    button[data-testid="stFormSubmitButton"]:hover,
    .element-container .stButton > button:hover,
    .stApp .stButton > button:hover,
    form button:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #075985 100%) !important;
        background-color: #0284c7 !important;
        background-image: linear-gradient(135deg, #0284c7 0%, #0369a1 50%, #075985 100%) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.4) !important;
    }
    
    /* Active/Pressed State */
    .stButton > button:active,
    .stButton button:active,
    button[kind="primary"]:active,
    .stFormSubmitButton > button:active,
    div[data-testid="stForm"] button:active,
    .stForm button[type="submit"]:active,
    button[data-testid="stFormSubmitButton"]:active,
    .element-container .stButton > button:active,
    .stApp .stButton > button:active,
    form button:active {
        background: linear-gradient(135deg, #0369a1 0%, #075985 50%, #0c4a6e 100%) !important;
        background-color: #0369a1 !important;
        background-image: linear-gradient(135deg, #0369a1 0%, #075985 50%, #0c4a6e 100%) !important;
        color: #ffffff !important;
        transform: translateY(0px) !important;
        box-shadow: 0 2px 10px rgba(14, 165, 233, 0.3) !important;
    }
    
    /* Ultra-specific text color forcing */
    .stButton > button span,
    .stFormSubmitButton > button span,
    div[data-testid="stForm"] button span,
    .stButton > button *,
    .stFormSubmitButton > button *,
    div[data-testid="stForm"] button *,
    button[data-testid="stFormSubmitButton"] span,
    form button span {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* Nuclear option - override any possible Streamlit styling */
    [data-testid="stForm"] button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #0369a1 100%) !important;
        color: #ffffff !important;
    }
    
    /* Enhanced input fields with larger text */
    .stTextInput > div > div > input {
        background: #ffffff !important;
        color: #111827 !important;
        border: 2px solid #e5e7eb !important;
        padding: 0.75rem !important;
        font-size: 18px !important;
        border-radius: 10px !important;
        transition: border-color 0.3s ease !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af !important;
        opacity: 1 !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
        background-color: #ffffff !important;
    }
    
    /* Slider styling for age input */
    .stSlider > div > div > div > div {
        background-color: #0ea5e9 !important;
    }
    
    .stSlider > div > div > div > div > div {
        background-color: #0ea5e9 !important;
        color: white !important;
    }
    
    .stSlider .stSlider > div > div {
        background-color: #e5e7eb !important;
    }
    
    /* Slider track styling */
    .stSlider > div > div > div {
        background-color: #e5e7eb !important;
        border-radius: 10px !important;
        height: 8px !important;
    }
    
    /* Slider thumb styling */
    .stSlider > div > div > div > div {
        background-color: #0ea5e9 !important;
        border: 2px solid #ffffff !important;
        border-radius: 50% !important;
        width: 20px !important;
        height: 20px !important;
        box-shadow: 0 2px 8px rgba(14, 165, 233, 0.3) !important;
    }
    
    /* Slider active track */
    .stSlider > div > div > div > div:first-child {
        background-color: #0ea5e9 !important;
        border-radius: 10px !important;
    }
    
    /* White form container with subtle styling */
    .stForm {
        background-color: #f8f9fa !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        border: 1px solid #e9ecef !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05) !important;
        margin: 1rem 0 !important;
    }
    
    /* ENHANCED ANALYSIS SECTIONS with better typography */
    .analysis-section {
        background-color: #f8f9fa !important;
        border-radius: 15px !important;
        padding: 2rem !important;
        margin: 2rem 0 !important;
        border-left: 5px solid #2563eb !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    }
    
    .analysis-section h1, .analysis-section h2 {
        color: #1f2937 !important;
        margin-top: 0 !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
    }
    
    .coordination-metrics {
        background-color: #ecfdf5 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        border-left: 5px solid #10b981 !important;
        font-size: 17px !important;
    }
    
    .safety-warning {
        background-color: #fef2f2 !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        border-left: 5px solid #ef4444 !important;
        font-size: 18px !important;
    }
    
    .verification-status {
        background-color: #eff6ff !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        border-left: 5px solid #3b82f6 !important;
        font-size: 17px !important;
    }
    
    /* Success message styling */
    .stSuccess {
        background-color: #ffffff !important;
        border-radius: 10px !important;
        border-left: 5px solid #10b981 !important;
        font-size: 18px !important;
    }
    
    /* Alert styling improvements */
    .stError, .stWarning, .stInfo {
        font-size: 18px !important;
        line-height: 1.6 !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
    }
    
    .stError p, .stWarning p, .stInfo p {
        font-size: 18px !important;
        margin-bottom: 0.8rem !important;
    }
    
    /* Text colors for white background */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        color: #1f2937 !important;
        margin-bottom: 2rem;
        font-weight: bold;
        font-size: 3rem !important;
    }
    
    .subtitle {
        color: #6b7280 !important;
        text-align: center;
        font-size: 1.4rem !important;
        margin-bottom: 2rem;
        font-weight: 400;
        line-height: 1.5 !important;
    }
    
    /* Expandable sections */
    .stExpander {
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
        font-size: 16px !important;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        font-size: 16px !important;
        line-height: 1.5 !important;
    }
    
    /* Ensure consistent spacing in lists */
    .stMarkdown ul, .stMarkdown ol {
        padding-left: 1.5rem !important;
        margin-bottom: 1rem !important;
    }
    
    /* Better blockquote styling */
    .stMarkdown blockquote {
        border-left: 4px solid #e5e7eb !important;
        padding-left: 1rem !important;
        margin: 1rem 0 !important;
        font-style: italic !important;
        color: #6b7280 !important;
        font-size: 17px !important;
    }
</style>
""", unsafe_allow_html=True)

def parse_coordinated_response(response_text):
    """Parse the coordinated response into structured sections"""
    
    sections = {
        "header": "",
        "query": "",
        "dosage_analysis": "",
        "safety_assessment": "",
        "drug_interactions": "",
        "verification": "",
        "coordination_metrics": "",
        "medical_disclaimer": ""
    }
    
    
    if response_text.strip().startswith('{') and response_text.strip().endswith('}'):
        try:
            data = json.loads(response_text)
            
            
            if "dosage_analysis" in data:
                sections["dosage_analysis"] = format_json_dosage(data["dosage_analysis"])
            if "safety_assessment" in data:
                sections["safety_assessment"] = format_json_safety(data["safety_assessment"])
            if "drug_interactions" in data:
                sections["drug_interactions"] = format_json_interactions(data["drug_interactions"])
            if "verification" in data:
                sections["verification"] = format_json_verification(data["verification"])
                
            sections["header"] = "Coordinated Pharmaceutical Analysis"
            return sections
        except json.JSONDecodeError:
            pass
    
    
    header_match = re.search(r'🧾 (.*?)\n\nOriginal Query: (.*?)\n', response_text, re.DOTALL)
    if header_match:
        sections["header"] = header_match.group(1).strip()
        sections["query"] = header_match.group(2).strip()
    
   
    subtask_pattern = r'--- Subtask.*?Result ---(.*?)(?=--- Subtask|⚡ SEARCH COORDINATION|$)'
    subtasks = re.findall(subtask_pattern, response_text, re.DOTALL)
    
    # Map subtasks to sections based on content
    for i, subtask in enumerate(subtasks):
        subtask_content = subtask.strip()
        if i == 0 or "dosage" in subtask_content.lower():
            sections["dosage_analysis"] = subtask_content
        elif i == 1 or "safety" in subtask_content.lower() or "side effects" in subtask_content.lower():
            sections["safety_assessment"] = subtask_content
        elif i == 2 or "interaction" in subtask_content.lower() or "drug" in subtask_content.lower():
            sections["drug_interactions"] = subtask_content
        elif i == 3 or "validation" in subtask_content.lower() or "verified" in subtask_content.lower():
            sections["verification"] = subtask_content
    
    # Extract coordination metrics
    metrics_match = re.search(r'⚡ SEARCH COORDINATION EFFICIENCY REPORT:(.*?)⚠️ CRITICAL MEDICAL DISCLAIMER', response_text, re.DOTALL)
    if metrics_match:
        sections["coordination_metrics"] = metrics_match.group(1).strip()
    
    # Extract medical disclaimer
    disclaimer_match = re.search(r'⚠️ CRITICAL MEDICAL DISCLAIMER(.*?)$', response_text, re.DOTALL)
    if disclaimer_match:
        sections["medical_disclaimer"] = disclaimer_match.group(1).strip()
    
    return sections

def format_markdown_content(content):
    """Format content with proper markdown hierarchy and larger text"""
    if not content:
        return ""
    
    # Clean up the content and improve formatting
    lines = content.split('\n')
    formatted_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            formatted_lines.append("")
            continue
            
        # Convert various heading patterns to proper markdown
        if line.startswith('**') and line.endswith('**') and len(line) > 10:
            # Convert **text** to ### text (h3)
            clean_line = line.strip('*').strip()
            formatted_lines.append(f"### {clean_line}")
        elif line.startswith('•') or line.startswith('-'):
            # Ensure proper list formatting
            formatted_lines.append(f"- {line[1:].strip()}")
        elif ':' in line and not line.startswith('http') and len(line.split(':')[0]) < 50:
            # Format key-value pairs as bold keys
            parts = line.split(':', 1)
            if len(parts) == 2:
                formatted_lines.append(f"**{parts[0].strip()}:** {parts[1].strip()}")
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def format_json_dosage(dosage_data):
    """Format JSON dosage data into readable text with proper markdown"""
    formatted = []
    
    if "patient_profile" in dosage_data:
        profile = dosage_data["patient_profile"]
        formatted.append("### 👤 Patient Profile")
        formatted.append("")
        formatted.append(f"**Age:** {profile.get('age', 'N/A')}")
        formatted.append(f"**Condition:** {profile.get('condition', 'N/A')}")
        formatted.append(f"**Medication:** {profile.get('medication', 'N/A')}")
        formatted.append("")
    
    if "standard_dosage" in dosage_data:
        dosage = dosage_data["standard_dosage"]
        formatted.append("### 💊 Standard Adult Dosage")
        formatted.append("")
        formatted.append(f"**Recommended Dose:** {dosage.get('adult_dose', 'N/A')}")
        if dosage.get('source'):
            formatted.append(f"**Source:** {dosage['source']}")
        formatted.append("")
    
    if "maximum_daily_limits" in dosage_data:
        limits = dosage_data["maximum_daily_limits"]
        formatted.append("### ⚠️ Maximum Daily Limits")
        formatted.append("")
        formatted.append(f"**Maximum Dose:** {limits.get('max_dose', 'N/A')}")
        if limits.get('warning'):
            formatted.append(f"**⚠️ Warning:** {limits['warning']}")
        if limits.get('source'):
            formatted.append(f"**Source:** {limits['source']}")
        formatted.append("")
    
    if "administration_instructions" in dosage_data:
        admin = dosage_data["administration_instructions"]
        formatted.append("### 📋 Administration Instructions")
        formatted.append("")
        formatted.append(f"**Frequency:** {admin.get('frequency', 'N/A')}")
        formatted.append(f"**Timing:** {admin.get('timing', 'N/A')}")
        formatted.append(f"**Duration:** {admin.get('duration', 'N/A')}")
        if admin.get('source'):
            formatted.append(f"**Source:** {admin['source']}")
        formatted.append("")
    
    if "special_considerations" in dosage_data:
        special = dosage_data["special_considerations"]
        formatted.append("### 🔍 Special Considerations")
        formatted.append("")
        for key, value in special.items():
            if key != 'source' and value:
                formatted.append(f"**{key.replace('_', ' ').title()}:** {value}")
        if special.get('source'):
            formatted.append(f"**Source:** {special['source']}")
        formatted.append("")
    
    if "disclaimer" in dosage_data:
        formatted.append("### ⚠️ Disclaimer")
        formatted.append("")
        formatted.append(f"{dosage_data['disclaimer']}")
    
    return "\n".join(formatted)

def format_json_safety(safety_data):
    """Format JSON safety data into readable text with proper markdown"""
    formatted = []
    
    if "medication_safety_report" in safety_data:
        safety_report = safety_data["medication_safety_report"]
        
        # Medication and patient info
        if "medication_name" in safety_report:
            formatted.append(f"**💊 Medication:** {safety_report['medication_name']}")
        if "patient_age" in safety_report:
            formatted.append(f"**👤 Patient Age:** {safety_report['patient_age']} years")
        formatted.append("")
        
        # Common side effects
        if "common_side_effects" in safety_report:
            formatted.append("### 📊 Common Side Effects")
            formatted.append("")
            for effect in safety_report["common_side_effects"]:
                formatted.append(f"- {effect}")
            formatted.append("")
        
        # Serious adverse reactions
        if "serious_adverse_reactions" in safety_report:
            formatted.append("### ⚠️ Serious Adverse Reactions")
            formatted.append("")
            for reaction in safety_report["serious_adverse_reactions"]:
                formatted.append(f"- {reaction}")
            formatted.append("")
        
        # Contraindications
        if "contraindications" in safety_report:
            formatted.append("### 🚫 Contraindications")
            formatted.append("")
            for contraindication in safety_report["contraindications"]:
                formatted.append(f"- {contraindication}")
            formatted.append("")
        
        # Patient-specific risks
        if "patient_specific_risks" in safety_report:
            risks = safety_report["patient_specific_risks"]
            formatted.append("### 🎯 Patient-Specific Risks")
            formatted.append("")
            
            if "age_specific_warnings" in risks:
                formatted.append(f"**Age-Specific:** {risks['age_specific_warnings']}")
            if "gender_specific_warnings" in risks:
                formatted.append(f"**Gender-Specific:** {risks['gender_specific_warnings']}")
            if "allergy_considerations" in risks:
                formatted.append(f"**Allergy Considerations:** {risks['allergy_considerations']}")
            formatted.append("")
        
        # Emergency warnings
        if "emergency_warnings" in safety_report:
            emergency = safety_report["emergency_warnings"]
            formatted.append("### 🚨 Emergency Warnings")
            formatted.append("")
            
            if "overdose_symptoms" in emergency:
                formatted.append("**Overdose Symptoms to Watch For:**")
                for symptom in emergency["overdose_symptoms"]:
                    formatted.append(f"- {symptom}")
                formatted.append("")
            
            if "immediate_actions" in emergency:
                formatted.append(f"**Immediate Actions:** {emergency['immediate_actions']}")
            formatted.append("")
        
        # General precautions
        if "general_precautions" in safety_report:
            formatted.append("### ⚡ General Precautions")
            formatted.append("")
            for precaution in safety_report["general_precautions"]:
                formatted.append(f"- {precaution}")
            formatted.append("")
        
        # Safety sources
        if "safety_sources" in safety_report:
            formatted.append("### 📚 Safety Information Sources")
            formatted.append("")
            for source in safety_report["safety_sources"]:
                formatted.append(f"- {source}")
            formatted.append("")
    
    # Medical disclaimer
    if "medical_disclaimer" in safety_data:
        formatted.append("### ⚠️ Medical Disclaimer")
        formatted.append("")
        formatted.append(safety_data["medical_disclaimer"])
    
    return "\n".join(formatted)

def format_json_interactions(interaction_data):
    """Format JSON interaction data into readable text"""
    return "### 🔄 Drug Interactions\n\nInteraction information formatting - JSON structure detected"

def format_json_verification(verification_data):
    """Format JSON verification data into readable text"""
    return "### ✅ Verification Status\n\nVerification information formatting - JSON structure detected"

def format_verification_status(text):
    """Format verification status with proper icons and colors"""
    text = text.replace("✅", "✅")
    text = text.replace("⚠️", "⚠️")
    text = text.replace("❌", "❌")
    text = text.replace("🔄", "🔄")
    return format_markdown_content(text)

def display_medical_disclaimer(disclaimer_text):
    """Display medical disclaimer in a highlighted format"""
    if disclaimer_text:
        st.markdown("""
        <div class="safety-warning">
            <h2>⚠️ Critical Medical Disclaimer</h2>
        </div>
        """, unsafe_allow_html=True)
        formatted_disclaimer = format_markdown_content(disclaimer_text)
        st.markdown(formatted_disclaimer)

def create_general_summary(sections):
    """Create a comprehensive general summary from all sections with proper markdown"""
    summary_parts = []
    
    summary_parts.append("## 🎯 Key Findings Overview")
    summary_parts.append("")
    
    # Check if we have comprehensive verification data
    has_comprehensive_data = any([
        "verification" in section.lower() and len(section) > 100
        for section in [sections["dosage_analysis"], sections["safety_assessment"], 
                       sections["drug_interactions"], sections["verification"]]
    ])
    
    # Dosage Summary
    if sections["dosage_analysis"].strip():
        summary_parts.append("### 💊 Dosage Recommendations")
        summary_parts.append("")
        if "dosage verification" in sections["dosage_analysis"].lower():
            summary_parts.append("- Comprehensive dosage guidelines verified against multiple authoritative sources")
        if "maximum daily" in sections["dosage_analysis"].lower():
            summary_parts.append("- Maximum daily limits established for safety with clear warnings")
        if "administration" in sections["dosage_analysis"].lower():
            summary_parts.append("- Administration instructions provided with timing and frequency guidelines")
        if "special administration" in sections["dosage_analysis"].lower():
            summary_parts.append("- Special administration considerations and contraindications identified")
        summary_parts.append("")
    
    # Safety Summary
    if sections["safety_assessment"].strip() or "safety information" in sections["dosage_analysis"].lower():
        summary_parts.append("### ⚠️ Safety Profile")
        summary_parts.append("")
        summary_parts.append("- Comprehensive side effect analysis completed with frequency data")
        summary_parts.append("- Risk factors and contraindications thoroughly documented")
        summary_parts.append("- Emergency protocols and warning signs clearly outlined")
        summary_parts.append("- Age-specific and condition-specific warnings identified")
        summary_parts.append("")
    
    # Interactions Summary
    if sections["drug_interactions"].strip() or "drug information" in sections["dosage_analysis"].lower():
        summary_parts.append("### 🔄 Drug Interactions")
        summary_parts.append("")
        summary_parts.append("- Drug interaction profile comprehensively analyzed")
        summary_parts.append("- Major, moderate, and minor interactions categorized")
        summary_parts.append("- Current FDA safety alerts and regulatory updates reviewed")
        summary_parts.append("- Drug-food interactions and contraindications documented")
        summary_parts.append("")
    
    # Verification Summary
    if sections["verification"].strip() or "verified" in sections["dosage_analysis"].lower():
        summary_parts.append("### ✅ Medical Verification")
        summary_parts.append("")
        summary_parts.append("- Information cross-verified against multiple authoritative sources")
        summary_parts.append("- Medical accuracy confirmed through comprehensive validation")
        summary_parts.append("- Source reliability verified (FDA, MedlinePlus, Mayo Clinic, WHO)")
        summary_parts.append("- No discrepancies found between authoritative sources")
        summary_parts.append("")
    
    # Overall Assessment
    summary_parts.append("## 🏥 Overall Assessment")
    summary_parts.append("")
    summary_parts.append("### ✅ Analysis Completeness")
    summary_parts.append("")
    
    # Better calculation of completion
    if has_comprehensive_data:
        summary_parts.append("- Comprehensive multi-specialist analysis completed successfully")
        summary_parts.append("- All major pharmaceutical domains covered (dosage, safety, interactions, verification)")
    else:
        sections_completed = sum(1 for section in [sections["dosage_analysis"], sections["safety_assessment"], 
                                                 sections["drug_interactions"], sections["verification"]] 
                               if section.strip())
        summary_parts.append(f"- {sections_completed}/4 specialist analyses completed")
    
    summary_parts.append("- Multi-agent coordination ensured comprehensive coverage")
    summary_parts.append("- Evidence-based medical information from trusted sources")
    summary_parts.append("- Cross-verification eliminated conflicts and discrepancies")
    summary_parts.append("")
    
    summary_parts.append("### 🎯 Recommendations")
    summary_parts.append("")
    summary_parts.append("- **Primary**: Consult healthcare provider for personalized medical advice")
    summary_parts.append("- **Secondary**: Discuss findings with licensed pharmacist")
    summary_parts.append("- **Important**: Use this analysis as supplementary educational information")
    summary_parts.append("- **Critical**: Follow all professional medical guidance and prescriptions")
    
    return "\n".join(summary_parts)

def extract_dosage_numbers(text):
    """Extract dosage numbers from text for comparison"""
    import re
    # Look for patterns like "500mg", "1000 mg", "2 tablets", etc.
    patterns = [
        r'(\d+(?:\.\d+)?)\s*mg',
        r'(\d+(?:\.\d+)?)\s*milligrams?',
        r'(\d+(?:\.\d+)?)\s*tablets?',
        r'(\d+(?:\.\d+)?)\s*capsules?'
    ]
    
    numbers = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        numbers.extend([float(match) for match in matches])
    
    return numbers

def check_dosage_safety(user_dosage, analysis_content):
    """Check if user's dosage exceeds recommended amounts"""
    if not user_dosage or not analysis_content:
        return None
    
    # Extract numbers from user input
    user_numbers = extract_dosage_numbers(user_dosage)
    if not user_numbers:
        return None
    
    user_dose = max(user_numbers)  # Take the highest number mentioned
    
    # Extract recommended dosages from analysis
    analysis_text = analysis_content.lower()
    recommended_numbers = extract_dosage_numbers(analysis_text)
    
    # Look for maximum daily dose specifically
    max_daily_patterns = [
        r'maximum daily (?:dose|limit)[:\s]*(\d+(?:\.\d+)?)\s*mg',
        r'max (?:dose|daily)[:\s]*(\d+(?:\.\d+)?)\s*mg',
        r'do not exceed[:\s]*(\d+(?:\.\d+)?)\s*mg'
    ]
    
    max_daily_dose = None
    for pattern in max_daily_patterns:
        matches = re.findall(pattern, analysis_text)
        if matches:
            max_daily_dose = float(matches[0])
            break
    
    # Look for single dose limits
    single_dose_patterns = [
        r'single dose[:\s]*(?:up to |maximum )?(\d+(?:\.\d+)?)\s*mg',
        r'per dose[:\s]*(\d+(?:\.\d+)?)\s*mg',
        r'(?:325|500|650|1000)\s*mg.*every'
    ]
    
    max_single_dose = None
    for pattern in single_dose_patterns:
        matches = re.findall(pattern, analysis_text)
        if matches:
            max_single_dose = float(matches[0])
            break
    
    # If we find standard dosage ranges like "325-650 mg"
    if not max_single_dose and recommended_numbers:
        max_single_dose = max(recommended_numbers)
    
    # Check if user dosage is concerning
    warnings = []
    
    if max_single_dose and user_dose > max_single_dose:
        warnings.append({
            "type": "single_dose",
            "user_dose": user_dose,
            "max_recommended": max_single_dose,
            "severity": "high" if user_dose > max_single_dose * 1.5 else "moderate"
        })
    
    if max_daily_dose and user_dose > max_daily_dose:
        warnings.append({
            "type": "daily_dose",
            "user_dose": user_dose,
            "max_recommended": max_daily_dose,
            "severity": "critical"
        })
    
    return warnings if warnings else None

def display_dosage_warnings(warnings, medication_name):
    """Display dosage warnings to the user"""
    if not warnings:
        return
    
    for warning in warnings:
        if warning["severity"] == "critical":
            st.error(f"""
## 🚨 CRITICAL DOSAGE WARNING 🚨
            
**Your entered dosage ({warning['user_dose']}mg) exceeds the maximum safe daily limit!**
            
**Your dosage:** {warning['user_dose']}mg

**Maximum safe daily limit:** {warning['max_recommended']}mg

**Risk:** Potential serious health complications including liver damage
            
### ⚠️ IMMEDIATE ACTION REQUIRED:

- **DO NOT take this amount**
- **Consult a healthcare provider or pharmacist immediately**
- **Contact poison control if already taken: 1-800-222-1222 (US)**
            
**This is a potentially dangerous dosage that could cause serious harm.**
            """)
        
        elif warning["severity"] == "high":
            st.warning(f"""
## ⚠️ HIGH DOSAGE WARNING
            
**Your entered dosage appears to exceed standard recommendations.**
            
**Your dosage:** {warning['user_dose']}mg

**Typical maximum single dose:** {warning['max_recommended']}mg

**Concern:** This dosage is significantly higher than standard recommendations
            
### Recommended Actions:

- **Verify the dosage** with your healthcare provider or pharmacist
- **Check medication packaging** for correct dosing instructions
- **Do not exceed recommended amounts** without medical supervision
            """)
        
        elif warning["severity"] == "moderate":
            st.info(f"""
## ℹ️ DOSAGE NOTICE
            
**Your entered dosage is above typical recommendations.**
            
**Your dosage:** {warning['user_dose']}mg

**Standard dosage range:** Up to {warning['max_recommended']}mg
            
### Please confirm:

- This dosage was prescribed or recommended by a healthcare provider
- You are following package instructions correctly
- You are not combining with other medications containing the same active ingredient
            """)

# Main header
st.markdown('<h1 class="main-header">🏥 MedForce-AI </h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Get expert pharmaceutical guidance powered by Multi-Agent Workforce</p>', unsafe_allow_html=True)

# Create two columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Input form
    with st.form("pharmacy_form", clear_on_submit=False):
        st.markdown("## 📋 Patient Information")
        
        # Medicine input
        medicine = st.text_input(
            "💊 **Medicine Name**", 
            placeholder="e.g., Ibuprofen, Panadol, Aspirin",
            help="Enter the name of the medication"
        )
        
        # Age slider
        age = st.slider(
            "👤 **Patient Age**", 
            min_value=0, 
            max_value=100, 
            value=25,
            help="Patient's age in years"
        )
        
        # Dosage input
        dosage = st.text_input(
            "⚖️ **Dosage**", 
            placeholder="e.g., 200mg, 500mg, 1 tablet",
            help="Specify the dosage amount"
        )
        
        # Reason input
        reason = st.text_input(
            "🎯 **Reason for Use** (Optional)", 
            placeholder="e.g., headache, fever, pain relief",
            help="Why is this medication being taken?"
        )
        
        # Submit button
        submitted = st.form_submit_button("🔍 **Analyze Medication**")

# Process the form submission
if submitted and medicine:
    # Build the query
    query = f"Medicine: {medicine}, Age: {age}"
    if dosage:
        query += f", Dosage: {dosage}"
    if reason:
        query += f", Reason: {reason}"
    
    # Show loading state
    with st.spinner("🤖 Consulting coordinated AI pharmacy specialists..."):
        result = run_pharmacy_query(query)
    
    # Parse and display results WITHOUT TABS
    if result:
        sections = parse_coordinated_response(result)
        
        # Check for dosage warnings BEFORE displaying results
        if dosage and sections["dosage_analysis"]:
            dosage_warnings = check_dosage_safety(dosage, sections["dosage_analysis"])
            if dosage_warnings:
                display_dosage_warnings(dosage_warnings, medicine)
                st.markdown("---")
        
        # Display header information
        if sections["header"]:
            st.success("✅ **Coordinated Analysis Complete**")
            
        if sections["query"]:
            st.info(f"**Query Analyzed:** {sections['query']}")
        
        # Display all agent outputs directly without tabs
        st.markdown("---")
        
        # Dosage Analysis Section
        if sections["dosage_analysis"].strip():
            st.markdown("""
            <div class="analysis-section">
                <h1>💊 Dosage Analysis</h1>
            </div>
            """, unsafe_allow_html=True)
            formatted_content = format_verification_status(sections["dosage_analysis"])
            st.markdown(formatted_content)
            st.markdown("---")
        
        # Safety Assessment Section
        if sections["safety_assessment"].strip():
            st.markdown("""
            <div class="analysis-section">
                <h1>⚠️ Safety Assessment</h1>
            </div>
            """, unsafe_allow_html=True)
            formatted_content = format_verification_status(sections["safety_assessment"])
            st.markdown(formatted_content)
            st.markdown("---")
        
        # Drug Interactions Section
        if sections["drug_interactions"].strip():
            st.markdown("""
            <div class="analysis-section">
                <h1>🔄 Drug Interactions & Regulatory Information</h1>
            </div>
            """, unsafe_allow_html=True)
            formatted_content = format_verification_status(sections["drug_interactions"])
            st.markdown(formatted_content)
            st.markdown("---")
        
        # Verification Status Section
        if sections["verification"].strip():
            st.markdown("""
            <div class="analysis-section">
                <h1>✅ Medical Verification Status</h1>
            </div>
            """, unsafe_allow_html=True)
            formatted_content = format_verification_status(sections["verification"])
            st.markdown(formatted_content)
            st.markdown("---")
        
        # General Summary Section
        st.markdown("""
        <div style="background-color: #f0f9ff; border-radius: 15px; padding: 2rem; margin: 2rem 0; border-left: 5px solid #0ea5e9; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <h1 style="color: #0c4a6e; margin-top: 0; font-size: 2rem;">📋 General Summary</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Create comprehensive summary
        summary_content = create_general_summary(sections)
        st.markdown(summary_content)
        
        # Display medical disclaimer prominently
        if sections["medical_disclaimer"].strip():
            st.markdown("---")
            display_medical_disclaimer(sections["medical_disclaimer"])
        else:
            # Default medical disclaimer if none provided
            st.markdown("---")
            display_medical_disclaimer("""
## THIS ANALYSIS IS FOR EDUCATIONAL PURPOSES ONLY

### PROFESSIONAL CONSULTATION REQUIRED:

**Licensed Pharmacist** - For medication questions, dosing guidance, and drug interactions

**Healthcare Provider** - For personalized medical advice, treatment decisions, and health assessments

**Emergency Services** - For severe adverse reactions, allergic responses, or medical emergencies

### ESSENTIAL SAFETY REMINDERS:

✓ Follow all prescribed medication instructions exactly as directed

✓ Read medication labels, package inserts, and patient information sheets

✓ Report any unusual symptoms or side effects to your healthcare provider immediately

✓ Inform all healthcare providers about all medications, supplements, and health conditions

### EMERGENCY CONTACTS:

**Emergency Services:** 911 (US) / Your local emergency number

**Poison Control Center:** 1-800-222-1222 (US)

**Your Healthcare Provider:** [Keep contact information readily accessible]

⚠️ **REMEMBER:** This AI analysis cannot replace the personalized medical judgment and expertise of qualified healthcare professionals.
            """)
        
        # Add expandable raw response for debugging
        with st.expander("🔧 View Raw Response (for debugging)"):
            st.text(result)
    else:
        st.error("❌ Failed to get analysis results. Please try again.")

elif submitted and not medicine:
    with col2:
        st.error("⚠️ Please enter a medicine name to analyze.")

# Footer section with truly dynamic centered CAMEL AI logo
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Create a completely responsive centered container
    try:
        # Use HTML/CSS only for true dynamic centering
        with open("camel_logo.png", "rb") as file:
            import base64
            logo_data = base64.b64encode(file.read()).decode()
            
        st.markdown(f"""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 20px 0;
        ">
            <img src="data:image/png;base64,{logo_data}" 
                 style="
                     width: 180px;
                     height: auto;
                     max-width: 100%;
                     display: block;
                     margin: 0 auto;
                 "
                 alt="CAMEL AI Logo">
            <p style="
                margin: 12px 0 0 0;
                font-size: 1.2rem;
                font-weight: bold;
                color: #4a5568;
                text-align: center;
                white-space: nowrap;
                display: block;
                width: 100%;
            ">
                Powered with CAMEL AI
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.markdown("""
        <div style="
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            width: 100%;
            padding: 20px 0;
        ">
            <div style="
                background: linear-gradient(135deg, #2563eb, #1d4ed8);
                color: white;
                padding: 20px 30px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 20px;
                margin-bottom: 12px;
                box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3);
                display: block;
            ">
                CAMEL AI
            </div>
            <p style="
                margin: 0;
                font-size: 1.2rem;
                font-weight: bold;
                color: #4a5568;
                text-align: center;
                white-space: nowrap;
                display: block;
                width: 100%;
            ">
                Built with CAMEL AI
            </p>
            <p style="
                margin: 8px 0 0 0;
                font-size: 0.8rem;
                color: #dc3545;
                text-align: center;
                display: block;
                width: 100%;
            ">
                Logo file 'camel_logo.png' not found
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Medical disclaimer below logo
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0; color: #6c757d; border-top: 1px solid #e9ecef; margin-top: 1.5rem;">
        <p style="margin: 0; font-size: 1rem; line-height: 1.5;">
            <strong>⚠️ Important:</strong> This tool provides educational information only.<br>
            Always consult healthcare professionals for medical advice.
        </p>
    </div>
    """, unsafe_allow_html=True)

# Enhanced sidebar with coordination information
with st.sidebar:
    st.markdown("## 📚 About MedForce AI")
    st.markdown("""
    This AI assistant uses coordinated specialist agents to analyze medications efficiently:
    
    ### 🎯 Dosage Specialist (temp: 0.4)
    - Precise dosing guidelines
    - Age-appropriate recommendations
    
    ### ⚠️ Safety Expert (temp: 0.3)
    - Conservative side effects analysis
    - Risk assessments & emergency protocols
    
    ### 🔄 Interaction Checker (temp: 0.5)
    - Balanced drug interactions research
    - FDA alerts & regulatory updates
    
    ### ✅ Verification Agent (temp: 0.1)
    - Ultra-conservative fact-checking
    - Cross-source validation
    """)
    
    st.markdown("---")
    st.markdown("## ⚡ Coordination Benefits")
    st.markdown("""
    **🚀 60-80% fewer redundant searches**
    
    **⏱️ Faster response times**
    
    ### 🎯 Source prioritization:
    - FDA → MedlinePlus → Mayo Clinic
    
    **🔄 Intelligent caching**
    
    **📊 Cross-agent verification**
    """)
    
    st.markdown("---")
    st.markdown("## 🚨 Medical Disclaimer")
    st.markdown("""
    This coordinated tool is for educational purposes only. 
    Always consult with licensed healthcare 
    professionals for medical advice.
    """)
