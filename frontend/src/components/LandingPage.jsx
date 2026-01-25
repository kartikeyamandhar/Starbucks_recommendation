import { useState } from 'react';
import { queries } from '../data/queries';

export default function LandingPage({ onSelectQuery }) {
  const [searchTerm, setSearchTerm] = useState('');
  
  // Filter queries based on search
  const filteredQueries = queries.filter(q => 
    q.text.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-starbucks-cream">
      {/* Header */}
      <header className="bg-starbucks-green">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-h1 text-white">Starbucks AI Barista</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <h2 className="text-h1 text-starbucks-dark mb-3">
            What can we get started for you today? ☕
          </h2>
          <p className="text-body text-neutral-700">
            Pick a query below and let our AI barista find your perfect drink
          </p>
        </div>

        {/* Search */}
        <div className="mb-6">
          <input
            type="text"
            placeholder="Search queries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-3 rounded-default border-2 border-neutral-200 text-body focus:outline-none focus:border-starbucks-green"
          />
        </div>

        {/* Query Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredQueries.map((query) => (
            <button
              key={query.id}
              onClick={() => onSelectQuery(query)}
              className="card text-left hover:shadow-soft transition-shadow duration-200 cursor-pointer group"
            >
              <div className="flex items-start justify-between mb-2">
                <span className="text-caption text-starbucks-green font-medium">
                  {query.id}
                </span>
                <svg 
                  className="w-5 h-5 text-neutral-300 group-hover:text-starbucks-green transition-colors"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
              <p className="text-body text-neutral-900">
                "{query.text}"
              </p>
            </button>
          ))}
        </div>

        {/* No Results */}
        {filteredQueries.length === 0 && (
          <div className="text-center py-10">
            <p className="text-body text-neutral-500">
              No queries found. Try a different search term.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-16 py-6 border-t border-neutral-200">
        <div className="max-w-7xl mx-auto px-4">
          <p className="text-caption text-neutral-500 text-center">
            UCLA Starbucks Data Challenge 2026 • NDCG: 0.7921 • Built by Kartikeya
          </p>
        </div>
      </footer>
    </div>
  );
}