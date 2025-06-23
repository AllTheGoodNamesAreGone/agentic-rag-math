# fix_setup.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from src.knowledge_base.setup import math_kb

# Delete existing collection and recreate
try:
    math_kb.client.delete_collection("math_knowledge_hybrid")
    print("✅ Deleted existing collection")
except:
    print("ℹ️ No existing collection to delete")

# Setup again with fixes
num_problems = math_kb.setup_knowledge_base()
print(f"✅ Setup complete with {num_problems} problems")