from pyscript import window, document
from datetime import datetime
import json
import random

cart = []


def get_inventory():
    raw_data = window.localStorage.getItem("paldotrons_inventory")
    if raw_data:
        try:
            return json.loads(raw_data)
        except Exception:
            pass
    return []

def save_inventory(items):
    window.localStorage.setItem("paldotrons_inventory", json.dumps(items))



def create_sku(event=None):
    format_elem = document.getElementById("format_type")
    artist_elem = document.getElementById("artist_name")
    album_elem = document.getElementById("album_title")
    qty_elem = document.getElementById("stock_qty")

    if not (format_elem and artist_elem and album_elem and qty_elem):
        return

    fmt = format_elem.value
    artist = artist_elem.value.strip()
    album = album_elem.value.strip()
    qty_str = qty_elem.value.strip()

    if not artist or not album or not qty_str:
        return

    clean_artist = "".join(char for char in artist if char.isalnum()).upper()
    artist_code = clean_artist[:2].ljust(2, "A")

    clean_album = "".join(char for char in album if char.isalnum()).upper()
    album_code = clean_album[:2].ljust(2, "X")

    try:
        qty = int(qty_str)
        qty_code = f"{qty:02d}"
    except ValueError:
        qty_code = "00"

    sku = f"{fmt}{artist_code}{album_code}{qty_code}"

    inventory = get_inventory()
    inventory.append({
        "sku": sku,
        "fmt": fmt,
        "artist": artist,
        "album": album,
        "qty": qty_str
    })
    save_inventory(inventory)

    
    sku_result_elem = document.getElementById("sku_result")
    if sku_result_elem:
        sku_result_elem.innerText = sku

   
    render_inventory_table()


def render_inventory_table():
    table_body = document.getElementById("inventory_body")
    if not table_body:
        return

    table_body.innerHTML = ""
    inventory = get_inventory()

    if not inventory:
        new_row = document.createElement("tr")
        new_row.innerHTML = "<td colspan='5' style='text-align: center; opacity: 0.65; padding: 20px;'>No custom SKUs found. Generate your first album SKU above!</td>"
        table_body.appendChild(new_row)
        return

    for item in inventory:
        new_row = document.createElement("tr")
        new_row.innerHTML = f"<td><strong>{item['sku']}</strong></td><td>{item['fmt']}</td><td>{item['artist']}</td><td>{item['album']}</td><td>{item['qty']}</td>"
        table_body.appendChild(new_row)


def clear_inventory(event=None):
    window.localStorage.removeItem("paldotrons_inventory")
    render_inventory_table()


# ==========================================
# RECEIPT PAGE LOGIC & SAVED SKU AUTOFILL
# ==========================================
def render_autofill_box(event=None):
    box = document.getElementById("autofill_box")
    list_container = document.getElementById("autofill_list")
    if not box or not list_container:
        return

    inventory = get_inventory()
    if not inventory:
        box.style.display = "none"
        return

    list_container.innerHTML = ""
    for item in inventory:
        sku_code = item['sku']
        album_title = item['album']
        artist_name = item['artist']
        fmt_type = item['fmt']

        item_div = document.createElement("div")
        item_div.className = "autofill-item"
        item_div.setAttribute("onclick", f"selectAutofillSku('{sku_code}')")
        item_div.innerHTML = f"""
            <span class="autofill-sku">{sku_code}</span>
            <div class="autofill-info">
                <span class="autofill-title">{album_title}</span>
                <span class="autofill-subtitle">{artist_name} • {fmt_type}</span>
            </div>
        """
        list_container.appendChild(item_div)

    box.style.display = "block"


def hide_autofill_box(event=None):
    box = document.getElementById("autofill_box")
    if box:
        box.style.display = "none"


def scan_sku(event=None):
    sku_input = document.getElementById("scan_sku")

    if not sku_input:
        return

    sku_code = sku_input.value.strip().upper()
    if not sku_code:
        return

    inventory = get_inventory()
    matched_item = None
    for item in inventory:
        if item["sku"].upper() == sku_code:
            matched_item = item
            break

    album_name = matched_item["album"] if matched_item else "Album/Item"
    artist_name = matched_item["artist"] if matched_item else "Artist"

    # Automatically generate random price between ₱199.00 and ₱2,499.00
    random_price = round(random.uniform(199.0, 2499.0), 2)

    cart.append({
        "sku": sku_code,
        "album": album_name,
        "artist": artist_name,
        "price": random_price,
        "qty": 1,
        "total": random_price
    })

    date_elem = document.getElementById("receipt_date")
    if date_elem:
        date_elem.innerText = datetime.now().strftime("%d %b %Y").upper()

    render_receipt_cart()
    sku_input.value = ""
    hide_autofill_box()


def render_receipt_cart():
    items_container = document.getElementById("receipt_items_list")
    total_elem = document.getElementById("receipt_total")

    if not items_container:
        return

    items_container.innerHTML = ""
    grand_total = 0.0

    if not cart:
        items_container.innerHTML = "<div style='opacity: 0.65; font-size: 0.85rem; text-align: center; padding: 10px 0;'>No items added yet. Select or enter an SKU code above to generate receipt.</div>"
        if total_elem:
            total_elem.innerText = "0.00"
        return

    for item in cart:
        grand_total += item["total"]
        row_div = document.createElement("div")
        row_div.className = "row"
        row_div.innerHTML = f"""
            <span class="label">[{item['sku']}] <strong>{item['album']}</strong> - {item['artist']}</span>
            <span class="value">₱{item['price']:,.2f}</span>
        """
        items_container.appendChild(row_div)

    if total_elem:
        total_elem.innerText = f"{grand_total:,.2f}"

render_inventory_table()
render_receipt_cart()