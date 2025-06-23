import streamlit as st
import time
import sys
from pathlib import Path
import plotly.express as px
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Fix imports - use factory functions
from src.config.settings import settings

# Page configuration
st.set_page_config(
    page_title="Math Professor AI",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS (same as before)
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow' not in st.session_state:
    # Create workflow and agent using factory functions
    from src.agents.math_agent import get_workflow
    st.session_state.workflow, st.session_state.math_agent = get_workflow()

if 'question_count' not in st.session_state:
    st.session_state.question_count = 0
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧮 Math Professor AI</h1>
    <p>Intelligent Mathematics Tutor powered by LangGraph & Hybrid RAG</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🔧 System Status")
    
    # API Key status
    if settings.OPENAI_API_KEY:
        st.success("✅ OpenAI API Connected")
    else:
        st.error("❌ OpenAI API Key Missing")
    
    # Usage statistics
    st.header("📊 Usage Statistics")
    st.metric("Questions Asked", st.session_state.question_count)
    st.metric("Total Tokens", st.session_state.math_agent.total_tokens)
    st.metric("Estimated Cost", f"${st.session_state.math_agent.total_cost:.4f}")
    
    # Sample questions
    st.header("💡 Sample Questions")
    sample_questions = [
        "Solve x² + 5x + 6 = 0",
        "Find derivative of x³ + 2x²",
        "Integrate x·ln(x) dx",
        "Explain quadratic formula",
        "What is a limit in calculus?"
    ]
    
    for question in sample_questions:
        if st.button(question, key=f"sample_{question[:20]}"):
            st.session_state.sample_question = question

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.header("Ask Your Math Question")
    
    # Handle sample questions
    default_question = ""
    if hasattr(st.session_state, 'sample_question'):
        default_question = st.session_state.sample_question
        delattr(st.session_state, 'sample_question')
    
    question = st.text_area(
        "Enter your mathematics question:",
        height=100,
        placeholder="e.g., How do I solve quadratic equations?",
        value=default_question
    )
    
    # Main action button
    if st.button("Get Solution", type="primary", use_container_width=True):
        if question:
            with st.spinner("🤔 Analyzing your question..."):
                start_time = time.time()
                
                try:
                    # Invoke the workflow
                    result = st.session_state.workflow.invoke({
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
                    
                    processing_time = time.time() - start_time
                    st.session_state.question_count += 1
                    
                    # Store result for feedback
                    st.session_state.last_result = result
                    st.session_state.last_question = question
                    
                    # Check if guardrails passed
                    if not result.get("guardrail_passed", True):
                        st.error(f"⚠️ {result.get('error_message', 'Question not appropriate')}")
                    else:
                        # Display solution
                        st.markdown("### 📝 Solution")
                        st.markdown(result["solution"])
                        
                        # Display metadata
                        col_a, col_b, col_c, col_d = st.columns(4)
                        
                        with col_a:
                            st.metric("Source", result.get("route_decision", "unknown").title())
                        
                        with col_b:
                            confidence = result.get("confidence_score", 0)
                            st.metric("Confidence", f"{confidence:.1%}")
                        
                        with col_c:
                            st.metric("Time", f"{processing_time:.1f}s")
                        
                        with col_d:
                            cost = result.get("cost_estimate", 0)
                            st.metric("Cost", f"${cost:.4f}")
                        
                        # Show warnings if needed
                        if result.get("needs_human_feedback"):
                            st.warning("⚠️ This solution may benefit from human review due to low confidence.")
                        
                        if confidence >= 0.8:
                            st.success("✅ High confidence solution!")
                        elif confidence >= 0.6:
                            st.info("ℹ️ Moderate confidence solution.")
                        else:
                            st.warning("⚠️ Low confidence solution - please verify.")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Please try rephrasing your question or check your internet connection.")
        else:
            st.warning("Please enter a question first!")

# ... (rest of the app.py code remains the same)

with col2:
    st.header("🎯 Quick Actions")
    
    # Topic filters
    st.subheader("📚 Topics")
    topics = ["Algebra", "Calculus", "Geometry", "Statistics", "Trigonometry"]
    selected_topic = st.selectbox("Filter by topic:", ["All"] + topics)
    
    # Difficulty levels
    st.subheader("📈 Difficulty")
    difficulty = st.selectbox("Choose level:", ["All", "Basic", "Intermediate", "Advanced"])
    
    # System actions
    st.subheader("⚙️ System")
    if st.button("Clear History"):
        st.session_state.question_count = 0
        st.session_state.feedback_data = []
        math_agent.total_tokens = 0
        math_agent.total_cost = 0.0
        st.success("History cleared!")

# Feedback section
if 'last_result' in st.session_state:
    st.markdown("---")
    st.header("💭 Feedback")
    
    feedback_col1, feedback_col2 = st.columns(2)
    
    with feedback_col1:
        rating = st.slider("Rate this solution (1-5):", 1, 5, 3, key="rating_slider")
        
    with feedback_col2:
        feedback_text = st.text_input("Additional comments:", key="feedback_text")
    
    feedback_button_col1, feedback_button_col2 = st.columns(2)
    
    with feedback_button_col1:
        if st.button("👍 Submit Positive Feedback", use_container_width=True):
            feedback_entry = {
                "question": st.session_state.last_question,
                "solution": st.session_state.last_result["solution"],
                "rating": rating,
                "comments": feedback_text,
                "timestamp": time.time()
            }
            st.session_state.feedback_data.append(feedback_entry)
            st.success("Thank you for your feedback! 🙏")
            del st.session_state.last_result
    
    with feedback_button_col2:
        if st.button("👎 Report Issue", use_container_width=True):
            feedback_entry = {
                "question": st.session_state.last_question,
                "solution": st.session_state.last_result["solution"],
                "rating": 1,
                "comments": f"Issue reported: {feedback_text}",
                "timestamp": time.time()
            }
            st.session_state.feedback_data.append(feedback_entry)
            st.warning("Issue reported. We'll work on improving this!")
            del st.session_state.last_result

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p>🧮 Math Professor AI - Powered by LangGraph, OpenAI, and Qdrant</p>
    <p>Built for educational purposes • Cost-optimized for minimal API usage</p>
</div>
""", unsafe_allow_html=True)