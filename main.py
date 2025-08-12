import joblib
from sentence_transformers import SentenceTransformer, util
import numpy as np
import sys

# Load model metadata
with open('model_metadata.txt') as f:
    model_name = f.read().strip().split('=')[1]

# Load classifier and transformer
clf = joblib.load('bangla_plagiarism_model.pkl')
model = SentenceTransformer(model_name)

# 🔍 Sample input
original_text = sys.stdin.buffer.readline().decode("utf-8").strip()
plagiarized_text = sys.stdin.buffer.readline().decode("utf-8").strip()

# Generate embeddings
original_emb = model.encode([original_text], convert_to_tensor=True)
plagiarized_emb = model.encode([plagiarized_text], convert_to_tensor=True)

# Compute cosine similarity
cosine_sim = util.cos_sim(original_emb, plagiarized_emb).item()
X_new = np.array([[cosine_sim]])

# Predict using trained classifier
prediction = clf.predict(X_new)

# Output result
print(f"Cosine Similarity: {cosine_sim:.4f}")
print("Prediction:", "Plagiarized" if prediction[0] == 1 else "Original")
