# RS Fashion Club — E-Fashion Platform

Full-stack e-commerce demo: React + Flask + SQL, JWT auth, cart, Stripe test-mode checkout,
and content-based product recommendations.

**Heads up:** this was built without the ability to run `npm install` / `pip install` in the
build environment (no network access there), so it's syntax-checked but not
end-to-end execution-tested. Budget 30-60 min to get it running locally and fix anything
minor that comes up — realistically expect small hiccups on first run.

---

## 1. Run locally

### Backend

**Delete the old database file before running** — the product schema changed again
(added brand, MRP/discount pricing, ratings, sizes, colors, wishlist):
`rm backend/efashion.db` (or delete `efashion.db` in File Explorer/Finder).

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env if you have a Stripe test key
python seed.py                  # creates + seeds the SQLite database
python app.py                   # runs on http://localhost:5000
```

No Stripe key? Leave `STRIPE_SECRET_KEY` blank in `.env` — checkout will auto-complete
in "demo mode" so the flow still works end-to-end without a real payment step.
To use real Stripe test mode: sign up free at stripe.com, grab the test **secret key**
(starts `sk_test_`) from the dashboard, and put it in `.env`.

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:5000" > .env
npm run dev                     # runs on http://localhost:5173
```

Open http://localhost:5173 — sign up, browse, add to cart, checkout.

---

## 2. Deploy live (for the interview)

### Backend → Render (free tier)

1. Push this whole project to a new GitHub repo.
2. Go to render.com → New → Web Service → connect your repo.
3. Root directory: `backend`
4. Build command: `pip install -r requirements.txt`
5. Start command: `python seed.py && gunicorn app:app`
6. Add environment variables: `JWT_SECRET_KEY` (any random string), `STRIPE_SECRET_KEY`
   (optional), `FRONTEND_URL` (you'll fill this in after step 3 below).
7. Deploy. Copy the resulting URL, e.g. `https://efashion-api.onrender.com`.

Note: Render's free tier uses ephemeral disk, so the SQLite file resets on redeploy —
fine for a demo/interview, not for production.

### Frontend → Vercel (free tier)

1. Go to vercel.com → New Project → import the same repo.
2. Root directory: `frontend`
3. Framework preset: Vite
4. Environment variable: `VITE_API_URL` = your Render backend URL from above.
5. Deploy. Copy the resulting URL, e.g. `https://maison-demo.vercel.app`.

### Connect them

Go back to Render → your backend service → environment variables → set
`FRONTEND_URL` to your Vercel URL → redeploy backend (needed for Stripe's
redirect-after-payment to land on the right site).

Total time: ~20-30 min once both accounts exist.

---

## 3. What's real vs. simplified (know this for the interview)

Be upfront about these if asked — it's more credible than pretending otherwise:

- **Auth**: real JWT-based auth, passwords hashed with Werkzeug, not a mock.
- **Cart & checkout**: real state in SQL. A payment method selection page (UPI / Card /
  Net Banking / Cash on Delivery) sits between Bag and order confirmation, Myntra-style.
  Cash on Delivery skips payment entirely and confirms the order directly. UPI, Card, and
  Net Banking are shown as separate options for the ordering flow, but there's no real UPI
  or net banking gateway behind them — all three route through the same Stripe test-mode
  checkout, since that's the only payment gateway wired up here.
- **Recommendations**: content-based filtering — scores other products by shared category
  + tag overlap. It's a real, explainable algorithm, not a trained ML recommender model.
  If asked "is this ML?" — answer honestly: it's a rule-based content filter, and say
  what you'd do to make it a learned model given more time (e.g. collaborative filtering
  from purchase history, or embeddings over product descriptions).
- **Product data**: placeholder products + Lorem-Picsum-style placeholder images, not a real
  catalog or real product photography.
- **UI/UX pattern**: styled after Myntra's browsing experience (sidebar filters, MRP/discount
  pricing, wishlist, sort bar) using original branding — not Myntra's logo or trademarked assets.
- **Payments**: Stripe test mode. Use card `4242 4242 4242 4242`, any future expiry, any CVC.

## 4. Project structure

```
backend/
  app.py            Flask app: auth, products, cart, checkout, recommendations
  seed.py           Seeds 20 placeholder fashion products
  requirements.txt
  Procfile           for Render/Railway
frontend/
  src/
    pages/           Home, ProductDetail, Login, Signup, Cart, Success
    context/         AuthContext, CartContext (React Context, no Redux needed)
    api.js           fetch wrapper for the backend
    index.css        design tokens + all styling
```
