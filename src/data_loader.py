"""
Data Loading Module
Loads products and queries from CSV files
"""
import pandas as pd
from typing import Dict, List
from config import PRODUCTS_FILE, TRAIN_QUERIES_FILE, TEST_QUERIES_FILE


def load_products() -> pd.DataFrame:
    """
    Load products from CSV
    
    Returns:
        DataFrame with product information
    """
    try:
        df = pd.read_csv(PRODUCTS_FILE)
        print(f"✓ Loaded {len(df)} products from {PRODUCTS_FILE}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {PRODUCTS_FILE} not found")
        print("Make sure you've downloaded products.csv to the data/ folder")
        raise


def load_train_queries() -> pd.DataFrame:
    """
    Load training queries (with answers)
    
    Returns:
        DataFrame with query_id, query_text, constraints, and relevant_products
    """
    try:
        df = pd.read_csv(TRAIN_QUERIES_FILE)
        print(f"✓ Loaded {len(df)} training queries from {TRAIN_QUERIES_FILE}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {TRAIN_QUERIES_FILE} not found")
        print("Make sure you've downloaded queries_train.csv to the data/ folder")
        raise


def load_test_queries() -> pd.DataFrame:
    """
    Load test queries (no answers - what we'll submit)
    
    Returns:
        DataFrame with query_id and query_text
    """
    try:
        df = pd.read_csv(TEST_QUERIES_FILE)
        print(f"✓ Loaded {len(df)} test queries from {TEST_QUERIES_FILE}")
        return df
    except FileNotFoundError:
        print(f"❌ Error: {TEST_QUERIES_FILE} not found")
        print("Make sure you've downloaded queries_test.csv to the data/ folder")
        raise


def prepare_product_text(row: pd.Series) -> str:
    """
    Create rich text representation of product for embedding
    Combines name, description, and key attributes
    
    Args:
        row: Product row from DataFrame
        
    Returns:
        Combined text representation
    """
    parts = []
    
    # Core product info
    parts.append(row['name'])
    
    if pd.notna(row.get('description')):
        parts.append(row['description'])
    
    # Category and type
    parts.append(f"Category: {row['category']}")
    parts.append(f"Temperature: {row['temperature']}")
    
    # Key attributes for search
    if row.get('contains_dairy') == False:
        parts.append("Dairy-free")
    if row.get('is_vegan') == True:
        parts.append("Vegan")
    
    # Caffeine info
    if pd.notna(row.get('caffeine_level')):
        parts.append(f"Caffeine: {row['caffeine_level']}")
    
    # Nutrition highlights
    if pd.notna(row.get('calories')):
        parts.append(f"{row['calories']} calories")
    if pd.notna(row.get('sugar_g')):
        parts.append(f"{row['sugar_g']}g sugar")
    
    return ". ".join(parts)


def get_product_metadata(row: pd.Series) -> Dict:
    """
    Extract metadata for Pinecone from product row
    
    Args:
        row: Product row from DataFrame
        
    Returns:
        Dictionary with metadata fields
    """
    metadata = {
        "product_id": row['product_id'],
        "name": row['name'],
        "category": row['category'],
        "temperature": row['temperature'],
    }
    
    # Add numeric fields if present
    numeric_fields = ['calories', 'sugar_g', 'price', 'caffeine_mg']
    for field in numeric_fields:
        if field in row and pd.notna(row[field]):
            metadata[field] = float(row[field])
    
    # Add boolean fields
    bool_fields = ['contains_dairy', 'is_vegan']
    for field in bool_fields:
        if field in row and pd.notna(row[field]):
            metadata[field] = bool(row[field])
    
    # Add caffeine level if present
    if 'caffeine_level' in row and pd.notna(row['caffeine_level']):
        metadata['caffeine_level'] = row['caffeine_level']
    
    return metadata


# Test function
if __name__ == "__main__":
    print("Testing Data Loading\n" + "="*50)
    
    # Load products
    products = load_products()
    print(f"\nProduct columns: {products.columns.tolist()}")
    print(f"First product: {products.iloc[0]['name']}")
    
    # Test text preparation
    print(f"\n{'Sample Product Text:':-^50}")
    sample_text = prepare_product_text(products.iloc[0])
    print(sample_text)
    
    # Test metadata extraction
    print(f"\n{'Sample Metadata:':-^50}")
    sample_metadata = get_product_metadata(products.iloc[0])
    print(sample_metadata)
    
    # Load queries
    print(f"\n{'Loading Queries:':-^50}")
    try:
        train_queries = load_train_queries()
        print(f"Sample training query: {train_queries.iloc[0]['query_text']}")
    except:
        print("Training queries not loaded (file may not exist yet)")
    
    try:
        test_queries = load_test_queries()
        print(f"Sample test query: {test_queries.iloc[0]['query_text']}")
    except:
        print("Test queries not loaded (file may not exist yet)")