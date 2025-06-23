from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from datasets import load_dataset
import uuid
import json
from typing import List, Dict, Optional
from src.config.settings import settings
from src.knowledge_base.curated_problems import ALL_CURATED_PROBLEMS

class MathKnowledgeBase:
    def __init__(self):
        self.client = QdrantClient(settings.QDRANT_URL)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "math_knowledge_hybrid"
        
    def setup_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        try:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
            print("✅ Created new Qdrant collection")
        except Exception as e:
            print(f"Collection may already exist: {e}")
    
    def load_public_datasets(self) -> List[Dict]:
        """Load free public math datasets"""
        all_problems = []
        
        # Try to load GSM8K dataset
        try:
            print("📚 Loading GSM8K dataset...")
            if settings.HUGGINGFACE_TOKEN:
                from huggingface_hub import login
                login(token=settings.HUGGINGFACE_TOKEN)
            
            gsm8k = load_dataset("gsm8k", "main", split="train")
            
            # Take first 1000 problems for speed
            for i, item in enumerate(gsm8k.select(range(min(1000, len(gsm8k))))):
                all_problems.append({
                    "problem": item['question'],
                    "solution": self.format_gsm8k_solution(item['answer']),
                    "topic": "word_problems",
                    "difficulty": "basic",
                    "source": "gsm8k",
                    "problem_id": f"gsm8k_{i}"
                })
            
            print(f"✅ Loaded {len(all_problems)} GSM8K problems")
            
        except Exception as e:
            print(f"❌ Failed to load GSM8K: {e}")
            print("📝 Will use curated problems only")
        
        # Try to load MATH competition dataset with correct name
        try:
            print("📚 Loading MATH competition dataset...")
            # Try different possible dataset names
            dataset_names = ["hendrycks/competition_math", "competition_math", "hendrycks_math"]
            
            math_dataset = None
            for name in dataset_names:
                try:
                    math_dataset = load_dataset(name, split="train")
                    print(f"✅ Found dataset: {name}")
                    break
                except:
                    continue
            
            if math_dataset is None:
                raise Exception("Could not find MATH competition dataset with any known name")
            
            # Take 300 problems for variety
            for i, item in enumerate(math_dataset.select(range(min(300, len(math_dataset))))):
                all_problems.append({
                    "problem": item['problem'],
                    "solution": item['solution'],
                    "topic": item['type'].lower().replace(" ", "_"),
                    "difficulty": self.map_competition_difficulty(item['level']),
                    "source": "competition_math",
                    "problem_id": f"math_{i}"
                })
            
            print(f"✅ Loaded 300 MATH competition problems")
            
        except Exception as e:
            print(f"❌ Failed to load MATH dataset: {e}")
            print("📝 Continuing with GSM8K and curated problems only")
        
        return all_problems
    
    def format_gsm8k_solution(self, answer: str) -> str:
        """Format GSM8K solutions to be more step-by-step"""
        # GSM8K answers are often in paragraph form, let's structure them
        sentences = answer.split('. ')
        formatted_steps = []
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                # Clean up the sentence
                clean_sentence = sentence.strip().rstrip('.')
                if clean_sentence:
                    formatted_steps.append(f"Step {i+1}: {clean_sentence}")
        
        return "\n".join(formatted_steps)
    
    def map_competition_difficulty(self, level: str) -> str:
        """Map MATH competition levels to our difficulty scale"""
        mapping = {
            "Level 1": "basic",
            "Level 2": "basic",
            "Level 3": "intermediate", 
            "Level 4": "intermediate",
            "Level 5": "advanced"
        }
        return mapping.get(level, "intermediate")
    
    def setup_knowledge_base(self) -> int:
        """Setup complete knowledge base with all data sources"""
        print("🚀 Setting up hybrid math knowledge base...")
        
        # Setup collection
        self.setup_collection()
        
        # Load all data sources
        public_problems = self.load_public_datasets()
        curated_problems = ALL_CURATED_PROBLEMS
        
        # Combine all problems
        all_problems = curated_problems + public_problems
        
        # Remove duplicates
        unique_problems = self.remove_duplicates(all_problems)
        
        print(f"📊 Processing {len(unique_problems)} unique problems...")
        
        # Batch insert
        self.batch_insert_problems(unique_problems)
        
        print(f"✅ Knowledge base setup complete with {len(unique_problems)} problems")
        return len(unique_problems)
    
    def remove_duplicates(self, problems: List[Dict]) -> List[Dict]:
        """Remove duplicate problems based on text similarity"""
        seen_problems = set()
        unique_problems = []
        
        for problem in problems:
            # Create a hash based on first 100 chars of problem
            problem_hash = problem['problem'].strip().lower()[:100]
            
            if problem_hash not in seen_problems:
                seen_problems.add(problem_hash)
                unique_problems.append(problem)
        
        return unique_problems
    
    def batch_insert_problems(self, problems: List[Dict]):
        """Insert problems in batches for efficiency"""
        batch_size = 100
        points = []
        
        for i, problem in enumerate(problems):
            # Create rich search text
            search_text = f"""
            Problem: {problem['problem']}
            Solution: {problem['solution']}
            Topic: {problem['topic']}
            Difficulty: {problem['difficulty']}
            Source: {problem['source']}
            """
            
            # Generate embedding
            vector = self.model.encode(search_text.strip()).tolist()
            
            # Use integer ID instead of string (Qdrant requirement)
            points.append(PointStruct(
                id=i,  # Use integer ID instead of string
                vector=vector,
                payload={
                    **problem,
                    "original_id": problem.get('problem_id', f"problem_{i}")  # Store original ID in payload
                }
            ))
            
            # Insert batch when full
            if len(points) >= batch_size:
                self.client.upsert(collection_name=self.collection_name, points=points)
                points = []
                print(f"📝 Uploaded batch ending at problem {i+1}")
        
        # Insert remaining points
        if points:
            self.client.upsert(collection_name=self.collection_name, points=points)
            print(f"📝 Uploaded final batch of {len(points)} problems")
    
    def search(self, query: str, limit: int = 5, topic_filter: Optional[str] = None) -> List[Dict]:
        """Search knowledge base with optional topic filtering"""
        try:
            query_vector = self.model.encode(query).tolist()
            
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_vector,
                "limit": limit
            }
            
            # Add topic filter if specified
            if topic_filter:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                search_params["query_filter"] = Filter(
                    must=[FieldCondition(key="topic", match=MatchValue(value=topic_filter))]
                )
            
            results = self.client.search(**search_params)
            
            return [
                {
                    "problem": hit.payload["problem"],
                    "solution": hit.payload["solution"],
                    "topic": hit.payload["topic"],
                    "difficulty": hit.payload["difficulty"],
                    "source": hit.payload["source"],
                    "score": hit.score
                }
                for hit in results
            ]
            
        except Exception as e:
            print(f"Search failed: {e}")
            return []

# Global instance
math_kb = MathKnowledgeBase()