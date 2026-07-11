const PRICE_RANGES = [
  { label: 'Under ₹1,500', min: 0, max: 1500 },
  { label: '₹1,500 - ₹3,500', min: 1500, max: 3500 },
  { label: '₹3,500 - ₹6,000', min: 3500, max: 6000 },
  { label: 'Above ₹6,000', min: 6000, max: 999999 },
];

const DISCOUNT_RANGES = [
  { label: '10% and above', value: 10 },
  { label: '20% and above', value: 20 },
  { label: '30% and above', value: 30 },
];

export default function FilterSidebar({
  categories, brands,
  activeCategory, setActiveCategory,
  activeBrands, toggleBrand,
  activePriceRange, setActivePriceRange,
  activeDiscount, setActiveDiscount,
  onClear,
}) {
  return (
    <aside className="filter-sidebar">
      <div className="filter-header">
        FILTERS
        <button className="filter-clear" onClick={onClear}>Clear all</button>
      </div>

      <div className="filter-group">
        <div className="filter-group-title">Category</div>
        <label className={`filter-checkbox-row ${activeCategory === 'all' ? 'active-label' : ''}`}>
          <input type="radio" checked={activeCategory === 'all'} onChange={() => setActiveCategory('all')} />
          All
        </label>
        {categories.map((c) => (
          <label key={c} className={`filter-checkbox-row ${activeCategory === c ? 'active-label' : ''}`}>
            <input type="radio" checked={activeCategory === c} onChange={() => setActiveCategory(c)} />
            {c}
          </label>
        ))}
      </div>

      <div className="filter-group">
        <div className="filter-group-title">Price</div>
        {PRICE_RANGES.map((r) => (
          <label key={r.label} className={`filter-checkbox-row ${activePriceRange?.label === r.label ? 'active-label' : ''}`}>
            <input
              type="radio"
              checked={activePriceRange?.label === r.label}
              onChange={() => setActivePriceRange(activePriceRange?.label === r.label ? null : r)}
            />
            {r.label}
          </label>
        ))}
      </div>

      <div className="filter-group">
        <div className="filter-group-title">Brand</div>
        {brands.map((b) => (
          <label key={b} className={`filter-checkbox-row ${activeBrands.includes(b) ? 'active-label' : ''}`}>
            <input type="checkbox" checked={activeBrands.includes(b)} onChange={() => toggleBrand(b)} />
            {b}
          </label>
        ))}
      </div>

      <div className="filter-group">
        <div className="filter-group-title">Discount Range</div>
        {DISCOUNT_RANGES.map((d) => (
          <label key={d.value} className={`filter-checkbox-row ${activeDiscount === d.value ? 'active-label' : ''}`}>
            <input
              type="radio"
              checked={activeDiscount === d.value}
              onChange={() => setActiveDiscount(activeDiscount === d.value ? null : d.value)}
            />
            {d.label}
          </label>
        ))}
      </div>
    </aside>
  );
}
