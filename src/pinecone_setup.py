"""
Pinecone Setup Module
Initialize Pinecone index and upload product embeddings
"""
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import pandas as pd
from typing import List, Dict
from tqdm import tqdm
import time

from config import (
    PINECONE_API_KEY, 
    PINECONE_INDEX_NAME, 
    PINECONE_METRIC,
    OPENAI_API_KEY,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS
)
from data_loader import load_products, prepare_product_text, get_product_metadata

# Initialize clients
pc = Pinecone(api_key=PINECONE_API_KEY)
openai_client = OpenAI(api_key=OPENAI_API_KEY)


def create_pinecone_index():
    """
    Create Pinecone index if it doesn't exist
    Uses serverless spec for cost efficiency
    """
    # Check if index exists
    existing_indexes = pc.list_indexes()
    index_names = [index['name'] for index in existing_indexes]
    
    if PINECONE_INDEX_NAME in index_names:
        print(f"✓ Index '{PINECONE_INDEX_NAME}' already exists")
        return pc.Index(PINECONE_INDEX_NAME)
    
    # Create new index
    print(f"Creating index '{PINECONE_INDEX_NAME}'...")
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EMBEDDING_DIMENSIONS,
        metric=PINECONE_METRIC,
        spec=ServerlessSpec(
            cloud='aws',
            region='us-east-1'
        )
    )
    
    # Wait for index to be ready
    while not pc.describe_index(PINECONE_INDEX_NAME).status['ready']:
        time.sleep(1)
    
    print(f"✓ Index '{PINECONE_INDEX_NAME}' created successfully")
    return pc.Index(PINECONE_INDEX_NAME)


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using OpenAI
    
    Args:
        text: Text to embed
        
    Returns:
        List of embedding values
    """
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return response.data[0].embedding


def get_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """
    Generate embeddings for multiple texts efficiently
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts per API call
        
    Returns:
        List of embeddings
    """
    all_embeddings = []
    
    for i in tqdm(range(0, len(texts), batch_size), desc="Generating embeddings"):
        batch = texts[i:i + batch_size]
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=batch
        )
        embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(embeddings)
        
        # Rate limiting: small pause between batches
        time.sleep(0.1)
    
    return all_embeddings


def upload_products_to_pinecone(products_df: pd.DataFrame, batch_size: int = 100):
    """
    Upload all products to Pinecone with embeddings and metadata
    
    Args:
        products_df: DataFrame with product information
        batch_size: Number of products to upload per batch
    """
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Check if products already uploaded
    stats = index.describe_index_stats()
    if stats['total_vector_count'] > 0:
        print(f"⚠️  Index already contains {stats['total_vector_count']} vectors")
        response = input("Do you want to delete and re-upload? (yes/no): ")
        if response.lower() == 'yes':
            index.delete(delete_all=True)
            print("✓ Cleared existing vectors")
        else:
            print("Skipping upload")
            return
    
    print(f"\nPreparing {len(products_df)} products for upload...")
    
    # Prepare product texts for embedding
    product_texts = [prepare_product_text(row) for _, row in products_df.iterrows()]
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = get_embeddings_batch(product_texts)
    
    # Prepare vectors for upload
    vectors = []
    for idx, row in products_df.iterrows():
        vector = {
            'id': row['product_id'],
            'values': embeddings[idx],
            'metadata': get_product_metadata(row)
        }
        vectors.append(vector)
    
    # Upload in batches
    print(f"Uploading to Pinecone...")
    for i in tqdm(range(0, len(vectors), batch_size), desc="Uploading"):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
    
    print(f"✓ Successfully uploaded {len(vectors)} products to Pinecone")
    
    # Verify upload
    stats = index.describe_index_stats()
    print(f"✓ Index now contains {stats['total_vector_count']} vectors")


def test_query(query_text: str, top_k: int = 5):
    """
    Test a query against Pinecone
    
    Args:
        query_text: Natural language query
        top_k: Number of results to return
    """
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Generate query embedding
    query_embedding = get_embedding(query_text)
    
    # Query Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    print(f"\n{'Query:':-^60}")
    print(query_text)
    print(f"\n{'Top {top_k} Results:':-^60}")
    
    for i, match in enumerate(results['matches'], 1):
        print(f"\n{i}. {match['metadata']['name']}")
        print(f"   Score: {match['score']:.4f}")
        print(f"   Category: {match['metadata']['category']}")
        print(f"   Temperature: {match['metadata']['temperature']}")
        if 'price' in match['metadata']:
            print(f"   Price: ${match['metadata']['price']:.2f}")


# Main setup function
def setup_pinecone():
    """
    Complete setup: create index and upload products
    """
    print("="*60)
    print("PINECONE SETUP")
    print("="*60)
    
    # Create index
    create_pinecone_index()
    
    # Load products
    products = load_products()
    
    # Upload products
    upload_products_to_pinecone(products)
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    # Run full setup
    setup_pinecone()
    
    # Test with a sample query
    print("\n" + "="*60)
    print("TESTING QUERY")
    print("="*60)
    test_query("I want something sweet and cold but dairy free", top_k=5)