from camel.societies.workforce import Workforce
from camel.tasks import Task
from camel.agents import ChatAgent
from camel.models import ModelFactory
from camel.configs import MistralConfig
from camel.types import ModelType, ModelPlatformType
from agents import get_all_agents
from search_coordinator import get_search_coordinator
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def create_mistral_coordinator():
    """Create Mistral-powered coordinator agent with search coordination awareness"""
    
    mistral_model = ModelFactory.create(
        model_platform=ModelPlatformType.MISTRAL,
        model_type=ModelType.MISTRAL_MEDIUM_3,
        model_config_dict=MistralConfig(temperature=0.3).as_dict(),
    )
    
    coordinator = ChatAgent(
        system_message="""You are a pharmacy workflow coordinator specializing in pharmaceutical analysis with advanced search coordination.

**ENHANCED COORDINATION CAPABILITIES:**
Your system now features intelligent search coordination that:
- Eliminates redundant searches across specialist agents
- Prioritizes authoritative medical sources (FDA, MedlinePlus, Mayo Clinic)
- Caches search results for efficiency
- Ensures comprehensive coverage without duplication

**COORDINATION RESPONSIBILITIES:**
- Analyze incoming pharmaceutical queries and patient information
- Assign tasks to appropriate medical specialist agents based on their expertise
- Orchestrate coordinated information gathering to avoid duplicate searches
- Monitor search efficiency and ensure comprehensive coverage
- Synthesize specialist findings into comprehensive medical recommendations

**AVAILABLE COORDINATED SPECIALISTS:**
- **Dosage Specialist**: Medication dosing with coordinated search for authoritative guidelines
- **Safety Specialist**: Side effects analysis using cached safety databases
- **Information Specialist**: Drug interactions via coordinated regulatory searches  
- **Verification Specialist**: Fact-checking using shared search results

**SEARCH COORDINATION STRATEGY:**
- DosageAgent focuses on: MedlinePlus, Mayo Clinic for dosing guidelines
- SideEffectsAgent prioritizes: FDA, MedlinePlus for safety information
- WebSearchAgent targets: FDA, WHO for regulatory updates and interactions
- ValidatorAgent cross-references: All sources for comprehensive verification

**QUALITY ASSURANCE:**
- Monitor search result quality and source reliability
- Ensure no critical information gaps due to search coordination
- Flag when manual searches may be needed for complex cases
- Maintain search efficiency metrics for continuous improvement

**SAFETY PROTOCOLS:**
- Always prioritize patient safety and evidence-based medical information
- Include appropriate medical disclaimers and professional consultation recommendations
- Ensure search coordination doesn't compromise information completeness
- Maintain high standards for medical accuracy and source authority

**WORKFLOW OPTIMIZATION:**
- Leverage cached results to provide faster responses
- Coordinate search timing to respect rate limits
- Balance search efficiency with information comprehensiveness
- Monitor and report on coordination effectiveness""",
        model=mistral_model,
        tools=[]
    )
    
    return coordinator

def create_mistral_task_planner():
    """Create Mistral-powered task planning agent with search coordination"""
    
    mistral_model = ModelFactory.create(
        model_platform=ModelPlatformType.MISTRAL,
        model_type=ModelType.MISTRAL_MEDIUM_3,
        model_config_dict=MistralConfig(temperature=0.2).as_dict(),
    )
    
    task_planner = ChatAgent(
        system_message="""You are a medical task planner for pharmaceutical analysis workflows with intelligent search coordination.

**COORDINATED WORKFLOW PLANNING:**

**1. COORDINATED INFORMATION GATHERING PHASE**
   - **Dosage Analysis**: Coordinated search of MedlinePlus, Mayo Clinic for dosing guidelines
     * Patient-specific considerations (age, weight, conditions)
     * Administration schedules and maximum limits
     * Special population dosing (pediatric, geriatric, renal impairment)
   
   - **Safety Assessment**: Prioritized search of FDA, MedlinePlus for safety data
     * Common and serious side effects with incidence rates
     * Contraindications and drug allergies
     * Age and condition-specific warnings
   
   - **Interaction Research**: Targeted search of FDA, regulatory databases
     * Drug-drug interactions with severity classifications
     * Drug-food interactions and dietary considerations
     * Current FDA alerts, warnings, and regulatory updates
   
   - **Search Optimization**: Coordinate to prevent redundant API calls
     * Cache frequently requested medication information
     * Share search results between specialist agents
     * Respect source rate limits and optimize query timing

**2. COORDINATED VERIFICATION PHASE**
   - **Shared Result Validation**: Use cached search results for cross-verification
     * Validate dosage recommendations against multiple authoritative sources
     * Cross-check safety information using shared search cache
     * Confirm interaction data across regulatory databases
   
   - **Source Authority Assessment**: Evaluate information quality and reliability
     * Prioritize FDA and MedlinePlus over secondary sources
     * Flag conflicting information between authoritative sources
     * Ensure evidence-based medical accuracy throughout

**3. EFFICIENT SYNTHESIS PHASE**
   - **Comprehensive Analysis**: Combine all coordinated findings efficiently
     * Integrate dosage, safety, and interaction information
     * Resolve any conflicts using source authority hierarchy
     * Ensure completeness despite search coordination optimizations
   
   - **Quality Assurance**: Verify search coordination didn't miss critical information
     * Monitor coverage gaps that might need additional searches
     * Ensure patient safety considerations are comprehensive
     * Validate that efficiency gains don't compromise medical accuracy

**SEARCH COORDINATION PRINCIPLES:**
- Efficiency without compromising safety or completeness
- Intelligent source assignment based on specialty and authority
- Result sharing to eliminate redundant searches
- Rate limiting respect and error handling
- Continuous monitoring of coordination effectiveness

**TASK SPECIFICITY REQUIREMENTS:**
Each coordinated subtask must be specific, medically sound, and contribute to comprehensive pharmaceutical analysis that prioritizes patient safety while leveraging search efficiency improvements.""",
        model=mistral_model,
        tools=[]
    )
    
    return task_planner

def create_pharmacy_workforce():
    """Create CAMEL Workforce with Mistral-powered coordination and search optimization"""
    
    # Initialize search coordinator
    search_coordinator = get_search_coordinator()
    logger.info("✓ Search Coordinator initialized")
    
    # Create custom Mistral agents for coordination
    coordinator = create_mistral_coordinator()
    task_planner = create_mistral_task_planner()
    
    # Create workforce with custom agents
    workforce = Workforce(
        description='Pharmacy AI Assistant Workforce - Multi-agent pharmaceutical analysis with Mistral coordination and intelligent search coordination',
        coordinator_agent=coordinator,
        task_agent=task_planner,
        graceful_shutdown_timeout=30.0,
        share_memory=False,
        use_structured_output_handler=False,
    )
    
    # Get existing specialist agents (now with search coordination)
    agents = get_all_agents()
    
    # Add specialist workers with enhanced descriptions
    workforce.add_single_agent_worker(
        description="Coordinated Dosage Analysis Specialist: Expert in medication dosing guidelines with intelligent search coordination. Uses cached results from MedlinePlus and Mayo Clinic for age-weight calculations, administration schedules, maximum daily limits, and frequency recommendations. Eliminates redundant searches while ensuring comprehensive dosage coverage.",
        worker=agents["DosageAgent"]
    ).add_single_agent_worker(
        description="Coordinated Safety Assessment Specialist: Expert in medication side effects and adverse reactions with prioritized search coordination. Leverages shared cache from FDA and medical databases to identify common and serious safety concerns without redundant API calls. Focuses on patient-specific risks and contraindications.",
        worker=agents["SideEffectsAgent"]
    ).add_single_agent_worker(
        description="Coordinated Drug Information Specialist: Expert in current drug interactions and regulatory updates with targeted search coordination. Efficiently accesses FDA alerts, medication recalls, and WHO databases through coordinated searches. Shares regulatory findings with verification team.",
        worker=agents["WebSearchAgent"]
    ).add_single_agent_worker(
        description="Coordinated Medical Verification Specialist: Medical fact-checker with access to shared search results from all specialist agents. Uses cached findings from FDA, MedlinePlus, Mayo Clinic, and other authoritative sources to validate dosage, safety, and interaction data without redundant searches.",
        worker=agents["ValidatorAgent"]
    )
    
    return workforce

def run_pharmacy_query(user_query: str):
    """
    Process pharmacy query using CAMEL Workforce with Mistral coordination and search optimization
    
    Args:
        user_query (str): User's pharmacy question
        
    Returns:
        str: Comprehensive pharmacy guidance response with search coordination metrics
    """
    
    try:
        # Verify Mistral API key
        if not os.getenv('MISTRAL_API_KEY'):
            return "⚠️ Configuration Error: MISTRAL_API_KEY not found in environment variables."
        
        # Get search coordinator for monitoring
        search_coordinator = get_search_coordinator()
        initial_stats = search_coordinator.get_cache_stats()
        
        print("Creating Mistral-powered pharmacy workforce with search coordination...")
        workforce = create_pharmacy_workforce()
        print("✓ Coordinated workforce created with intelligent search optimization")
        
        # Create comprehensive pharmaceutical analysis task with search coordination
        task_content = f"""
        **COORDINATED PHARMACEUTICAL ANALYSIS REQUEST**
        
        **Patient Query:** {user_query}
        
        **COORDINATED MULTI-SPECIALIST ANALYSIS WITH SEARCH OPTIMIZATION:**
        
        **COORDINATED DOSAGE ANALYSIS:**
        - Utilize shared search results from MedlinePlus and Mayo Clinic for dosage guidelines
        - Determine safe and effective medication dosages with patient-specific considerations
        - Leverage cached results for age, weight, and health status factors
        - Specify administration frequency, timing, and duration from authoritative sources
        - Include maximum daily limits and safety thresholds from coordinated searches
        - Note special administration instructions from verified medical databases
        
        **COORDINATED SAFETY ASSESSMENT:**
        - Access cached FDA and medical database results for side effect information
        - Identify common side effects (>1% incidence) using shared search data
        - List serious adverse reactions from coordinated regulatory searches
        - Note contraindications and patient-specific risks from verified sources
        - Include age-specific, gender-specific warnings from cached medical data
        - Highlight allergy considerations using shared safety databases
        
        **COORDINATED DRUG INFORMATION RESEARCH:**
        - Efficiently search FDA and WHO databases for current drug interactions
        - Research drug-food interactions using coordinated regulatory searches
        - Find current FDA safety alerts through optimized search coordination
        - Check recent regulatory updates via shared search results
        - Investigate condition-specific contraindications from cached data
        - Share findings with verification team to eliminate duplicate searches
        
        **COORDINATED VERIFICATION PROCESS:**
        - Cross-check dosage recommendations using shared search cache
        - Validate safety information against coordinated database results
        - Confirm interaction data using previously searched FDA and medical sources
        - Ensure all medical claims are evidence-based using coordinated verification
        - Verify information accuracy through shared authoritative source data
        - Flag any discrepancies found in coordinated search results
        
        **SEARCH COORDINATION REQUIREMENTS:**
        - Eliminate redundant searches across all specialist agents
        - Prioritize authoritative sources: FDA, MedlinePlus, Mayo Clinic, WHO
        - Share search results between agents to improve efficiency
        - Respect API rate limits and implement intelligent search timing
        - Cache frequently requested medication information for faster responses
        - Monitor search coordination effectiveness and report any coverage gaps
        
        **SAFETY AND PROFESSIONAL STANDARDS:**
        - Maintain high medical accuracy despite search optimization
        - Use only trusted medical sources prioritized by search coordination
        - Include comprehensive medical disclaimers in all recommendations
        - Specify situations requiring immediate professional medical consultation
        - Ensure search efficiency doesn't compromise patient safety priorities
        - Maintain evidence-based medical accuracy throughout coordinated analysis
        
        **COORDINATED DELIVERABLE:**
        Synthesize all coordinated specialist findings into a comprehensive, safe, and medically sound pharmaceutical guidance response that combines dosage recommendations, safety considerations, interaction warnings, and verification status. Include search coordination metrics to demonstrate efficiency improvements while maintaining medical accuracy and safety standards.
        """
        
        # Create and process task
        task = Task(
            content=task_content,
            id="coordinated_pharmacy_workforce_analysis"
        )
        
        print("🔄 Processing coordinated pharmaceutical analysis with search optimization...")
        workforce.process_task(task)
        
        # Get results and coordination metrics
        result = task.result
        final_stats = search_coordinator.get_cache_stats()
        
        print("✅ Coordinated workforce analysis completed successfully")
        
        if result:
            return format_coordinated_workforce_response(result, user_query, initial_stats, final_stats)
        else:
            return create_professional_fallback()
            
    except Exception as e:
        return handle_workforce_error(e)

def format_coordinated_workforce_response(result, original_query, initial_stats, final_stats):
    """Format workforce result with search coordination metrics"""
    
    try:
        # Extract content from result
        if isinstance(result, str):
            content = result
        elif hasattr(result, 'content'):
            content = result.content  
        elif hasattr(result, 'msg') and hasattr(result.msg, 'content'):
            content = result.msg.content
        else:
            content = str(result)
        
        # Calculate search efficiency improvements
        searches_saved = calculate_search_efficiency(initial_stats, final_stats)
        
        # Create structured medical response with coordination metrics
        formatted_response = f"""🧾 **COORDINATED PHARMACY ANALYSIS**
*(Powered by Mistral AI Multi-Agent Workforce with Intelligent Search Coordination)*

**Original Query:** {original_query}

**📋 COORDINATED MULTI-SPECIALIST FINDINGS:**

{content}

---

**⚡ SEARCH COORDINATION EFFICIENCY REPORT:**

{searches_saved}

---

**⚠️ CRITICAL MEDICAL DISCLAIMER**

**THIS ANALYSIS IS FOR EDUCATIONAL PURPOSES ONLY**

**PROFESSIONAL CONSULTATION REQUIRED:**
• **Licensed Pharmacist** - For medication questions, dosing guidance, and drug interactions
• **Healthcare Provider** - For personalized medical advice, treatment decisions, and health assessments
• **Emergency Services** - For severe adverse reactions, allergic responses, or medical emergencies

**SEARCH COORDINATION BENEFITS:**
✓ **Faster Response Times** - Eliminated redundant searches across specialist agents
✓ **Comprehensive Coverage** - Intelligent source prioritization ensures thorough analysis
✓ **Enhanced Reliability** - Cached results improve consistency and reduce API failures
✓ **Resource Efficiency** - Optimized searches respect rate limits and reduce costs

**ESSENTIAL SAFETY REMINDERS:**
✓ Follow all prescribed medication instructions exactly as directed
✓ Read medication labels, package inserts, and patient information sheets
✓ Report any unusual symptoms or side effects to your healthcare provider immediately
✓ Inform all healthcare providers about all medications, supplements, and health conditions
✓ Store medications safely according to package instructions and away from children
✓ Never share medications with others or use expired medications
✓ Keep an updated list of all medications for medical appointments and emergencies

**EMERGENCY CONTACTS:**
• **Emergency Services:** 911 (US) / Your local emergency number
• **Poison Control Center:** 1-800-222-1222 (US)
• **Your Healthcare Provider:** [Keep contact information readily accessible]

**TRUSTED MEDICAL RESOURCES:**
• MedlinePlus: https://medlineplus.gov/ (NIH)
• FDA Drug Information: https://www.fda.gov/drugs/
• Mayo Clinic: https://www.mayoclinic.org/drugs-supplements

⚠️ **REMEMBER:** This coordinated AI analysis cannot replace the personalized medical judgment and expertise of qualified healthcare professionals who understand your complete medical history and current health status. The search coordination improvements enhance efficiency while maintaining the highest standards of medical accuracy and safety."""

        return formatted_response
        
    except Exception as e:
        print(f"Response formatting error: {e}")
        return create_professional_fallback()

def calculate_search_efficiency(initial_stats, final_stats):
    """Calculate and format search efficiency improvements"""
    
    try:
        initial_searches = initial_stats.get('total_cached_results', 0)
        final_searches = final_stats.get('total_cached_results', 0)
        new_searches = final_searches - initial_searches
        
        cache_hit_rate = final_stats.get('cache_hit_rate', '0%')
        successful_searches = final_stats.get('successful_searches', 0)
        failed_searches = final_stats.get('failed_searches', 0)
        
        efficiency_report = f"""**📊 Search Coordination Metrics:**
• **New Searches Performed:** {new_searches}
• **Cache Hit Rate:** {cache_hit_rate}
• **Successful Searches:** {successful_searches}
• **Failed Searches:** {failed_searches}
• **Search Efficiency:** Coordinated search system prevented redundant API calls
• **Source Prioritization:** Authoritative medical sources prioritized automatically
• **Response Speed:** Improved through intelligent caching and coordination"""
        
        return efficiency_report
        
    except Exception as e:
        return f"**📊 Search Coordination:** Active (metrics calculation error: {str(e)[:50]}...)"

def handle_workforce_error(error):
    """Handle workforce errors with search coordination context"""
    
    error_msg = str(error)
    print(f"Coordinated Workforce Error: {error_msg}")
    
    if "MISTRAL_API_KEY" in error_msg:
        return """⚠️ **API Configuration Error**
        
Please verify your MISTRAL_API_KEY is properly set in your .env file:
```
MISTRAL_API_KEY=your_actual_mistral_key_here
```

**Search Coordination Status:** Ready (API key needed for workforce activation)

Ensure the key is valid, active, and properly formatted without extra spaces or quotes."""
    
    else:
        return f"""⚠️ **Coordinated Workforce System Error**

The multi-specialist pharmaceutical analysis system with search coordination encountered an error and cannot complete the analysis at this time.

**SEARCH COORDINATION STATUS:** System initialization failed

**FOR IMMEDIATE MEDICATION GUIDANCE:**

**Primary Healthcare Resources:**
• Contact your licensed pharmacist for medication questions
• Consult your healthcare provider for medical advice
• Visit your local urgent care center for pressing concerns
• Call emergency services for severe reactions or emergencies

**Trusted Online Medical Resources:**
• MedlinePlus: https://medlineplus.gov/ (NIH)
• FDA Drug Information: https://www.fda.gov/drugs/
• Mayo Clinic Drug Information: https://www.mayoclinic.org/drugs-supplements

**Emergency Contacts:**
• Emergency Services: 911 (US) / Your local emergency number
• Poison Control: 1-800-222-1222 (US)

**Technical Details:** {error_msg[:150]}...

**Note:** The search coordination system was designed to improve efficiency while maintaining medical accuracy. When digital analysis tools are unavailable, direct consultation with qualified healthcare professionals remains the safest and most reliable approach."""

def create_professional_fallback():
    """Create professional fallback response with search coordination context"""
    
    return """⚠️ **COORDINATED ANALYSIS SYSTEM UNAVAILABLE**

The multi-specialist pharmaceutical analysis with search coordination could not be completed at this time.

**SEARCH COORDINATION STATUS:** System temporarily unavailable

**RECOMMENDED IMMEDIATE ACTIONS:**

**For Medication Questions:**
• **Your Pharmacist** - Most accessible for drug-related questions, dosing guidance, and interaction checks
• **Healthcare Provider** - For medical advice, prescription questions, and health assessments  
• **Urgent Care Center** - For pressing medication concerns requiring prompt attention

**For Emergency Situations:**
• **Emergency Room** - For severe adverse reactions or serious medical concerns
• **Poison Control** - For medication overdoses or toxic exposures: 1-800-222-1222 (US)

**Trusted Medical Information Sources:**
• **MedlinePlus:** https://medlineplus.gov/ - Comprehensive drug information from NIH
• **FDA Drug Database:** https://www.accessdata.fda.gov/scripts/cder/daf/ - Official medication information
• **Mayo Clinic:** https://www.mayoclinic.org/drugs-supplements - Professional medical guidance

**About Search Coordination:**
Our system was designed to eliminate redundant searches and improve response times while maintaining medical accuracy. When unavailable, these authoritative sources provide the same high-quality information our coordinated system would access.

**Remember:** Professional healthcare consultation provides the personalized, comprehensive, and safe medical guidance that digital tools cannot match, regardless of their coordination sophistication."""
