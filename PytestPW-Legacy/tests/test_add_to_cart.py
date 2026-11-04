import re

from playwright.sync_api import Page, expect

# Public demo credentials published on the bstackdemo.com sign-in page
DEMO_USER = "demouser"
DEMO_PASSWORD = "testingisfun99"


def price(text: str) -> float:
    return float(re.search(r"\$\s*([\d.]+)", text).group(1))


def test_add_two_products_adjust_quantity_and_checkout(page: Page):
    page.goto("/")
    products = page.locator(".shelf-item")
    expect(products.first).to_be_visible()

    # Capture names and prices of the first two products
    names = [products.nth(i).locator(".shelf-item__title").inner_text() for i in (0, 1)]
    prices = [price(products.nth(i).locator(".val").inner_text()) for i in (0, 1)]

    # Add both products to the cart
    products.nth(0).get_by_text("Add to cart").click()
    products.nth(1).get_by_text("Add to cart").click()

    cart = page.locator(".float-cart__content")
    cart_items = cart.locator(".shelf-item")
    expect(cart_items).to_have_count(2)
    expect(cart.locator(".shelf-item__details .title")).to_have_text(names)
    expect(page.locator(".float-cart .bag__quantity")).to_have_text("2")
    expect(page.locator(".sub-price__val")).to_have_text(f"$ {sum(prices):.2f}")

    # Increase the quantity of the first product -> subtotal reflects 2 x first + second
    cart_items.nth(0).locator(".change-product-button").nth(1).click()
    expect(cart_items.nth(0)).to_contain_text("Quantity: 2")
    expect(page.locator(".sub-price__val")).to_have_text(f"$ {2 * prices[0] + prices[1]:.2f}")

    # Remove the second product -> only first product (qty 2) remains
    cart_items.nth(1).locator(".shelf-item__del").click()
    expect(cart_items).to_have_count(1)
    expect(cart.locator(".shelf-item__details .title")).to_have_text(names[0])
    expect(page.locator(".sub-price__val")).to_have_text(f"$ {2 * prices[0]:.2f}")

    # Checkout requires sign in
    page.locator(".buy-btn").click()
    expect(page).to_have_url(re.compile(r"/signin\?checkout=true"))
    page.locator("#username").click()
    page.get_by_text(DEMO_USER, exact=True).click()
    page.locator("#password").click()
    page.get_by_text(DEMO_PASSWORD, exact=True).click()
    page.locator("#login-btn").click()

    # Shipping address
    expect(page).to_have_url(re.compile(r"/checkout$"))
    page.locator("#firstNameInput").fill("Test")
    page.locator("#lastNameInput").fill("User")
    page.locator("#addressLine1Input").fill("1 Main St")
    page.locator("#provinceInput").fill("CA")
    page.locator("#postCodeInput").fill("12345")
    page.locator("#checkout-shipping-continue").click()

    # Order confirmation
    expect(page).to_have_url(re.compile(r"/confirmation$"))
    expect(page.locator("#confirmation-message")).to_have_text(
        "Your Order has been successfully placed."
    )
    expect(page.get_by_text(re.compile(r"Your order number is \d+"))).to_be_visible()
    expect(page.locator(".cart-priceItem--total")).to_contain_text(f"${2 * prices[0]:.2f}")
