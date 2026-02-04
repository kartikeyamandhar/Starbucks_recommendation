import { useState } from 'react';
import LandingPage from './components/LandingPage';
import ResultsPage from './components/ResultsPage';
import OrderPage from './components/OrderPage';
import './index.css';

function App() {
  const [currentPage, setCurrentPage] = useState('landing');
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [selectedProductIds, setSelectedProductIds] = useState([]);
  const [allProducts, setAllProducts] = useState([]);

  const handleSelectQuery = (query) => {
    setSelectedQuery(query);
    setCurrentPage('results');
  };

  const handlePlaceOrder = (productIds, products) => {
    setSelectedProductIds(productIds);
    setAllProducts(products);
    setCurrentPage('order');
  };

  const handleBackToLanding = () => {
    setSelectedQuery(null);
    setSelectedProductIds([]);
    setAllProducts([]);
    setCurrentPage('landing');
  };

  const handleBackToResults = () => {
    setCurrentPage('results');
  };

  const handleOrderConfirm = () => {
    handleBackToLanding();
  };

  return (
    <>
      {currentPage === 'landing' && (
        <LandingPage onSelectQuery={handleSelectQuery} />
      )}
      
      {currentPage === 'results' && (
        <ResultsPage
          query={selectedQuery}
          onPlaceOrder={handlePlaceOrder}
          onBack={handleBackToLanding}
        />
      )}
      
      {currentPage === 'order' && (
        <OrderPage
          selectedProductIds={selectedProductIds}
          allProducts={allProducts}
          onBack={handleBackToResults}
          onConfirm={handleOrderConfirm}
        />
      )}
    </>
  );
}

export default App;