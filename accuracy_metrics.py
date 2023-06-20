
import json, ast
from rouge import Rouge
from sentence_transformers import SentenceTransformer, util

# Configure metrics libraries
rouge = Rouge()
model = SentenceTransformer('all-MiniLM-L6-v2')

def rouge_metric(dialogue):
    return rouge.get_scores(dialogue["completion"], dialogue["chatgpt_completion"], avg=True)

def sbert_metric(dialogue_1, dialogue_2):
    embeddings1 = model.encode(dialogue_1, show_progress_bar=False, convert_to_numpy=True)
    embeddings2 = model.encode(dialogue_2, show_progress_bar=False, convert_to_numpy=True)
    return util.cos_sim(embeddings1, embeddings2).item()

def get_accuracy(dialogue):
    
    return

