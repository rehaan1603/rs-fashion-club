import { Link, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { useWishlist } from '../context/WishlistContext';

const CATEGORY_MENU = ['Outerwear', 'Tops', 'Bottoms', 'Dresses', 'Footwear', 'Accessories'];

function GenderMenu({ gender }) {
  return (
    <div className="nav-item">
      <Link to={`/?gender=${gender}`}>{gender}</Link>
      <div className="mega-dropdown">
        {CATEGORY_MENU.map((c) => (
          <Link key={c} to={`/?gender=${gender}&category=${c}`}>{c}</Link>
        ))}
      </div>
    </div>
  );
}

export default function Header() {
  const { user, logout } = useAuth();
  const { count: cartCount, refresh: refreshCart } = useCart();
  const { count: wishCount, refresh: refreshWishlist } = useWishlist();
  const navigate = useNavigate();
  const [search, setSearch] = useState('');

  useEffect(() => { refreshCart(); refreshWishlist(); }, [user]);

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(search ? `/?q=${encodeURIComponent(search)}` : '/');
  };

  return (
    <header className="site-header">
      <div className="header-inner">
        <Link to="/" className="wordmark">
          RS FASHION CLUB
          <span className="wordmark-sub">considered wardrobe</span>
        </Link>

        <nav className="main-nav">
          <GenderMenu gender="Women" />
          <GenderMenu gender="Men" />
          <GenderMenu gender="Kids" />
        </nav>

        <form className="header-search" onSubmit={handleSearch}>
          <span className="search-icon">⌕</span>
          <input
            placeholder="Search for products, brands and more"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </form>

        <div className="header-actions">
          {user ? (
            <button className="header-action" onClick={() => { logout(); navigate('/'); }}>
              <span className="action-icon">⏻</span>
              Logout
            </button>
          ) : (
            <Link className="header-action" to="/login">
              <span className="action-icon">⛉</span>
              Profile
            </Link>
          )}
          <Link className="header-action" to="/wishlist">
            <span className="action-icon">♡</span>
            Wishlist
            {wishCount > 0 && <span className="badge-count">{wishCount}</span>}
          </Link>
          <Link className="header-action" to="/cart">
            <span className="action-icon">⛃</span>
            Bag
            {cartCount > 0 && <span className="badge-count">{cartCount}</span>}
          </Link>
        </div>
      </div>
    </header>
  );
}
