"""
Comprehensive validation before re-running submission
Tests problematic queries + sample NDCG to ensure improvements
"""
from pipeline import query_products
from evaluation import evaluate_training_set
import sys

print("="*70)
print("COMPREHENSIVE VALIDATION")
print("="*70)

# Step 1: Test the 5 problematic queries
print("\nStep 1: Testing 5 Previously Failed Queries")
print("-"*70)

problematic_queries = [
    "yo i need green tea that's regular caffeine and max $6.5",
    "trying to be healthy, got some cold brew that's under $4.0 and strong?",
    "Could I have green tea that's under 250 cal and medium caffeine?",
    "anything that's a tea that's medium caffeine, cheaper than $5.0, and dairy free?",
    "ooh do you have a chai or tea that's warm, regular caffeine, and no dairy?",
]

failed_count = 0
for i, query_text in enumerate(problematic_queries, 1):
    products = query_products(query_text)
    status = "✓" if len(products) > 0 else "❌"
    print(f"{status} Query {i}: {len(products)} products")
    if len(products) == 0:
        failed_count += 1

print(f"\nResult: {5 - failed_count}/5 queries now return products")

if failed_count > 0:
    print(f"⚠️  Warning: {failed_count} queries still return 0 products")
    response = input("\nContinue with NDCG validation? (yes/no): ")
    if response.lower() != 'yes':
        sys.exit(0)

# Step 2: Quick NDCG validation on 20 sample queries
print("\n" + "="*70)
print("Step 2: NDCG Validation on 20 Sample Training Queries")
print("-"*70)

results = evaluate_training_set(sample_size=20, save_results=False)

print("\n" + "="*70)
print("VALIDATION SUMMARY")
print("="*70)
print(f"✓ Problematic queries fixed: {5 - failed_count}/5")
print(f"✓ Average NDCG on sample: {results['ndcg'].mean():.4f}")
print(f"✓ Median NDCG on sample: {results['ndcg'].median():.4f}")

if results['ndcg'].mean() < 0.60:
    print("\n⚠️  Warning: NDCG seems lower than expected")
    print("Consider reviewing the changes before full submission")
else:
    print("\n✓ NDCG looks good! Ready for full submission.")

print("\nNext step: Run submission.py to generate final CSV")