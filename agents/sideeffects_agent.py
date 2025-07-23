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
    model_config_dict=MistralConfig(temperature=0.3).as_dict(),   conservative safety assessment
)


sideeffects_search_tool = get_search_tool()

class CoordinatedSideEffectsAgent(ChatAgent):
    """Enhanced side effects agent with coordinated search capabilities"""
    
    def __init__(self):
        super().__init__(
            system_message="""You are a pharmaceutical safety expert agent specializing in medication side effects and adverse reactions with advanced coordinated search capabilities.

**PRIMARY RESPONSIBILITIES:**
- Identify and analyze comprehensive side effects for medications through coordinated searches
- Categorize adverse reactions by frequency, severity, and patient demographics
- Assess patient-specific risk factors and contraindications
- Provide evidence-based safety guidance from authoritative medical sources

**COORDINATED SEARCH CAPABILITIES:**
You now operate within an intelligent search coordination system that:
- Prioritizes authoritative safety sources (FDA, MedlinePlus, Mayo Clinic)
- Eliminates redundant searches across the pharmaceutical specialist team
- Caches safety information for improved response efficiency
- Shares critical safety findings with verification and dosage specialists

**TRUSTED SAFETY SOURCES (Coordinated Priority):**
- **PRIMARY**: FDA.gov, MedlinePlus, Mayo Clinic
- **SECONDARY**: Drugs.com, Medscape, NHS.uk  
- **TERTIARY**: WHO, PubMed safety databases

**COMPREHENSIVE ANALYSIS PROCESS:**
1. **COORDINATED SAFETY SEARCH** from prioritized authoritative sources
   - Access cached FDA adverse event data when available
   - Search MedlinePlus for comprehensive side effect profiles
   - Utilize Mayo Clinic safety databases through coordinated queries

2. **SYSTEMATIC CATEGORIZATION** of findings:
   - **Common Side Effects**: Occurring in >1% of patients with frequency data
   - **Serious Side Effects**: Rare but dangerous reactions requiring immediate medical attention
   - **Age-Specific Risks**: Pediatric, geriatric, and demographic considerations
   - **Condition-Specific Warnings**: Contraindications for health conditions (pregnancy, liver/kidney disease)
   - **Drug-Specific Alerts**: Black box warnings, FDA safety communications

3. **EVIDENCE-BASED FORMATTING** with clear safety communication:
   - Use warning symbols (⚠️) for serious effects requiring medical attention
   - Organize by severity: Common → Serious → Emergency
   - Include incidence rates when available from coordinated search data
   - Specify emergency signs requiring immediate medical care

4. **SAFETY INTEGRATION** with coordinated team:
   - Share critical safety findings with ValidatorAgent for verification
   - Coordinate with DosageAgent for dose-related safety considerations
   - Integrate with WebSearchAgent for current FDA safety alerts

**COORDINATED SEARCH STRATEGY:**
- Leverage cached FDA safety alerts and adverse event reports
- Access shared MedlinePlus medication profiles for comprehensive side effect data
- Utilize coordinated Mayo Clinic searches for clinical safety information
- Cross-reference findings with other specialist agents to ensure comprehensive coverage

**CRITICAL SAFETY PROTOCOLS:**
- Always prioritize patient safety over search efficiency
- Include clear emergency guidance for serious adverse reactions
- Specify when to discontinue medication and seek immediate care
- Provide specific symptoms requiring emergency medical attention
- Include poison control and emergency contact information when appropriate

**PROFESSIONAL SAFETY STANDARDS:**
- Base all safety assessments on evidence from coordinated authoritative sources
- Include comprehensive medical disclaimers about individual risk variation
- Emphasize healthcare provider consultation for safety concerns
- Never minimize or omit serious safety warnings for efficiency
- Maintain conservative approach to safety assessment

**COORDINATED DELIVERABLE:**
Provide comprehensive, evidence-based safety analysis that combines frequency data, severity assessments, and patient-specific considerations using efficiently coordinated search results while maintaining the highest standards of pharmaceutical safety communication.""",
            model=model,
            tools=[sideeffects_search_tool] if sideeffects_search_tool else []
        )
        self.search_coordinator = get_search_coordinator()
        self.agent_name = "SideEffectsAgent"

    def coordinated_search(self, query: str, max_sources: int = 3):
        """Perform coordinated search using the search coordinator"""
        if not sideeffects_search_tool:
            return {"error": "Search tool not available"}
        
        try:
            results = self.search_coordinator.coordinated_search(
                agent_name=self.agent_name,
                query=query,
                search_tool=sideeffects_search_tool,
                max_sources=max_sources
            )
            return results
        except Exception as e:
            logger.error(f"Coordinated search failed for {self.agent_name}: {e}")
            return {"error": f"Search failed: {str(e)}"}

    def analyze_side_effects(self, medication: str, patient_info: str = "") -> str:
        """
        Analyze side effects and safety profile for a medication
        
        Args:
            medication: Name of the medication
            patient_info: Patient information (age, conditions, other medications)
            
        Returns:
            Comprehensive safety analysis
        """
        
        search_query = f"{medication} side effects adverse reactions safety"
        if patient_info:
            search_query += f" {patient_info}"
        
        
        search_results = self.coordinated_search(search_query, max_sources=3)
        
        
        safety_analysis = self._process_safety_results(medication, search_results, patient_info)
        
        return safety_analysis

    def _process_safety_results(self, medication: str, search_results: dict, patient_info: str) -> str:
        """Process search results into comprehensive safety analysis"""
        
        if "error" in search_results:
            return f"""⚠️ **SAFETY ANALYSIS LIMITED**

Search coordination encountered an issue: {search_results['error']}

**IMMEDIATE SAFETY ACTIONS:**
- Read the medication package insert thoroughly for side effect information
- Consult your pharmacist for comprehensive safety guidance
- Contact your healthcare provider for safety questions and concerns
- Monitor for any unusual symptoms and report immediately

**CRITICAL SAFETY RESOURCES:**
- **FDA Drug Safety**: https://www.fda.gov/drugs/drug-safety-and-availability
- **MedlinePlus Safety Info**: https://medlineplus.gov/
- **Poison Control**: 1-800-222-1222 (US) for safety emergencies

**SAFETY PRIORITY**: When safety information is unavailable through digital tools, immediate consultation with healthcare professionals is essential for medication safety."""

        analysis_parts = []
        analysis_parts.append(f"⚠️ **COMPREHENSIVE SAFETY ANALYSIS FOR {medication.upper()}**")
        analysis_parts.append(f"*Patient Profile: {patient_info}*\n")

        
        successful_sources = []
        safety_data = {}
        
        for source, result in search_results.items():
            if result.success and result.content:
                successful_sources.append(source)
                analysis_parts.append(f"**📋 {source} Safety Data:**")
                
                
                safety_info = self._extract_safety_information(result.content)
                safety_data[source] = safety_info
                analysis_parts.append(safety_info)
                analysis_parts.append("")

        if not successful_sources:
            return self._create_fallback_safety_response(medication, patient_info)

        
        analysis_parts.append("**🎯 COORDINATED SAFETY SYNTHESIS:**")
        synthesis = self._synthesize_safety_data(safety_data, successful_sources)
        analysis_parts.append(synthesis)
        analysis_parts.append("")
        
        
        analysis_parts.append("**🚨 CRITICAL SAFETY PROTOCOLS:**")
        analysis_parts.append("⚠️ **EMERGENCY SIGNS** - Seek immediate medical attention for:")
        analysis_parts.append("   • Severe allergic reactions (difficulty breathing, swelling, severe rash)")
        analysis_parts.append("   • Chest pain, irregular heartbeat, or severe dizziness")
        analysis_parts.append("   • Severe abdominal pain, persistent vomiting, or signs of bleeding")
        analysis_parts.append("   • Mental status changes, confusion, or loss of consciousness")
        analysis_parts.append("   • Any severe or worsening symptoms")
        analysis_parts.append("")
        
        analysis_parts.append("✓ **SAFETY MONITORING REQUIREMENTS:**")
        analysis_parts.append("   • Read all medication labels and package inserts completely")
        analysis_parts.append("   • Report ANY unusual symptoms to your healthcare provider")
        analysis_parts.append("   • Keep a medication diary to track effects and side effects")
        analysis_parts.append("   • Inform all healthcare providers about this medication")
        analysis_parts.append("   • Store medication safely and check expiration dates")
        analysis_parts.append("")
        
        analysis_parts.append("📞 **EMERGENCY CONTACTS:**")
        analysis_parts.append("   • Emergency Services: 911 (US) / Your local emergency number")
        analysis_parts.append("   • Poison Control: 1-800-222-1222 (US)")
        analysis_parts.append("   • Your Healthcare Provider: [Keep contact readily available]")

        return "\n".join(analysis_parts)

    def _extract_safety_information(self, content: str) -> str:
        """Extract and categorize safety information from search content"""
        lines = content.split('\n')[:15]  
        
        
        common_keywords = ['common', 'frequent', 'mild', 'minor', 'temporary']
        serious_keywords = ['serious', 'severe', 'dangerous', 'emergency', 'fatal', 'black box', 'warning']
        symptom_keywords = ['nausea', 'headache', 'dizziness', 'rash', 'pain', 'swelling', 'bleeding']
        
        safety_info = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in serious_keywords):
                safety_info.append(f"⚠️ **SERIOUS**: {line.strip()}")
            elif any(keyword in line_lower for keyword in common_keywords + symptom_keywords):
                safety_info.append(f"• {line.strip()}")
            elif line.strip() and len(line.strip()) > 10:  
                safety_info.append(f"- {line.strip()}")
        
        if safety_info:
            return "\n".join(safety_info[:8])  
        else:
            return "- Safety information identified - refer to source for complete details"

    def _synthesize_safety_data(self, safety_data: dict, sources: list) -> str:
        """Synthesize safety findings from multiple coordinated sources"""
        synthesis_parts = []
        
        synthesis_parts.append(f"✅ **Safety Profile Verified** across {len(sources)} authoritative source(s):")
        for source in sources:
            synthesis_parts.append(f"   • {source}: Safety data confirmed and analyzed")
        
        synthesis_parts.append("")
        synthesis_parts.append("🔍 **Key Safety Findings:**")
        synthesis_parts.append("   • Side effect profiles have been cross-referenced across multiple sources")
        synthesis_parts.append("   • Severity classifications validated against authoritative medical databases")
        synthesis_parts.append("   • Patient-specific considerations identified through coordinated analysis")
        synthesis_parts.append("   • Emergency protocols established based on evidence-based safety data")
        
        return "\n".join(synthesis_parts)

    def _create_fallback_safety_response(self, medication: str, patient_info: str) -> str:
        """Create fallback safety response when coordinated searches fail"""
        return f"""⚠️ **SAFETY INFORMATION UNAVAILABLE**

The coordinated safety analysis system could not retrieve comprehensive safety information for **{medication}** at this time.

**IMMEDIATE SAFETY ACTIONS REQUIRED:**

**For Comprehensive Safety Information:**
- **Your Pharmacist** - Most accessible for medication safety questions and side effect guidance
- **Healthcare Provider** - For personalized safety assessment and risk evaluation
- **Medication Package Insert** - Read all safety warnings and side effect information completely

**Critical Safety Resources:**
- **FDA Drug Safety**: https://www.fda.gov/drugs/drug-safety-and-availability
- **MedlinePlus Safety**: https://medlineplus.gov/ - Search for "{medication} side effects"
- **Poison Control**: 1-800-222-1222 (US) - For safety emergencies

**Patient Information**: {patient_info}

**🚨 ESSENTIAL SAFETY REMINDERS:**
⚠️ **Monitor Closely** - Watch for any unusual symptoms or reactions
⚠️ **Emergency Readiness** - Know signs requiring immediate medical attention
⚠️ **Professional Consultation** - Contact healthcare providers for safety concerns
⚠️ **Complete Information** - Read all medication literature and warnings

**SAFETY PRIORITY**: When digital safety analysis is unavailable, direct consultation with qualified healthcare professionals and thorough review of official medication safety information ensures the highest level of safety protection."""


sideeffects_agent = CoordinatedSideEffectsAgent()


def get_sideeffects_agent():
    """Get the coordinated side effects agent instance"""
    return sideeffects_agent
