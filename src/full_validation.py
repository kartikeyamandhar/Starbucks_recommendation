"""
Comprehensive Validation Script
Run full evaluation on all 100 training queries with detailed analysis
"""
from evaluation import evaluate_training_set, evaluate_query, parse_relevant_products
from pipeline import query_products
from data_loader import load_train_queries
import pandas as pd
import json
from collections import Counter

def analyze_constraint_satisfaction(query_text, products, constraints):
    """
    Check how many products actually satisfy the extracted constraints
    """
    satisfied_count = 0
    violations = []
    
    for product in products[:5]:  # Check top 5
        violated = []
        
        # Check price constraint
        if constraints.get('max_price') and product.get('price'):
            if product['price'] > constraints['max_price']:
                violated.append(f"price ${product['price']} > ${constraints['max_price']}")
        
        # Check calories constraint
        if constraints.get('max_calories') and product.get('calories'):
            if product['calories'] > constraints['max_calories']:
                violated.append(f"calories {product['calories']} > {constraints['max_calories']}")
        
        # Check sugar constraint
        if constraints.get('max_sugar') and product.get('sugar_g'):
            if product['sugar_g'] > constraints['max_sugar']:
                violated.append(f"sugar {product['sugar_g']}g > {constraints['max_sugar']}g")
        
        # Check dairy constraint
        if constraints.get('dairy_free') and product.get('contains_dairy'):
            if product['contains_dairy']:
                violated.append("contains dairy")
        
        # Check vegan constraint
        if constraints.get('vegan') and product.get('is_vegan'):
            if not product['is_vegan']:
                violated.append("not vegan")
        
        if not violated:
            satisfied_count += 1
        else:
            violations.append({
                'product': product['name'],
                'violations': violated
            })
    
    return satisfied_count, violations

def run_full_validation():
    """
    Comprehensive validation on all 100 training queries
    """
    print("="*70)
    print("COMPREHENSIVE VALIDATION - ALL 100 TRAINING QUERIES")
    print("="*70)
    
    # Step 1: Run full NDCG evaluation
    print("\n[1/5] Running NDCG Evaluation on All 100 Queries...")
    print("-"*70)
    results_df = evaluate_training_set(sample_size=None, save_results=True)
    
    # Step 2: Summary statistics
    print("\n[2/5] Summary Statistics")
    print("-"*70)
    print(f"Total Queries: {len(results_df)}")
    print(f"\nNDCG Distribution:")
    print(f"  Mean:   {results_df['ndcg'].mean():.4f}")
    print(f"  Median: {results_df['ndcg'].median():.4f}")
    print(f"  Std:    {results_df['ndcg'].std():.4f}")
    print(f"  Min:    {results_df['ndcg'].min():.4f}")
    print(f"  Max:    {results_df['ndcg'].max():.4f}")
    print(f"\nRecall:")
    print(f"  Mean:   {results_df['recall'].mean():.4f}")
    print(f"  Median: {results_df['recall'].median():.4f}")
    
    # Step 3: Identify problem queries
    print("\n[3/5] Worst Performing Queries (NDCG < 0.5)")
    print("-"*70)
    worst_queries = results_df[results_df['ndcg'] < 0.5].sort_values('ndcg')
    
    if len(worst_queries) > 0:
        print(f"Found {len(worst_queries)} queries with NDCG < 0.5:\n")
        for idx, row in worst_queries.head(10).iterrows():
            print(f"{row['query_id']}: {row['ndcg']:.4f}")
            print(f"  Query: {row['query_text'][:80]}...")
            print(f"  Recall: {row['recall']:.2f}")
            print()
    else:
        print("✓ No queries with NDCG < 0.5!")
    
    # Step 4: Zero-result queries
    print("\n[4/5] Queries Returning 0 Products")
    print("-"*70)
    zero_result_queries = results_df[results_df['num_predicted'] == 0]
    
    if len(zero_result_queries) > 0:
        print(f"Found {len(zero_result_queries)} queries with 0 results:\n")
        for idx, row in zero_result_queries.iterrows():
            print(f"{row['query_id']}: {row['query_text'][:80]}...")
    else:
        print("✓ All queries returned at least 1 product!")
    
    # Step 5: Manual constraint check on sample
    print("\n[5/5] Constraint Satisfaction Check (Sample of 10 queries)")
    print("-"*70)
    
    queries_df = load_train_queries()
    sample_queries = queries_df.sample(n=10, random_state=42)
    
    total_satisfied = 0
    total_checked = 0
    
    for _, row in sample_queries.iterrows():
        from constraint_extraction import extract_constraints
        
        query_text = row['query_text']
        constraints = extract_constraints(query_text)
        products = query_products(query_text)
        
        if len(products) > 0:
            satisfied, violations = analyze_constraint_satisfaction(
                query_text, products, constraints
            )
            total_satisfied += satisfied
            total_checked += min(5, len(products))
            
            print(f"\n{row['query_id']}: {satisfied}/5 top products satisfy constraints")
            if violations:
                print(f"  Violations found:")
                for v in violations[:2]:  # Show first 2
                    print(f"    - {v['product']}: {', '.join(v['violations'])}")
    
    if total_checked > 0:
        satisfaction_rate = (total_satisfied / total_checked) * 100
        print(f"\n{'='*70}")
        print(f"Overall Constraint Satisfaction: {satisfaction_rate:.1f}%")
        print(f"({total_satisfied}/{total_checked} top-5 products satisfy all constraints)")
    
    # Final Summary
    print("\n" + "="*70)
    print("VALIDATION SUMMARY")
    print("="*70)
    print(f"✓ Full NDCG:           {results_df['ndcg'].mean():.4f} (mean)")
    print(f"✓ Median NDCG:         {results_df['ndcg'].median():.4f}")
    print(f"✓ Recall:              {results_df['recall'].mean():.4f}")
    print(f"✓ Queries < 0.5 NDCG:  {len(worst_queries)}/100")
    print(f"✓ Zero-result queries: {len(zero_result_queries)}/100")
    if total_checked > 0:
        print(f"✓ Constraint satisfaction: {satisfaction_rate:.1f}%")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    mean_ndcg = results_df['ndcg'].mean()
    
    if mean_ndcg >= 0.75:
        print("✓ EXCELLENT: Your model is performing very well!")
        print("  - NDCG > 0.75 is competitive for this challenge")
        print("  - Focus on edge cases and constraint satisfaction")
    elif mean_ndcg >= 0.65:
        print("✓ GOOD: Your model is solid and competitive")
        print("  - NDCG 0.65-0.75 is respectable performance")
        print("  - Consider: hybrid scoring, better constraint extraction")
    else:
        print("⚠ NEEDS IMPROVEMENT: Consider optimizations")
        print("  - Review worst queries to find patterns")
        print("  - Check constraint extraction accuracy")
        print("  - Consider adjusting filtering logic")
    
    if len(zero_result_queries) > 5:
        print("\n⚠ Too many zero-result queries")
        print("  - Review fallback logic")
        print("  - Check if constraints are too strict")
    
    if total_checked > 0 and satisfaction_rate < 70:
        print("\n⚠ Low constraint satisfaction rate")
        print("  - Products may not match user requirements")
        print("  - Consider stricter filtering or better scoring")
    
    print("\n" + "="*70)
    print("Results saved to: training_evaluation_results.csv")
    print("="*70)
    
    return results_df

if __name__ == "__main__":
    results = run_full_validation()
    print("\nValidation complete! Review the results above.")