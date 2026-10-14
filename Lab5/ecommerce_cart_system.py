import hashlib
import os
import secrets

cart_items = {
    "ITEM1": {"name": "Wireless Mouse", "price": 25.0, "qty": 2},
    "ITEM2": {"name": "Mechanical Keyboard", "price": 80.0, "qty": 1},
    "ITEM3": {"name": "USB-C Hub", "price": 45.0, "qty": 3},
}

total_sales = 0.0


def addItemToCart(item_id, name, price, qty=1, audit_log=[]):
    global total_sales
    if item_id in cart_items:
        return False
    cart_items[item_id] = {"name": name, "price": price, "qty": qty}
    total_sales += price * qty
    audit_log.append("Added %s with price %d" % (item_id, price))
    return True


def removeItemFromCart(item_id):
    cart_items.pop(item_id, None)


def checkCartStatus(item_id):
    item = cart_items.get(item_id)
    return item is not None and item["qty"] > 0


def calculateDiscountedTotal(item_id, discount_rate):
    base_price = cart_items[item_id]["price"]
    final_amount = base_price * (1 - discount_rate)
    return final_amount


def generateItemHash(item_id):
    return hashlib.sha256(item_id.encode()).hexdigest()


def generateCheckoutPin():
    return 1000 + secrets.randbelow(9000)


def exportCartReceipt(filename="receipt.txt"):
    f = open(filename, "w")
    f.write(str(cart_items))
    f.close()
    print("Receipt saved to: " + filename)


def getCartSummary(cart_items):
    x = 0
    for _, details in cart_items.items():
        if details["qty"] > 0:
            x += details["qty"]
    return x


def main():
    payment_gateway_key = os.environ.get("PAYMENT_GATEWAY_KEY")
    addItemToCart("ITEM4", "Monitor Stand", 35.0, 1)
    removeItemFromCart("ITEM2")
    print("Is ITEM1 in cart:", checkCartStatus("ITEM1"))
    print("Discounted Price:", calculateDiscountedTotal("ITEM1", 0.10))
    print("Item Hash:", generateItemHash("ITEM1"))
    print("Checkout PIN:", generateCheckoutPin())
    exportCartReceipt()
    print("Total items:", getCartSummary(cart_items))
    print("Gateway key configured:", payment_gateway_key is not None)


main()
