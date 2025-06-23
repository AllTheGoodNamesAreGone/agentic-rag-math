#!/usr/bin/env python3
"""
Test script for the Math Agent
"""

import sys
from pathlib import Path
import time

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_math_agent():
    """Comprehensive testing of the math agent"""
    
    # Import using factory function
    from src.agents.math_agent import get_workflow
    
    try:
        workflow, math_agent = get_workflow()
        print("✅ Workflow created successfully")
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        return
    
    test_cases = [
        {
            "question": "Solve the quadratic equation: 2x² + 7x - 4 = 0",
            "expected_route": "knowledge_base",
            "category": "Algebra"
        },
        {
            "question": "Find the derivative of f(x) = x³ - 2x² + 5x - 1",
            "expected_route": "knowledge_base", 
            "category": "Calculus"
        },
        {
            "question": "What are the latest developments in mathematical AI research?",
            "expected_route": "web_search",
            "category": "Current Research"
        },
        {
            "question": "How do I integrate x·ln(x) dx using integration by parts?",
            "expected_route": "knowledge_base",
            "category": "Advanced Calculus"
        },
        {
            "question": "Explain the fundamental theorem of calculus",
            "expected_route": "knowledge_base",
            "category": "Theory"
        }
    ]
    
    print("🧪 Testing Math Agent")
    print("=" * 50)
    
    results = []
    total_cost = 0.0
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['category']}")
        print(f"Question: {test_case['question']}")
        print("-" * 30)
        
        start_time = time.time()
        
        try:
            result = workflow.invoke({
                "question": test_case["question"],
                "route_decision": "",
                "knowledge_base_results": "",
                "web_search_results": "",
                "context": "",
                "solution": "",
                "confidence_score": 0.0,
                "needs_human_feedback": False,
                "guardrail_passed": True,
                "error_message": None,
                "processing_time": 0.0,
                "tokens_used": 0,
                "cost_estimate": 0.0
            })
            
            processing_time = time.time() - start_time
            
            # Analyze results
            route_match = result["route_decision"] == test_case["expected_route"]
            confidence = result.get("confidence_score", 0)
            
            results.append({
                "test": test_case["category"],
                "route_correct": route_match,
                "confidence": confidence,
                "processing_time": processing_time,
                "tokens": result.get("tokens_used", 0),
                "cost": result.get("cost_estimate", 0)
            })
            
            # Display results
            print(f"✅ Route: {result['route_decision']} {'✓' if route_match else '✗'}")
            print(f"✅ Confidence: {confidence:.2f}")
            print(f"✅ Processing time: {processing_time:.2f}s")
            print(f"✅ Solution preview: {result['solution'][:150]}...")
            
            if result.get("needs_human_feedback"):
                print("⚠️  Needs human feedback")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            results.append({
                "test": test_case["category"],
                "route_correct": False,
                "confidence": 0,
                "processing_time": 0,
                "tokens": 0,
                "cost": 0
            })
    
    # Summary
    print(f"\n📊 Test Summary")
    print("=" * 50)
    
    total_tests = len(results)
    successful_routes = sum(1 for r in results if r["route_correct"])
    avg_confidence = sum(r["confidence"] for r in results) / total_tests
    total_time = sum(r["processing_time"] for r in results)
    total_tokens = sum(r["tokens"] for r in results)
    final_cost = math_agent.total_cost
    
    print(f"Total tests: {total_tests}")
    print(f"Correct routing: {successful_routes}/{total_tests} ({successful_routes/total_tests*100:.1f}%)")
    print(f"Average confidence: {avg_confidence:.2f}")
    print(f"Total processing time: {total_time:.2f}s")
    print(f"Total tokens used: {total_tokens}")
    print(f"Total cost: ${final_cost:.4f}")
    
    return results

if __name__ == "__main__":
    test_math_agent()