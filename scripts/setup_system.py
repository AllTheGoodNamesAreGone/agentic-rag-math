#!/usr/bin/env python3
"""
Complete system setup script for Math Agentic RAG
"""

import os
import sys
import time
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from src.config.settings import settings
from src.knowledge_base.setup import math_kb

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking system requirements...")
    
    # Check API keys
    try:
        settings.validate_required_keys()
        print("✅ API keys validated")
    except ValueError as e:
        print(f"❌ {e}")
        print("Please set your OPENAI_API_KEY in the .env file")
        return False
    
    # Check if Qdrant is running
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(settings.QDRANT_URL)
        client.get_collections()
        print("✅ Qdrant database connection successful")
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        print("Please start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        return False
    
    return True

def setup_knowledge_base():
    """Setup the hybrid knowledge base"""
    print("\n📚 Setting up knowledge base...")
    
    try:
        num_problems = math_kb.setup_knowledge_base()
        print(f"✅ Knowledge base ready with {num_problems} problems")
        return True
    except Exception as e:
        print(f"❌ Knowledge base setup failed: {e}")
        return False

def test_system():
    """Test the complete system"""
    print("\n🧪 Testing system components...")
    
    # Import workflow creation function
    from src.agents.math_agent import get_workflow
    
    try:
        workflow, math_agent = get_workflow()
        print("✅ Workflow created successfully")
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        return False
    
    test_questions = [
        "How do I solve x² + 5x + 6 = 0?",
        "Find the derivative of x³ + 2x²",
        "What is integration by parts?"
    ]
    
    for i, question in enumerate(test_questions):
        print(f"\nTest {i+1}: {question}")
        
        try:
            result = workflow.invoke({
                "question": question,
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
            
            print(f"✅ Route: {result.get('route_decision', 'unknown')}")
            print(f"✅ Confidence: {result.get('confidence_score', 0):.2f}")
            print(f"✅ Solution preview: {result.get('solution', '')[:100]}...")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            return False
    
    print(f"\n💰 Estimated cost so far: ${math_agent.total_cost:.4f}")
    return True

def main():
    """Main setup function"""
    print("🚀 Math Agentic RAG System Setup")
    print("=" * 40)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Setup failed. Please fix the issues above and try again.")
        return False
    
    # Setup knowledge base
    if not setup_knowledge_base():
        print("\n❌ Knowledge base setup failed.")
        return False
    
    # Test system
    if not test_system():
        print("\n❌ System testing failed.")
        return False
    
    print("\n🎉 System setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the Streamlit app: streamlit run app.py")
    print("2. Test with various math questions")
    print("3. Check cost tracking in the sidebar")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)