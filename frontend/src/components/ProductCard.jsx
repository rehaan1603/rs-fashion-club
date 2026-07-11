import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWishlist } from '../context/WishlistContext';
import { useCart } from '../context/CartContext';
import { resolveImageUrl } from '../api';

export default function ProductCard({ product, index = 0 }) {
  const { user } = useAuth();
  const { isWishlisted, toggle } = useWishlist();
  const { addToCart } = useCart();
  const navigate = useNavigate();
  const [added, setAdded] = useState(false);
  const [adding, setAdding] = useState(false);
  const wished = user && isWishlisted(product.id);

  const handleWishlist = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) { navigate('/login'); return; }
    toggle(product.id);
  };

  const handleQuickAdd = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) { navigate('/login'); return; }
    if (adding || added) return;
    setAdding(true);
    try {
      await addToCart(product.id, 1);
      setAdded(true);
      setTimeout(() => setAdded(false), 1600);
    } finally {
      setAdding(false);
    }
  };

  return (
    <Link
      to={`/product/${product.id}`}
      className="product-card"
      style={{ animationDelay: `${Math.min(index, 11) * 45}ms` }}
    >
      <div className="product-image-wrap">
        <button
          className={`wishlist-heart ${wished ? 'active' : ''}`}
          onClick={handleWishlist}
          aria-label={wished ? 'Remove from wishlist' : 'Add to wishlist'}
        >
          {wished ? '♥' : '♡'}
        </button>
        <img
          src={resolveImageUrl(product.image_url)}
          alt={product.name}
          loading="lazy"
          onError={(e) => { e.target.onerror = null; e.target.src = 'https://loremflickr.com/600/800/fashion,clothing'; }}
        />
        {product.discount_pct > 0 && (
          <div className="discount-ribbon">{product.discount_pct}% OFF</div>
        )}
        <button
          className={`quick-add-btn ${added ? 'added' : ''}`}
          onClick={handleQuickAdd}
          aria-label="Quick add to bag"
        >
          {added ? 'Added ✓' : adding ? 'Adding…' : 'Quick Add'}
        </button>
      </div>
      <div className="product-info">
        <div className="product-brand">{product.brand}</div>
        <div className="product-name">{product.name}</div>
        <div className="product-price-row">
          <span className="price-current">₹{Math.round(product.price)}</span>
          {product.original_price > product.price && (
            <span className="price-mrp">₹{Math.round(product.original_price)}</span>
          )}
          {product.discount_pct > 0 && (
            <span className="price-discount">({product.discount_pct}% OFF)</span>
          )}
        </div>
        <div className="product-rating">
          <span className="star">★</span> {product.rating} <span>| {product.rating_count}</span>
        </div>
      </div>
    </Link>
  );
}
