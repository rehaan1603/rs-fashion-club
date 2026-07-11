import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { api } from '../api';
import ProductCard from '../components/ProductCard';
import FilterSidebar from '../components/FilterSidebar';

export default function Home() {
  const [searchParams, setSearchParams] = useSearchParams();
  const gender = searchParams.get('gender') || 'All';
  const q = searchParams.get('q') || '';

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [brands, setBrands] = useState([]);
  const [loading, setLoading] = useState(true);

  const [activeCategory, setActiveCategory] = useState(searchParams.get('category') || 'all');
  const [activeBrands, setActiveBrands] = useState([]);
  const [activePriceRange, setActivePriceRange] = useState(null);
  const [activeDiscount, setActiveDiscount] = useState(null);
  const [sort, setSort] = useState('');

  useEffect(() => {
    api.getCategories().then(setCategories).catch(() => {});
    api.getBrands().then(setBrands).catch(() => {});
  }, []);

  useEffect(() => {
    setActiveCategory('all');
    setActiveBrands([]);
    setActivePriceRange(null);
    setActiveDiscount(null);
  }, [gender]);

  useEffect(() => {
    setLoading(true);
    const params = {};
    if (gender !== 'All') params.gender = gender;
    if (activeCategory !== 'all') params.category = activeCategory;
    if (q) params.q = q;
    if (activePriceRange) {
      params.min_price = activePriceRange.min;
      params.max_price = activePriceRange.max;
    }
    if (activeDiscount) params.min_discount = activeDiscount;
    if (sort) params.sort = sort;

    api.getProducts(params).then((data) => {
      let results = data;
      if (activeBrands.length > 0) {
        results = results.filter((p) => activeBrands.includes(p.brand));
      }
      setProducts(results);
    }).finally(() => setLoading(false));
  }, [gender, activeCategory, q, activePriceRange, activeDiscount, sort, activeBrands]);

  const toggleBrand = (b) => {
    setActiveBrands((prev) => prev.includes(b) ? prev.filter((x) => x !== b) : [...prev, b]);
  };

  const clearAll = () => {
    setActiveCategory('all');
    setActiveBrands([]);
    setActivePriceRange(null);
    setActiveDiscount(null);
  };

  const heroCopy = q
    ? { title: `Results for "${q}"`, sub: `${products.length} items found` }
    : {
        All: { title: 'New Arrivals — Autumn Collection', sub: 'A considered edit of wardrobe staples in natural fabrics.' },
        Women: { title: "Women's Edit", sub: 'Tailored pieces for every day.' },
        Men: { title: "Men's Edit", sub: 'Sharp lines, lasting fabric.' },
        Kids: { title: "Kids' Edit", sub: 'Made to play, built to last.' },
      }[gender];

  return (
    <>
      <div className="hero-strip">
        <h1>{heroCopy.title}</h1>
        <p>{heroCopy.sub}</p>
      </div>

      <div className="shop-layout">
        <FilterSidebar
          categories={categories}
          brands={brands}
          activeCategory={activeCategory}
          setActiveCategory={setActiveCategory}
          activeBrands={activeBrands}
          toggleBrand={toggleBrand}
          activePriceRange={activePriceRange}
          setActivePriceRange={setActivePriceRange}
          activeDiscount={activeDiscount}
          setActiveDiscount={setActiveDiscount}
          onClear={clearAll}
        />

        <div>
          <div className="sort-bar">
            <div className="sort-count">
              <strong>{products.length}</strong> items
            </div>
            <div className="sort-select-wrap">
              <label>Sort by</label>
              <select value={sort} onChange={(e) => setSort(e.target.value)}>
                <option value="">Recommended</option>
                <option value="newest">What's New</option>
                <option value="price_asc">Price: Low to High</option>
                <option value="price_desc">Price: High to Low</option>
                <option value="rating">Customer Rating</option>
              </select>
            </div>
          </div>

          {loading ? (
            <div className="product-grid">
              {Array.from({ length: 8 }).map((_, i) => (
                <div className="skeleton-card" key={i}>
                  <div className="skeleton-img" />
                  <div className="skeleton-line w-60" />
                  <div className="skeleton-line w-40" />
                  <div className="skeleton-line w-30" />
                </div>
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="empty-state"><p>No pieces match these filters.</p></div>
          ) : (
            <div className="product-grid">
              {products.map((p, i) => <ProductCard key={p.id} product={p} index={i} />)}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
