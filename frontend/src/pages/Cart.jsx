import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { api, resolveImageUrl } from '../api';

export default function Cart() {
  const { items, total, mrpTotal, discountTotal, updateQuantity, removeItem, refresh } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  if (!user) {
    return (
      <div className="empty-state">
        <p>Sign in to view your bag.</p>
        <Link to="/login" className="btn btn-primary" style={{ marginTop: 16 }}>Sign in</Link>
      </div>
    );
  }

  const handleCheckout = () => {
    navigate('/payment');
  };

  if (items.length === 0) {
    return (
      <div className="empty-state">
        <p>Your bag is empty.</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>Continue shopping</Link>
      </div>
    );
  }

  return (
    <div className="bag-layout">
      <div className="bag-panel">
        <div className="bag-panel-header">MY BAG ({items.length})</div>
        {error && <div className="form-error" style={{ margin: '12px 20px 0' }}>{error}</div>}
        {items.map((item) => (
          <div className="bag-item" key={item.id}>
            <img
              src={resolveImageUrl(item.product.image_url)}
              alt={item.product.name}
              onError={(e) => { e.target.onerror = null; e.target.src = 'https://loremflickr.com/600/800/fashion,clothing'; }}
            />
            <div>
              <div className="bag-item-brand">{item.product.brand}</div>
              <div className="bag-item-name">{item.product.name}</div>
              <div className="bag-item-price-row">
                <span className="price-current">₹{Math.round(item.product.price)}</span>
                {item.product.original_price > item.product.price && (
                  <span className="price-mrp">₹{Math.round(item.product.original_price)}</span>
                )}
              </div>
              <button className="remove-link" onClick={() => removeItem(item.id)}>Remove</button>
            </div>
            <div className="qty-control">
              <button onClick={() => updateQuantity(item.id, item.quantity - 1)}>−</button>
              <span>{item.quantity}</span>
              <button onClick={() => updateQuantity(item.id, item.quantity + 1)}>+</button>
            </div>
          </div>
        ))}
      </div>

      <div className="bag-panel">
        <div className="bag-panel-header">PRICE DETAILS</div>
        <div className="summary-row">
          <span>Total MRP</span>
          <span>₹{Math.round(mrpTotal)}</span>
        </div>
        {discountTotal > 0 && (
          <div className="summary-row">
            <span>Discount on MRP</span>
            <span className="value-discount">−₹{Math.round(discountTotal)}</span>
          </div>
        )}
        <div className="summary-row">
          <span>Shipping Fee</span>
          <span className="value-discount">FREE</span>
        </div>
        <div className="summary-row total">
          <span>Total Amount</span>
          <span>₹{Math.round(total)}</span>
        </div>
        <div style={{ padding: '4px 20px 16px' }}>
          <button className="btn btn-primary btn-block" onClick={handleCheckout}>
            Place Order
          </button>
        </div>
        <div className="checkout-note">
          Choose UPI, Card, Net Banking or Cash on Delivery on the next step.
        </div>
      </div>
    </div>
  );
}
