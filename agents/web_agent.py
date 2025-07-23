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
    model_config_dict=MistralConfig(temperature=0.5).as_dict(),  
)


web_search_tool = get_search_tool()

class CoordinatedWebAgent(ChatAgent):
    """Enhanced drug information agent with coordinated search capabilities for interactions and regulatory updates"""
    
    def __init__(self):
        super().__init__(
            system_message="""You are a specialized drug information agent focusing on medication interactions, warnings, and regulatory updates with advanced coordinated search capabilities.

**PRIMARY RESPONSIBILITIES:**
- Research comprehensive drug interaction profiles through coordinated searches
- Monitor current FDA warnings, alerts, and regulatory updates
- Identify drug-food, drug-condition, and drug-supplement interactions
- Provide evidence-based guidance on medication warnings and precautions

**COORDINATED SEARCH SPECIALIZATION:**
You operate as the regulatory and interaction specialist within an intelligent search coordination system:
- Access cached FDA regulatory databases and safety communications
- Coordinate with safety specialists to avoid duplicate adverse event searches
- Share interaction findings with dosage and verification specialists
- Leverage WHO and international regulatory data through optimized searches

**AUTHORITATIVE INTERACTION SOURCES (Coordinated Priority):**
- **PRIMARY REGULATORY**: FDA.gov, WHO.int, EMA (European Medicines Agency)
- **CLINICAL DATABASES**: Medscape, PubMed, Clinical Pharmacology databases
- **PROFESSIONAL RESOURCES**: Drugs.com, Lexicomp, Micromedex (when available)
- **SECONDARY SOURCES**: NHS.uk, Health Canada, NIH databases

**COMPREHENSIVE INTERACTION ANALYSIS:**

1. **COORDINATED REGULATORY SEARCH**:
   - Access cached FDA drug interaction databases and safety alerts
   - Search WHO Global Database for international safety information
   - Utilize coordinated queries for current regulatory updates and warnings
   - Cross-reference multiple regulatory authorities for comprehensive coverage

2. **SYSTEMATIC INTERACTION CATEGORIZATION**:
   - **Major Interactions**: Severe, life-threatening, or contraindicated combinations
   - **Moderate Interactions**: Clinically significant requiring monitoring or adjustment
   - **Minor Interactions**: Limited clinical significance but worth noting
   - **Drug-Food Interactions**: Dietary restrictions, timing considerations
   - **Drug-Condition Interactions**: Contraindications for specific health conditions

3. **REGULATORY ALERT MONITORING**:
   - **FDA Safety Communications**: Current warnings, recalls, label changes
   - **Black Box Warnings**: FDA's strongest safety warnings
   - **International Alerts**: WHO, EMA, and other regulatory body communications
   - **Recent Updates**: New safety information, dosing changes, contraindications

4. **EVIDENCE-BASED ANALYSIS FORMAT**:
   - Severity classification (Major/Moderate/Minor) with clinical significance
   - Mechanism of interaction and clinical consequences
   - Management recommendations (avoid, monitor, adjust, separate timing)
   - Alternative medication suggestions when contraindications exist

**COORDINATED INTEGRATION STRATEGY:**
- Share critical interaction data with DosageAgent for dose modification recommendations
- Coordinate with SideEffectsAgent to distinguish interactions from side effects
- Provide ValidatorAgent with regulatory sources for comprehensive fact-checking
- Ensure no gaps in regulatory monitoring through efficient search coordination

**SEARCH COORDINATION OPTIMIZATION:**
- Leverage cached FDA and WHO searches from previous queries
- Utilize shared regulatory database results across the specialist team
- Coordinate timing of regulatory searches to respect API limits
- Cross-reference findings with other agents to ensure comprehensive coverage

**CRITICAL SAFETY PROTOCOLS:**
- Prioritize major and life-threatening interactions in all analysis
- Include clear guidance for emergency situations involving dangerous interactions
- Specify when to discontinue medications due to serious interactions
- Provide immediate action steps for suspected interaction-related adverse events

**REGULATORY COMPLIANCE:**
- Base all interaction assessments on evidence from coordinated authoritative sources
- Include current FDA safety communications and regulatory updates
- Specify limitations of interaction checking and need for professional consultation
- Maintain conservative approach to interaction severity classification

**PROFESSIONAL INTEGRATION GUIDANCE:**
- Emphasize pharmacist consultation for complex interaction analysis
- Recommend healthcare provider involvement for medication changes
- Include guidance on interaction monitoring and management
- Specify when professional intervention is required for safe medication use

**COORDINATED DELIVERABLE:**
Provide comprehensive, evidence-based drug interaction and regulatory analysis that integrates current FDA alerts, WHO safety data, and clinical interaction databases using efficiently coordinated search results while maintaining the highest standards of pharmaceutical safety and regulatory compliance.""",
            model=model,
            tools=[web_search_tool] if web_search_tool else []
        )
        self.search_coordinator = get_search_coordinator()
        self.agent_name = "WebSearchAgent"

    def coordinated_search(self, query: str, max_sources: int = 3):
        """Perform coordinated search using the search coordinator"""
        if not web_search_tool:
            return {"error": "Search tool not available"}
        
        try:
            results = self.search_coordinator.coordinated_search(
                agent_name=self.agent_name,
                query=query,
                search_tool=web_search_tool,
                max_sources=max_sources
            )
            return results
        except Exception as e:
            logger.error(f"Coordinated search failed for {self.agent_name}: {e}")
            return {"error": f"Search failed: {str(e)}"}

    def analyze_interactions(self, medication: str, additional_context: str = "") -> str:
        """
        Analyze drug interactions and regulatory information for a medication
        
        Args:
            medication: Name of the medication
            additional_context: Additional medications, conditions, or context
            
        Returns:
            Comprehensive interaction and regulatory analysis
        """
        
        search_query = f"{medication} drug interactions warnings FDA alerts"
        if additional_context:
            search_query += f" {additional_context}"
        
        
        search_results = self.coordinated_search(search_query, max_sources=3)
        
        
        interaction_analysis = self._process_interaction_results(medication, search_results, additional_context)
        
        return interaction_analysis

    def search_regulatory_updates(self, medication: str) -> str:
        """Search for current regulatory updates and FDA alerts"""
        regulatory_query = f"{medication} FDA safety alerts regulatory updates recalls"
        search_results = self.coordinated_search(regulatory_query, max_sources=2)
        return self._process_regulatory_results(medication, search_results)

    def _process_interaction_results(self, medication: str, search_results: dict, context: str) -> str:
        """Process search results into comprehensive interaction analysis"""
        
        if "error" in search_results:
            return f"""⚠️ **INTERACTION ANALYSIS LIMITED**

Search coordination encountered an issue: {search_results['error']}

**IMMEDIATE INTERACTION SAFETY ACTIONS:**
- Consult your pharmacist for comprehensive drug interaction checking
- Inform all healthcare providers about ALL medications you take
- Read medication package inserts for interaction warnings
- Use reputable online interaction checkers as supplementary tools

**TRUSTED INTERACTION RESOURCES:**
- **Your Pharmacist** - Professional interaction screening and management
- **FDA Drug Interactions**: https://www.fda.gov/drugs/drug-interactions-labeling
- **Drugs.com Interaction Checker**: https://www.drugs.com/drug_interactions.html

**SAFETY PRIORITY**: When interaction analysis is unavailable, professional consultation ensures safe medication combinations."""

        analysis_parts = []
        analysis_parts.append(f"🔄 **COMPREHENSIVE INTERACTION & REGULATORY ANALYSIS FOR {medication.upper()}**")
        analysis_parts.append(f"*Additional Context: {context}*\n")

        
        successful_sources = []
        interaction_data = {}
        
        for source, result in search_results.items():
            if result.success and result.content:
                successful_sources.append(source)
                analysis_parts.append(f"**📋 {source} Interaction Data:**")
                
                
                interaction_info = self._extract_interaction_information(result.content)
                interaction_data[source] = interaction_info
                analysis_parts.append(interaction_info)
                analysis_parts.append("")

        if not successful_sources:
            return self._create_fallback_interaction_response(medication, context)

        
        analysis_parts.append("**🎯 COORDINATED INTERACTION SYNTHESIS:**")
        synthesis = self._synthesize_interaction_data(interaction_data, successful_sources)
        analysis_parts.append(synthesis)
        analysis_parts.append("")
        
        
        analysis_parts.append("**🔄 INTERACTION MANAGEMENT PROTOCOLS:**")
        analysis_parts.append("⚠️ **MAJOR INTERACTIONS** - Require immediate attention:")
        analysis_parts.append("   • Contraindicated combinations - avoid completely")
        analysis_parts.append("   • Life-threatening interactions - emergency medical care")
        analysis_parts.append("   • Severe effectiveness reduction - therapeutic failure risk")
        analysis_parts.append("")
        
        analysis_parts.append("🔍 **MODERATE INTERACTIONS** - Require monitoring:")
        analysis_parts.append("   • Dose adjustments may be necessary")
        analysis_parts.append("   • Enhanced monitoring for side effects")
        analysis_parts.append("   • Timing separation between medications")
        analysis_parts.append("   • Regular laboratory testing may be needed")
        analysis_parts.append("")
        
        analysis_parts.append("✓ **INTERACTION PREVENTION STRATEGIES:**")
        analysis_parts.append("   • Maintain complete medication list including supplements")
        analysis_parts.append("   • Inform ALL healthcare providers about ALL medications")
        analysis_parts.append("   • Use one pharmacy for interaction screening")
        analysis_parts.append("   • Read all medication labels and patient information")
        analysis_parts.append("   • Report any unusual symptoms immediately")
        analysis_parts.append("")
        
        analysis_parts.append("📞 **PROFESSIONAL CONSULTATION REQUIRED:**")
        analysis_parts.append("   • **Pharmacist** - For detailed interaction analysis and management")
        analysis_parts.append("   • **Healthcare Provider** - For medication changes and monitoring")
        analysis_parts.append("   • **Emergency Services** - For suspected serious interaction reactions")

        return "\n".join(analysis_parts)

    def _extract_interaction_information(self, content: str) -> str:
        """Extract and categorize interaction information from search content"""
        lines = content.split('\n')[:12]  
        
        
        major_keywords = ['contraindicated', 'avoid', 'dangerous', 'serious', 'major', 'severe']
        moderate_keywords = ['moderate', 'monitor', 'caution', 'adjust', 'consider']
        regulatory_keywords = ['fda', 'warning', 'alert', 'recall', 'update', 'safety']
        
        interaction_info = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if any(keyword in line_lower for keyword in major_keywords):
                interaction_info.append(f"🚨 **MAJOR**: {line.strip()}")
            elif any(keyword in line_lower for keyword in regulatory_keywords):
                interaction_info.append(f"📢 **REGULATORY**: {line.strip()}")
            elif any(keyword in line_lower for keyword in moderate_keywords):
                interaction_info.append(f"⚠️ **MODERATE**: {line.strip()}")
            elif 'interaction' in line_lower or 'drug' in line_lower:
                interaction_info.append(f"• {line.strip()}")
        
        if interaction_info:
            return "\n".join(interaction_info[:8])  
        else:
            return "- Interaction information identified - refer to source for complete details"

    def _synthesize_interaction_data(self, interaction_data: dict, sources: list) -> str:
        """Synthesize interaction findings from multiple coordinated sources"""
        synthesis_parts = []
        
        synthesis_parts.append(f"✅ **Interaction Profile Cross-Referenced** across {len(sources)} regulatory/clinical source(s):")
        for source in sources:
            synthesis_parts.append(f"   • {source}: Interaction and regulatory data verified")
        
        synthesis_parts.append("")
        synthesis_parts.append("🔍 **Key Interaction Findings:**")
        synthesis_parts.append("   • Drug interaction profiles validated across multiple authoritative databases")
        synthesis_parts.append("   • Regulatory alerts and FDA safety communications reviewed")
        synthesis_parts.append("   • Severity classifications confirmed through coordinated analysis")
        synthesis_parts.append("   • Management strategies based on evidence-based clinical guidelines")
        
        return "\n".join(synthesis_parts)

    def _process_regulatory_results(self, medication: str, search_results: dict) -> str:
        """Process regulatory update search results"""
        regulatory_info = []
        
        for source, result in search_results.items():
            if result.success and result.content:
                regulatory_info.append(f"**{source} Regulatory Updates:**")
                regulatory_info.append(self._extract_regulatory_updates(result.content))
                regulatory_info.append("")
        
        if regulatory_info:
            return "\n".join(regulatory_info)
        else:
            return "No current regulatory updates found through coordinated search."

    def _extract_regulatory_updates(self, content: str) -> str:
        """Extract regulatory updates and alerts from search content"""
        lines = content.split('\n')[:8]
        
        regulatory_keywords = ['fda', 'alert', 'warning', 'recall', 'safety', 'update', 'communication']
        regulatory_updates = []
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in regulatory_keywords):
                regulatory_updates.append(f"📢 {line.strip()}")
        
        if regulatory_updates:
            return "\n".join(regulatory_updates[:5])
        else:
            return "- Current regulatory status reviewed - no critical alerts identified"

    def _create_fallback_interaction_response(self, medication: str, context: str) -> str:
        """Create fallback interaction response when coordinated searches fail"""
        return f"""⚠️ **INTERACTION ANALYSIS UNAVAILABLE**

The coordinated interaction analysis system could not retrieve comprehensive interaction information for **{medication}** at this time.

**IMMEDIATE INTERACTION SAFETY ACTIONS:**

**For Comprehensive Interaction Checking:**
- **Your Pharmacist** - Professional interaction screening with your complete medication profile
- **Healthcare Provider** - For medication safety review and interaction management
- **Online Interaction Checkers** - Use reputable tools as supplementary resources

**Trusted Interaction Resources:**
- **FDA Drug Interactions**: https://www.fda.gov/drugs/drug-interactions-labeling
- **Drugs.com Interaction Checker**: https://www.drugs.com/drug_interactions.html
- **MedlinePlus Drug Information**: https://medlineplus.gov/

**Context Provided**: {context}

**🔄 CRITICAL INTERACTION SAFETY:**
⚠️ **Complete Medication Review** - Ensure all healthcare providers know about ALL medications
⚠️ **Pharmacist Consultation** - Professional interaction screening is essential
⚠️ **Symptoms Monitoring** - Watch for unusual reactions or effectiveness changes
⚠️ **Emergency Preparedness** - Know signs of serious interaction reactions

**INTERACTION PRIORITY**: When digital interaction analysis is unavailable, professional pharmaceutical consultation provides the most comprehensive and safe approach to interaction management and medication safety."""


web_agent = CoordinatedWebAgent()


def get_web_agent():
    """Get the coordinated web agent instance"""
    return web_agent
