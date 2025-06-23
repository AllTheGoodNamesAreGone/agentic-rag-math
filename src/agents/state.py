from typing import TypedDict, List, Optional, Any

class MathAgentState(TypedDict):
    # Input
    question: str
    
    # Routing
    route_decision: str  # "knowledge_base", "web_search", "both"
    
    # Search results
    knowledge_base_results: str
    web_search_results: str
    context: str
    
    # Generation
    solution: str
    confidence_score: float
    needs_human_feedback: bool
    
    # Safety & validation
    guardrail_passed: bool
    error_message: Optional[str]
    
    # Metadata
    processing_time: float
    tokens_used: int
    cost_estimate: float