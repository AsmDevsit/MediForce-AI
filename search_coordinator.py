"""
Centralized Search Coordination System for Pharmacy Multi-Agent System

This module provides intelligent search coordination to eliminate redundant API calls
and ensure efficient information gathering across all specialist agents.
"""

import hashlib
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SourcePriority(Enum):
    """Priority levels for medical information sources"""
    PRIMARY = 1      # FDA, MedlinePlus, Mayo Clinic
    SECONDARY = 2    # Drugs.com, Medscape  
    TERTIARY = 3     # WHO, Healthline, PubMed

class InformationType(Enum):
    """Types of medical information being searched"""
    DOSAGE = "dosage"
    SIDE_EFFECTS = "side_effects"
    INTERACTIONS = "interactions"
    WARNINGS = "warnings"
    GENERAL = "general"
    VERIFICATION = "verification"

@dataclass
class SearchResult:
    """Container for search results with metadata"""
    query: str
    source: str
    content: str
    timestamp: float
    agent_name: str
    info_type: InformationType
    success: bool = True
    error_message: Optional[str] = None

@dataclass
class SourceSpec:
    """Specification for medical information sources"""
    name: str
    url_pattern: str
    priority: SourcePriority
    specialties: List[InformationType]
    rate_limit: float = 1.0  # seconds between requests

class SearchCoordinator:
    """
    Centralized coordinator for managing searches across all pharmacy agents.
    
    Features:
    - Search result caching to avoid redundant API calls
    - Intelligent source assignment based on information type
    - Rate limiting and error handling
    - Search result sharing between agents
    """
    
    def __init__(self, cache_ttl: int = 3600):  # 1 hour cache TTL
        self.cache: Dict[str, SearchResult] = {}
        self.cache_ttl = cache_ttl
        self.last_request_time: Dict[str, float] = {}
        self.failed_sources: Dict[str, float] = {}  # Track temporary failures
        
        # Define authoritative medical sources with their specialties
        self.sources = {
            # PRIMARY SOURCES (Highest Authority)
            "FDA": SourceSpec(
                name="FDA.gov",
                url_pattern="fda.gov",
                priority=SourcePriority.PRIMARY,
                specialties=[InformationType.WARNINGS, InformationType.INTERACTIONS, InformationType.VERIFICATION],
                rate_limit=2.0
            ),
            "MedlinePlus": SourceSpec(
                name="MedlinePlus",
                url_pattern="medlineplus.gov",
                priority=SourcePriority.PRIMARY,
                specialties=[InformationType.DOSAGE, InformationType.SIDE_EFFECTS, InformationType.GENERAL],
                rate_limit=1.5
            ),
            "MayoClinic": SourceSpec(
                name="Mayo Clinic",
                url_pattern="mayoclinic.org",
                priority=SourcePriority.PRIMARY,
                specialties=[InformationType.DOSAGE, InformationType.SIDE_EFFECTS, InformationType.VERIFICATION],
                rate_limit=1.5
            ),
            
            # SECONDARY SOURCES (Good Authority)
            "Drugs": SourceSpec(
                name="Drugs.com",
                url_pattern="drugs.com",
                priority=SourcePriority.SECONDARY,
                specialties=[InformationType.DOSAGE, InformationType.SIDE_EFFECTS, InformationType.INTERACTIONS],
                rate_limit=1.0
            ),
            "Medscape": SourceSpec(
                name="Medscape",
                url_pattern="medscape.com",
                priority=SourcePriority.SECONDARY,
                specialties=[InformationType.INTERACTIONS, InformationType.WARNINGS, InformationType.VERIFICATION],
                rate_limit=1.0
            ),
            
            # TERTIARY SOURCES (Supporting Information)
            "WHO": SourceSpec(
                name="WHO",
                url_pattern="who.int",
                priority=SourcePriority.TERTIARY,
                specialties=[InformationType.WARNINGS, InformationType.GENERAL],
                rate_limit=2.0
            ),
            "PubMed": SourceSpec(
                name="PubMed",
                url_pattern="pubmed.ncbi.nlm.nih.gov",
                priority=SourcePriority.TERTIARY,
                specialties=[InformationType.VERIFICATION, InformationType.GENERAL],
                rate_limit=1.0
            )
        }
        
        # Agent specialization mapping
        self.agent_specializations = {
            "DosageAgent": InformationType.DOSAGE,
            "SideEffectsAgent": InformationType.SIDE_EFFECTS,
            "WebSearchAgent": InformationType.INTERACTIONS,
            "ValidatorAgent": InformationType.VERIFICATION
        }

    def _generate_cache_key(self, query: str, source: str, info_type: InformationType) -> str:
        """Generate unique cache key for search queries"""
        key_string = f"{query.lower().strip()}_{source}_{info_type.value}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.cache:
            return False
        
        result = self.cache[cache_key]
        age = time.time() - result.timestamp
        return age < self.cache_ttl

    def _get_optimal_sources(self, info_type: InformationType, limit: int = 3) -> List[str]:
        """Get optimal sources for a specific information type"""
        # Filter sources by specialty and sort by priority
        relevant_sources = [
            (name, spec) for name, spec in self.sources.items()
            if info_type in spec.specialties
        ]
        
        # Sort by priority (PRIMARY first)
        relevant_sources.sort(key=lambda x: x[1].priority.value)
        
        # Filter out temporarily failed sources
        current_time = time.time()
        available_sources = [
            name for name, spec in relevant_sources
            if self.failed_sources.get(name, 0) < current_time - 300  # 5 min cooldown
        ]
        
        return available_sources[:limit]

    def _enforce_rate_limit(self, source: str) -> bool:
        """Enforce rate limiting for source requests"""
        if source not in self.sources:
            return True
            
        rate_limit = self.sources[source].rate_limit
        last_request = self.last_request_time.get(source, 0)
        time_since_last = time.time() - last_request
        
        if time_since_last < rate_limit:
            logger.warning(f"Rate limit hit for {source}. Waiting {rate_limit - time_since_last:.1f}s")
            time.sleep(rate_limit - time_since_last)
        
        self.last_request_time[source] = time.time()
        return True

    def coordinated_search(self, 
                         agent_name: str, 
                         query: str, 
                         search_tool: Any,
                         max_sources: int = 2) -> Dict[str, SearchResult]:
        """
        Perform coordinated search across optimal sources for the agent's specialty.
        
        Args:
            agent_name: Name of the requesting agent
            query: Search query
            search_tool: Agent's search tool
            max_sources: Maximum number of sources to search
            
        Returns:
            Dictionary of search results by source name
        """
        info_type = self.agent_specializations.get(agent_name, InformationType.GENERAL)
        optimal_sources = self._get_optimal_sources(info_type, max_sources)
        
        results = {}
        
        for source in optimal_sources:
            cache_key = self._generate_cache_key(query, source, info_type)
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.info(f"Cache hit for {agent_name}: {query} from {source}")
                results[source] = self.cache[cache_key]
                continue
            
            # Perform new search
            try:
                # Enforce rate limiting
                self._enforce_rate_limit(source)
                
                # Construct source-specific query
                enhanced_query = self._enhance_query_for_source(query, source, info_type)
                
                # Execute search
                logger.info(f"New search for {agent_name}: {enhanced_query} from {source}")
                search_content = search_tool.run(enhanced_query)
                
                # Create and cache result
                result = SearchResult(
                    query=enhanced_query,
                    source=source,
                    content=search_content,
                    timestamp=time.time(),
                    agent_name=agent_name,
                    info_type=info_type,
                    success=True
                )
                
                self.cache[cache_key] = result
                results[source] = result
                
                # Reset failure counter on success
                if source in self.failed_sources:
                    del self.failed_sources[source]
                    
            except Exception as e:
                logger.error(f"Search failed for {agent_name} on {source}: {str(e)}")
                
                # Record failure for temporary blacklisting
                self.failed_sources[source] = time.time()
                
                # Create error result
                error_result = SearchResult(
                    query=query,
                    source=source,
                    content="",
                    timestamp=time.time(),
                    agent_name=agent_name,
                    info_type=info_type,
                    success=False,
                    error_message=str(e)
                )
                results[source] = error_result

        return results

    def _enhance_query_for_source(self, query: str, source: str, info_type: InformationType) -> str:
        """Enhance search query based on source and information type"""
        enhancements = {
            "FDA": f"site:fda.gov {query}",
            "MedlinePlus": f"site:medlineplus.gov {query}",
            "MayoClinic": f"site:mayoclinic.org {query}",
            "Drugs": f"site:drugs.com {query}",
            "Medscape": f"site:medscape.com {query}",
            "WHO": f"site:who.int {query}",
            "PubMed": f"site:pubmed.ncbi.nlm.nih.gov {query}"
        }
        
        # Add information type context
        type_context = {
            InformationType.DOSAGE: "dosage dose administration",
            InformationType.SIDE_EFFECTS: "side effects adverse reactions",
            InformationType.INTERACTIONS: "drug interactions warnings",
            InformationType.WARNINGS: "warnings precautions contraindications",
            InformationType.VERIFICATION: "clinical information facts"
        }
        
        enhanced_query = enhancements.get(source, query)
        if info_type in type_context:
            enhanced_query += f" {type_context[info_type]}"
            
        return enhanced_query

    def get_shared_results(self, query: str, requesting_agent: str) -> Dict[str, List[SearchResult]]:
        """
        Get search results that other agents have already found for similar queries.
        Useful for ValidatorAgent to access previous search results.
        """
        shared_results = {}
        query_lower = query.lower()
        
        for cache_key, result in self.cache.items():
            # Find results from other agents with similar queries
            if (result.agent_name != requesting_agent and 
                query_lower in result.query.lower() and
                result.success):
                
                if result.source not in shared_results:
                    shared_results[result.source] = []
                shared_results[result.source].append(result)
        
        return shared_results

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring"""
        total_results = len(self.cache)
        successful_results = sum(1 for r in self.cache.values() if r.success)
        failed_results = total_results - successful_results
        
        # Count by agent
        agent_stats = {}
        for result in self.cache.values():
            agent = result.agent_name
            if agent not in agent_stats:
                agent_stats[agent] = {"success": 0, "failed": 0}
            
            if result.success:
                agent_stats[agent]["success"] += 1
            else:
                agent_stats[agent]["failed"] += 1
        
        return {
            "total_cached_results": total_results,
            "successful_searches": successful_results,
            "failed_searches": failed_results,
            "cache_hit_rate": f"{(successful_results/total_results*100):.1f}%" if total_results > 0 else "0%",
            "agent_statistics": agent_stats,
            "failed_sources": list(self.failed_sources.keys()),
            "cache_ttl_hours": self.cache_ttl / 3600
        }

    def clear_cache(self):
        """Clear all cached search results"""
        self.cache.clear()
        self.failed_sources.clear()
        logger.info("Search cache cleared")

# Global coordinator instance
search_coordinator = SearchCoordinator()

def get_search_coordinator() -> SearchCoordinator:
    """Get the global search coordinator instance"""
    return search_coordinator
