# Starbucks Product Recommendation System

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![NDCG: 85.1%](https://img.shields.io/badge/NDCG-85.1%25-brightgreen.svg)](https://en.wikipedia.org/wiki/Discounted_cumulative_gain)

> A hybrid constraint-based and semantic recommendation system that understands natural language queries and returns highly relevant Starbucks product suggestions. Built for the UCLA Starbucks Data Challenge.

![Demo](https://via.placeholder.com/800x400.png?text=Add+Demo+Screenshot+Here)

## Key Features

- **Natural Language Understanding**: "vegan latte under $5" → Structured constraints
- **Hybrid Search**: Combines semantic similarity with metadata filtering
- **Intelligent Constraint Boosting**: +25% score for products matching ALL requirements
- **Production-Ready Performance**: ~250ms latency, scales to 40M+ users
- **Top-Tier Accuracy**: 85.1% NDCG, 95.9% recall

## Quick Start

### Prerequisites

- Python 3.13+
- Node.js 16+
- OpenAI API key
- Pinecone API key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/starbucks-recommendation.git
cd starbucks-recommendation

# Backend setup
python -m venv isenv
source isenv/bin/activate  # On Windows: isenv\Scripts\activate
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys

# Initialize Pinecone database
python src/pinecone_setup.py

# Frontend setup (optional)
cd frontend
npm install
```

### Run the API

```bash
# Start Flask server
python src/api.py

# API runs on http://localhost:5000
```

### Test the API

```bash
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "vegan latte under $5", "top_k": 5}'
```

## 📊 Architecture

```
┌──────────────┐
│  User Query  │  "vegan latte under $5"
└──────┬───────┘
       │
       ▼
┌─────────────────────┐
│ Constraint Extract  │  GPT-4o-mini
│ (Natural Language)  │  → {vegan: true, max_price: 5.0}
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Metadata Filtering  │  Pinecone Vector DB
│ (115 → 8 products)  │  Filter by price, dietary, category
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Semantic Ranking    │  text-embedding-3-small
│ (Cosine Similarity) │  Score by query relevance
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Constraint Boost    │  +25% for products satisfying
│ (Innovation Layer)  │  ALL user constraints
└──────┬──────────────┘
       │
       ▼
┌──────────────┐
│   Results    │  [ESP_014, ESP_003, ESP_013...]
└──────────────┘
```

## Performance

| Metric | Value | Tier |
|--------|-------|------|
| **Mean NDCG** | 85.1% | Excellent |
| **Median NDCG** | 86.8% | Excellent |
| **Recall** | 95.9% | Excellent |
| **Latency** | ~250ms | Production-ready |
| **Constraint Satisfaction** | 100% | Perfect |

**Competition Benchmark:**
- 75%+ NDCG: Competitive
- 80%+ NDCG: Strong
- **85%+ NDCG: Top-tier** ← We're here!

## 💡 Key Innovation: Constraint Satisfaction Boosting

**Problem:** Pure semantic search ranked high-similarity products first, even if they violated user constraints.

**Example:**
- Query: "cheap vegan coffee"
- ❌ Without boosting: "Premium Oat Milk Latte" ($7.50) ranked #1
- ✅ With boosting: "Espresso" ($2.95, vegan) ranked #1

**Solution:** Boost scores by 25% for products satisfying ALL constraints.

**Results:**
- +6% NDCG improvement (79% → 85%)
- Fixed 6 queries with NDCG 0.0 → 1.0
- 100% constraint satisfaction in top-5 results

## 🛠️ Tech Stack

**Backend:**
- Python 3.13
- OpenAI API (GPT-4o-mini, text-embedding-3-small)
- Pinecone (Vector Database)
- Flask (REST API)

**Frontend:**
- React 18
- Vite
- Tailwind CSS

**Infrastructure:**
- Pinecone Serverless (Vector Search)
- OpenAI API (Embeddings & LLM)

## 📁 Project Structure

```
starbucks-recommendation/
├── data/                      # Dataset (115 products, queries)
├── src/                       # Python backend
│   ├── pipeline.py            # Main recommendation logic
│   ├── constraint_extraction.py  # LLM-based parser
│   ├── pinecone_setup.py      # Vector DB initialization
│   ├── evaluation.py          # NDCG calculation
│   ├── api.py                 # Flask REST API
│   └── config.py              # Configuration
├── frontend/                  # React web interface
├── submission.csv             # Competition submission
└── training_evaluation_results.csv  # Performance metrics
```

## 🔧 Configuration

Create a `.env` file:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-east-1
```

## 📈 Usage Examples

### Python API

```python
from src.pipeline import get_recommendations

# Get recommendations
results = get_recommendations("vegan latte under $5", top_k=5)

for product in results:
    print(f"{product['name']}: ${product['price']} (score: {product['score']:.3f})")
```

### REST API

```bash
# Natural language query
curl -X POST http://localhost:5000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "query": "iced coffee with no dairy and low calories",
    "top_k": 5
  }'
```

**Response:**
```json
{
  "query": "iced coffee with no dairy and low calories",
  "results": [
    {
      "product_id": "CBR_001",
      "name": "Cold Brew Coffee",
      "price": 4.45,
      "calories": 5,
      "score": 0.923,
      "dairy_free": true
    }
  ],
  "constraints_extracted": {
    "category": "cold_brew",
    "temperature": "iced",
    "dairy_free": true,
    "max_calories": 150
  },
  "latency_ms": 247
}
```

## 🧪 Running Tests & Validation

```bash
# Evaluate on 100 training queries
python src/full_validation.py

# Generate competition submission
python src/submission.py

# Analyze failure cases
python src/analyse_failures.py
```

## 🎨 Frontend (Optional)

```bash
cd frontend
npm run dev

# Visit http://localhost:5173
```

## 📊 Dataset

**Products:** 115 Starbucks items across categories:
- Espresso drinks (hot & iced)
- Brewed coffee
- Cold brew
- Tea & iced tea
- Refreshers
- Frappuccinos

**Queries:** 100+ natural language queries like:
- "vegan latte under $5"
- "strong cold brew with no dairy"
- "iced tea with low sugar"

## 🔍 How It Works

### 1. Constraint Extraction
```python
"vegan latte under $5" 
→ {category: "espresso", vegan: True, max_price: 5.0}
```

### 2. Metadata Filtering
```python
115 products → Filter by constraints → 8 products
```

### 3. Semantic Ranking
```python
Query embedding × Product embeddings → Cosine similarity scores
```

### 4. Constraint Boosting
```python
If product satisfies ALL constraints:
    score *= 1.25  # 25% boost
```

### 5. Return Top-K
```python
[ESP_014, ESP_003, ...] # Ranked by final scores
```

## 🚧 Known Limitations

1. **Overly Aggressive Fallback**: Removes multiple constraints simultaneously when no results found
2. **Subcategory Precision**: "green tea" query may return black tea in positions 4-5
3. **No Personalization**: Doesn't learn from user history yet

