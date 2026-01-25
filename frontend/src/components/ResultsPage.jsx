import { useState, useEffect } from 'react';

export default function ResultsPage({ query, onPlaceOrder, onBack }) {
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Call real Python API
    setLoading(true);
    setError(null);
    
    fetch('http://localhost:5001/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: query.text })
    })
      .then(res => {
        if (!res.ok) {
          throw new Error('API request failed');
        }
        return res.json();
      })
      .then(data => {
        console.log('Received products:', data);
        setProducts(data.products || []);
        setLoading(false);
      })
      .catch(err => {
        console.error('API Error:', err);
        setError('Failed to fetch results. Make sure the Python API is running on port 5001.');
        setLoading(false);
      });
  }, [query]);

  const toggleProductSelection = (productId) => {
    setSelectedProducts(prev => 
      prev.includes(productId)
        ? prev.filter(id => id !== productId)
        : [...prev, productId]
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-starbucks-cream flex items-center justify-center">
        <div className="text-center">
          <div className="mb-6">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-starbucks-green border-t-transparent"></div>
          </div>
          <h2 className="text-h2 text-starbucks-dark mb-2">
            Wait a lil mate, the chef's are cooking something 👨‍🍳
          </h2>
          <p className="text-body text-neutral-600">
            Searching through 115 drinks to find your perfect match...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-starbucks-cream flex items-center justify-center">
        <div className="max-w-2xl mx-4">
          <div className="card bg-red-50 border-2 border-red-200">
            <h2 className="text-h2 text-red-800 mb-2">⚠️ Connection Error</h2>
            <p className="text-body text-red-700 mb-4">{error}</p>
            <div className="flex gap-3">
              <button onClick={onBack} className="btn-primary">
                ← Go Back
              </button>
              <button 
                onClick={() => window.location.reload()} 
                className="btn-secondary"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-starbucks-cream">
      {/* Header */}
      <header className="bg-starbucks-green">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-h2 text-white">Your Results</h1>
            <p className="text-caption text-white/80 mt-1">
              Based on: "{query.text}"
            </p>
          </div>
          <button
            onClick={onBack}
            className="btn-secondary bg-white/10 border-white text-white hover:bg-white/20"
          >
            ← Back
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* AI Response */}
        <div className="card mb-8 bg-starbucks-dark text-white">
          <div className="flex items-start gap-4">
            <div className="text-4xl">🤖</div>
            <div>
              <h3 className="text-h2 mb-2">Yo, I think you should try these!</h3>
              <p className="text-body">
                Found {products.length} drinks that match what you're looking for. 
                I ranked them by how well they fit your vibe. Check them out below! 👇
              </p>
            </div>
          </div>
        </div>

        {/* No Results */}
        {products.length === 0 && (
          <div className="card text-center py-10">
            <p className="text-h2 text-neutral-600 mb-2">😕 No drinks found</p>
            <p className="text-body text-neutral-500">
              Try adjusting your filters or search for something else
            </p>
          </div>
        )}

        {/* Products Grid */}
        {products.length > 0 && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
              {products.map((product, index) => (
                <div
                  key={product.product_id}
                  className={`card cursor-pointer transition-all duration-200 ${
                    selectedProducts.includes(product.product_id)
                      ? 'ring-2 ring-starbucks-green shadow-soft'
                      : 'hover:shadow-soft'
                  }`}
                  onClick={() => toggleProductSelection(product.product_id)}
                >
                  {/* Rank Badge */}
                  <div className="flex items-center justify-between mb-3">
                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-starbucks-green text-white text-caption font-medium">
                      #{index + 1}
                    </span>
                    <span className="text-caption text-neutral-500">
                      Match: {(product.score * 100).toFixed(0)}%
                    </span>
                  </div>

                  {/* Product Name */}
                  <h3 className="text-body font-medium text-neutral-900 mb-2">
                    {product.name}
                  </h3>

                  {/* Product Details */}
                  <div className="space-y-1 mb-4">
                    {product.price && (
                      <div className="flex justify-between text-caption text-neutral-600">
                        <span>Price:</span>
                        <span className="font-medium">${product.price.toFixed(2)}</span>
                      </div>
                    )}
                    {product.calories !== undefined && (
                      <div className="flex justify-between text-caption text-neutral-600">
                        <span>Calories:</span>
                        <span>{product.calories} cal</span>
                      </div>
                    )}
                    {product.sugar_g !== undefined && (
                      <div className="flex justify-between text-caption text-neutral-600">
                        <span>Sugar:</span>
                        <span>{product.sugar_g}g</span>
                      </div>
                    )}
                    {product.caffeine_mg !== undefined && (
                      <div className="flex justify-between text-caption text-neutral-600">
                        <span>Caffeine:</span>
                        <span>{product.caffeine_mg}mg</span>
                      </div>
                    )}
                  </div>

                  {/* Selection Indicator */}
                  <div className="pt-3 border-t border-neutral-200">
                    {selectedProducts.includes(product.product_id) ? (
                      <div className="flex items-center gap-2 text-starbucks-green text-caption font-medium">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                        </svg>
                        <span>Selected</span>
                      </div>
                    ) : (
                      <span className="text-caption text-neutral-500">Click to select</span>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Place Order CTA */}
            {selectedProducts.length > 0 && (
              <div className="card bg-starbucks-green text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-h2 mb-1">Ready to order?</h3>
                    <p className="text-body">
                      You've selected {selectedProducts.length} drink{selectedProducts.length > 1 ? 's' : ''}
                    </p>
                  </div>
                  <button
                    onClick={() => onPlaceOrder(selectedProducts, products)}
                    className="btn-primary bg-white text-starbucks-green hover:bg-neutral-50"
                  >
                    Place Order →
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}