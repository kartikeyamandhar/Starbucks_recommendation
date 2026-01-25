"""
Constraint Extraction Module
Uses GPT-4o-mini to extract structured constraints from natural language queries
"""
from openai import OpenAI
import json
from typing import Dict, Optional
from config import OPENAI_API_KEY, OPENAI_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)

# System prompt for constraint extraction
CONSTRAINT_EXTRACTION_PROMPT = """You are a Starbucks product constraint extractor. 
Extract structured constraints from customer queries about Starbucks products.

Return ONLY valid JSON with these exact fields (use null if not mentioned):
{
  "category": null or one of ["brewed", "cold_brew", "espresso", "frappuccino", "refresher", "tea"],
  "temperature": null or one of ["hot", "iced", "blended"],
  "max_calories": null or number,
  "max_sugar": null or number,
  "max_price": null or number,
  "dairy_free": null or boolean,
  "vegan": null or boolean,
  "caffeine_level": null or one of ["none", "low", "medium", "high"]
}

Guidelines:
- "sweet" or "sugary" → don't set max_sugar (they WANT sugar)
- "low sugar" or "not too sweet" → max_sugar: 20
- "no dairy" or "lactose free" → dairy_free: true
- "coffee" → category: "espresso" or "brewed"
- "strong coffee" or "extra caffeine" or "high caffeine" → caffeine_level: "high"
- "decaf" or "no caffeine" or "caffeine free" → caffeine_level: "none"
- "mild" or "low caffeine" or "not too much caffeine" → caffeine_level: "low"
- "regular caffeine" or "medium caffeine" or "normal caffeine" → caffeine_level: null (don't filter, most products are medium)
- "need the caffeine" or "need caffeine" or "pick me up" without "strong" → caffeine_level: null
- "cold" → temperature: "iced" or "blended"
- "budget" or "cheap" → max_price: 5.0
- "under $X" → max_price: X

Examples:
Query: "I want something sweet and cold but I'm trying to avoid dairy"
Output: {"category": null, "temperature": "iced", "max_calories": null, "max_sugar": null, "max_price": null, "dairy_free": true, "vegan": null, "caffeine_level": null}

Query: "Strong coffee under $5"
Output: {"category": "espresso", "temperature": null, "max_calories": null, "max_sugar": null, "max_price": 5.0, "dairy_free": null, "vegan": null, "caffeine_level": "high"}

Query: "Iced tea with low sugar and no caffeine"
Output: {"category": "tea", "temperature": "iced", "max_calories": null, "max_sugar": 20, "max_price": null, "dairy_free": null, "vegan": null, "caffeine_level": "none"}
"""


def extract_constraints(query: str) -> Dict:
    """
    Extract structured constraints from a natural language query
    
    Args:
        query: Natural language customer query
        
    Returns:
        Dictionary with extracted constraints
    """
    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": CONSTRAINT_EXTRACTION_PROMPT},
                {"role": "user", "content": query}
            ],
            response_format={"type": "json_object"},  # Enforce JSON output
            temperature=0.0  # Deterministic output
        )
        
        constraints = json.loads(response.choices[0].message.content)
        return constraints
        
    except Exception as e:
        print(f"Error extracting constraints: {e}")
        # Return empty constraints on error
        return {
            "category": None,
            "temperature": None,
            "max_calories": None,
            "max_sugar": None,
            "max_price": None,
            "dairy_free": None,
            "vegan": None,
            "caffeine_level": None
        }


def validate_constraints(constraints: Dict) -> bool:
    """
    Validate that extracted constraints have valid values
    
    Args:
        constraints: Dictionary of constraints
        
    Returns:
        True if valid, False otherwise
    """
    valid_categories = [None, "brewed", "cold_brew", "espresso", "frappuccino", "refresher", "tea"]
    valid_temperatures = [None, "hot", "iced", "blended"]
    valid_caffeine = [None, "none", "low", "medium", "high"]
    
    if constraints.get("category") not in valid_categories:
        return False
    if constraints.get("temperature") not in valid_temperatures:
        return False
    if constraints.get("caffeine_level") not in valid_caffeine:
        return False
    
    return True


# Test function
if __name__ == "__main__":
    test_queries = [
        "I want something sweet and cold but I'm trying to avoid dairy",
        "Strong coffee under $5",
        "Low calorie iced tea with no caffeine",
        "Vegan frappuccino",
        "Hot espresso drink with extra caffeine"
    ]
    
    print("Testing Constraint Extraction\n" + "="*50)
    for query in test_queries:
        print(f"\nQuery: {query}")
        constraints = extract_constraints(query)
        print(f"Constraints: {json.dumps(constraints, indent=2)}")
        print(f"Valid: {validate_constraints(constraints)}")