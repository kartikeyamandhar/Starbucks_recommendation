"""
Evaluation Module
Validate pipeline performance on training data using NDCG metric
"""
import pandas as pd
import numpy as np
from typing import List, Dict
from sklearn.metrics import ndcg_score
from tqdm import tqdm
import json

from data_loader import load_train_queries
from pipeline import query_products


def parse_relevant_products(relevant_products_str: str) -> List[str]:
    """
    Parse product IDs from training data
    Handles both semicolon-separated and list-formatted strings
    
    Args:
        relevant_products_str: String like "BEV_001;BEV_002" or "['BEV_001', 'BEV_002']"
        
    Returns:
        List of product IDs
    """
    if pd.isna(relevant_products_str) or relevant_products_str == "":
        return []
    
    # Check if it's a list format string
    if relevant_products_str.startswith('[') and relevant_products_str.endswith(']'):
        # Parse as Python list
        import ast
        try:
            return ast.literal_eval(relevant_products_str)
        except:
            # Fallback: strip brackets and split by comma
            clean_str = relevant_products_str.strip('[]').replace("'", "").replace('"', '').replace(' ', '')
            return [x.strip() for x in clean_str.split(',') if x.strip()]
    
    # Otherwise assume semicolon-separated
    return [x.strip() for x in relevant_products_str.split(';') if x.strip()]


def compute_ndcg(predicted: List[str], ground_truth: List[str], k: int = None) -> float:
    """
    Compute NDCG (Normalized Discounted Cumulative Gain) score
    
    Args:
        predicted: List of predicted product IDs (ranked)
        ground_truth: List of ground truth product IDs (ranked)
        k: Consider only top k predictions (None = all)
        
    Returns:
        NDCG score between 0 and 1
    """
    if not ground_truth:
        return 0.0
    
    if not predicted:
        return 0.0
    
    # Truncate to top k if specified
    if k:
        predicted = predicted[:k]
    
    # Create relevance scores: 1 if in ground truth, 0 otherwise
    # Higher position in ground truth = higher relevance
    relevance = []
    for pred_id in predicted:
        if pred_id in ground_truth:
            # Higher relevance for products that appear earlier in ground truth
            position = ground_truth.index(pred_id)
            relevance.append(len(ground_truth) - position)
        else:
            relevance.append(0)
    
    # If no relevant items found, NDCG is 0
    if sum(relevance) == 0:
        return 0.0
    
    # Compute ideal DCG (sort ground truth relevances in descending order)
    ideal_relevance = sorted(range(len(ground_truth), 0, -1), reverse=True)
    
    # Pad to same length for sklearn
    max_len = max(len(relevance), len(ideal_relevance))
    relevance_padded = relevance + [0] * (max_len - len(relevance))
    ideal_padded = ideal_relevance + [0] * (max_len - len(ideal_relevance))
    
    # Reshape for sklearn (expects 2D array)
    y_true = np.array([ideal_padded])
    y_score = np.array([relevance_padded])
    
    try:
        score = ndcg_score(y_true, y_score)
        return score
    except:
        return 0.0


def evaluate_query(query_id: str, query_text: str, ground_truth: List[str]) -> Dict:
    """
    Evaluate pipeline on a single query
    
    Args:
        query_id: Query ID
        query_text: Natural language query
        ground_truth: List of relevant product IDs (ranked)
        
    Returns:
        Dictionary with evaluation metrics
    """
    # Get predictions from pipeline
    predicted_products = query_products(query_text)
    predicted_ids = [p['product_id'] for p in predicted_products]
    
    # Compute metrics
    ndcg = compute_ndcg(predicted_ids, ground_truth)
    ndcg_at_5 = compute_ndcg(predicted_ids, ground_truth, k=5)
    ndcg_at_10 = compute_ndcg(predicted_ids, ground_truth, k=10)
    
    # Compute recall (what % of relevant products did we find?)
    if ground_truth:
        found = len(set(predicted_ids) & set(ground_truth))
        recall = found / len(ground_truth)
    else:
        recall = 0.0
    
    return {
        'query_id': query_id,
        'query_text': query_text,
        'num_predicted': len(predicted_ids),
        'num_relevant': len(ground_truth),
        'ndcg': ndcg,
        'ndcg@5': ndcg_at_5,
        'ndcg@10': ndcg_at_10,
        'recall': recall
    }


def evaluate_training_set(sample_size: int = None, save_results: bool = True) -> pd.DataFrame:
    """
    Evaluate pipeline on entire training set
    
    Args:
        sample_size: Number of queries to evaluate (None = all)
        save_results: Save results to CSV
        
    Returns:
        DataFrame with evaluation results
    """
    print("="*70)
    print("TRAINING SET EVALUATION")
    print("="*70)
    
    # Load training queries
    train_df = load_train_queries()
    
    # Sample if requested
    if sample_size:
        train_df = train_df.sample(n=min(sample_size, len(train_df)), random_state=42)
        print(f"Evaluating on {len(train_df)} sampled queries")
    else:
        print(f"Evaluating on all {len(train_df)} training queries")
    
    # Evaluate each query
    results = []
    for idx, row in tqdm(train_df.iterrows(), total=len(train_df), desc="Evaluating queries"):
        ground_truth = parse_relevant_products(row['relevant_products'])
        
        try:
            result = evaluate_query(
                query_id=row['query_id'],
                query_text=row['query_text'],
                ground_truth=ground_truth
            )
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error on query {row['query_id']}: {e}")
            results.append({
                'query_id': row['query_id'],
                'query_text': row['query_text'],
                'num_predicted': 0,
                'num_relevant': len(ground_truth),
                'ndcg': 0.0,
                'ndcg@5': 0.0,
                'ndcg@10': 0.0,
                'recall': 0.0
            })
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Print summary statistics
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"Total queries evaluated: {len(results_df)}")
    print(f"\nAverage Metrics:")
    print(f"  NDCG:      {results_df['ndcg'].mean():.4f}")
    print(f"  NDCG@5:    {results_df['ndcg@5'].mean():.4f}")
    print(f"  NDCG@10:   {results_df['ndcg@10'].mean():.4f}")
    print(f"  Recall:    {results_df['recall'].mean():.4f}")
    
    print(f"\nMedian Metrics:")
    print(f"  NDCG:      {results_df['ndcg'].median():.4f}")
    print(f"  NDCG@5:    {results_df['ndcg@5'].median():.4f}")
    print(f"  NDCG@10:   {results_df['ndcg@10'].median():.4f}")
    print(f"  Recall:    {results_df['recall'].median():.4f}")
    
    # Distribution
    print(f"\nNDCG Distribution:")
    print(f"  Min:  {results_df['ndcg'].min():.4f}")
    print(f"  25%:  {results_df['ndcg'].quantile(0.25):.4f}")
    print(f"  50%:  {results_df['ndcg'].quantile(0.50):.4f}")
    print(f"  75%:  {results_df['ndcg'].quantile(0.75):.4f}")
    print(f"  Max:  {results_df['ndcg'].max():.4f}")
    
    # Best and worst performing queries
    print(f"\n{'Top 5 Best Queries (by NDCG):':-^70}")
    best_queries = results_df.nlargest(5, 'ndcg')[['query_id', 'query_text', 'ndcg']]
    for _, row in best_queries.iterrows():
        print(f"{row['query_id']}: {row['ndcg']:.4f} - {row['query_text'][:50]}...")
    
    print(f"\n{'Top 5 Worst Queries (by NDCG):':-^70}")
    worst_queries = results_df.nsmallest(5, 'ndcg')[['query_id', 'query_text', 'ndcg']]
    for _, row in worst_queries.iterrows():
        print(f"{row['query_id']}: {row['ndcg']:.4f} - {row['query_text'][:50]}...")
    
    # Save results
    if save_results:
        output_file = 'training_evaluation_results.csv'
        results_df.to_csv(output_file, index=False)
        print(f"\n✓ Results saved to {output_file}")
    
    return results_df


def analyze_query(query_id: str):
    """
    Deep dive analysis of a specific query
    
    Args:
        query_id: Query ID to analyze
    """
    # Load training data
    train_df = load_train_queries()
    query_row = train_df[train_df['query_id'] == query_id].iloc[0]
    
    print("="*70)
    print(f"QUERY ANALYSIS: {query_id}")
    print("="*70)
    print(f"Query: {query_row['query_text']}")
    print()
    
    # Get predictions
    predicted_products = query_products(query_row['query_text'])
    predicted_ids = [p['product_id'] for p in predicted_products]
    
    # Get ground truth
    ground_truth = parse_relevant_products(query_row['relevant_products'])
    
    # Compute metrics
    result = evaluate_query(query_id, query_row['query_text'], ground_truth)
    
    print(f"\nMetrics:")
    print(f"  NDCG: {result['ndcg']:.4f}")
    print(f"  NDCG@5: {result['ndcg@5']:.4f}")
    print(f"  Recall: {result['recall']:.4f}")
    
    print(f"\n{'Ground Truth (Correct Order):':-^70}")
    for i, prod_id in enumerate(ground_truth[:10], 1):
        print(f"{i}. {prod_id}")
    
    print(f"\n{'Predicted (Our Ranking):':-^70}")
    for i, product in enumerate(predicted_products[:10], 1):
        in_gt = "✓" if product['product_id'] in ground_truth else "✗"
        print(f"{i}. {in_gt} {product['name']} ({product['product_id']}) - Score: {product['score']:.4f}")
    
    # Show overlap
    correct = set(predicted_ids) & set(ground_truth)
    missing = set(ground_truth) - set(predicted_ids)
    extra = set(predicted_ids[:len(ground_truth)]) - set(ground_truth)
    
    print(f"\n{'Analysis:':-^70}")
    print(f"Found {len(correct)}/{len(ground_truth)} relevant products")
    if missing:
        print(f"Missing products: {', '.join(list(missing)[:5])}")
    if extra:
        print(f"Extra products in top-{len(ground_truth)}: {', '.join(list(extra)[:5])}")


# Test function
if __name__ == "__main__":
    # Quick test on 5 queries
    print("Testing evaluation on 5 sample queries...\n")
    results = evaluate_training_set(sample_size=5, save_results=False)
    
    # Analyze the best and worst query
    if len(results) > 0:
        print("\n" + "="*70)
        print("Analyzing best performing query...")
        best_query_id = results.nlargest(1, 'ndcg').iloc[0]['query_id']
        analyze_query(best_query_id)