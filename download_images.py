import requests
import os

SAVE_FOLDER = "static/images"
os.makedirs(SAVE_FOLDER, exist_ok=True)

items = {
    "Chicken Biryani": "biryani.jpg",
    "Veg Burger": "burger.jpg",
    "Paneer Tikka": "paneer-tikka.jpg",
    "Masala Dosa": "dosa.jpg",
    "Chicken 65": "chicken65.jpg",
    "Veg Biryani": "veg_biryani.jpg",
    "Chicken Burger": "chicken_burger.jpg",
    "Margherita Pizza": "margherita_pizza.jpg",
    "Chicken Pizza": "chicken_pizza.jpg",
    "Idli Sambar": "idli_sambar.jpg",
    "Chicken Fried Rice": "chicken_fried_rice.jpg",
    "Veg Noodles": "veg_noodles.jpg",
    "Butter Chicken": "butter_chicken.jpg",
    "Gulab Jamun": "gulab_jamun.jpg",
    "Cold Coffee": "cold_coffee.jpg",
}


def get_wikipedia_image(query):
    url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "format": "json",
        "prop": "pageimages",
        "piprop": "original",
        "generator": "search",
        "gsrsearch": query,
        "gsrlimit": 1,
    }

    response = requests.get(
        url,
        params=params,
        timeout=15,
        headers={"User-Agent": "QuickBiteFoodApp/1.0"}
    )

    response.raise_for_status()

    data = response.json()

    pages = data.get("query", {}).get("pages", {})

    for page in pages.values():
        original = page.get("original")

        if original:
            return original["source"]

    return None


for name, filename in items.items():

    print(f"\nFetching: {name}")

    try:
        image_url = get_wikipedia_image(name)

        if not image_url:
            print("  ✘ No image found")
            continue

        response = requests.get(
            image_url,
            timeout=15,
            headers={"User-Agent": "QuickBiteFoodApp/1.0"}
        )

        response.raise_for_status()

        filepath = os.path.join(SAVE_FOLDER, filename)

        with open(filepath, "wb") as file:
            file.write(response.content)

        print(f"  ✔ Saved: {filename}")

    except Exception as e:
        print(f"  ✘ Failed: {e}")


print("\n==============================")
print("DONE!")
print("Check static/images folder.")
print("==============================")