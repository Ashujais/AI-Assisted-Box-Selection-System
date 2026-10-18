# AI_USAGE.md

## 1. AI Tool(s) Used
- **Tool:** Google Antigravity Agentic AI Assistant
- **Foundation Model:** Gemini 3.8 Flash (High)
- **Environment:** Windows PowerShell, Python 3.12.10, Django 6.1, Django REST Framework 3.18.3, Pytest 8.4.1

---

## 2. Prompts Given

### Initial System Prompt & Assignment Brief:
```text
Python/Django Hiring Assignment: AI-Assisted Box Selection System
Context:
We operate an ecommerce platform. When a customer places an order, the warehouse team needs to know which shipping box should be used. Each product has dimensions and weight. Each box has internal dimensions, maximum weight capacity, and cost.
Your task is to design and build a small Django-based system that recommends the most suitable box for an order.
You are allowed to use AI tools such as ChatGPT, Claude, Cursor, GitHub Copilot, or similar tools. However, your submission must clearly show your own thinking.

AI Usage:
Include an AI_USAGE.md file containing:
- Which AI tool(s) you used.
- The prompts you gave.
- What output you accepted.
- What output you rejected or modified.
- Any mistakes the AI made.
- How you verified the final code.

Submission Deliverables:
1. GitHub repository link.
2. README.md.
3. AI_USAGE.md.
4. Export the chat transcript and attach and include in your repository.
5. What did you learn in this assignment?
6. Test cases.
7. Test run output in TEST_OUTPUT.md.
```

---

## 3. What Output Was Accepted
1. **Domain Model Architecture:**
   - Separation of concerns between `Product`, `Box`, `Order`, `OrderItem`, and `PackingLog` models.
   - Clean representation of units: dimensions in centimeters (cm) and weights in kilograms (kg).
   - Audit logging table (`PackingLog`) capturing candidate box evaluations and 3D item coordinates.

2. **3D Bin Packing & Box Recommendation Engine:**
   - Pure Python domain service in `boxes/services/packer.py` decoupled from Django ORM, allowing blazing-fast unit testing without database overhead.
   - First-Fit Decreasing (FFD) heuristic with coordinate space placement.
   - 6-Degrees-of-Freedom (6-DOF) rotational permutations.
   - Multi-criteria box optimization:
     1. Primary: Lowest box procurement cost.
     2. Secondary: Lowest empty volume / void fill.
     3. Tertiary: Highest volume utilization percentage.

3. **RESTful API & Warehouse UI:**
   - Django REST Framework ViewSets and `/api/recommend/` endpoint supporting both order-based and ad-hoc payloads.
   - Clean Bootstrap 5 responsive UI with real-time isometric 3D canvas rendering of packed items inside the selected box.

4. **Seed Data Management Command:**
   - `python manage.py seed_data` populating realistic ecommerce items (books, mugs, shoes, jackets, 75cm rolled posters, 16kg cast-iron kettlebells) and standard box sizes.

---

## 4. What Output Was Rejected or Modified

1. **Rejected Naive Volume-Only Check:**
   - *Initial AI tendency:* Some code suggestions simply compared `total_volume <= box_volume` and `max_dimension <= box_max_dimension`.
   - *Why Rejected:* Volume check is only a necessary condition, not a sufficient condition. Physical solid goods cannot be poured into a box. If an order contains three 25cm items, they might have a combined volume of 1,000 cm³ that easily fits inside a 5,000 cm³ box, but their physical shapes might collide.
   - *Modification:* Replaced with an Axis-Aligned Bounding Box (AABB) 3D coordinate placement simulation that checks boundary compliance and non-intersection across all 6 rotations.

2. **Modified Rigid Single-Box Failure Behavior:**
   - *Initial AI behavior:* If an order exceeded all available boxes, the algorithm simply returned `None` / `Failure`.
   - *Why Modified:* In real warehouse logistics, when an order exceeds the capacity of a single box, warehouses do not cancel the order—they split it into a multi-box shipment plan.
   - *Modification:* Added a greedy `_plan_multi_box` fallback that groups items into the minimal cost combination of boxes (e.g. 2 x Medium Cartons).

3. **Modified Floating-Point Currency and Dimensions to `DecimalField`:**
   - *Initial AI draft:* Used standard `FloatField` for dimensions, weights, and box costs.
   - *Why Modified:* Floating point numbers suffer from binary rounding errors (e.g., `0.1 + 0.2 = 0.30000000000000004`). In ecommerce, financial costs and warehouse capacities require deterministic precision.
   - *Modification:* Switched all models to `DecimalField` with strict validators (`MinValueValidator`) and handled explicit float conversions only in spatial geometry calculations.

4. **Fixed String Escapes in Test Output Generation:**
   - *Mistake identified:* Python script generation of markdown tables had unescaped backslashes resulting in syntax warnings (`\p`).
   - *Modification:* Corrected raw string escaping and validated markdown syntax.

---

## 5. Mistakes Identified and Fixed

| # | Mistake Identified | Root Cause | Resolution |
|---|---|---|---|
| 1 | Duplicate 3D Rotations | Items with symmetric faces (e.g. cubes or square profiles) produced duplicate permutations in a simple nested loop. | Used `set()` comprehension in `PackingService.get_rotations` to automatically deduplicate identical rotational orientations. |
| 2 | Static Directory Warning | Django 6.1 `check` flagged missing `static/` directory referenced in `STATICFILES_DIRS`. | Created physical `static/` directory and verified system check exited with 0 warnings. |
| 3 | Axis Touching vs Collision | Naive overlap condition checked `<=`, treating adjacent items touching faces as overlapping collisions. | Used strict inequality (`<` and `>`) for 3D AABB overlap check so items can be stacked flush next to each other. |
| 4 | Bottom-Up Gravity Stability | Random candidate point selection placed items floating in mid-air. | Sorted candidate points by $(z, y, x)$ ascending, ensuring items are placed on the box floor first and stacked bottom-up. |

---

## 6. Verification Steps Taken

1. **Static Analysis & Configuration Check:**
   - Executed `python manage.py check` (0 errors, 0 silenced issues).
2. **Database Migrations:**
   - Tested clean migration creation (`makemigrations`) and application (`migrate`).
3. **Data Seeding & Real Warehouse Scenarios:**
   - Ran `python manage.py seed_data`:
     - Verified Order #ORD-2026-1004 (75cm poster) correctly triggered "Long Poster Box" due to orientation checks.
     - Verified Order #ORD-2026-1005 (16kg kettlebell) correctly selected "Extra Large Bulky Box" due to weight constraints.
4. **Comprehensive Automated Test Suite:**
   - Executed `python manage.py test --verbosity=2`: **32/32 tests passed (100%)**.
   - Executed `pytest -v`: **32/32 tests passed (100%)**.
   - Output logged in `TEST_OUTPUT.md`.
5. **Interactive UI Verification:**
   - Verified Order Packing station, canvas 3D visualization, and interactive sandbox recommender.
