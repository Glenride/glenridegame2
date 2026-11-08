"""Store and payment handlers for premium content."""

from __future__ import annotations

import logging
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    Update,
)
from telegram.ext import (
    BaseHandler,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    PreCheckoutQueryHandler,
    filters,
)

from bot.config import load_config
from bot.logging_utils import instrument_handler
from bot.products import (
    ALL_PRODUCTS,
    Product,
    ProductType,
    get_product,
    get_products_by_route,
    check_user_has_product,
)
from bot.state import StateStore

__all__ = ["build_handlers"]

logger = logging.getLogger(__name__)

STORE_CALLBACK_PREFIX = "store:"


def build_handlers(state_store: StateStore) -> list[BaseHandler]:
    """Return handlers for store and payments."""
    config = load_config()
    payments_token = config.payments_provider_token

    @instrument_handler("store_command")
    async def store_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show the store menu."""
        chat = update.effective_chat
        user = update.effective_user
        if not chat or not user:
            return

        state = state_store.load_user_state(user.id)
        if not state:
            await chat.send_message(
                "You need to start your story first! Use /start to begin."
            )
            return

        # Build category menu
        keyboard = [
            [InlineKeyboardButton("💎 Calvin Route", callback_data=f"{STORE_CALLBACK_PREFIX}route:calvin")],
            [InlineKeyboardButton("🔥 Jackson Route", callback_data=f"{STORE_CALLBACK_PREFIX}route:jackson")],
            [InlineKeyboardButton("👻 Cole Route", callback_data=f"{STORE_CALLBACK_PREFIX}route:cole")],
            [InlineKeyboardButton("⚡ Energy & Utilities", callback_data=f"{STORE_CALLBACK_PREFIX}category:utility")],
        ]

        await chat.send_message(
            "🏪 **Neon City Store**\n\n"
            "Unlock premium scenes, extended routes, and exclusive content.\n\n"
            "Choose a category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    @instrument_handler("store_callback")
    async def store_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle store navigation callbacks."""
        query = update.callback_query
        if not query or not query.data:
            return

        await query.answer()
        user = query.from_user
        data = query.data.removeprefix(STORE_CALLBACK_PREFIX)

        state = state_store.load_user_state(user.id)
        if not state:
            await query.edit_message_text("Session expired. Use /store to try again.")
            return

        # Route category
        if data.startswith("route:"):
            route = data.removeprefix("route:")
            products = get_products_by_route(route)
            await _show_route_products(query, products, route, state)

        # Utility category
        elif data.startswith("category:utility"):
            utility_products = [p for p in ALL_PRODUCTS.values() if p.route == ""]
            await _show_utility_products(query, utility_products, state)

        # Back to main menu
        elif data == "back":
            keyboard = [
                [InlineKeyboardButton("💎 Calvin Route", callback_data=f"{STORE_CALLBACK_PREFIX}route:calvin")],
                [InlineKeyboardButton("🔥 Jackson Route", callback_data=f"{STORE_CALLBACK_PREFIX}route:jackson")],
                [InlineKeyboardButton("👻 Cole Route", callback_data=f"{STORE_CALLBACK_PREFIX}route:cole")],
                [InlineKeyboardButton("⚡ Energy & Utilities", callback_data=f"{STORE_CALLBACK_PREFIX}category:utility")],
            ]
            await query.edit_message_text(
                "🏪 **Neon City Store**\n\n"
                "Unlock premium scenes, extended routes, and exclusive content.\n\n"
                "Choose a category:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown",
            )

        # Buy specific product
        elif data.startswith("buy:"):
            product_id = data.removeprefix("buy:")
            await _initiate_purchase(query, context, product_id, state, payments_token)

    async def _show_route_products(query, products: list[Product], route: str, state) -> None:
        """Show products for a specific route."""
        route_names = {"calvin": "Calvin", "jackson": "Jackson", "cole": "Cole"}
        route_emojis = {"calvin": "💎", "jackson": "🔥", "cole": "👻"}
        
        parts = [f"{route_emojis.get(route, '📦')} **{route_names.get(route, route.title())} Premium Content**\n"]

        keyboard = []
        for product in products:
            owned = check_user_has_product(
                product.id,
                state.flags,
                state.premium_packs | state.premium_items
            )
            
            price_str = f"${product.price_cents / 100:.2f}"
            status = "✅ Owned" if owned else price_str
            type_emoji = _get_type_emoji(product.product_type)
            
            parts.append(f"\n{type_emoji} **{product.name}**")
            parts.append(f"_{product.description}_")
            parts.append(f"Status: {status}")

            if not owned:
                keyboard.append([
                    InlineKeyboardButton(
                        f"Buy {product.name} ({price_str})",
                        callback_data=f"{STORE_CALLBACK_PREFIX}buy:{product.id}"
                    )
                ])

        keyboard.append([InlineKeyboardButton("« Back", callback_data=f"{STORE_CALLBACK_PREFIX}back")])

        await query.edit_message_text(
            "\n".join(parts),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    async def _show_utility_products(query, products: list[Product], state) -> None:
        """Show utility products like energy."""
        parts = ["⚡ **Energy & Utilities**\n"]

        keyboard = []
        for product in products:
            price_str = f"${product.price_cents / 100:.2f}"
            type_emoji = _get_type_emoji(product.product_type)
            
            parts.append(f"\n{type_emoji} **{product.name}**")
            parts.append(f"_{product.description}_")
            parts.append(f"Price: {price_str}")

            keyboard.append([
                InlineKeyboardButton(
                    f"Buy {product.name} ({price_str})",
                    callback_data=f"{STORE_CALLBACK_PREFIX}buy:{product.id}"
                )
            ])

        keyboard.append([InlineKeyboardButton("« Back", callback_data=f"{STORE_CALLBACK_PREFIX}back")])

        await query.edit_message_text(
            "\n".join(parts),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )

    async def _initiate_purchase(query, context, product_id: str, state, payments_token: str) -> None:
        """Start the payment flow for a product."""
        product = get_product(product_id)
        if not product:
            await query.answer("Product not found.", show_alert=True)
            return

        # Check if already owned (except consumables like energy)
        if product.product_type != ProductType.ENERGY:
            owned = check_user_has_product(
                product.id,
                state.flags,
                state.premium_packs | state.premium_items
            )
            if owned:
                await query.answer("You already own this!", show_alert=True)
                return

        # Check if payments are configured
        if not payments_token:
            # Test mode - grant item directly
            await _grant_product(state, product, state_store)
            await query.edit_message_text(
                f"🎁 **[TEST MODE]** {product.name} unlocked!\n\n"
                f"_{product.description}_\n\n"
                "Use /start to continue your story.",
                parse_mode="Markdown",
            )
            logger.info("test_purchase_granted", extra={
                "user_id": state.user_id,
                "product_id": product.id,
            })
            return

        # Real payment flow
        title = product.name
        description = product.description[:255]  # Telegram limit
        payload = f"{state.user_id}:{product.id}"
        currency = "USD"
        prices = [LabeledPrice(label=product.name, amount=product.price_cents)]

        try:
            await context.bot.send_invoice(
                chat_id=query.message.chat_id,
                title=title,
                description=description,
                payload=payload,
                provider_token=payments_token,
                currency=currency,
                prices=prices,
                start_parameter=f"buy_{product.id}",
            )
            await query.edit_message_text(
                f"💳 Invoice sent for **{product.name}**!\n\n"
                "Complete the payment in the message above.",
                parse_mode="Markdown",
            )
        except Exception as e:
            logger.error("invoice_send_failed", extra={"error": str(e), "product_id": product.id})
            await query.answer("Failed to create invoice. Please try again.", show_alert=True)

    @instrument_handler("pre_checkout")
    async def pre_checkout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Validate the payment before processing."""
        query = update.pre_checkout_query
        if not query:
            return

        payload = query.invoice_payload
        parts = payload.split(":")
        if len(parts) != 2:
            await query.answer(ok=False, error_message="Invalid payment data.")
            return

        user_id_str, product_id = parts
        
        # Validate user
        try:
            user_id = int(user_id_str)
        except ValueError:
            await query.answer(ok=False, error_message="Invalid user data.")
            return

        if user_id != query.from_user.id:
            await query.answer(ok=False, error_message="User mismatch.")
            return

        # Validate product exists
        product = get_product(product_id)
        if not product:
            await query.answer(ok=False, error_message="Product no longer available.")
            return

        # Check if already owned (except consumables)
        state = state_store.load_user_state(user_id)
        if state and product.product_type != ProductType.ENERGY:
            owned = check_user_has_product(
                product.id,
                state.flags,
                state.premium_packs | state.premium_items
            )
            if owned:
                await query.answer(ok=False, error_message="You already own this item.")
                return

        # All good!
        await query.answer(ok=True)

    @instrument_handler("successful_payment")
    async def successful_payment_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle successful payment and grant the product."""
        message = update.message
        if not message or not message.successful_payment:
            return

        payment = message.successful_payment
        payload = payment.invoice_payload
        parts = payload.split(":")
        
        if len(parts) != 2:
            logger.error("invalid_payment_payload", extra={"payload": payload})
            return

        user_id_str, product_id = parts
        user_id = int(user_id_str)

        product = get_product(product_id)
        if not product:
            logger.error("product_not_found_after_payment", extra={"product_id": product_id})
            await message.reply_text("⚠️ Error processing purchase. Please contact support.")
            return

        state = state_store.load_user_state(user_id)
        if not state:
            logger.error("user_not_found_after_payment", extra={"user_id": user_id})
            await message.reply_text("⚠️ Error processing purchase. Please contact support.")
            return

        # Grant the product
        await _grant_product(state, product, state_store)

        logger.info("purchase_completed", extra={
            "user_id": user_id,
            "product_id": product.id,
            "amount": payment.total_amount,
            "currency": payment.currency,
        })

        await message.reply_text(
            f"🎉 **Thank you for your purchase!**\n\n"
            f"**{product.name}** has been unlocked!\n\n"
            f"_{product.description}_\n\n"
            "Use /start to continue your story with your new content.",
            parse_mode="Markdown",
        )

    async def _grant_product(state, product: Product, store: StateStore) -> None:
        """Grant a product to a user's account."""
        if product.product_type == ProductType.ENERGY:
            # Energy adds directly to stats
            store.update_stats_atomic(state.user_id, {"energy": 10})
        elif product.product_type == ProductType.ROUTE_PACK:
            state.premium_packs.add(product.flag_key)
            store.save_user_state(state)
        elif product.product_type == ProductType.COSMETIC:
            if "title" in product.flag_key:
                # Extract title name from flag key like "has_title_calvin_experiment"
                title_name = product.name
                state.titles.add(title_name)
            state.premium_items.add(product.flag_key)
            store.save_user_state(state)
        else:
            # Scene, Item, Bundle, Event
            state.premium_items.add(product.flag_key)
            store.save_user_state(state)

        # If bundle, grant included items
        if product.product_type == ProductType.BUNDLE:
            for included_id in product.includes:
                included_product = get_product(included_id)
                if included_product:
                    await _grant_product(state, included_product, store)

    def _get_type_emoji(product_type: ProductType) -> str:
        """Get emoji for product type."""
        return {
            ProductType.ROUTE_PACK: "📖",
            ProductType.SCENE: "🎬",
            ProductType.ITEM: "🔧",
            ProductType.COSMETIC: "🏷️",
            ProductType.BUNDLE: "📦",
            ProductType.ENERGY: "⚡",
            ProductType.EVENT: "🎭",
        }.get(product_type, "📦")

    return [
        CommandHandler("store", store_command),
        CallbackQueryHandler(store_callback, pattern=f"^{STORE_CALLBACK_PREFIX}"),
        PreCheckoutQueryHandler(pre_checkout_handler),
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_handler),
    ]
