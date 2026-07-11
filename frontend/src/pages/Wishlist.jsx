import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWishlist } from '../context/WishlistContext';
import ProductCard from '../components/ProductCard';

export default function Wishlist() {
  const { user } = useAuth();
  const { items } = useWishlist();

  if (!user) {
    return (
      <div className="empty-state">
        <p>Sign in to view your wishlist.</p>
        <Link to="/login" className="btn btn-primary" style={{ marginTop: 16 }}>Sign in</Link>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="empty-state">
        <p>Your wishlist is empty.</p>
        <Link to="/" className="btn btn-primary" style={{ marginTop: 16 }}>Continue shopping</Link>
      </div>
    );
  }

  return (
    <>
      <div className="hero-strip">
        <h1>My Wishlist</h1>
        <p>{items.length} items saved</p>
      </div>
      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '24px 40px 80px' }}>
        <div className="product-grid">
          {items.map((item, idx) => <ProductCard key={item.id} product={item.product} index={idx} />)}
        </div>
      </div>
    </>
  );
}
