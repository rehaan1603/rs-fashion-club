import { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../api';
import { useAuth } from './AuthContext';

const WishlistContext = createContext(null);

export function WishlistProvider({ children }) {
  const { user } = useAuth();
  const [items, setItems] = useState([]);

  const refresh = useCallback(async () => {
    if (!user) { setItems([]); return; }
    try {
      const data = await api.getWishlist();
      setItems(data);
    } catch {
      setItems([]);
    }
  }, [user]);

  const isWishlisted = (productId) => items.some((i) => i.product.id === productId);

  const toggle = async (productId) => {
    if (isWishlisted(productId)) {
      await api.removeFromWishlist(productId);
    } else {
      await api.addToWishlist(productId);
    }
    await refresh();
  };

  return (
    <WishlistContext.Provider value={{ items, count: items.length, refresh, isWishlisted, toggle }}>
      {children}
    </WishlistContext.Provider>
  );
}

export const useWishlist = () => useContext(WishlistContext);
