import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { api } from '../api';
import { useCart } from '../context/CartContext';

export default function Success() {
  const [params] = useSearchParams();
  const orderId = params.get('order_id');
  const isDemo = params.get('demo') === '1';
  const isCod = params.get('cod') === '1';
  const { refresh } = useCart();
  const [status, setStatus] = useState('Confirming your order…');

  useEffect(() => {
    if (!orderId) return;
    if (isDemo || isCod) {
      setStatus(isCod ? 'cod' : 'paid');
      return;
    }
    api.confirmOrder(orderId).then((data) => {
      setStatus(data.status);
      refresh();
    });
  }, [orderId]);

  const confirmed = status === 'paid' || status === 'cod';

  return (
    <div className="success-wrap">
      <div style={{ fontSize: 40 }}>✓</div>
      <h1>{confirmed ? 'Order confirmed' : 'Processing…'}</h1>
      <p style={{ color: 'var(--ink-soft)' }}>
        {status === 'cod'
          ? 'Thank you — your order is confirmed. Pay in cash when it arrives.'
          : status === 'paid'
          ? 'Thank you — your payment went through and your order has been placed.'
          : 'Hang tight while we confirm your payment.'}
      </p>
      <Link to="/" className="btn btn-primary" style={{ marginTop: 24 }}>Continue shopping</Link>
    </div>
  );
}
