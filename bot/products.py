"""Product catalog for premium content and monetization."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProductType(str, Enum):
    """Types of purchasable products."""
    
    ROUTE_PACK = "route_pack"       # Unlocks full route chapters
    SCENE = "scene"                  # Single premium scene
    ITEM = "item"                    # Gameplay boost or lore item
    COSMETIC = "cosmetic"            # Titles, badges, etc.
    BUNDLE = "bundle"                # Discounted collection
    ENERGY = "energy"                # Night cycles refill
    EVENT = "event"                  # Limited-time content


@dataclass(frozen=True)
class Product:
    """A purchasable product definition."""
    
    id: str
    name: str
    description: str
    product_type: ProductType
    price_cents: int  # Price in cents (USD)
    flag_key: str  # Key stored in user state when purchased
    includes: tuple[str, ...] = ()  # For bundles: product IDs included
    route: str = ""  # Which character route this belongs to
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.product_type.value,
            "price_cents": self.price_cents,
            "route": self.route,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# CALVIN PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

CALVIN_S1 = Product(
    id="CALVIN_S1",
    name="Glass Towers: Extended Route",
    description=(
        "Unlock the doors Calvin keeps closed to everyone else. "
        "Follow him into internal experiments, power plays, and endings "
        "the tower would rather delete."
    ),
    product_type=ProductType.ROUTE_PACK,
    price_cents=499,
    flag_key="has_pack_calvin_s1",
    route="calvin",
)

CALVIN_SCENE1 = Product(
    id="CALVIN_SCENE1",
    name="Midnight Terms",
    description=(
        "See the moment Calvin stops sounding like a boss "
        "and starts sounding like a sin."
    ),
    product_type=ProductType.SCENE,
    price_cents=199,
    flag_key="has_item_calvin_scene1",
    route="calvin",
)

CALVIN_ACCESS = Product(
    id="CALVIN_ACCESS",
    name="Emotional Access Override",
    description=(
        "Become more than another datapoint. Give Calvin the tools to see "
        "every spike in your system—and be rewarded for every reaction."
    ),
    product_type=ProductType.ITEM,
    price_cents=149,
    flag_key="has_item_calvin_access",
    route="calvin",
)

CALVIN_FASTPASS = Product(
    id="CALVIN_FASTPASS",
    name="Tower Fast-Track",
    description=(
        "In Echocity, people like you don't do their own paperwork. "
        "Buy your way past the boring parts and straight into the dangerous ones."
    ),
    product_type=ProductType.ITEM,
    price_cents=249,
    flag_key="has_item_calvin_fastpass",
    route="calvin",
)

CALVIN_TITLE = Product(
    id="CALVIN_TITLE",
    name="Calvin's Experiment",
    description=(
        "Wear it proudly—or as a warning. Either way, everyone will know "
        "who's been in the tower too long."
    ),
    product_type=ProductType.COSMETIC,
    price_cents=99,
    flag_key="has_title_calvin_experiment",
    route="calvin",
)

CALVIN_BUNDLE1 = Product(
    id="CALVIN_BUNDLE1",
    name="Tower & Temptation Pack",
    description=(
        "Not just the keys to his tower, but the keyhole view into "
        "what he won't show anyone else. Includes Extended Route, "
        "Midnight Terms scene, and exclusive title."
    ),
    product_type=ProductType.BUNDLE,
    price_cents=699,  # Discount from 499 + 199 + 99 = 797
    flag_key="has_bundle_calvin1",
    includes=("CALVIN_S1", "CALVIN_SCENE1", "CALVIN_TITLE"),
    route="calvin",
)

# ═══════════════════════════════════════════════════════════════════════════════
# JACKSON PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

JACKSON_S1 = Product(
    id="JACKSON_S1",
    name="Deeper Debts: Extended Route",
    description=(
        "You've had your first night on the Verge. You've seen what Jackson does "
        "for a living—and what it does to him. Meet the people who hold his leash, "
        "decide whether to pay off his debts, run with him, or sell him out."
    ),
    product_type=ProductType.ROUTE_PACK,
    price_cents=499,
    flag_key="has_pack_jackson_s1",
    route="jackson",
)

JACKSON_SCENE1 = Product(
    id="JACKSON_SCENE1",
    name="Back-Room Confession",
    description=(
        "See the rare moment when Jackson stops performing and tells you "
        "exactly what's breaking him."
    ),
    product_type=ProductType.SCENE,
    price_cents=199,
    flag_key="has_item_jackson_scene1",
    route="jackson",
)

JACKSON_ACCESS = Product(
    id="JACKSON_ACCESS",
    name="Shadow Link",
    description=(
        "Let Jackson piggyback on your clearance. He keeps you off the worst "
        "radars; you keep him out of the worst trouble. Increased risk of "
        "getting flagged by AmourCorp."
    ),
    product_type=ProductType.ITEM,
    price_cents=149,
    flag_key="has_item_jackson_access",
    route="jackson",
)

JACKSON_FASTPASS = Product(
    id="JACKSON_FASTPASS",
    name="Shortcut Through the Verge",
    description=(
        "Skip the grindy undercity errands. Pay off locals, bribe the right people, "
        "and get straight to the dangerous parts."
    ),
    product_type=ProductType.ITEM,
    price_cents=249,
    flag_key="has_item_jackson_fastpass",
    route="jackson",
)

JACKSON_TITLE = Product(
    id="JACKSON_TITLE",
    name="Verge Addict",
    description=(
        "Admit what everyone down here already knows: you keep coming back. "
        "Displayed on your profile and chapter summaries."
    ),
    product_type=ProductType.COSMETIC,
    price_cents=99,
    flag_key="has_title_verge_addict",
    route="jackson",
)

JACKSON_BUNDLE1 = Product(
    id="JACKSON_BUNDLE1",
    name="Tracks & Trouble Pack",
    description=(
        "Everything you need to stop pretending Jackson is just a phase. "
        "Includes Extended Route, Back-Room Confession, and exclusive title."
    ),
    product_type=ProductType.BUNDLE,
    price_cents=699,
    flag_key="has_bundle_jackson1",
    includes=("JACKSON_S1", "JACKSON_SCENE1", "JACKSON_TITLE"),
    route="jackson",
)

JACKSON_EVENT = Product(
    id="JACKSON_EVENT",
    name="Lockdown Night",
    description=(
        "One night where the district goes into lockdown. Raids, betrayals, "
        "and a choice: leave with him or don't."
    ),
    product_type=ProductType.EVENT,
    price_cents=299,
    flag_key="has_event_jackson_lockdown",
    route="jackson",
)

# ═══════════════════════════════════════════════════════════════════════════════
# COLE PRODUCTS
# ═══════════════════════════════════════════════════════════════════════════════

COLE_S1 = Product(
    id="COLE_S1",
    name="Ghost in the Network: Extended Route",
    description=(
        "Calvin wants your metrics. Jackson wants your nights. "
        "Cole wants your *pattern*. Unlock this route to see the logs "
        "AmourCorp keeps on you, break or reinforce the lives you've built, "
        "and decide whether you're a person with a past—or a story you rewrote last night."
    ),
    product_type=ProductType.ROUTE_PACK,
    price_cents=499,
    flag_key="has_pack_cole_s1",
    route="cole",
)

COLE_SCENE1 = Product(
    id="COLE_SCENE1",
    name="Deep Dive: Your Archive",
    description=(
        "Cole can show you everything the system has ever recorded about you: "
        "every crush, every abandoned chat, every time your heart spiked for the wrong person. "
        "This premium scene doesn't just reveal lore—it lets Cole comment on the routes "
        "and packs you've chosen, and what kind of player that makes you."
    ),
    product_type=ProductType.SCENE,
    price_cents=249,
    flag_key="has_item_cole_scene1",
    route="cole",
)

COLE_MASK = Product(
    id="COLE_MASK",
    name="Anonymity Mask",
    description=(
        "Tired of being a product? Buy yourself a little static. "
        "Your name appears glitched in profile, and some NPCs can't fully read you."
    ),
    product_type=ProductType.COSMETIC,
    price_cents=149,
    flag_key="has_item_cole_mask",
    route="cole",
)

COLE_OVERRIDE = Product(
    id="COLE_OVERRIDE",
    name="Profile Rewrite",
    description=(
        "We can't change what you felt. But we can change what the records say you did. "
        "One-use item that lets you reroll a key stat or flip a major story flag."
    ),
    product_type=ProductType.ITEM,
    price_cents=349,
    flag_key="has_item_cole_override",
    route="cole",
)

COLE_TITLE = Product(
    id="COLE_TITLE",
    name="Heartline Glitch",
    description=(
        "Cole left a permanent anomaly in your emotional record. "
        "Wear the proof on your profile."
    ),
    product_type=ProductType.COSMETIC,
    price_cents=99,
    flag_key="has_title_heartline_glitch",
    route="cole",
)

COLE_BUNDLE1 = Product(
    id="COLE_BUNDLE1",
    name="Static & Ghosts Pack",
    description=(
        "Why buy one loophole when you can buy the whole breach? "
        "Includes Extended Route, Archive Deep Dive, and Anonymity Mask."
    ),
    product_type=ProductType.BUNDLE,
    price_cents=749,  # Discount from 499 + 249 + 149 = 897
    flag_key="has_bundle_cole1",
    includes=("COLE_S1", "COLE_SCENE1", "COLE_MASK"),
    route="cole",
)

# ═══════════════════════════════════════════════════════════════════════════════
# ENERGY / NIGHT CYCLES
# ═══════════════════════════════════════════════════════════════════════════════

ENERGY_10 = Product(
    id="ENERGY_10",
    name="Night Cycles (x10)",
    description=(
        "You're not supposed to run at this intensity forever. "
        "But who listens to warnings?"
    ),
    product_type=ProductType.ENERGY,
    price_cents=99,
    flag_key="",  # Energy is added directly to stats
    route="",
)

# ═══════════════════════════════════════════════════════════════════════════════
# EVENT CONTENT (Future)
# ═══════════════════════════════════════════════════════════════════════════════

CALVIN_EVENT = Product(
    id="CALVIN_EVENT",
    name="Crisis Night: Executive Scandal",
    description=(
        "One night where every choice is a headline. "
        "Survive it with him—or watch him survive without you."
    ),
    product_type=ProductType.EVENT,
    price_cents=299,
    flag_key="has_event_calvin_crisis",
    route="calvin",
)


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCT REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

ALL_PRODUCTS: dict[str, Product] = {
    p.id: p for p in [
        # Calvin products
        CALVIN_S1,
        CALVIN_SCENE1,
        CALVIN_ACCESS,
        CALVIN_FASTPASS,
        CALVIN_TITLE,
        CALVIN_BUNDLE1,
        CALVIN_EVENT,
        # Jackson products
        JACKSON_S1,
        JACKSON_SCENE1,
        JACKSON_ACCESS,
        JACKSON_FASTPASS,
        JACKSON_TITLE,
        JACKSON_BUNDLE1,
        JACKSON_EVENT,
        # Cole products
        COLE_S1,
        COLE_SCENE1,
        COLE_MASK,
        COLE_OVERRIDE,
        COLE_TITLE,
        COLE_BUNDLE1,
        # Utility
        ENERGY_10,
    ]
}


def get_product(product_id: str) -> Product | None:
    """Get a product by ID."""
    return ALL_PRODUCTS.get(product_id)


def get_products_by_route(route: str) -> list[Product]:
    """Get all products for a specific route."""
    return [p for p in ALL_PRODUCTS.values() if p.route == route]


def get_bundle_products(bundle_id: str) -> list[Product]:
    """Get all products included in a bundle."""
    bundle = get_product(bundle_id)
    if not bundle or bundle.product_type != ProductType.BUNDLE:
        return []
    return [ALL_PRODUCTS[pid] for pid in bundle.includes if pid in ALL_PRODUCTS]


def check_user_has_product(product_id: str, user_flags: dict, premium_packs: set) -> bool:
    """Check if a user owns a specific product."""
    product = get_product(product_id)
    if not product:
        return False
    
    # Check direct ownership
    if product.flag_key in user_flags or product.flag_key in premium_packs:
        return True
    
    # Check if owned via bundle
    for bundle in ALL_PRODUCTS.values():
        if bundle.product_type == ProductType.BUNDLE:
            if product_id in bundle.includes:
                if bundle.flag_key in user_flags or bundle.flag_key in premium_packs:
                    return True
    
    return False
