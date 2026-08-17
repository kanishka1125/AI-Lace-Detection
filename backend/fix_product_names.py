import json
import os
import re


BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

METADATA_FILE = os.path.join(
    BASE_DIR,
    "metadata",
    "catalogue_metadata.json"
)


with open(
    METADATA_FILE,
    "r",
    encoding="utf-8"
) as f:
    metadata = json.load(f)


def clean_text(text):

    text = text.lower()

    # Remove things that describe the photo,
    # not the actual fabric.

    noise = [
        "white background",
        "plain white surface",
        "white surface",
        "wooden surface",
        "wooden floor",
        "white floor",
        "label",
        "barcode",
        "logo",
        "brand name",
        "text",
        "tag",
        "background",
        "photograph",
        "image"
    ]

    for word in noise:
        text = text.replace(word, " ")

    return text


def find_first(text, words):

    for word in words:

        if re.search(
            r"\b" + re.escape(word) + r"\b",
            text
        ):
            return word

    return None


colors = {
    "black": "Black",
    "white": "White",
    "ivory": "Ivory",
    "cream": "Cream",
    "beige": "Beige",
    "champagne": "Champagne",
    "blush": "Blush",
    "pink": "Pink",
    "blue": "Blue",
    "navy": "Navy",
    "green": "Green",
    "red": "Red",
    "purple": "Purple",
    "lavender": "Lavender",
    "gold": "Gold",
    "silver": "Silver",
    "brown": "Brown",
    "peach": "Peach",
    "orange": "Orange",
    "yellow": "Yellow",
}


patterns = {
    "floral": "Floral",
    "flower": "Floral",
    "leaf": "Leaf",
    "leaves": "Leaf",
    "rose": "Rose",
    "scroll": "Scroll",
    "geometric": "Geometric",
    "diamond": "Diamond",
    "lattice": "Lattice",
    "zigzag": "Zigzag",
    "chevron": "Chevron",
    "striped": "Striped",
    "stripe": "Striped",
    "paisley": "Paisley",
    "vine": "Vine",
}


styles = {
    "embroidered": "Embroidered",
    "embroidery": "Embroidered",
    "beaded": "Beaded",
    "corded": "Corded",
    "guipure": "Guipure",
    "chantilly": "Chantilly",
    "cutwork": "Cutwork",
    "scalloped": "Scallop",
    "scallop": "Scallop",
    "mesh": "Mesh",
    "net": "Net",
}


for product_id, product in metadata.items():

    description = product.get(
        "description",
        ""
    )

    text = clean_text(
        description
    )

    color = None
    pattern = None
    style = None

    for key, value in colors.items():

        if re.search(
            r"\b" + re.escape(key) + r"\b",
            text
        ):

            color = value
            break

    for key, value in patterns.items():

        if re.search(
            r"\b" + re.escape(key) + r"\b",
            text
        ):

            pattern = value
            break

    for key, value in styles.items():

        if re.search(
            r"\b" + re.escape(key) + r"\b",
            text
        ):

            style = value
            break


    parts = []

    if color:
        parts.append(color)

    if pattern:
        parts.append(pattern)

    if style:
        parts.append(style)

    parts.append("Lace")


    # Remove duplicate words

    final_parts = []

    for part in parts:

        if part not in final_parts:
            final_parts.append(part)


    name = " ".join(
        final_parts
    )


    # --------------------------------------
    # Product ID makes the catalogue item
    # uniquely identifiable.
    # --------------------------------------

    product["name"] = name


    print(
        product_id,
        "->",
        name
    )


# ==========================================
# SAVE
# ==========================================

with open(
    METADATA_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        metadata,
        f,
        indent=4,
        ensure_ascii=False
    )


print("\n========================================")
print("PRODUCT NAMES UPDATED")
print("========================================")