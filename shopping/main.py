import asyncio
import os
from pydantic import BaseModel, Field
from typing import Literal

# Note: The browser-use library assumes environment variables like BROWSER_USE_API_KEY
# are loaded, typically using dotenv, which is often handled by uv or a similar tool.
# We will use the standard imports here.
from browser_use import Agent, Browser, ChatBrowserUse


class GroceryItem(BaseModel):
    """A single grocery item found during the shopping task."""

    name: str = Field(..., description="The exact name of the product found.")
    price: float = Field(..., description="The price of the item as a number (e.g., 4.99).")
    brand: str | None = Field(None, description="The brand name of the product.")
    size: str | None = Field(None, description="The size or quantity (e.g., '1 Gallon', '12 oz').")
    url: str = Field(..., description="The full URL to the item's product page.")
    rating: float | None = Field(None, description="The average customer star rating for the item (e.g., 4.7).")
    in_stock: bool = Field(True, description="True if the item was the original choice and was in stock. False if it was substituted or completely unavailable.")
    notes: str | None = Field(None, description="Substitution notes or special observations. REQUIRED if in_stock is False (e.g., 'Original item out of stock, substituted with similar product from Brand X').")


class GroceryCart(BaseModel):
    """A collection of grocery items for a specific store."""
    store_name: str = Field(..., description="The name of the grocery store where the items were shopped (e.g., 'Kroger').")
    total_cost: float = Field(..., description="The calculated sum of all item prices in the cart.")
    items: list[GroceryItem] = Field(
        default_factory=list, description="All grocery items found or substituted."
    )


async def add_to_cart(store: str, items: list[str], preference: str):
    """
    Runs the automated shopping agent for a specific store and set of items/preferences.
    """
    # Initialize the browser and LLM connection.
    # Assumes launch_chrome_debug.py is running on port 9222
    browser = Browser(cdp_url="http://localhost:9222")
    llm = ChatBrowserUse()

    items_list_str = ', '.join(items)

    # Dynamic Task prompt incorporating the advanced logic
    task = f"""
    You are an expert, multi-store grocery shopper using Instacart. Your goal is to find the best possible cart based on the user's specific requirements.

    Shopping List: {items_list_str}
    Store to check: {store}
    Shopping Preference: "{preference}" (e.g., 'organic', 'gluten-free', 'cheapest')

    Site:
    - Instacart: https://www.instacart.com/

    Instructions for Shopping:
    1. Navigate to Instacart and specify the items are for the "{store}" location.
    2. For each item in the Shopping List:
        a. Search for the item.
        b. Prioritize items that strictly match the user's Shopping Preference: "{preference}".
        c. If multiple items match the preference, choose the one with the lowest price. Use the highest 'rating' as the tie-breaker.
        d. Add the chosen item to the cart.
        e. **Handle Out-of-Stock/Substitution:** If the originally chosen item is listed as 'Out of Stock' or 'Unavailable', search for the next best substitute of similar size/quantity (different brand is allowed).
    3. **Set Output Fields:**
        - Ensure the 'in_stock' field is True only if the preferred/original item was found in stock. It must be False if a substitution was made.
        - **If a substitution was made (in_stock=False), the 'notes' field is MANDATORY** to clearly explain the substitution (e.g., 'Original item out of stock, substituted with similar product from Brand X').
    4. After the last item is processed, calculate the total cost of all found items and set the 'total_cost' field in the output model.
    5. Set the 'store_name' field to "{store}".
    """

    # Create agent with structured output
    agent = Agent(
        browser=browser,
        llm=llm,
        task=task,
        output_model_schema=GroceryCart,
    )

    # Run the agent
    result = await agent.run()

    # The result may contain structured_output (a GroceryCart instance) or be None on failure
    if result and result.structured_output:
        return result.structured_output
    return None


if __name__ == "__main__":
    # --- User Input ---
    items_input = input(
        "What items would you like to add to cart (comma-separated, e.g., milk, eggs, bread)? "
    ).strip()
    preference = input(
        "What is your shopping preference (e.g., 'organic', 'gluten-free', 'cheapest')? "
    ).strip() or "cheapest"

    if not items_input:
        items = ["milk", "eggs", "bread"]
        print(f"Using default items: {items}")
    else:
        items = [item.strip() for item in items_input.split(",")]

    # --- Multi-Store Comparison Setup ---
    # Define the stores we want to compare on Instacart
    STORES = ["Kroger", "Safeway", "Aldi"]
    all_carts: list[GroceryCart] = []

    print(f"\nSearching for items: {', '.join(items)} with preference: '{preference}'")
    print(f"Comparing prices across stores: {', '.join(STORES)}\n")

    # --- Run Automation for Each Store ---
    for store in STORES:
        print(f"--- 🛒 Running search for {store} ---")
        try:
            # Run the asynchronous function for the current store
            cart = asyncio.run(add_to_cart(store, items, preference))

            if cart:
                # Re-calculate total cost in Python to ensure accuracy,
                # as the LLM's calculation might sometimes be slightly off.
                cart.total_cost = sum(item.price for item in cart.items)
                all_carts.append(cart)
                print(f"--- ✅ {store} Cart Total: ${cart.total_cost:.2f} ---\n")
            else:
                print(f"--- ❌ Failed to get structured results for {store} ---\n")
        except Exception as e:
            print(f"--- 🛑 An error occurred while processing {store}: {e} ---\n")


    # --- Find and Display Best Cart ---
    if not all_carts:
        print("\n\n❌ Error: No carts were successfully retrieved. Check your API key and Chrome connection.")
    else:
        # Find the cart with the lowest total_cost
        best_cart = min(all_carts, key=lambda cart: cart.total_cost)

        print(f"\n{'=' * 70}")
        print("🏆 Final Price Comparison Results")
        print(f"{'=' * 70}")

        # Summary of all stores
        print("\n--- Summary of All Stores ---")
        for cart in sorted(all_carts, key=lambda c: c.total_cost):
            status = "🏆 BEST PRICE" if cart == best_cart else ""
            print(f"| {cart.store_name:<10} | Total Items: {len(cart.items):<2} | Total Cost: ${cart.total_cost:>.2f} {status}")
        print("-" * 70)


        # Best Cart Details
        print(f"\n✅ Best Option Found at: {best_cart.store_name}")
        print(f"Total Cost: ${best_cart.total_cost:.2f}")
        print(f"Items requested: {len(items)}, Items found/substituted: {len(best_cart.items)}\n")

        print(f"{'=' * 70}")
        print(f"Details for Best Cart at {best_cart.store_name}:")
        print(f"{'=' * 70}")

        for item in best_cart.items:
            stock_status = "✅ In Stock" if item.in_stock else "⚠️ SUBSTITUTED"
            notes_str = f"Notes: {item.notes}" if item.notes else ""
            rating_str = f"| Rating: {item.rating}/5.0" if item.rating else ""

            print(f"Name: {item.name}")
            print(f"Price: ${item.price:.2f}")
            print(f"Brand: {item.brand or 'N/A'}")
            print(f"Size: {item.size or 'N/A'}")
            print(f"Status: {stock_status} {rating_str}")
            if notes_str:
                 print(f"{notes_str}")
            print(f"URL: {item.url}")
            print(f"{'-' * 70}")