"""
Submission Generator
Process test queries and generate submission CSV
"""
import pandas as pd
from typing import List
from tqdm import tqdm
import time

from config import TEST_QUERIES_FILE, SUBMISSION_FILE
from data_loader import load_test_queries
from pipeline import query_products


def generate_submission(output_file: str = None, add_delays: bool = True) -> pd.DataFrame:
    """
    Generate submission CSV for test queries
    
    Args:
        output_file: Output CSV filename (default: submission.csv)
        add_delays: Add small delays between queries to avoid rate limits
        
    Returns:
        DataFrame with submission data
    """
    if output_file is None:
        output_file = SUBMISSION_FILE
    
    print("="*70)
    print("GENERATING SUBMISSION")
    print("="*70)
    
    # Load test queries
    test_df = load_test_queries()
    print(f"\nProcessing {len(test_df)} test queries...")
    
    # Process each query
    submission_rows = []
    
    for idx, row in tqdm(test_df.iterrows(), total=len(test_df), desc="Processing queries"):
        query_id = row['query_id']
        query_text = row['query_text']
        
        try:
            # Get predictions
            products = query_products(query_text)
            
            # Format as semicolon-separated product IDs
            product_ids = ';'.join([p['product_id'] for p in products])
            
            submission_rows.append({
                'query_id': query_id,
                'products': product_ids
            })
            
            # Optional: Add small delay to avoid rate limits
            if add_delays and (idx + 1) % 10 == 0:
                time.sleep(1)
                
        except Exception as e:
            print(f"\n❌ Error on query {query_id}: {e}")
            # Add empty submission row for failed queries
            submission_rows.append({
                'query_id': query_id,
                'products': ''
            })
    
    # Create DataFrame
    submission_df = pd.DataFrame(submission_rows)
    
    # Validate format
    print(f"\n{'Validating submission...':-^70}")
    print(f"✓ Total rows: {len(submission_df)}")
    print(f"✓ Columns: {submission_df.columns.tolist()}")
    
    # Check for empty products
    empty_count = (submission_df['products'] == '').sum()
    if empty_count > 0:
        print(f"⚠️  Warning: {empty_count} queries have no products")
    
    # Sample output
    print(f"\n{'Sample Submission Rows:':-^70}")
    print(submission_df.head(3).to_string(index=False))
    
    # Save to CSV
    submission_df.to_csv(output_file, index=False)
    print(f"\n✓ Submission saved to: {output_file}")
    print("="*70)
    
    return submission_df


def preview_submission(num_queries: int = 3):
    """
    Preview submission for a few test queries without generating full file
    
    Args:
        num_queries: Number of queries to preview
    """
    print("="*70)
    print(f"SUBMISSION PREVIEW ({num_queries} queries)")
    print("="*70)
    
    # Load test queries
    test_df = load_test_queries()
    sample_queries = test_df.head(num_queries)
    
    for idx, row in sample_queries.iterrows():
        print(f"\n{'='*70}")
        print(f"Query ID: {row['query_id']}")
        print(f"Query: {row['query_text']}")
        print(f"{'='*70}")
        
        # Get predictions
        products = query_products(row['query_text'])
        
        # Show top 5
        print(f"\nTop 5 Products:")
        for i, product in enumerate(products[:5], 1):
            print(f"{i}. {product['name']} ({product['product_id']}) - Score: {product['score']:.4f}")
        
        # Show submission format
        product_ids = ';'.join([p['product_id'] for p in products])
        print(f"\nSubmission row:")
        print(f"{row['query_id']},{product_ids[:80]}...")
        
        print()


def validate_submission_file(filename: str):
    """
    Validate a submission CSV file
    
    Args:
        filename: Path to submission CSV
    """
    print(f"\n{'Validating submission file...':-^70}")
    
    try:
        df = pd.read_csv(filename)
        
        # Check columns
        if list(df.columns) != ['query_id', 'products']:
            print(f"❌ Invalid columns: {df.columns.tolist()}")
            print("   Expected: ['query_id', 'products']")
            return False
        
        # Check number of rows
        print(f"✓ Rows: {len(df)}")
        if len(df) != 100:
            print(f"⚠️  Warning: Expected 100 rows, got {len(df)}")
        
        # Check for duplicates
        duplicates = df['query_id'].duplicated().sum()
        if duplicates > 0:
            print(f"❌ Found {duplicates} duplicate query_ids")
            return False
        else:
            print(f"✓ No duplicate query_ids")
        
        # Check product format
        sample_products = df['products'].head(3)
        print(f"\n{'Sample product lists:':-^70}")
        for idx, products in enumerate(sample_products):
            product_count = len(products.split(';')) if products else 0
            print(f"  {df.iloc[idx]['query_id']}: {product_count} products")
        
        # Check for empty rows
        empty_rows = (df['products'] == '').sum()
        if empty_rows > 0:
            print(f"\n⚠️  {empty_rows} queries have empty product lists")
        else:
            print(f"\n✓ All queries have products")
        
        print(f"\n✓ Submission file is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Error validating file: {e}")
        return False


# Main function
if __name__ == "__main__":
    import sys
    
    # Check command line args
    if len(sys.argv) > 1 and sys.argv[1] == "--preview":
        # Preview mode: just show a few queries
        preview_submission(num_queries=3)
    elif len(sys.argv) > 1 and sys.argv[1] == "--validate":
        # Validate existing submission file
        filename = sys.argv[2] if len(sys.argv) > 2 else SUBMISSION_FILE
        validate_submission_file(filename)
    else:
        # Full generation mode
        print("\n⚠️  WARNING: This will process all 100 test queries!")
        print("This will take approximately 5-10 minutes.")
        print("It will also use OpenAI API credits for embeddings and constraint extraction.")
        response = input("\nContinue? (yes/no): ")
        
        if response.lower() == 'yes':
            submission_df = generate_submission()
            
            # Validate the generated file
            validate_submission_file(SUBMISSION_FILE)
            
            print("\n" + "="*70)
            print("✓ SUBMISSION READY!")
            print(f"Upload {SUBMISSION_FILE} to the challenge portal")
            print("="*70)
        else:
            print("\nCancelled. Use --preview to test on a few queries first:")
            print("  python submission.py --preview")