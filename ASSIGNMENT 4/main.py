from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


# Sample Product Database

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "in_stock": True},
]


# In-memory storage

cart = []
orders = []
order_id_counter = 1



# Pydantic Model for Checkout

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str


# Helper Functions

def find_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def calculate_subtotal(price, quantity):
    return price * quantity


# 1️. Add to Cart

@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    product = find_product(product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if not product["in_stock"]:
        raise HTTPException(
            status_code=400,
            detail=f"{product['name']} is out of stock"
        )

    # Check if product already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = calculate_subtotal(product["price"], item["quantity"])

            return {
                "message": "Cart updated",
                "cart_item": item
            }

    subtotal = calculate_subtotal(product["price"], quantity)

    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }

    cart.append(cart_item)

    return {
        "message": "Added to cart",
        "cart_item": cart_item
    }



# 2️.View Cart

@app.get("/cart")
def view_cart():

    if not cart:
        return {"message": "Cart is empty"}

    grand_total = sum(item["subtotal"] for item in cart)

    return {
        "items": cart,
        "item_count": len(cart),
        "grand_total": grand_total
    }



# 3️.Remove Item from Cart

@app.delete("/cart/{product_id}")
def remove_item(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": f"Product {product_id} removed from cart"}

    raise HTTPException(status_code=404, detail="Item not found in cart")



# 4️.Checkout

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest):

    global order_id_counter

    if not cart:
        raise HTTPException(
            status_code=400,
            detail="Cart is empty — add items first"
        )

    placed_orders = []
    grand_total = 0

    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": data.customer_name,
            "delivery_address": data.delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "total_price": item["subtotal"]
        }

        orders.append(order)
        placed_orders.append(order)

        grand_total += item["subtotal"]
        order_id_counter += 1

    cart.clear()

    return {
        "message": "Checkout successful",
        "orders_placed": placed_orders,
        "grand_total": grand_total
    }



# 5️.View Orders

@app.get("/orders")
def get_orders():

    return {
        "orders": orders,
        "total_orders": len(orders)
    }