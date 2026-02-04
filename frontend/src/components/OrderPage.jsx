import { useState } from 'react';

export default function OrderPage({ selectedProductIds, allProducts, onBack, onConfirm }) {
  const [orderType, setOrderType] = useState('pickup');
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [orderPlaced, setOrderPlaced] = useState(false);

  // Get selected products details
  const orderItems = allProducts.filter(p => selectedProductIds.includes(p.product_id));
  
  // Calculate total
  const subtotal = orderItems.reduce((sum, item) => sum + item.price, 0);
  const tax = subtotal * 0.0875; // 8.75% tax
  const total = subtotal + tax;

  const handlePlaceOrder = () => {
    setOrderPlaced(true);
  };

  if (orderPlaced) {
    return (
      <div className="min-h-screen bg-starbucks-cream flex items-center justify-center">
        <div className="max-w-2xl w-full mx-4">
          <div className="card text-center">
            {/* Success Icon */}
            <div className="mb-6">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-starbucks-green/10">
                <svg className="w-12 h-12 text-starbucks-green" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
            </div>

            {/* Success Message */}
            <h2 className="text-h1 text-starbucks-dark mb-2">
              Order Placed! 🎉
            </h2>
            <p className="text-body text-neutral-600 mb-8">
              Your order has been confirmed. We'll have it ready in about 5-7 minutes.
            </p>

            {/* Order Details */}
            <div className="bg-starbucks-cream rounded-default p-4 mb-8 text-left">
              <div className="flex justify-between items-center mb-4">
                <span className="text-body font-medium">Order #</span>
                <span className="text-body text-starbucks-green font-medium">A{Math.floor(Math.random() * 1000)}</span>
              </div>
              <div className="flex justify-between items-center mb-4">
                <span className="text-body font-medium">Pickup at</span>
                <span className="text-body">UCLA Ackerman Union</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-body font-medium">Ready by</span>
                <span className="text-body">{new Date(Date.now() + 7 * 60000).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-3">
              <button
                onClick={() => onConfirm()}
                className="btn-primary flex-1"
              >
                Done
              </button>
              <button
                onClick={onBack}
                className="btn-secondary flex-1"
              >
                Order Another
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
          <h1 className="text-h2 text-white">Place Order</h1>
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
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Order Options */}
          <div className="lg:col-span-2 space-y-6">
            {/* Order Type */}
            <div className="card">
              <h2 className="text-h2 mb-4">Order Type</h2>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setOrderType('pickup')}
                  className={`p-4 rounded-default border-2 transition-colors ${
                    orderType === 'pickup'
                      ? 'border-starbucks-green bg-starbucks-green/5'
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="text-2xl mb-2">🏪</div>
                  <div className="text-body font-medium">Pickup</div>
                  <div className="text-caption text-neutral-600">Ready in 5-7 min</div>
                </button>
                <button
                  onClick={() => setOrderType('delivery')}
                  className={`p-4 rounded-default border-2 transition-colors ${
                    orderType === 'delivery'
                      ? 'border-starbucks-green bg-starbucks-green/5'
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="text-2xl mb-2">🚴</div>
                  <div className="text-body font-medium">Delivery</div>
                  <div className="text-caption text-neutral-600">15-20 min</div>
                </button>
              </div>
            </div>

            {/* Location */}
            <div className="card">
              <h2 className="text-h2 mb-4">
                {orderType === 'pickup' ? 'Pickup Location' : 'Delivery Address'}
              </h2>
              <div className="p-4 bg-starbucks-cream rounded-default border-2 border-neutral-200">
                <div className="flex items-center gap-3">
                  <div className="text-2xl">📍</div>
                  <div>
                    <div className="text-body font-medium">UCLA Ackerman Union</div>
                    <div className="text-caption text-neutral-600">308 Westwood Plaza, Los Angeles, CA 90024</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment */}
            <div className="card">
              <h2 className="text-h2 mb-4">Payment Method</h2>
              <div className="space-y-3">
                <button
                  onClick={() => setPaymentMethod('card')}
                  className={`w-full p-4 rounded-default border-2 transition-colors text-left ${
                    paymentMethod === 'card'
                      ? 'border-starbucks-green bg-starbucks-green/5'
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">💳</div>
                      <div>
                        <div className="text-body font-medium">Card ending in 4242</div>
                        <div className="text-caption text-neutral-600">Visa • Expires 12/25</div>
                      </div>
                    </div>
                    {paymentMethod === 'card' && (
                      <svg className="w-5 h-5 text-starbucks-green" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
                <button
                  onClick={() => setPaymentMethod('apple')}
                  className={`w-full p-4 rounded-default border-2 transition-colors text-left ${
                    paymentMethod === 'apple'
                      ? 'border-starbucks-green bg-starbucks-green/5'
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="text-2xl">🍎</div>
                      <div>
                        <div className="text-body font-medium">Apple Pay</div>
                        <div className="text-caption text-neutral-600">iPhone 15 Pro</div>
                      </div>
                    </div>
                    {paymentMethod === 'apple' && (
                      <svg className="w-5 h-5 text-starbucks-green" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Order Summary */}
          <div className="lg:col-span-1">
            <div className="card sticky top-4">
              <h2 className="text-h2 mb-4">Order Summary</h2>

              {/* Items */}
              <div className="space-y-4 mb-6 pb-6 border-b border-neutral-200">
                {orderItems.map((item) => (
                  <div key={item.product_id} className="flex justify-between gap-3">
                    <div className="flex-1">
                      <div className="text-body font-medium">{item.name}</div>
                      <div className="text-caption text-neutral-600">
                        {item.temperature} • {item.category}
                      </div>
                    </div>
                    <div className="text-body font-medium">
                      ${item.price.toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>

              {/* Totals */}
              <div className="space-y-3 mb-6">
                <div className="flex justify-between text-body">
                  <span className="text-neutral-600">Subtotal</span>
                  <span>${subtotal.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-body">
                  <span className="text-neutral-600">Tax (8.75%)</span>
                  <span>${tax.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-h2 pt-3 border-t border-neutral-200">
                  <span>Total</span>
                  <span className="text-starbucks-green">${total.toFixed(2)}</span>
                </div>
              </div>

              {/* Place Order Button */}
              <button
                onClick={handlePlaceOrder}
                className="btn-primary w-full text-h2 py-4"
              >
                Place Order
              </button>

              {/* Rewards Info */}
              <div className="mt-4 p-3 bg-starbucks-green/5 rounded-default">
                <div className="flex items-center gap-2 text-caption text-starbucks-green font-medium">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span>Earn {Math.floor(total * 2)} stars with this order</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}