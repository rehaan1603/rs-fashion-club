"""Seed the database with a Myntra-style Men's / Women's / Kids' fashion catalog:
brands, MRP + discounted price, star ratings, sizes, colors.
Images come from LoremFlickr (real Creative Commons photos from Flickr, tag-matched).

Run with: python seed.py
"""
import random
from app import app, db, Product

random.seed(42)


def img(tags, lock):
    # /all forces LoremFlickr to match ALL tags together (AND), not just any one of them (OR).
    # Without /all, a 3-tag query like "men,jacket,fashion" matches anything tagged
    # just "fashion" alone, which is why images were coming back unrelated.
    return f"https://loremflickr.com/600/800/{tags}/all?lock={lock}"


def pexels(photo_id):
    # Hand-verified real Pexels photos (individually checked, not tag-matched blindly)
    # for the highest-visibility "hero" products.
    return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w=600"


def local(filename):
    # Real photos uploaded by the user, served from Flask's /static folder.
    return f"/static/products/{filename}"


HERO_IMAGES = {
    "Oxford Wool Overcoat": pexels(11354217),
    "Denim Trucker Jacket": pexels(30395493),
    "Selvedge Denim Jeans": pexels(2815417),
    "Wrap Midi Dress": pexels(4352249),
    "Leather Ankle Boots": pexels(6591577),
    "Hooded Rain Jacket": pexels(14753791),
    "Party Tutu Dress": pexels(2607045),

    # --- Overrides with user-uploaded real product photos ---
    # (Only used where the photo's actual garment genuinely matches the product;
    # descriptions/colors below were adjusted to match what's really in each photo.)
    "Leather Oxford Brogues": local("men-oxford-brogues.jpg"),
    "Minimal Court Sneakers": local("men-campus-sneaker.webp"),
    "Tapered Wool Trousers": local("men-khaki-trousers.jpg"),
    "Cotton Poplin Shirt": local("women-white-shirt.jpg"),
    "Floral Print Blouse": local("women-floral-blouse-bag.webp"),
    "Button-Front Shirt": local("kids-toddler-teal-shirt.jpg"),

    # --- New arrivals ---
    "Striped Casual Shirt": local("men-striped-shirt.jpg"),
    "Charcoal Gingham Shirt": local("men-gingham-shirt.jpg"),
    "Windowpane Check Shirt": local("men-windowpane-shirt.jpg"),
    "Green Plaid Overshirt": local("men-green-plaid-overshirt.jpg"),
    "Retro Two-Tone Sneakers": local("men-uspa-cream-sneaker.jpg"),
    "Canvas Trainer Sneakers": local("men-uspa-navy-sneaker.jpg"),
    "Relaxed Navy Trousers": local("men-navy-trousers-side.jpg"),
    "Wide-Leg Linen Trousers": local("women-linen-widepants-front.jpg"),
    "Floral Print Co-ord Set": local("women-floral-coord-set.jpg"),
    "Abstract Print Resort Shirt": local("women-abstract-print-shirt.jpg"),
    "Pearl Hair Clip Set": local("women-pearl-hairclips.jpg"),
    "Cotton Two-Piece Set": local("kids-toddler-white-linen-set.jpg"),
}


def price(mrp, discount_pct):
    return round(mrp * (1 - discount_pct / 100), 2)


BRANDS_MEN = ["URBAN THREAD", "STONE & CO", "FIELDNOTE", "ARCH STUDIO", "KIN"]
BRANDS_WOMEN = ["LUNE", "NOVA WEAR", "ARCH STUDIO", "KIN", "STONE & CO"]
BRANDS_KIDS = ["PEBBLE KIDS", "LITTLE ATLAS", "KIN JUNIOR"]

SIZES_CLOTHING = "XS,S,M,L,XL,XXL"
SIZES_SHOES_MEN = "7,8,9,10,11"
SIZES_SHOES_WOMEN = "5,6,7,8,9"
SIZES_SHOES_KIDS = "10,11,12,13,1"
SIZES_KIDS_CLOTHING = "2-3Y,4-5Y,6-7Y,8-9Y,10-11Y"
SIZES_ONE = "One Size"


def rating():
    return round(random.uniform(3.6, 4.8), 1), random.randint(40, 3200)


def row(name, brand, desc, mrp, discount, category, gender, tags, sizes, color, img_tags, lock, stock=None):
    r, rc = rating()
    image_url = HERO_IMAGES.get(name, img(img_tags, lock))
    return dict(
        name=name, brand=brand, description=desc,
        price=price(mrp, discount), original_price=mrp,
        rating=r, rating_count=rc,
        category=category, gender=gender, tags=tags,
        sizes=sizes, color=color,
        image_url=image_url,
        stock=stock if stock is not None else random.randint(4, 60),
    )


PRODUCTS = [
    # ---------------- MEN ----------------
    row("Oxford Wool Overcoat", "STONE & CO", "Tailored double-breasted overcoat in charcoal wool blend.", 8999, 30, "Outerwear", "Men", "wool,formal,winter", SIZES_CLOTHING, "Charcoal", "men,overcoat", 101),
    row("Quilted Field Jacket", "FIELDNOTE", "Lightweight quilted jacket with corduroy collar.", 4499, 25, "Outerwear", "Men", "casual,autumn,quilted", SIZES_CLOTHING, "Olive", "men,jacket", 102),
    row("Denim Trucker Jacket", "URBAN THREAD", "Classic straight-fit denim jacket, stonewashed.", 3299, 20, "Outerwear", "Men", "denim,casual", SIZES_CLOTHING, "Blue", "denim,jacket", 103),
    row("Merino Crew Sweater", "KIN", "Fine-gauge merino wool sweater.", 3499, 35, "Tops", "Men", "wool,knit,winter", SIZES_CLOTHING, "Forest Green", "men,sweater", 104),
    row("Linen Relaxed Shirt", "ARCH STUDIO", "Breathable linen shirt with mother-of-pearl buttons.", 2599, 20, "Tops", "Men", "linen,summer,casual", SIZES_CLOTHING, "White", "men,shirt", 105),
    row("Ribbed Turtleneck", "KIN", "Slim ribbed turtleneck in brushed cotton.", 1999, 15, "Tops", "Men", "cotton,winter,layering", SIZES_CLOTHING, "Black", "men,turtleneck", 106),
    row("Graphic Tee", "URBAN THREAD", "100% organic cotton tee with minimalist print.", 1299, 40, "Tops", "Men", "cotton,casual,streetwear", SIZES_CLOTHING, "White", "men,tshirt", 107),
    row("Tapered Wool Trousers", "STONE & CO", "Tailored trousers in khaki cotton-blend twill.", 4299, 25, "Bottoms", "Men", "formal", SIZES_CLOTHING, "Khaki", "men,trousers", 108),
    row("Selvedge Denim Jeans", "URBAN THREAD", "Straight-fit selvedge denim, raw indigo.", 4999, 30, "Bottoms", "Men", "denim,casual", SIZES_CLOTHING, "Indigo", "men,jeans", 109),
    row("Cargo Utility Pants", "FIELDNOTE", "Relaxed cargo pants with articulated knees.", 2999, 20, "Bottoms", "Men", "casual,streetwear,utility", SIZES_CLOTHING, "Khaki", "men,cargo", 110),
    row("Leather Oxford Brogues", "STONE & CO", "Classic wingtip brogue oxfords in black leather.", 6999, 25, "Footwear", "Men", "leather,formal,brogues", SIZES_SHOES_MEN, "Black", "men,boots", 111),
    row("Minimal Court Sneakers", "ARCH STUDIO", "Grey and white low-top sneakers with a cushioned sole.", 3999, 30, "Footwear", "Men", "casual,sneakers", SIZES_SHOES_MEN, "Grey/White", "men,sneakers", 112),
    row("Suede Loafers", "KIN", "Penny loafers in soft suede.", 4499, 20, "Footwear", "Men", "suede,formal,loafers", SIZES_SHOES_MEN, "Brown", "men,loafers", 113),
    row("Leather Belt", "STONE & CO", "Full-grain leather belt with brushed brass buckle.", 1499, 30, "Accessories", "Men", "leather,formal", SIZES_ONE, "Black", "men,belt", 114),
    row("Wool Scarf", "KIN", "Herringbone wool scarf.", 1799, 25, "Accessories", "Men", "wool,winter,scarf", SIZES_ONE, "Forest Green", "men,scarf", 115),
    row("Aviator Sunglasses", "ARCH STUDIO", "Classic aviator frames with polarized lenses.", 2499, 35, "Accessories", "Men", "sunglasses,summer", SIZES_ONE, "Gold", "men,sunglasses", 116),

    # --- New arrivals from real product photos ---
    row("Striped Casual Shirt", "URBAN THREAD", "Long-sleeve striped shirt in soft cotton weave.", 2299, 20, "Tops", "Men", "cotton,casual,stripe", SIZES_CLOTHING, "Grey/Black Stripe", "men,shirt", 118),
    row("Charcoal Gingham Shirt", "ARCH STUDIO", "Brushed cotton gingham check shirt.", 2499, 25, "Tops", "Men", "cotton,casual,check", SIZES_CLOTHING, "Charcoal Gingham", "men,shirt", 119),
    row("Windowpane Check Shirt", "KIN", "Cotton flannel shirt in a soft windowpane check.", 2399, 20, "Tops", "Men", "cotton,casual,check", SIZES_CLOTHING, "Cream/Grey Check", "men,shirt", 120),
    row("Green Plaid Overshirt", "FIELDNOTE", "Heavyweight flannel overshirt in a bold plaid check.", 3299, 25, "Outerwear", "Men", "flannel,casual,plaid", SIZES_CLOTHING, "Green/Cream Plaid", "men,jacket", 121),
    row("Retro Two-Tone Sneakers", "URBAN THREAD", "Retro-style lace-up sneakers with contrast side stripes.", 3499, 30, "Footwear", "Men", "casual,sneakers,retro", SIZES_SHOES_MEN, "Cream/Tan", "men,sneakers", 122),
    row("Canvas Trainer Sneakers", "STONE & CO", "Low-top canvas trainers with contrast heel tab.", 2999, 25, "Footwear", "Men", "canvas,casual,sneakers", SIZES_SHOES_MEN, "Navy/Tan", "men,sneakers", 123),
    row("Relaxed Navy Trousers", "ARCH STUDIO", "Straight-fit tailored trousers in navy cotton twill.", 2999, 20, "Bottoms", "Men", "formal,casual", SIZES_CLOTHING, "Navy", "men,trousers", 124),

    # ---------------- WOMEN ----------------
    row("Tailored Wool Blazer", "NOVA WEAR", "Structured single-breasted blazer in camel wool.", 7999, 30, "Outerwear", "Women", "wool,formal,camel", SIZES_CLOTHING, "Camel", "women,blazer", 201),
    row("Belted Trench Coat", "LUNE", "Classic double-breasted trench in water-resistant cotton.", 8499, 25, "Outerwear", "Women", "cotton,formal,trench", SIZES_CLOTHING, "Beige", "women,trenchcoat", 202),
    row("Quilted Puffer Jacket", "ARCH STUDIO", "Cropped puffer with recycled down fill.", 5499, 35, "Outerwear", "Women", "casual,winter,puffer", SIZES_CLOTHING, "Black", "women,jacket", 203),
    row("Floral Print Blouse", "LUNE", "Fluid floral-print blouse with a soft draped collar.", 4299, 20, "Tops", "Women", "formal,elegant,floral", SIZES_CLOTHING, "Cream Floral", "women,blouse", 204),
    row("Ribbed Knit Sweater", "KIN", "Fitted ribbed sweater in soft merino wool.", 3299, 25, "Tops", "Women", "wool,knit,winter", SIZES_CLOTHING, "Rust", "women,sweater", 205),
    row("Cotton Poplin Shirt", "NOVA WEAR", "Crisp white poplin shirt with a relaxed fit.", 2799, 20, "Tops", "Women", "cotton,formal,white", SIZES_CLOTHING, "White", "women,shirt", 206),
    row("Pleated Midi Skirt", "LUNE", "Flowing pleated skirt in satin finish.", 3699, 30, "Bottoms", "Women", "elegant,satin,skirt", SIZES_CLOTHING, "Emerald", "women,skirt", 207),
    row("High-Rise Wide Jeans", "URBAN THREAD", "Wide-leg jeans in mid-wash denim.", 4299, 25, "Bottoms", "Women", "denim,casual", SIZES_CLOTHING, "Blue", "women,jeans", 208),
    row("Tailored Trousers", "NOVA WEAR", "Straight-leg tailored trousers.", 4499, 20, "Bottoms", "Women", "formal,tailored", SIZES_CLOTHING, "Charcoal", "women,trousers", 209),
    row("Wrap Midi Dress", "LUNE", "Floral wrap dress in lightweight viscose.", 4799, 30, "Dresses", "Women", "dress,elegant,floral", SIZES_CLOTHING, "Floral Print", "women,dress", 210),
    row("Slip Dress", "NOVA WEAR", "Bias-cut satin slip dress.", 3999, 25, "Dresses", "Women", "dress,satin,elegant", SIZES_CLOTHING, "Champagne", "women,gown", 211),
    row("Leather Ankle Boots", "STONE & CO", "Block-heel ankle boots in soft leather.", 6499, 30, "Footwear", "Women", "leather,boots", SIZES_SHOES_WOMEN, "Black", "women,boots", 212),
    row("Ballet Flats", "ARCH STUDIO", "Classic leather ballet flats.", 2999, 20, "Footwear", "Women", "leather,flats,casual", SIZES_SHOES_WOMEN, "Nude", "women,flats", 213),
    row("Strappy Block Heels", "LUNE", "Suede block heels with ankle strap.", 4299, 25, "Footwear", "Women", "suede,heels,elegant", SIZES_SHOES_WOMEN, "Black", "women,heels", 214),
    row("Leather Crossbody Bag", "KIN", "Compact crossbody bag in vegetable-tanned leather.", 4999, 30, "Accessories", "Women", "leather,bag", SIZES_ONE, "Tan", "women,handbag", 215),
    row("Silver Chain Necklace", "NOVA WEAR", "Minimalist sterling silver chain, adjustable.", 2199, 20, "Accessories", "Women", "silver,jewelry", SIZES_ONE, "Silver", "women,necklace", 216),
    row("Silk Scarf", "LUNE", "Hand-rolled silk scarf with abstract print.", 2499, 25, "Accessories", "Women", "silk,scarf", SIZES_ONE, "Multi", "women,scarf", 217),

    # --- New arrivals from real product photos ---
    row("Wide-Leg Linen Trousers", "LUNE", "High-rise wide-leg trousers in soft linen blend.", 3299, 20, "Bottoms", "Women", "linen,casual", SIZES_CLOTHING, "Beige", "women,trousers", 218),
    row("Floral Print Co-ord Set", "NOVA WEAR", "Shawl-collar vest and matching trousers in a floral jacquard print.", 6999, 30, "Outerwear", "Women", "elegant,floral,coord", SIZES_CLOTHING, "Cream Floral", "women,dress", 219),
    row("Abstract Print Resort Shirt", "KIN", "Relaxed short-sleeve shirt in an abstract watercolor print.", 2799, 20, "Tops", "Women", "casual,print", SIZES_CLOTHING, "Brown/Black Abstract", "women,shirt", 220),
    row("Pearl Hair Clip Set", "NOVA WEAR", "Set of pearl and crystal hair clips.", 899, 25, "Accessories", "Women", "hair,accessory", SIZES_ONE, "Pearl/Gold", "women,jewelry", 221),

    # ---------------- KIDS ----------------
    row("Hooded Rain Jacket", "PEBBLE KIDS", "Waterproof hooded jacket in bright yellow.", 2199, 30, "Outerwear", "Kids", "waterproof,casual", SIZES_KIDS_CLOTHING, "Yellow", "kids,jacket", 301),
    row("Puffer Vest", "LITTLE ATLAS", "Lightweight puffer vest for layering.", 1799, 25, "Outerwear", "Kids", "casual,winter", SIZES_KIDS_CLOTHING, "Red", "kids,vest", 302),
    row("Striped Cotton Tee", "PEBBLE KIDS", "Soft organic cotton tee with classic stripes.", 899, 20, "Tops", "Kids", "cotton,casual", SIZES_KIDS_CLOTHING, "Navy Stripe", "kids,tshirt", 303),
    row("Button-Front Shirt", "KIN JUNIOR", "Soft cotton button-front shirt with a playful bear patch.", 1499, 25, "Tops", "Kids", "cotton,casual", SIZES_KIDS_CLOTHING, "Teal", "kids,cardigan", 304),
    row("Denim Overalls", "LITTLE ATLAS", "Classic denim overalls with adjustable straps.", 1999, 20, "Bottoms", "Kids", "denim,casual", SIZES_KIDS_CLOTHING, "Blue", "kids,overalls", 305),
    row("Jogger Pants", "PEBBLE KIDS", "Soft fleece joggers with elastic cuffs.", 1199, 30, "Bottoms", "Kids", "casual,comfortable", SIZES_KIDS_CLOTHING, "Grey", "kids,pants", 306),
    row("Party Tutu Dress", "LITTLE ATLAS", "Tulle party dress with satin sash.", 2199, 25, "Dresses", "Kids", "dress,party,tulle", SIZES_KIDS_CLOTHING, "Pink", "kids,tutu", 307),
    row("Everyday Cotton Dress", "KIN JUNIOR", "Simple A-line dress in soft cotton jersey.", 1599, 20, "Dresses", "Kids", "dress,cotton,casual", SIZES_KIDS_CLOTHING, "Sky Blue", "kids,dress", 308),
    row("Canvas Sneakers", "PEBBLE KIDS", "Easy slip-on canvas sneakers with velcro strap.", 1399, 25, "Footwear", "Kids", "canvas,casual,sneakers", SIZES_SHOES_KIDS, "White", "kids,sneakers", 309),
    row("Rain Boots", "LITTLE ATLAS", "Waterproof rubber rain boots in bright print.", 1299, 20, "Footwear", "Kids", "waterproof,boots", SIZES_SHOES_KIDS, "Yellow Print", "kids,rainboots", 310),
    row("Knit Beanie", "KIN JUNIOR", "Soft knit beanie with pom-pom.", 699, 25, "Accessories", "Kids", "knit,winter", SIZES_ONE, "Red", "kids,beanie", 311),
    row("Backpack", "PEBBLE KIDS", "Durable canvas backpack, kid-sized.", 1599, 20, "Accessories", "Kids", "canvas,school", SIZES_ONE, "Multi", "kids,backpack", 312),

    # --- New arrivals from real product photos ---
    row("Cotton Two-Piece Set", "LITTLE ATLAS", "Collared shirt and trousers set in soft cotton, with sun hat.", 1899, 20, "Tops", "Kids", "cotton,casual", SIZES_KIDS_CLOTHING, "White", "kids,tshirt", 313),
]


def run():
    with app.app_context():
        db.create_all()
        existing = Product.query.count()
        if existing == len(PRODUCTS):
            print("Products already seeded, skipping.")
            return
        Product.query.delete()
        for p in PRODUCTS:
            db.session.add(Product(**p))
        db.session.commit()
        print(f"Seeded {len(PRODUCTS)} products across Men / Women / Kids.")


if __name__ == "__main__":
    run()
