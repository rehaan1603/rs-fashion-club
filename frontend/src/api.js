export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// Product images are either full external URLs (Pexels/LoremFlickr) or
// relative paths to images served by the Flask backend (/static/products/...).
// Relative paths need the backend's origin prefixed, since the frontend and
// backend run on different ports/domains.
export function resolveImageUrl(url) {
  if (!url) return url;
  return url.startsWith('http') ? url : `${API_URL}${url}`;
}

async function request(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(data.error || 'Something went wrong');
  }
  return data;
}

export const api = {
  signup: (body) => request('/api/auth/signup', { method: 'POST', body: JSON.stringify(body) }),
  login: (body) => request('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }),
  me: () => request('/api/auth/me'),

  getProducts: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return request(`/api/products${qs ? `?${qs}` : ''}`);
  },
  getProduct: (id) => request(`/api/products/${id}`),
  getRecommendations: (id) => request(`/api/products/${id}/recommendations`),
  getCategories: () => request('/api/categories'),
  getBrands: () => request('/api/brands'),
  getGenders: () => request('/api/genders'),

  getWishlist: () => request('/api/wishlist'),
  addToWishlist: (productId) => request('/api/wishlist', { method: 'POST', body: JSON.stringify({ product_id: productId }) }),
  removeFromWishlist: (productId) => request(`/api/wishlist/${productId}`, { method: 'DELETE' }),

  getCart: () => request('/api/cart'),
  addToCart: (productId, quantity = 1) =>
    request('/api/cart', { method: 'POST', body: JSON.stringify({ product_id: productId, quantity }) }),
  updateCartItem: (itemId, quantity) =>
    request(`/api/cart/${itemId}`, { method: 'PATCH', body: JSON.stringify({ quantity }) }),
  removeCartItem: (itemId) => request(`/api/cart/${itemId}`, { method: 'DELETE' }),

  checkout: (paymentMethod) => request('/api/checkout', { method: 'POST', body: JSON.stringify({ payment_method: paymentMethod }) }),
  confirmOrder: (orderId) => request(`/api/checkout/confirm/${orderId}`, { method: 'POST' }),
};
