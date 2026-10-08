A2.
➜  asses python3 learn2earn.py
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 1
ID: F001
Name: Laptop
Category: Electronics
Total units: 10
Added F001: Laptop (Electronics), 10 units.
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 2
R001   Laptop          Electronics    total=10   available=10
R002   Keyboard        Accessories    total=5    available=5
R003   Headset         Accessories    total=3    available=3
F001   Laptop          Electronics    total=10   available=10
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 3
Fellow ID: F001
Resource ID: R003
Quantity: 1
Ada (F001) borrowed 1 Headset(s). Available now: 2.
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 4
Fellow ID: F001
Resource ID: R003
Quantity: 1
Ada (F001) returned 1 Headset(s). Available now: 3.
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 5
Name to search: Ada
No matches found.
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 5
Name to search: keyboard
R002   Keyboard        Accessories    total=5    available=5
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 6
Category: electronics
R001   Laptop          Electronics    total=10   available=10
F001   Laptop          Electronics    total=10   available=10
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 7
=== INVENTORY REPORT ===
Total units:     28
Available units: 28
Borrowed units:  0
Low stock (fewer than 3 available):
  None
Most borrowed: none (no units currently on loan)
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 8
Saved to learn2earn_data.json.
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 9
Data loaded.
1. Add resource
2. List resources
3. Borrow
4. Return
5. Search
6. Filter by category
7. Report
8. Save to JSON
9. Load from JSON
0. Exit
Choose an option: 0
Goodbye!
➜  asses python3 learn2earn.py --demo
1. F001 borrows 2 laptops
   -> OK: Ada (F001) borrowed 2 Laptop(s). Available now: 8.
   Laptop available = 8
2. F002 borrows 3 keyboards
   -> OK: John (F002) borrowed 3 Keyboard(s). Available now: 2.
   Keyboard available = 2
3. F001 returns 1 laptop
   -> OK: Ada (F001) returned 1 Laptop(s). Available now: 9.
   Laptop available = 9
4. F003 requests 4 headsets
   -> REJECTED: Rejected: requested 4 Headset(s) but only 3 available.
   Headset available = 3; state unchanged: True
5. F002 tries to return 4 keyboards
   -> REJECTED: Rejected: John (F002) has only 3 Keyboard(s) on loan, cannot return 4.
   Keyboard available = 2; state unchanged: True
6. Search for 'LAPtop'
   -> R001   Laptop          Electronics    total=10   available=9
7. Report
=== INVENTORY REPORT ===
Total units:     18
Available units: 14
Borrowed units:  4
Low stock (fewer than 3 available):
  - Keyboard (2)
Most borrowed: Keyboard (3)
8. Extra invalid-input tests
8a. F001 borrows quantity 'abc'
   -> REJECTED: 'abc' is not a valid whole number (use digits only, e.g. 2).
8b. F001 borrows quantity -2
   -> REJECTED: '-2' is not a valid whole number (use digits only, e.g. 2).
8c. F999 borrows 1 laptop
   -> REJECTED: Unknown fellow ID 'F999'.
8d. Add duplicate ID R001
   -> REJECTED: Resource ID R001 already exists.
   State unchanged after invalid inputs: True



A3:

- functions:
1. borrow_resource() 
2. return_resource()
3. add_resource() 
4. search_by_name() 

Inventory: a list of dictionaries with id, name, category, total and available.
Fellows: a dictionary mapping fellow ID to name.
Loans: a list of records {fellow_id, resource_id, borrowed, returned}. A fellow's current loan is the sum of borrowed - returned over their records for that resource. Returns settle the oldest loans first.

Design limitation: loan history is stored only as quantity totals, with no timestamps, due dates or per item tracking. It cannot say which individual laptop a fellow holds or when it is overdue. Fellows are also hard coded, with no option to add new ones. Looking up loans scans the whole records list, which is fine at this scale but would be slow for large data.
