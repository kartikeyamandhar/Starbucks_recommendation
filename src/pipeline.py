"""
Query Pipeline Module
Combines constraint extraction, filtering, and semantic ranking
"""
from pinecone import Pinecone
from openai import OpenAI
from typing import List, Dict, Optional
import pandas as pd

from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, OPENAI_API_KEY, EMBEDDING_MODEL
from constraint_extraction import extract_constraints
from pinecone_setup import get_embedding

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def build_pinecone_filter(constraints: Dict) -> Optional[Dict]:
    """
    Build Pinecone metadata filter from extracted constraints
    
    Args:
        constraints: Dictionary of extracted constraints
        
    Returns:
        Pinecone filter dictionary or None if no constraints
    """
    filters = []
    
    # Category filter
    if constraints.get("category"):
        filters.append({"category": {"$eq": constraints["category"]}})
    
    # Temperature filter
    if constraints.get("temperature"):
        filters.append({"temperature": {"$eq": constraints["temperature"]}})
    
    # Max calories filter
    if constraints.get("max_calories"):
        filters.append({"calories": {"$lte": constraints["max_calories"]}})
    
    # Max sugar filter
    if constraints.get("max_sugar"):
        filters.append({"sugar_g": {"$lte": constraints["max_sugar"]}})
    
    # Max price filter
    if constraints.get("max_price"):
        filters.append({"price": {"$lte": constraints["max_price"]}})
    
    # Dairy-free filter
    if constraints.get("dairy_free") == True:
        filters.append({"contains_dairy": {"$eq": False}})
    
    # Vegan filter
    if constraints.get("vegan") == True:
        filters.append({"is_vegan": {"$eq": True}})
    
    # Caffeine level filter
    if constraints.get("caffeine_level"):
        # More lenient caffeine ranges - adjusted for actual product distribution
        caffeine_ranges = {
            "none": (0, 15),      # Decaf/herbal
            "low": (15, 100),     # Mild teas, light coffee
            "medium": (75, 250),  # Most teas and regular coffee (broader range)
            "high": (200, 500)    # Strong coffee, espresso
        }
        min_caff, max_caff = caffeine_ranges[constraints["caffeine_level"]]
        filters.append({"caffeine_mg": {"$gte": min_caff, "$lte": max_caff}})
    
    # Return combined filter with $and, or None if no filters
    if not filters:
        return None
    
    return {"$and": filters} if len(filters) > 1 else filters[0]


def query_products(query_text: str, top_k: int = 115) -> List[Dict]:
    """
    Complete pipeline: Extract constraints → Filter → Rank
    
    Args:
        query_text: Natural language query
        top_k: Maximum number of results to return
        
    Returns:
        List of product dictionaries with scores, sorted by relevance
    """
    # Stage 1: Extract constraints
    print(f"Query: {query_text}")
    constraints = extract_constraints(query_text)
    print(f"Constraints: {constraints}")
    
    # Stage 2: Build filter
    pinecone_filter = build_pinecone_filter(constraints)
    if pinecone_filter:
        print(f"Filter: {pinecone_filter}")
    else:
        print("Filter: None (no constraints)")
    
    # Stage 3: Get query embedding
    query_embedding = get_embedding(query_text)
    
    # Stage 4: Query Pinecone with filter + semantic search
    index = pc.Index(PINECONE_INDEX_NAME)
    results = index.query(
        vector=query_embedding,
        filter=pinecone_filter,
        top_k=top_k,
        include_metadata=True
    )
    
    # Fallback: If 0 results, try relaxing constraints
    if len(results['matches']) == 0 and pinecone_filter:
        print("⚠️  0 results found, trying fallback with relaxed constraints...")
        
        # Try removing price and caffeine constraints (most restrictive)
        relaxed_constraints = constraints.copy()
        relaxed_constraints['max_price'] = None
        relaxed_constraints['caffeine_level'] = None
        
        relaxed_filter = build_pinecone_filter(relaxed_constraints)
        
        results = index.query(
            vector=query_embedding,
            filter=relaxed_filter,
            top_k=top_k,
            include_metadata=True
        )
        print(f"Fallback found {len(results['matches'])} products")
    

    # Stage 5: Format results and boost products that satisfy ALL constraints
    products = []
    for match in results['matches']:
        product = {
            'product_id': match['id'],
            'score': match['score'],
            'name': match['metadata']['name'],
            'category': match['metadata']['category'],
            'temperature': match['metadata']['temperature'],
        }
        
        # Add optional fields if present
        for field in ['price', 'calories', 'sugar_g', 'caffeine_mg', 'contains_dairy', 'is_vegan']:
            if field in match['metadata']:
                product[field] = match['metadata'][field]
        
        # Check if product satisfies ALL extracted constraints
        satisfies_all_constraints = True
        
        # Check each constraint
        if constraints.get('max_price') and product.get('price'):
            if product['price'] > constraints['max_price']:
                satisfies_all_constraints = False
        
        if constraints.get('max_calories') and product.get('calories'):
            if product['calories'] > constraints['max_calories']:
                satisfies_all_constraints = False
        
        if constraints.get('max_sugar') and product.get('sugar_g'):
            if product['sugar_g'] > constraints['max_sugar']:
                satisfies_all_constraints = False
        
        if constraints.get('dairy_free') and product.get('contains_dairy'):
            if product['contains_dairy']:
                satisfies_all_constraints = False
        
        if constraints.get('vegan') and product.get('is_vegan'):
            if not product['is_vegan']:
                satisfies_all_constraints = False
        
        # Boost score by 25% if satisfies ALL constraints
        # This ensures constraint-matching products rank higher than semantic-only matches
        if satisfies_all_constraints:
            product['score'] = product['score'] * 1.25
        
        products.append(product)
    
    # Re-sort by boosted scores
    products.sort(key=lambda x: x['score'], reverse=True)
    
    print(f"Found {len(products)} matching products")
    return products


def format_submission_row(query_id: str, products: List[Dict]) -> str:
    """
    Format products as submission CSV row
    
    Args:
        query_id: Query ID (e.g., TEST_001)
        products: List of product dictionaries
        
    Returns:
        CSV row string: "query_id,product1;product2;product3"
    """
    product_ids = [p['product_id'] for p in products]
    return f"{query_id},{';'.join(product_ids)}"


def display_results(products: List[Dict], top_n: int = 10):
    """
    Pretty print query results
    
    Args:
        products: List of product dictionaries
        top_n: Number of top results to display
    """
    print(f"\n{'='*70}")
    print(f"TOP {min(top_n, len(products))} RESULTS")
    print(f"{'='*70}")
    
    for i, product in enumerate(products[:top_n], 1):
        print(f"\n{i}. {product['name']}")
        print(f"   Score: {product['score']:.4f}")
        print(f"   ID: {product['product_id']}")
        print(f"   Category: {product['category']} | Temperature: {product['temperature']}")
        
        details = []
        if 'price' in product:
            details.append(f"${product['price']:.2f}")
        if 'calories' in product:
            details.append(f"{product['calories']:.0f} cal")
        if 'sugar_g' in product:
            details.append(f"{product['sugar_g']:.0f}g sugar")
        if 'caffeine_mg' in product:
            details.append(f"{product['caffeine_mg']:.0f}mg caffeine")
        
        if details:
            print(f"   {' | '.join(details)}")
        
        flags = []
        if product.get('contains_dairy') == False:
            flags.append("Dairy-free")
        if product.get('is_vegan') == True:
            flags.append("Vegan")
        
        if flags:
            print(f"   🏷️  {', '.join(flags)}")


# Test function
if __name__ == "__main__":
    test_queries = [
        "I want something sweet and cold but I'm trying to avoid dairy",
        "Strong coffee under $5",
        "Low calorie iced tea with no caffeine",
        "Vegan frappuccino",
        "Hot espresso drink with extra caffeine"
    ]
    
    for query in test_queries:
        print("\n" + "="*70)
        products = query_products(query)
        display_results(products, top_n=5)
        
        # Show submission format
        submission_row = format_submission_row("TEST_001", products)
        print(f"\nSubmission format preview:")
        print(submission_row[:100] + "...")
        
        print("\n" + "="*70)
        input("Press Enter for next query...")