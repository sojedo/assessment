import copy
import json
import os
import sys

DATA_FILE = "learn2earn_data.json"
LOW_STOCK_THRESHOLD = 3

STARTING_RESOURCES = [
    {"id": "R001", "name": "Laptop", "category": "Electronics", "total": 10, "available": 10},
    {"id": "R002", "name": "Keyboard", "category": "Accessories", "total": 5, "available": 5},
    {"id": "R003", "name": "Headset", "category": "Accessories", "total": 3, "available": 3},
]
STARTING_FELLOWS = {"F001": "Ada", "F002": "John", "F003": "Grace"}


def parse_positive_int(value):
    text = str(value).strip()
    if text == "":
        return None, "Quantity cannot be empty."
    if not text.isdigit():
        return None, f"'{text}' is not a valid whole number (use digits only, e.g. 2)."
    number = int(text)
    if number <= 0:
        return None, "Quantity must be greater than zero."
    return number, None


def find_resource(resources, resource_id):
    rid = str(resource_id).strip().upper()
    for resource in resources:
        if resource["id"].upper() == rid:
            return resource
    return None

def normalise_id(value):
    return str(value).strip().upper()

def add_resource(resources, rid, name, category, total):
    rid = normalise_id(rid)
    name, category = str(name).strip(), str(category).strip()
    if not rid or not name or not category:
        return False, "ID, name and category are all required."
    if find_resource(resources, rid) is not None:
        return False, f"Resource ID {rid} already exists."
    total_n, err = parse_positive_int(total)
    if err:
        return False, f"Invalid total units: {err}"
    resources.append({"id": rid, "name": name, "category": category,
                      "total": total_n, "available": total_n})
    return True, f"Added {rid}: {name} ({category}), {total_n} units."

def format_resource(r):
    return (f"{r['id']:<6} {r['name']:<15} {r['category']:<14} "
            f"total={r['total']:<4} available={r['available']}")

def list_resources(resources):
    if not resources:
        return "No resources in inventory."
    return "\n".join(format_resource(r) for r in resources)

def on_loan(borrow_records, fellow_id, resource_id):
    return sum(rec["borrowed"] - rec["returned"] for rec in borrow_records
               if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource_id)

def units_on_loan_by_resource(resources, borrow_records):
    return {r["id"]: sum(rec["borrowed"] - rec["returned"] for rec in borrow_records
                         if rec["resource_id"] == r["id"]) for r in resources}

def borrow_resource(resources, fellows, borrow_records, fellow_id, resource_id, quantity):
    fellow_id, resource_id = normalise_id(fellow_id), normalise_id(resource_id)
    if fellow_id not in fellows:
        return False, f"Unknown fellow ID '{fellow_id}'."
    resource = find_resource(resources, resource_id)
    if resource is None:
        return False, f"Unknown resource ID '{resource_id}'."
    qty, err = parse_positive_int(quantity)
    if err:
        return False, err
    if qty > resource["available"]:
        return False, (f"Rejected: requested {qty} {resource['name']}(s) but only "
                       f"{resource['available']} available.")
    resource["available"] -= qty
    borrow_records.append({"fellow_id": fellow_id, "resource_id": resource["id"],
                           "borrowed": qty, "returned": 0})
    return True, (f"{fellows[fellow_id]} ({fellow_id}) borrowed {qty} {resource['name']}(s). "
                  f"Available now: {resource['available']}.")


def return_resource(resources, fellows, borrow_records, fellow_id, resource_id, quantity):
    fellow_id, resource_id = normalise_id(fellow_id), normalise_id(resource_id)
    if fellow_id not in fellows:
        return False, f"Unknown fellow ID '{fellow_id}'."
    resource = find_resource(resources, resource_id)
    if resource is None:
        return False, f"Unknown resource ID '{resource_id}'."
    qty, err = parse_positive_int(quantity)
    if err:
        return False, err
    held = on_loan(borrow_records, fellow_id, resource["id"])
    if qty > held:
        return False, (f"Rejected: {fellows[fellow_id]} ({fellow_id}) has only {held} "
                       f"{resource['name']}(s) on loan, cannot return {qty}.")
    remaining = qty
    for rec in borrow_records:  
        if remaining == 0:
            break
        if rec["fellow_id"] == fellow_id and rec["resource_id"] == resource["id"]:
            take = min(remaining, rec["borrowed"] - rec["returned"])
            rec["returned"] += take
            remaining -= take
    resource["available"] += qty
    return True, (f"{fellows[fellow_id]} ({fellow_id}) returned {qty} {resource['name']}(s). "
                  f"Available now: {resource['available']}.")

def search_by_name(resources, term):
    term = str(term).strip().lower()
    if not term:
        return []
    return [r for r in resources if term in r["name"].lower()]


def filter_by_category(resources, category):
    category = str(category).strip().lower()
    return [r for r in resources if r["category"].lower() == category]

def build_report(resources, borrow_records):
    total = sum(r["total"] for r in resources)
    available = sum(r["available"] for r in resources)
    loans = units_on_loan_by_resource(resources, borrow_records)
    borrowed = sum(loans.values())
    low = [r for r in resources if r["available"] < LOW_STOCK_THRESHOLD]
    top = max(loans.values(), default=0)
    leaders = [r for r in resources if loans[r["id"]] == top] if top > 0 else []
    return {"total": total, "available": available, "borrowed": borrowed,
            "low_stock": low, "top_count": top, "leaders": leaders}


def format_report(resources, borrow_records):
    rep = build_report(resources, borrow_records)
    lines = ["=== INVENTORY REPORT ===",
             f"Total units:     {rep['total']}",
             f"Available units: {rep['available']}",
             f"Borrowed units:  {rep['borrowed']}",
             f"Low stock (fewer than {LOW_STOCK_THRESHOLD} available):"]
    if rep["low_stock"]:
        lines += [f"  - {r['name']} ({r['available']})" for r in rep["low_stock"]]
    else:
        lines.append("  None")
    if rep["leaders"]:
        label = "Most borrowed" if len(rep["leaders"]) == 1 else "Most borrowed (TIE)"
        lines.append(f"{label}: " + ", ".join(r["name"] for r in rep["leaders"])
                     + f" ({rep['top_count']})")
    else:
        lines.append("Most borrowed: none (no units currently on loan)")
    return "\n".join(lines)

def save_data(resources, fellows, borrow_records, path=DATA_FILE):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"resources": resources, "fellows": fellows,
                       "borrow_records": borrow_records}, fh, indent=2)
        return True, f"Saved to {path}."
    except OSError as exc:
        return False, f"Could not save: {exc}"


def load_data(path=DATA_FILE):
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data["resources"], data["fellows"], data["borrow_records"]
    except (OSError, ValueError, KeyError):
        return None

def prompt(text):
    return input(text).strip()


def main():
    resources = copy.deepcopy(STARTING_RESOURCES)
    fellows = dict(STARTING_FELLOWS)
    records = []
    loaded = load_data()
    if loaded:
        resources, fellows, records = loaded
        print(f"Loaded saved data from {DATA_FILE}.")
    while True:
        print("1. Add resource")
        print("2. List resources")
        print("3. Borrow")
        print("4. Return")
        print("5. Search")
        print("6. Filter by category")
        print("7. Report")
        print("8. Save to JSON")
        print("9. Load from JSON")
        print("0. Exit")
        try:
            choice = prompt("Choose an option: ")
        except EOFError:
            print("\nInput ended. Goodbye!")
            return
        if choice == "1":
            ok, msg = add_resource(resources, prompt("ID: "), prompt("Name: "),
                                   prompt("Category: "), prompt("Total units: "))
            print(msg)
        elif choice == "2":
            print(list_resources(resources))
        elif choice == "3":
            print(borrow_resource(resources, fellows, records, prompt("Fellow ID: "),
                                  prompt("Resource ID: "), prompt("Quantity: "))[1])
        elif choice == "4":
            print(return_resource(resources, fellows, records, prompt("Fellow ID: "),
                                  prompt("Resource ID: "), prompt("Quantity: "))[1])
        elif choice == "5":
            found = search_by_name(resources, prompt("Name to search: "))
            print("\n".join(format_resource(r) for r in found) if found else "No matches found.")
        elif choice == "6":
            found = filter_by_category(resources, prompt("Category: "))
            print("\n".join(format_resource(r) for r in found) if found else "No resources in that category.")
        elif choice == "7":
            print(format_report(resources, records))
        elif choice == "8":
            print(save_data(resources, fellows, records)[1])
        elif choice == "9":
            loaded = load_data()
            if loaded:
                resources, fellows, records = loaded
                print("Data loaded.")
            else:
                print("No valid saved data found.")
        elif choice == "0":
            print("Goodbye!")
            return
        else:
            print(f"'{choice}' is not a valid option. Enter a number from 0 to 9.")

def run_demo():
    resources = copy.deepcopy(STARTING_RESOURCES)
    fellows = dict(STARTING_FELLOWS)
    records = []

    def show(step, text, result):
        print(f"{step}. {text}\n   -> {'OK' if result[0] else 'REJECTED'}: {result[1]}")

    def stock(rid):
        return find_resource(resources, rid)["available"]

    show(1, "F001 borrows 2 laptops", borrow_resource(resources, fellows, records, "F001", "R001", 2))
    print(f"   Laptop available = {stock('R001')}")
    show(2, "F002 borrows 3 keyboards", borrow_resource(resources, fellows, records, "F002", "R002", 3))
    print(f"   Keyboard available = {stock('R002')}")
    show(3, "F001 returns 1 laptop", return_resource(resources, fellows, records, "F001", "R001", 1))
    print(f"   Laptop available = {stock('R001')}")
    before = copy.deepcopy((resources, records))
    show(4, "F003 requests 4 headsets", borrow_resource(resources, fellows, records, "F003", "R003", 4))
    print(f"   Headset available = {stock('R003')}; state unchanged: {before == (resources, records)}")
    before = copy.deepcopy((resources, records))
    show(5, "F002 tries to return 4 keyboards", return_resource(resources, fellows, records, "F002", "R002", 4))
    print(f"   Keyboard available = {stock('R002')}; state unchanged: {before == (resources, records)}")
    print("6. Search for 'LAPtop'")
    for r in search_by_name(resources, "LAPtop"):
        print("   ->", format_resource(r))
    print("7. Report")
    print(format_report(resources, records))
    before = copy.deepcopy((resources, records))
    print("8. Extra invalid-input tests")
    show("8a", "F001 borrows quantity 'abc'", borrow_resource(resources, fellows, records, "F001", "R001", "abc"))
    show("8b", "F001 borrows quantity -2", borrow_resource(resources, fellows, records, "F001", "R001", "-2"))
    show("8c", "F999 borrows 1 laptop", borrow_resource(resources, fellows, records, "F999", "R001", 1))
    show("8d", "Add duplicate ID R001", add_resource(resources, "R001", "Mouse", "Accessories", 4))
    print(f"   State unchanged after invalid inputs: {before == (resources, records)}")


if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        main()