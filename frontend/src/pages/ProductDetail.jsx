import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api, resolveImageUrl } from '../api';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { useWishlist } from '../context/WishlistContext';
import ProductCard from '../components/ProductCard';

export default function ProductDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const { addToCart } = useCart();
  const { isWishlisted, toggle } = useWishlist();
  const navigate = useNavigate();

  const [product, setProduct] = useState(null);
  const [recs, setRecs] = useState([]);
  const [selectedSize, setSelectedSize] = useState(null);
  const [status, setStatus] = useState('');

  useEffect(() => {
    setStatus('');
    setSelectedSize(null);
    api.getProduct(id).then(setProduct);
    api.getRecommendations(id).then(setRecs);
    window.scrollTo(0, 0);
  }, [id]);

  const handleAdd = async () => {
    if (!user) { navigate('/login'); return; }
    if (product.sizes?.length > 1 && !selectedSize) {
      setStatus('Please select a size');
      return;
    }
    await addToCart(Number(id), 1);
    setStatus('Added to bag');
    setTimeout(() => setStatus(''), 2000);
  };

  const handleWishlist = () => {
    if (!user) { navigate('/login'); return; }
    toggle(Number(id));
  };

  if (!product) return <div className="loading-row">Loading…</div>;

  const wished = user && isWishlisted(product.id);

  return (
    <>
      <div className="product-detail">
        <div className="detail-image">
          <img
            src={resolveImageUrl(product.image_url)}
            alt={product.name}
            onError={(e) => { e.target.onerror = null; e.target.src = 'https://loremflickr.com/600/800/fashion,clothing'; }}
          />
        </div>
        <div>
          <div className="detail-brand">{product.brand}</div>
          <div className="detail-name">{product.name}</div>

          <div className="detail-rating-row">
            <span className="detail-rating-badge">{product.rating} ★</span>
            <span className="detail-rating-count">{product.rating_count} Ratings</span>
          </div>

          <div className="detail-price-row">
            <span className="detail-price-current">₹{Math.round(product.price)}</span>
            {product.original_price > product.price && (
              <span className="detail-price-mrp">₹{Math.round(product.original_price)}</span>
            )}
            {product.discount_pct > 0 && (
              <span className="detail-price-discount">({product.discount_pct}% OFF)</span>
            )}
          </div>
          <div className="detail-tax-note">inclusive of all taxes</div>

          {product.sizes?.length > 0 && (
            <div className="size-section">
              <div className="size-label">Select Size</div>
              <div className="size-grid">
                {product.sizes.map((s) => (
                  <button
                    key={s}
                    className={`size-chip ${selectedSize === s ? 'selected' : ''}`}
                    onClick={() => setSelectedSize(s)}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          {product.color && (
            <div className="detail-color-note">Color: <strong>{product.color}</strong></div>
          )}

          <div className="detail-actions">
            <button className="btn btn-primary" onClick={handleAdd}>
              {user ? 'Add to Bag' : 'Sign in to add to bag'}
            </button>
            <button className={`btn btn-wishlist ${wished ? 'active' : ''}`} onClick={handleWishlist}>
              {wished ? '♥ Wishlisted' : '♡ Wishlist'}
            </button>
          </div>
          {status && <p style={{ marginTop: -14, marginBottom: 20, fontSize: 13, color: 'var(--pink)' }}>{status}</p>}

          <div className="detail-desc-block">
            <h3>Product Details</h3>
            <p>{product.description}</p>
            <p style={{ marginTop: 10, fontSize: 13 }}>{product.stock} in stock</p>
          </div>
        </div>
      </div>

      {recs.length > 0 && (
        <div className="recs-section">
          <h3>Similar Products</h3>
          <div className="recs-grid">
            {recs.map((p, i) => <ProductCard key={p.id} product={p} index={i} />)}
          </div>
        </div>
      )}
    </>
  );
}
