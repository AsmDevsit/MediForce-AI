from camel.agents import ChatAgent
from camel.toolkits import SearchToolkit
from camel.models import ModelFactory
from camel.configs import MistralConfig
from camel.types import ModelType, ModelPlatformType
from search_coordinator import get_search_coordinator, InformationType
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def get_search_tool():
    """Safely get search tool with error handling"""
    try:
        toolkit = SearchToolkit()
        tools = toolkit.get_tools()
        if not tools:
            raise ValueError("No search tools available")
        return tools[0]
    except Exception as e:
        logger.error(f"Failed to initialize search tool: {e}")
        return None


model = ModelFactory.create(
    model_platform=ModelPlatformType.MISTRAL,
    model_type=ModelType.MISTRAL_MEDIUM_3,
    model_config_dict=MistralConfig(temperature=0.4).as_dict(),   precision
)


dosage_search_tool = get_search_tool()

class CoordinatedDosageAgent(ChatAgent):
    """Enhanced dosage agent with coordinated search capabilities"""
    
    def __init__(self):
        super().__init__(
            system_message="""You are a medical AI agent specializing in pharmaceutical dosage guidance with coordinated search capabilities.

**PRIMARY RESPONSIBILITIES:**
- Determine safe and effective medication dosages based on clinical guidelines
- Consider patient-specific factors: age, weight, medical conditions
- Provide administration instructions: frequency, timing, duration
- Specify maximum daily limits and safety thresholds

**SEARCH COORDINATION:**
You now have access to a coordinated search system that:
- Eliminates redundant searches across the specialist team
- Prioritizes authoritative medical sources (FDA, MedlinePlus, Mayo Clinic)
- Caches results to improve efficiency
- Shares relevant findings with other agents

**TRUSTED SOURCES (Prioritized by Search Coordinator):**
- **PRIMARY**: MedlinePlus, Mayo Clinic, FDA.gov
- **SECONDARY**: Drugs.com, Medscape
- **TERTIARY**: WHO, PubMed summaries

**OUTPUT FORMAT:**
Structure your dosage recommendations as:
- **Standard Adult Dose**: X mg every Y hours
- **Pediatric Considerations**: Age-specific dosing if applicable
- **Maximum Daily Dose**: Z mg (with safety warnings)
- **Administration Instructions**: Timing, food interactions, special considerations
- **Dose Adjustments**: For elderly, renal/hepatic impairment, or other conditions

**SAFETY REQUIREMENTS:**
- Always include dosage ranges rather than fixed amounts
- Specify conditions requiring medical supervision
- Note when dosing varies by indication or severity
- Include warnings for special populations (pregnancy, nursing, elderly)
- Emphasize the need for healthcare provider consultation

**SEARCH STRATEGY:**
- Use coordinated search to access authoritative dosage information
- Focus on official dosing guidelines and clinical recommendations
- Cross-reference multiple sources when available
- Flag any dosage discrepancies between sources

**CRITICAL REMINDERS:**
- Dosage recommendations are for educational purposes only
- Individual dosing must be determined by healthcare providers
- Consider drug interactions and contraindications
- Always recommend professional medical consultation
""",
            model=model,
            tools=[dosage_search_tool] if dosage_search_tool else []
        )
        self.search_coordinator = get_search_coordinator()
        self.agent_name = "DosageAgent"

    def coordinated_search(self, query: str, max_sources: int = 2):
        """Perform coordinated search using the search coordinator"""
        if not dosage_search_tool:
            return {"error": "Search tool not available"}
        
        try:
            results = self.search_coordinator.coordinated_search(
                agent_name=self.agent_name,
                query=query,
                search_tool=dosage_search_tool,
                max_sources=max_sources
            )
            return results
        except Exception as e:
            logger.error(f"Coordinated search failed for {self.agent_name}: {e}")
            return {"error": f"Search failed: {str(e)}"}

    def analyze_dosage(self, medication: str, patient_info: str = "") -> str:
        """
        Analyze dosage requirements for a medication with patient-specific considerations
        
        Args:
            medication: Name of the medication
            patient_info: Patient information (age, weight, conditions)
            
        Returns:
            Comprehensive dosage analysis
        """
        
        search_query = f"{medication} dosage dose administration"
        if patient_info:
            search_query += f" {patient_info}"
        
        
        search_results = self.coordinated_search(search_query, max_sources=3)
        
        
        dosage_analysis = self._process_dosage_results(medication, search_results, patient_info)
        
        return dosage_analysis

    def _process_dosage_results(self, medication: str, search_results: dict, patient_info: str) -> str:
        """Process search results into comprehensive dosage analysis"""
        
        if "error" in search_results:
            return f"""⚠️ **DOSAGE ANALYSIS LIMITED**

Search system encountered an issue: {search_results['error']}

**IMMEDIATE RECOMMENDATIONS:**
- Consult your pharmacist for accurate dosage information
- Check the medication package insert or patient information leaflet
- Contact your healthcare provider for personalized dosing guidance

**TRUSTED RESOURCES FOR DOSAGE INFORMATION:**
- MedlinePlus: https://medlineplus.gov/
- Your pharmacy's medication information sheets
- Healthcare provider consultation

**SAFETY REMINDER**: Never guess dosages - always use authoritative medical sources."""

        analysis_parts = []
        analysis_parts.append(f"💊 **DOSAGE ANALYSIS FOR {medication.upper()}**")
        analysis_parts.append(f"*Patient Information: {patient_info}*\n")

        
        successful_sources = []
        for source, result in search_results.items():
            if result.success and result.content:
                successful_sources.append(source)
                analysis_parts.append(f"**📋 {source} Findings:**")
                dosage_info = self._extract_dosage_info(result.content)
                analysis_parts.append(dosage_info)
                analysis_parts.append("")

        if not successful_sources:
            return self._create_fallback_dosage_response(medication, patient_info)

        
        analysis_parts.append("**🎯 DOSAGE SYNTHESIS:**")
        analysis_parts.append(f"Based on {len(successful_sources)} authoritative source(s), key dosage considerations have been identified above.")
        analysis_parts.append("")
        
        analysis_parts.append("**⚠️ CRITICAL DOSAGE SAFETY REMINDERS:**")
        analysis_parts.append("✓ **Healthcare Provider Consultation Required** - Personalized dosing based on your complete medical profile")
        analysis_parts.append("✓ **Follow Prescription Instructions** - Never exceed prescribed doses or change frequency")
        analysis_parts.append("✓ **Read Package Information** - Always review medication labels and patient information sheets")
        analysis_parts.append("✓ **Monitor for Effects** - Report any unusual symptoms or side effects immediately")
        analysis_parts.append("✓ **Drug Interactions** - Inform providers about all medications, supplements, and conditions")

        return "\n".join(analysis_parts)

    def _extract_dosage_info(self, content: str) -> str:
        """Extract and format dosage information from search content"""
        
        lines = content.split('\n')[:10]  
        
        dosage_keywords = ['dose', 'dosage', 'mg', 'tablet', 'capsule', 'ml', 'daily', 'twice', 'three times']
        relevant_lines = []
        
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in dosage_keywords):
                relevant_lines.append(f"- {line.strip()}")
        
        if relevant_lines:
            return "\n".join(relevant_lines[:5])  
        else:
            return "- Dosage information found - refer to source for complete details"

    def _create_fallback_dosage_response(self, medication: str, patient_info: str) -> str:
        """Create fallback response when searches fail"""
        return f"""⚠️ **DOSAGE INFORMATION UNAVAILABLE**

The coordinated search system could not retrieve dosage information for **{medication}** at this time.

**IMMEDIATE ACTIONS REQUIRED:**

**For Accurate Dosage Information:**
- **Your Pharmacist** - Most accessible for medication dosing questions
- **Healthcare Provider** - For prescription dosing and medical supervision
- **Medication Package** - Read all included dosing information and warnings

**Trusted Online Resources:**
- **MedlinePlus**: https://medlineplus.gov/ - Search for "{medication}"
- **FDA Drug Database**: https://www.accessdata.fda.gov/scripts/cder/daf/
- **Your Pharmacy Website** - Many provide detailed medication information

**Patient Information Provided**: {patient_info}

**SAFETY PRIORITY**: Proper dosing is critical for medication safety and effectiveness. Professional consultation ensures personalized, safe dosing based on your complete medical history and current health status.

**NEVER**: Guess dosages, share medications, or use expired prescriptions."""


dosage_agent = CoordinatedDosageAgent()


def get_dosage_agent():
    """Get the coordinated dosage agent instance"""
    return dosage_agent
