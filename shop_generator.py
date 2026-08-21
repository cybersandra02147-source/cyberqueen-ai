import os

def create_shop(shop_name):
    folder = f"shops/{shop_name.replace(' ', '_')}"

    os.makedirs(folder, exist_ok=True)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{shop_name}</title>
</head>
<body>
    <h1>Welcome to {shop_name}</h1>
    <p>Your online shop has been created successfully.</p>

    <h2>Products</h2>

    <ul>
        <li>Product 1 - ₦0.00</li>
        <li>Product 2 - ₦0.00</li>
    </ul>

</body>
</html>
"""

    with open(f"{folder}/index.html", "w", encoding="utf-8") as file:
        file.write(html)

    print("Shop created successfully!")

if __name__ == "__main__":
    name = input("Enter shop name: ")
    create_shop(name)
