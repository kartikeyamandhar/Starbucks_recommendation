"""
Manually verify the 6 problematic queries return ground truth products at rank #1
"""
from pipeline import query_products
from data_loader import load_train_queries

# The 6 queries with issues
problem_queries = {
    "TRAIN_045": "ESP_014",  # Espresso
    "TRAIN_051": "BRW_004",  # Decaf Pike Place
    "TRAIN_060": "CBR_001",  # Cold Brew
    "TRAIN_063": "BRW_004",  # Decaf Pike Place
    "TRAIN_073": "BRW_004",  # Decaf Pike Place
    "TRAIN_090": "BRW_004",  # Decaf Pike Place
}

queries_df = load_train_queries()

print("="*70)
print("MANUAL VERIFICATION - Are we returning ground truth products?")
print("="*70)

for query_id, expected_product_id in problem_queries.items():
    query_row = queries_df[queries_df['query_id'] == query_id].iloc[0]
    query_text = query_row['query_text']
    
    print(f"\n{query_id}")
    print(f"Query: {query_text[:60]}...")
    print(f"Expected: {expected_product_id}")
    
    # Run pipeline
    products = query_products(query_text)
    
    if len(products) == 0:
        print("❌ NO PRODUCTS RETURNED")
        continue
    
    # Check if expected product is in results
    actual_top = products[0]['product_id']
    print(f"Actual #1: {actual_top}")
    
    if actual_top == expected_product_id:
        print(f"✓ CORRECT! {products[0]['name']} is #1 (score: {products[0]['score']:.4f})")
    else:
        print(f"❌ WRONG! Expected {expected_product_id}, got {actual_top}")
        
        # Find where expected product is
        for i, p in enumerate(products):
            if p['product_id'] == expected_product_id:
                print(f"   Expected product found at rank #{i+1} (score: {p['score']:.4f})")
                break
        else:
            print(f"   Expected product NOT in results at all!")

print("\n" + "="*70)