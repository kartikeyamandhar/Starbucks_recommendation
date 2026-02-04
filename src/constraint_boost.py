"""
Test that constraint boosting ranks the single matching product #1
"""
from pipeline import query_products

# Test the 6 queries that have exactly 1 matching product
test_queries = [
    "May I get an americano or latte that's no more than $4.0 and oat milk or something dairy free?",
    "hey there, i'd love basic brewed coffee that's not too much caffeine, no dairy, and no more than 200 cal",
    "lemme get that cold brew stuff that's less than $4.5, no more than 15g sugar, and no animal stuff",
    "I'd like drip coffee that's not too much caffeine, cheaper than $5.5, and under 150 cal please",
    "what do you have for drip coffee that's low caffeine, less than 400 calories, and dairy free?",
    "get me house coffee that's less than 250 calories, less than $6.0, and mild",
]

expected_products = [
    "Espresso",
    "Decaf Pike Place Roast",
    "Cold Brew Coffee",
    "Decaf Pike Place Roast",
    "Decaf Pike Place Roast",
    "Decaf Pike Place Roast",
]

print("="*70)
print("TESTING CONSTRAINT BOOSTING")
print("="*70)

success_count = 0

for i, (query, expected) in enumerate(zip(test_queries, expected_products), 1):
    print(f"\n[{i}/6] Testing query...")
    print(f"Query: {query[:60]}...")
    print(f"Expected #1: {expected}")
    
    products = query_products(query)
    
    if len(products) > 0:
        actual = products[0]['name']
        if expected.lower() in actual.lower():
            print(f"✓ SUCCESS: #{1} is {actual} (score: {products[0]['score']:.4f})")
            success_count += 1
        else:
            print(f"❌ FAIL: #{1} is {actual}, expected {expected}")
            print(f"   Top 3:")
            for j, p in enumerate(products[:3], 1):
                print(f"     {j}. {p['name']} (score: {p['score']:.4f})")
    else:
        print(f"❌ FAIL: No products returned")

print("\n" + "="*70)
print(f"RESULTS: {success_count}/6 queries correctly ranked")
print("="*70)

if success_count == 6:
    print("🎉 Perfect! All constraint-matching products ranked #1!")
    print("Your NDCG should improve significantly on these queries.")
elif success_count >= 4:
    print("✓ Good! Most queries improved. Consider running full validation.")
else:
    print("⚠ Some queries still failing. May need to adjust boost factor.")