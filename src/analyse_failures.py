"""
Analyze if the 11 failing queries are truly impossible
Check actual products data to see if matches exist
"""
import pandas as pd
from constraint_extraction import extract_constraints

# The 11 queries with NDCG < 0.5 from the validation
failing_queries = [
    "TRAIN_045",  # May I get an americano or latte that's no more than $4.0 and oat milk or something dairy free?
    "TRAIN_051",  # hey there, i'd love basic brewed coffee that's not too much caffeine, no dairy, and no more than 200 cal
    "TRAIN_060",  # lemme get that cold brew stuff that's less than $4.5, no more than 15g sugar, and no animal stuff
    "TRAIN_063",  # I'd like drip coffee that's not too much caffeine, cheaper than $5.5, and under 150 cal
    "TRAIN_073",  # what do you have for drip coffee that's low caffeine, less than 400 calories, and dairy free?
    "TRAIN_085",  # it's hot out, i need a plain coffee that's low caffeine, 100 calories or less, and no more than $5.5
    "TRAIN_090",  # get me house coffee that's less than 250 calories, less than $6.0, and mild
]

# Load data
products = pd.read_csv('../data/products.csv')
queries_train = pd.read_csv('../data/queries_train.csv')

print("="*70)
print("ANALYZING 11 FAILING QUERIES")
print("="*70)

for query_id in failing_queries:
    query_row = queries_train[queries_train['query_id'] == query_id]
    
    if query_row.empty:
        continue
        
    query_text = query_row.iloc[0]['query_text']
    
    print(f"\n{query_id}")
    print(f"Query: {query_text}")
    print("-"*70)
    
    # Extract constraints
    constraints = extract_constraints(query_text)
    print(f"Extracted constraints: {constraints}")
    
    # Manually filter products based on constraints
    filtered = products.copy()
    
    # Category filter
    if constraints.get('category'):
        filtered = filtered[filtered['category'] == constraints['category']]
        print(f"After category filter ({constraints['category']}): {len(filtered)} products")
    
    # Temperature filter
    if constraints.get('temperature'):
        filtered = filtered[filtered['temperature'] == constraints['temperature']]
        print(f"After temperature filter ({constraints['temperature']}): {len(filtered)} products")
    
    # Price filter
    if constraints.get('max_price'):
        filtered = filtered[filtered['price'] <= constraints['max_price']]
        print(f"After price filter (≤${constraints['max_price']}): {len(filtered)} products")
    
    # Calories filter
    if constraints.get('max_calories'):
        filtered = filtered[filtered['calories'] <= constraints['max_calories']]
        print(f"After calories filter (≤{constraints['max_calories']} cal): {len(filtered)} products")
    
    # Sugar filter
    if constraints.get('max_sugar'):
        filtered = filtered[filtered['sugar_g'] <= constraints['max_sugar']]
        print(f"After sugar filter (≤{constraints['max_sugar']}g): {len(filtered)} products")
    
    # Dairy filter
    if constraints.get('dairy_free'):
        filtered = filtered[filtered['contains_dairy'] == False]
        print(f"After dairy-free filter: {len(filtered)} products")
    
    # Vegan filter
    if constraints.get('vegan'):
        filtered = filtered[filtered['is_vegan'] == True]
        print(f"After vegan filter: {len(filtered)} products")
    
    # Caffeine filter
    if constraints.get('caffeine_level'):
        caffeine_ranges = {
            "none": (0, 15),
            "low": (15, 100),
            "medium": (75, 250),
            "high": (200, 500)
        }
        min_caff, max_caff = caffeine_ranges[constraints['caffeine_level']]
        filtered = filtered[(filtered['caffeine_mg'] >= min_caff) & (filtered['caffeine_mg'] <= max_caff)]
        print(f"After caffeine filter ({constraints['caffeine_level']}: {min_caff}-{max_caff}mg): {len(filtered)} products")
    
    print(f"\n✓ FINAL: {len(filtered)} products match all constraints")
    
    if len(filtered) > 0:
        print("Matching products:")
        for idx, row in filtered.head(5).iterrows():
            print(f"  - {row['name']} (${row['price']}, {row['calories']} cal, {row['caffeine_mg']}mg caffeine)")
    else:
        print("❌ NO PRODUCTS MATCH - Query is truly impossible!")
        
        # Try to identify which constraint is most restrictive
        print("\n  Constraint analysis:")
        test = products.copy()
        
        if constraints.get('category'):
            test = test[test['category'] == constraints['category']]
            if len(test) == 0:
                print(f"    ⚠️  No products in category '{constraints['category']}'")
        
        if constraints.get('caffeine_level') and len(test) > 0:
            min_caff, max_caff = caffeine_ranges[constraints['caffeine_level']]
            caffeine_matches = test[(test['caffeine_mg'] >= min_caff) & (test['caffeine_mg'] <= max_caff)]
            if len(caffeine_matches) == 0:
                actual_range = (test['caffeine_mg'].min(), test['caffeine_mg'].max())
                print(f"    ⚠️  No products with {constraints['caffeine_level']} caffeine ({min_caff}-{max_caff}mg)")
                print(f"        Actual range in category: {actual_range[0]}-{actual_range[1]}mg")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)