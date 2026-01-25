"""
Test the 5 problematic queries that returned 0 results
"""
from pipeline import query_products

# The 5 queries that had 0 results
problematic_queries = [
    ("TEST_001", "yo i need green tea that's regular caffeine and max $6.5"),
    ("TEST_002", "trying to be healthy, got some cold brew that's under $4.0 and strong?"),
    ("TEST_044", "Could I have green tea that's under 250 cal and medium caffeine?"),
    ("TEST_090", "anything that's a tea that's medium caffeine, cheaper than $5.0, and dairy free?"),
    ("TEST_094", "ooh do you have a chai or tea that's warm, regular caffeine, and no dairy?"),
]

print("="*70)
print("TESTING FIXES FOR PROBLEMATIC QUERIES")
print("="*70)

for query_id, query_text in problematic_queries:
    print(f"\n{query_id}: {query_text}")
    print("-"*70)
    
    products = query_products(query_text)
    
    if len(products) == 0:
        print("❌ STILL RETURNS 0 PRODUCTS")
    else:
        print(f"✓ Found {len(products)} products")
        print("\nTop 3:")
        for i, p in enumerate(products[:3], 1):
            print(f"  {i}. {p['name']} ({p['product_id']}) - Score: {p['score']:.4f}")
    
    print()

print("="*70)
print("DONE!")
print("="*70)