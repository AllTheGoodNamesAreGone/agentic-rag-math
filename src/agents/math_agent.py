from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import Dict, Any
import time
import re
from src.config.settings import settings
from src.agents.state import MathAgentState
from src.tools.search_tools import web_search_tool
from src.knowledge_base.setup import math_kb

class CostOptimizedMathAgent:
    def __init__(self):
        # Initialize LLMs with cost optimization
        self.llm_router = ChatOpenAI(
            model=settings.ROUTER_MODEL,
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )
        
        self.llm_generator = ChatOpenAI(
            model=settings.GENERATOR_MODEL,
            temperature=0.1,
            api_key=settings.OPENAI_API_KEY
        )
        
        # Usage tracking
        self.total_tokens = 0
        self.total_cost = 0.0
    
    def track_usage(self, tokens: int, model: str):
        """Track API usage and costs"""
        self.total_tokens += tokens
        
        # Rough cost estimates (as of 2024)
        cost_per_token = {
            "gpt-3.5-turbo": 0.0000015,  # $1.50 per 1M tokens
            "gpt-4o-mini": 0.00000015,   # $0.15 per 1M tokens
        }
        
        self.total_cost += tokens * cost_per_token.get(model, 0.000001)
    
    def free_input_guardrails(self, state: MathAgentState) -> Dict[str, Any]:
        """Free basic input validation"""
        question = state["question"]
        
        # Basic checks
        if not question or len(question.strip()) < 3:
            return {
                "guardrail_passed": False,
                "error_message": "Question is too short. Please provide a clear math question."
            }
        
        if len(question) > 1000:
            return {
                "guardrail_passed": False,
                "error_message": "Question is too long. Please keep it under 1000 characters."
            }
        
        # Simple content filtering
        inappropriate_terms = ["hack", "illegal", "harmful", "dangerous", "cheat"]
        if any(term in question.lower() for term in inappropriate_terms):
            return {
                "guardrail_passed": False,
                "error_message": "Please ask educational mathematics questions only."
            }
        
        # Check for math indicators
        math_indicators = [
            "solve", "calculate", "find", "derive", "integrate", "differentiate",
            "equation", "function", "graph", "theorem", "proof", "formula",
            "x", "y", "=", "+", "-", "*", "/", "²", "³", "√"
        ]
        
        if not any(indicator in question.lower() for indicator in math_indicators):
            return {
                "guardrail_passed": False,
                "error_message": "This doesn't appear to be a mathematics question. Please ask about mathematical concepts, problems, or calculations."
            }
        
        return {"guardrail_passed": True}
    
    def smart_route_question(self, state: MathAgentState) -> Dict[str, Any]:
        """Smart routing using cost-effective model"""
        question = state["question"]
        
        routing_prompt = f"""Analyze this mathematics question and decide the best information source.

Question: "{question}"

Choose ONE option:
- "knowledge_base": Standard math problems, textbook concepts, homework-style questions, established mathematical procedures
- "web_search": Recent developments, current research, latest mathematical discoveries, very specific modern applications
- "both": Complex questions that might benefit from both historical knowledge and current information

Guidelines:
- Most student math questions should use "knowledge_base"
- Only use "web_search" for explicitly current/recent topics
- Use "both" sparingly for complex research-level questions

Respond with exactly one word: knowledge_base, web_search, or both"""
        
        try:
            start_time = time.time()
            response = self.llm_router.invoke(routing_prompt)
            processing_time = time.time() - start_time
            
            # Track usage
            estimated_tokens = len(routing_prompt.split()) + 10
            self.track_usage(estimated_tokens, settings.ROUTER_MODEL)
            
            route = response.content.strip().lower()
            
            # Validate response
            valid_routes = ["knowledge_base", "web_search", "both"]
            if route not in valid_routes:
                route = "knowledge_base"  # Safe fallback
            
            return {
                "route_decision": route,
                "processing_time": processing_time
            }
            
        except Exception as e:
            print(f"Routing failed: {e}")
            return {
                "route_decision": "knowledge_base",
                "processing_time": 0.0
            }
    
    def search_knowledge_base_node(self, state: MathAgentState) -> Dict[str, Any]:
        """Search internal knowledge base"""
        try:
            results = math_kb.search(state["question"], limit=3)
            
            if not results:
                return {"knowledge_base_results": "No relevant problems found in knowledge base."}
            
            formatted_results = []
            for i, result in enumerate(results):
                formatted_results.append(
                    f"Example {i+1}:\n"
                    f"Problem: {result['problem']}\n"
                    f"Solution: {result['solution'][:600]}{'...' if len(result['solution']) > 600 else ''}\n"
                    f"Topic: {result['topic']} | Difficulty: {result['difficulty']}\n"
                    f"Relevance Score: {result['score']:.2f}\n"
                    f"---"
                )
            
            return {"knowledge_base_results": "\n".join(formatted_results)}
            
        except Exception as e:
            return {"knowledge_base_results": f"Knowledge base search failed: {str(e)}"}
    
    def search_web_node(self, state: MathAgentState) -> Dict[str, Any]:
        """Search web using free DuckDuckGo"""
        try:
            results = web_search_tool.search_mathematics(state["question"])
            return {"web_search_results": results}
        except Exception as e:
            return {"web_search_results": f"Web search failed: {str(e)}"}
    
    def combine_context(self, state: MathAgentState) -> Dict[str, Any]:
        """Combine information from different sources"""
        context_parts = []
        
        # Add knowledge base results
        if state.get("knowledge_base_results") and "No relevant" not in state["knowledge_base_results"]:
            context_parts.append("=== SIMILAR PROBLEMS FROM KNOWLEDGE BASE ===")
            context_parts.append(str(state["knowledge_base_results"]))
        
        # Add web search results  
        if state.get("web_search_results") and "failed" not in state["web_search_results"].lower():
            context_parts.append("=== CURRENT INFORMATION FROM WEB ===")
            context_parts.append(str(state["web_search_results"]))
        
        context = "\n\n".join(context_parts) if context_parts else "Limited context available. Will use mathematical knowledge to solve."
        
        # Truncate context to control costs
        if len(context) > settings.MAX_CONTEXT_LENGTH:
            context = context[:settings.MAX_CONTEXT_LENGTH] + "\n...[context truncated for efficiency]"
        
        return {"context": context}
    
    def generate_solution(self, state: MathAgentState) -> Dict[str, Any]:
        """Generate solution using premium model"""
        
        solution_prompt = f"""You are an expert mathematics tutor. Provide a clear, step-by-step solution for this question.

    Question: {state["question"]}

    Context (use this to inform your solution):
    {state["context"]}

    Requirements:
    1. Provide clear, numbered steps
    2. Explain the reasoning for each step
    3. Show all mathematical work
    4. End with a clearly marked final answer
    5. Make it educational and suitable for students
    6. If the context doesn't fully address the question, use your mathematical knowledge

    Format your response as:
    **Step-by-Step Solution:**
    Step 1: [explanation with work]
    Step 2: [explanation with work]
    ...
    **Final Answer:** [clear final result]"""
        
        try:
            start_time = time.time()
            response = self.llm_generator.invoke(solution_prompt)
            processing_time = time.time() - start_time
            
            # Track usage
            estimated_tokens = len(solution_prompt.split()) + len(response.content.split())
            self.track_usage(estimated_tokens, settings.GENERATOR_MODEL)
            
            # Calculate confidence
            confidence = self.calculate_confidence(state["context"], response.content)
            
            return {
                "solution": response.content,
                "confidence_score": confidence,
                "needs_human_feedback": confidence < 0.7,
                "processing_time": processing_time,
                "tokens_used": estimated_tokens,
                "cost_estimate": self.total_cost
            }
            
        except Exception as e:
            return {
                "solution": f"I apologize, but I encountered an error generating the solution: {str(e)}",
                "confidence_score": 0.0,
                "needs_human_feedback": True,
                "processing_time": 0.0,
                "tokens_used": 0,
                "cost_estimate": self.total_cost
            }
    
    def calculate_confidence(self, context: str, solution: str) -> float:
        """Calculate confidence score based on context and solution quality"""
        confidence = 0.5  # Base confidence
        
        # Boost for good context
        if context and len(context) > 100 and "Limited context" not in context:
            confidence += 0.2
        
        # Boost for structured solution
        if "Step" in solution and solution.count("Step") >= 2:
            confidence += 0.2
        
        # Boost for final answer
        if any(phrase in solution for phrase in ["Final Answer", "Answer:", "Solution:"]):
            confidence += 0.1
        
        # Boost for mathematical notation
        math_indicators = ["=", "+", "-", "×", "÷", "∫", "∑", "√", "²", "³"]
        if any(indicator in solution for indicator in math_indicators):
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def free_output_guardrails(self, state: MathAgentState) -> Dict[str, Any]:
        """Basic output quality validation"""
        solution = state["solution"]
        
        # Check minimum length
        if len(solution) < 50:
            return {
                "solution": "I need to provide a more detailed solution. Could you please rephrase your question or provide more context?",
                "confidence_score": 0.2
            }
        
        # Check for error messages
        if any(phrase in solution.lower() for phrase in ["error", "apologize", "unable to", "cannot"]):
            return {
                "solution": solution,
                "confidence_score": 0.1
            }
        
        # Ensure educational format
        if "step" not in solution.lower() and len(solution) > 100:
            solution = f"**Mathematical Solution:**\n\n{solution}\n\n**Note:** This solution provides the mathematical reasoning for the given problem."
        
        return {"solution": solution}
    
    def create_workflow(self) -> StateGraph:
        """Create optimized LangGraph workflow"""
        workflow = StateGraph(MathAgentState)
        
        # Add all nodes
        workflow.add_node("input_guardrails", self.free_input_guardrails)
        workflow.add_node("route_question", self.smart_route_question)
        workflow.add_node("search_kb", self.search_knowledge_base_node)
        workflow.add_node("search_web", self.search_web_node)
        workflow.add_node("combine_context", self.combine_context)
        workflow.add_node("generate_solution", self.generate_solution)
        workflow.add_node("output_guardrails", self.free_output_guardrails)
        
        # Set entry point
        workflow.set_entry_point("input_guardrails")
        
        # Define conditional flows
        workflow.add_conditional_edges(
            "input_guardrails",
            lambda state: "proceed" if state.get("guardrail_passed", False) else "blocked",
            {
                "proceed": "route_question",
                "blocked": END
            }
        )
        
        workflow.add_conditional_edges(
            "route_question", 
            lambda state: state["route_decision"],
            {
                "knowledge_base": "search_kb",
                "web_search": "search_web",
                "both": "search_kb"  # Start with KB, then web
            }
        )
        
        workflow.add_edge("search_kb", "combine_context")
        workflow.add_edge("search_web", "combine_context")
        
        # Handle "both" route
        workflow.add_conditional_edges(
            "combine_context",
            lambda state: "search_web" if (
                state["route_decision"] == "both" and 
                not state.get("web_search_results")
            ) else "generate",
            {
                "search_web": "search_web",
                "generate": "generate_solution"
            }
        )
        
        workflow.add_edge("generate_solution", "output_guardrails")
        workflow.add_edge("output_guardrails", END)
        
        return workflow.compile()
    
def get_math_agent():
    """Factory function to create math agent"""
    return CostOptimizedMathAgent()

def get_workflow():
    """Factory function to create workflow"""
    agent = get_math_agent()
    return agent.create_workflow(), agent