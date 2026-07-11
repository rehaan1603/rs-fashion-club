import { createContext, useContext, useState, useCallback } from 'react';
import { api } from '../api';
import { useAuth } from './AuthContext';

const CartContext = createContext(null);

export function CartProvider({ children }) {
  const { user } = useAuth();
  const [items, setItems] = useState([]);

  const refresh = useCallback(async () => {
    if (!user) { setItems([]); return; }
    try {
      const data = await api.getCart();
      setItems(data);
    } catch {
      setItems([]);
    }
  }, [user]);

  const addToCart = async (productId, quantity = 1) => {
    await api.addToCart(productId, quantity);
    await refresh();
  };

  const updateQuantity = async (itemId, quantity) => {
    await api.updateCartItem(itemId, quantity);
    await refresh();
  };

  const removeItem = async (itemId) => {
    await api.removeCartItem(itemId);
    await refresh();
  };

  const count = items.reduce((sum, i) => sum + i.quantity, 0);
  const total = items.reduce((sum, i) => sum + i.quantity * i.product.price, 0);
  const mrpTotal = items.reduce((sum, i) => sum + i.quantity * (i.product.original_price || i.product.price), 0);
  const discountTotal = mrpTotal - total;

  return (
    <CartContext.Provider value={{ items, count, total, mrpTotal, discountTotal, refresh, addToCart, updateQuantity, removeItem }}>
      {children}
    </CartContext.Provider>
  );
}

export const useCart = () => useContext(CartContext);
