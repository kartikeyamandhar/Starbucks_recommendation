"""
Test script to verify file paths
"""
import os
from config import PRODUCTS_FILE, TRAIN_QUERIES_FILE, TEST_QUERIES_FILE, PROJECT_ROOT, DATA_DIR

print("="*70)
print("PATH VERIFICATION")
print("="*70)

print(f"\nCurrent directory: {os.getcwd()}")
print(f"This script location: {__file__}")
print(f"\nProject root: {PROJECT_ROOT}")
print(f"Data directory: {DATA_DIR}")

print(f"\n{'File Paths:':-^70}")
print(f"Products:      {PRODUCTS_FILE}")
print(f"Train queries: {TRAIN_QUERIES_FILE}")
print(f"Test queries:  {TEST_QUERIES_FILE}")

print(f"\n{'File Existence:':-^70}")
print(f"Products exists:      {os.path.exists(PRODUCTS_FILE)}")
print(f"Train queries exists: {os.path.exists(TRAIN_QUERIES_FILE)}")
print(f"Test queries exists:  {os.path.exists(TEST_QUERIES_FILE)}")

if not os.path.exists(PRODUCTS_FILE):
    print(f"\n❌ Products file not found!")
    print(f"Looking for: {PRODUCTS_FILE}")
    print(f"\nPlease ensure products.csv is in the data/ folder")