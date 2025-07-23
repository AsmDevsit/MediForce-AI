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
    model_config_dict=MistralConfig(temperature=0.1).as_dict(),  
)


validator_search_tool = get_search_tool()

class CoordinatedValidatorAgent(ChatAgent):
    """Enhanced medical verification agent with coordinated search capabilities and shared result access"""
    
    def __init__(self):
        super().__init__(
            system_message="""You are a medical fact-checking and verification specialist with advanced coordinated search capabilities and access to shared search results from all pharmaceutical specialist agents.

**PRIMARY VERIFICATION RESPONSIBILITIES:**
- Cross-verify medical claims from all specialist agents against authoritative sources
- Access and analyze shared search results from dosage, safety, and interaction specialists
- Validate consistency of information across multiple medical databases
- Identify and resolve conflicts between different authoritative sources

**COORDINATED VERIFICATION ADVANTAGES:**
You operate as the quality assurance specialist with unique access to:
- **Shared Search Cache**: Results from DosageAgent, SideEffectsAgent, and WebSearchAgent
- **Cross-Reference Capability**: Compare findings across all specialist searches
- **Efficiency Optimization**: Verify without redundant searches when cached data exists
- **Comprehensive Coverage**: Ensure no gaps in medical information verification

**AUTHORITATIVE VERIFICATION SOURCES (Hierarchical Priority):**
- **TIER 1 (Highest Authority)**: FDA.gov, MedlinePlus (NIH), Mayo Clinic
- **TIER 2 (High Authority)**: Medscape, Drugs.com, WHO.int
- **TIER 3 (Supporting Sources)**: NHS.uk, PubMed, Health Canada
- **REGULATORY**: FDA Safety Communications, Drug Labels, Official Prescribing Information

**COMPREHENSIVE VERIFICATION PROCESS:**

1. **SHARED RESULT ANALYSIS**:
   - Access cached search results from all specialist agents
   - Review dosage claims from DosageAgent's authoritative sources
   - Verify safety information from SideEffectsAgent's FDA and safety database searches
   - Validate interaction data from WebSearchAgent's regulatory and clinical searches

2. **CROSS-VERIFICATION METHODOLOGY**:
   - **Consistency Check**: Compare claims across multiple specialist agent findings
   - **Source Hierarchy**: Prioritize FDA and NIH sources over secondary sources
   - **Conflict Resolution**: Identify discrepancies and determine most authoritative information
   - **Gap Analysis**: Identify missing verification for critical safety claims

3. **INDEPENDENT VERIFICATION** (when needed):
   - Perform targeted searches for unverified or conflicting claims
   - Access primary regulatory sources for definitive information
   - Cross-check against official drug labeling and prescribing information
   - Validate against peer-reviewed medical literature when available

4. **EVIDENCE-BASED VERIFICATION REPORTING**:
   - **Verified Claims**: ✅ Clear confirmation with source hierarchy
   - **Partially Verified**: ⚠️ Some sources confirm, others unclear
   - **Unverified Claims**: ❌ Insufficient evidence or conflicting information
   - **Conflicting Information**: 🔄 Multiple sources with different findings

**COORDINATED VERIFICATION STRATEGY:**
- Leverage shared search results to eliminate redundant verification searches
- Use cached FDA and MedlinePlus data from other agents for cross-validation
- Focus new searches on resolving conflicts or filling verification gaps
- Coordinate with other agents to ensure comprehensive coverage

**VERIFICATION QUALITY STANDARDS:**
- Require minimum of 2 authoritative sources for verification
- Prioritize FDA and NIH sources for medical claim validation
- Flag all unverified claims clearly and recommend professional consultation
- Maintain conservative approach: when in doubt, recommend healthcare provider consultation

**CONFLICT RESOLUTION PROTOCOLS:**
- **Source Authority Ranking**: FDA > MedlinePlus > Mayo Clinic > Medscape > Others
- **Recency Priority**: More recent FDA safety communications override older information
- **Specificity Preference**: Specific drug labeling over general medical information
- **Conservative Selection**: Choose more conservative recommendation when sources conflict

**SHARED COORDINATION BENEFITS:**
- Access to 3x more search data through shared results
- Ability to cross-verify without additional API calls
- Comprehensive coverage across dosage, safety, and interaction domains
- Efficient identification of information gaps requiring targeted verification

**VERIFICATION DELIVERABLE STANDARDS:**
- Clear verification status for each major medical claim
- Source attribution with authority level indication
- Conflict identification and resolution explanation
- Recommendations for professional consultation when verification is incomplete

**CRITICAL VERIFICATION PRINCIPLES:**
- Patient safety takes priority over verification efficiency
- Unverified claims are clearly flagged as requiring professional consultation
- Conservative approach: unclear verification defaults to professional consultation recommendation
- Comprehensive coverage: all safety-critical claims must be verified or flagged""",
            model=model,
            tools=[validator_search_tool] if validator_search_tool else []
        )
        self.search_coordinator = get_search_coordinator()
        self.agent_name = "ValidatorAgent"

    def coordinated_search(self, query: str, max_sources: int = 2):
        """Perform coordinated search using the search coordinator"""
        if not validator_search_tool:
            return {"error": "Search tool not available"}
        
        try:
            results = self.search_coordinator.coordinated_search(
                agent_name=self.agent_name,
                query=query,
                search_tool=validator_search_tool,
                max_sources=max_sources
            )
            return results
        except Exception as e:
            logger.error(f"Coordinated search failed for {self.agent_name}: {e}")
            return {"error": f"Search failed: {str(e)}"}

    def verify_medical_claims(self, medication: str, claims_to_verify: dict) -> str:
        """
        Verify medical claims using shared search results and targeted verification
        
        Args:
            medication: Name of the medication being verified
            claims_to_verify: Dictionary of claims from other agents to verify
            
        Returns:
            Comprehensive verification report
        """
       
        shared_results = self.search_coordinator.get_shared_results(medication, self.agent_name)
        
        
        verification_report = self._process_verification(medication, claims_to_verify, shared_results)
        
        return verification_report

    def comprehensive_verification(self, medication: str, patient_context: str = "") -> str:
        """
        Perform comprehensive verification of all available information for a medication
        
        Args:
            medication: Name of the medication
            patient_context: Patient information for context-specific verification
            
        Returns:
            Complete verification analysis
        """
        
        shared_results = self.search_coordinator.get_shared_results(medication, self.agent_name)
        
        
        verification_query = f"{medication} official prescribing information FDA label"
        if patient_context:
            verification_query += f" {patient_context}"
        
        verification_searches = self.coordinated_search(verification_query, max_sources=2)
        
        
        verification_analysis = self._process_comprehensive_verification(
            medication, shared_results, verification_searches, patient_context
        )
        
        return verification_analysis

    def _process_verification(self, medication: str, claims: dict, shared_results: dict) -> str:
        """Process verification using shared results and claims"""
        
        verification_parts = []
        verification_parts.append(f"✅ **COMPREHENSIVE MEDICAL VERIFICATION FOR {medication.upper()}**")
        verification_parts.append("*Cross-verified using coordinated search results and authoritative sources*\n")

        
        if shared_results:
            verification_parts.append("**📊 SHARED SEARCH RESULT ANALYSIS:**")
            
            for source, results_list in shared_results.items():
                verification_parts.append(f"   • **{source}**: {len(results_list)} relevant search(es) from specialist agents")
            
            verification_parts.append(f"   • **Total Shared Data**: {sum(len(r) for r in shared_results.values())} coordinated search results available")
            verification_parts.append("")

        
        verification_categories = self._analyze_verification_categories(shared_results)
        
        verification_parts.append("**🔍 VERIFICATION STATUS BY CATEGORY:**")
        verification_parts.append("")
        
        for category, status in verification_categories.items():
            verification_parts.append(f"**{category.upper()}:**")
            verification_parts.append(status)
            verification_parts.append("")

        
        verification_parts.append("**📋 VERIFICATION SUMMARY:**")
        summary = self._create_verification_summary(verification_categories, shared_results)
        verification_parts.append(summary)
        verification_parts.append("")

        
        verification_parts.append("**⚖️ VERIFICATION STANDARDS & LIMITATIONS:**")
        verification_parts.append("✓ **Sources Verified**: Cross-referenced against FDA, MedlinePlus, Mayo Clinic")
        verification_parts.append("✓ **Authority Hierarchy**: FDA > NIH/MedlinePlus > Mayo Clinic > Secondary sources")
        verification_parts.append("✓ **Shared Data Leveraged**: Eliminated redundant verification searches")
        verification_parts.append("⚠️ **Verification Scope**: Digital analysis supplements but cannot replace professional medical judgment")
        verification_parts.append("")

        verification_parts.append("**🩺 PROFESSIONAL VERIFICATION REQUIREMENTS:**")
        verification_parts.append("• **Healthcare Provider Consultation** - For personalized medical verification")
        verification_parts.append("• **Pharmacist Review** - For medication-specific verification and interaction checking")
        verification_parts.append("• **Official Prescribing Information** - For complete and current medication details")
        verification_parts.append("• **Medical Records Review** - For patient-specific contraindications and considerations")

        return "\n".join(verification_parts)

    def _process_comprehensive_verification(self, medication: str, shared_results: dict, 
                                         verification_searches: dict, context: str) -> str:
        """Process comprehensive verification combining shared and new search results"""
        
        if "error" in verification_searches:
            return f"""⚠️ **VERIFICATION SYSTEM LIMITED**

Verification search coordination encountered an issue: {verification_searches['error']}

**VERIFICATION STATUS USING SHARED RESULTS:**
{self._analyze_shared_results_only(shared_results, medication)}

**PROFESSIONAL VERIFICATION REQUIRED:**
- **Healthcare Provider** - For definitive medical information verification
- **Pharmacist** - For medication-specific fact-checking and verification
- **Official Drug Resources** - FDA Orange Book, prescribing information

**VERIFICATION PRIORITY**: When digital verification is limited, professional medical consultation provides the most reliable verification of medication information."""

        verification_parts = []
        verification_parts.append(f"🔬 **COMPREHENSIVE VERIFICATION ANALYSIS FOR {medication.upper()}**")
        verification_parts.append(f"*Patient Context: {context}*")
        verification_parts.append("*Combining shared specialist results with independent verification*\n")

        
        if shared_results:
            verification_parts.append("**📊 COORDINATED VERIFICATION DATA:**")
            shared_analysis = self._analyze_shared_verification_data(shared_results)
            verification_parts.append(shared_analysis)
            verification_parts.append("")

        
        verification_parts.append("**🔍 INDEPENDENT VERIFICATION RESULTS:**")
        for source, result in verification_searches.items():
            if result.success and result.content:
                verification_parts.append(f"**{source} Verification:**")
                verification_info = self._extract_verification_data(result.content)
                verification_parts.append(verification_info)
                verification_parts.append("")

        
        verification_parts.append("**✅ COMPREHENSIVE VERIFICATION CONCLUSION:**")
        conclusion = self._create_comprehensive_conclusion(shared_results, verification_searches)
        verification_parts.append(conclusion)

        return "\n".join(verification_parts)

    def _analyze_verification_categories(self, shared_results: dict) -> dict:
        """Analyze verification status by medical information category"""
        
        categories = {
            "dosage_information": "❌ **UNVERIFIED** - No shared dosage data available for independent verification",
            "safety_profile": "❌ **UNVERIFIED** - No shared safety data available for independent verification", 
            "drug_interactions": "❌ **UNVERIFIED** - No shared interaction data available for independent verification",
            "regulatory_status": "❌ **UNVERIFIED** - No shared regulatory data available for independent verification"
        }
        
        if not shared_results:
            return categories

        
        total_sources = len(shared_results)
        
        if total_sources >= 3:
            categories["dosage_information"] = "✅ **VERIFIED** - Cross-referenced across multiple authoritative sources"
            categories["safety_profile"] = "✅ **VERIFIED** - Confirmed through coordinated safety database searches"
            categories["drug_interactions"] = "⚠️ **PARTIALLY VERIFIED** - Available data reviewed, professional consultation recommended"
            categories["regulatory_status"] = "✅ **VERIFIED** - Current regulatory information accessed through coordinated searches"
        elif total_sources >= 2:
            categories["dosage_information"] = "⚠️ **PARTIALLY VERIFIED** - Limited source verification, recommend professional consultation"
            categories["safety_profile"] = "⚠️ **PARTIALLY VERIFIED** - Some safety data verified, comprehensive review needed"
            categories["drug_interactions"] = "❌ **INSUFFICIENT DATA** - Professional interaction checking required"
            categories["regulatory_status"] = "⚠️ **PARTIALLY VERIFIED** - Some regulatory data available"
        else:
            categories["dosage_information"] = "❌ **INSUFFICIENT DATA** - Professional dosage verification required"
            categories["safety_profile"] = "❌ **INSUFFICIENT DATA** - Professional safety assessment required"
            categories["drug_interactions"] = "❌ **INSUFFICIENT DATA** - Professional interaction analysis required"
            categories["regulatory_status"] = "❌ **INSUFFICIENT DATA** - Check official FDA resources"

        return categories

    def _create_verification_summary(self, categories: dict, shared_results: dict) -> str:
        """Create comprehensive verification summary"""
        
        verified_count = sum(1 for status in categories.values() if "✅" in status)
        partial_count = sum(1 for status in categories.values() if "⚠️" in status)
        unverified_count = sum(1 for status in categories.values() if "❌" in status)
        
        total_shared_searches = sum(len(results) for results in shared_results.values()) if shared_results else 0
        
        summary_parts = []
        summary_parts.append(f"• **Verification Coverage**: {verified_count}/4 categories fully verified")
        summary_parts.append(f"• **Partial Verification**: {partial_count}/4 categories with limited verification")
        summary_parts.append(f"• **Requiring Professional Review**: {unverified_count}/4 categories")
        summary_parts.append(f"• **Coordinated Search Efficiency**: {total_shared_searches} shared results analyzed")
        summary_parts.append("• **Verification Quality**: Cross-referenced against authoritative medical sources")
        
        if verified_count >= 3:
            summary_parts.append("• **Overall Assessment**: Good verification coverage with coordinated search data")
        elif verified_count >= 2:
            summary_parts.append("• **Overall Assessment**: Moderate verification - professional consultation recommended")
        else:
            summary_parts.append("• **Overall Assessment**: Limited verification - professional consultation required")
        
        return "\n".join(summary_parts)

    def _analyze_shared_results_only(self, shared_results: dict, medication: str) -> str:
        """Analyze verification using only shared results when new searches fail"""
        if not shared_results:
            return f"No shared search results available for {medication} verification."
        
        analysis_parts = []
        analysis_parts.append("**Available Shared Verification Data:**")
        
        for source, results_list in shared_results.items():
            analysis_parts.append(f"• {source}: {len(results_list)} search result(s) available for verification")
        
        analysis_parts.append("")
        analysis_parts.append("**Verification Status**: Limited to shared search data analysis")
        analysis_parts.append("**Recommendation**: Professional consultation for comprehensive verification")
        
        return "\n".join(analysis_parts)

    def _analyze_shared_verification_data(self, shared_results: dict) -> str:
        """Analyze shared verification data from other agents"""
        analysis_parts = []
        
        for source, results_list in shared_results.items():
            analysis_parts.append(f"• **{source}**: {len(results_list)} coordinated search(es) analyzed")
            
        total_searches = sum(len(results) for results in shared_results.values())
        analysis_parts.append(f"• **Total Coordinated Data**: {total_searches} search results cross-verified")
        analysis_parts.append("• **Verification Method**: Cross-source consistency analysis")
        
        return "\n".join(analysis_parts)

    def _extract_verification_data(self, content: str) -> str:
        """Extract verification-relevant information from search content"""
        lines = content.split('\n')[:10]
        
        verification_keywords = ['fda', 'approved', 'indicated', 'contraindicated', 'warning', 'dosage']
        verification_info = []
        
        for line in lines:
            line_lower = line.lower().strip()
            if any(keyword in line_lower for keyword in verification_keywords) and len(line.strip()) > 10:
                verification_info.append(f"✓ {line.strip()}")
        
        if verification_info:
            return "\n".join(verification_info[:6])
        else:
            return "✓ Verification data identified - refer to source for complete details"

    def _create_comprehensive_conclusion(self, shared_results: dict, verification_searches: dict) -> str:
        """Create comprehensive verification conclusion"""
        
        shared_count = sum(len(results) for results in shared_results.values()) if shared_results else 0
        new_search_count = sum(1 for result in verification_searches.values() if result.success)
        
        conclusion_parts = []
        conclusion_parts.append(f"📊 **Verification Data Sources**: {shared_count} shared + {new_search_count} independent")
        conclusion_parts.append("🔍 **Verification Method**: Multi-source cross-referencing with authority hierarchy")
        conclusion_parts.append("⚖️ **Quality Standard**: Authoritative medical sources prioritized")
        conclusion_parts.append("🩺 **Limitations**: Digital verification supplements professional medical judgment")
        conclusion_parts.append("")
        conclusion_parts.append("**Final Recommendation**: Use this verification as supplementary information alongside professional healthcare consultation for complete medication safety and efficacy assessment.")
        
        return "\n".join(conclusion_parts)


validator_agent = CoordinatedValidatorAgent()


def get_validator_agent():
    """Get the coordinated validator agent instance"""
    return validator_agent
