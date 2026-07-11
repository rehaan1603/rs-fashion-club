import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';

const METHODS = [
  { id: 'upi', label: 'UPI', hint: 'Pay via any UPI app' },
  { id: 'card', label: 'Credit / Debit Card', hint: 'Visa, Mastercard, RuPay' },
  { id: 'netbanking', label: 'Net Banking', hint: 'All major banks' },
  { id: 'cod', label: 'Cash on Delivery', hint: 'Pay when your order arrives' },
];

export default function Payment() {
  const { items, total, refresh } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [selected, setSelected] = useState('upi');
  const [placing, setPlacing] = useState(false);
  const [error, setError] = useState('');

  if (!user) {
    return (
      <div className="empty-state">
        <p>Sign in to continue to payment.</p>
        <Link to="/login" className="btn btn-primary" style={{ marginTop: 16 }}>Sign in</Link>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="empty-state">
        <p>Your bag is empty.</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>Continue shopping</Link>
      </div>
    );
  }

  const handlePay = async () => {
    setError('');
    setPlacing(true);
    try {
      const data = await api.checkout(selected);
      if (data.cod) {
        await refresh();
        navigate(`/success?order_id=${data.order_id}&cod=1`);
      } else if (data.demo_mode) {
        await refresh();
        navigate(`/success?order_id=${data.order_id}&demo=1`);
      } else {
        window.location.href = data.checkout_url;
      }
    } catch (err) {
      setError(err.message);
      setPlacing(false);
    }
  };

  return (
    <div className="bag-layout">
      <div className="bag-panel">
        <div className="bag-panel-header">SELECT PAYMENT METHOD</div>
        {error && <div className="form-error" style={{ margin: '12px 20px 0' }}>{error}</div>}
        <div style={{ padding: '8px 20px 20px' }}>
          {METHODS.map((m) => (
            <label
              key={m.id}
              className={`filter-checkbox-row ${selected === m.id ? 'active-label' : ''}`}
              style={{
                border: '1px solid var(--line)',
                borderColor: selected === m.id ? 'var(--pink)' : 'var(--line)',
                padding: '14px 16px',
                marginBottom: 10,
                cursor: 'pointer',
              }}
            >
              <input
                type="radio"
                name="payment-method"
                checked={selected === m.id}
                onChange={() => setSelected(m.id)}
              />
              <span>
                <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--ink)' }}>{m.label}</div>
                <div style={{ fontSize: 12 }}>{m.hint}</div>
              </span>
            </label>
          ))}
        </div>
        {selected !== 'cod' && (
          <div className="checkout-note" style={{ paddingTop: 0 }}>
            Processed via Stripe in test mode — use card 4242 4242 4242 4242, any future date, any CVC.
            UPI and Net Banking are shown for the ordering flow but route through the same test payment.
          </div>
        )}
      </div>

      <div className="bag-panel">
        <div className="bag-panel-header">PRICE DETAILS</div>
        <div className="summary-row">
          <span>Items ({items.length})</span>
          <span>₹{Math.round(total)}</span>
        </div>
        <div className="summary-row total">
          <span>Total Payable</span>
          <span>₹{Math.round(total)}</span>
        </div>
        <div style={{ padding: '4px 20px 16px' }}>
          <button className="btn btn-primary btn-block" onClick={handlePay} disabled={placing}>
            {placing ? 'Placing order…' : selected === 'cod' ? 'Place Order' : `Pay ₹${Math.round(total)}`}
          </button>
        </div>
      </div>
    </div>
  );
}
