# Auto-Shopper: Intelligent E-commerce Agent

[![Demo Video](https://img.youtube.com/vi/4xfdCCGYcuQ/maxresdefault.jpg)](https://www.youtube.com/watch?v=4xfdCCGYcuQ)

---

## Overview
Auto-Shopper is an intelligent e-commerce automation agent built using **browser-use**, enabling fully autonomous multi-store grocery shopping on **Instacart**.  
It performs store discovery, real-time product comparison, substitution logic, and structured output generation — all driven by an AI workflow.

---

## 🔧 Technologies Used

- **Python 3.11+**
- **browser-use** (AI browser automation)
- **Chrome DevTools Protocol (CDP)**  
- **Pydantic** for typed data validation  
- **AsyncIO** for multi-store orchestration  
- **uv** for environment + dependency management  
- **YouTube Demo** for project setup & walkthrough  

---

## 🚀 Key Features (Deep Technical Breakdown)

### 🏬 1. Dynamic Instacart Store Discovery
Unlike earlier versions that required manually hardcoded store lists, this version automatically determines which grocery stores are available in the user’s region on Instacart.  
This ensures:
- Geographic adaptability  
- No manual configuration required  
- Automatic scaling to new markets  

### 🧠 2. Preference-Aware Item Selection
The agent intelligently prioritizes products matching the user’s shopping preference:
- organic  
- gluten-free  
- cheapest  
- or any custom search preference  

After filtering items by preference, additional ranking rules are applied:
1. Lowest price  
2. Highest rating  
3. Closest matching size/quantity  

### 🔄 3. Advanced Substitution Logic  
If an item is unavailable:
- The agent marks `in_stock=False`
- Searches again for the closest acceptable alternative  
- Requires a mandatory human-readable substitution note

### 📦 4. Full Structured Output with Pydantic  
All results are validated through strongly-typed Pydantic models:
- GroceryItem  
- GroceryCart  
- AvailableStores  

The output is guaranteed to be clean, machine-parseable JSON every time.

### 🛒 5. Multi-Store Price Comparison
Auto-Shopper runs the full agent flow for **each store**, collecting:
- Cart items  
- Total price  
- Stock/substitution data  
- Ratings & brands  

Then it compares totals and selects the cheapest cart.

### 🖥️ 6. Command-Line Interface  
Run the automation via simple flags:

```
--items
--preference
```

Example:
```
uv run main.py --items "milk, eggs" --preference "organic"
```

### 💾 7. Persistent JSON Output
Each run saves the winning cart to a timestamped file:
```
best_cart_results_YYYYMMDD_HHMMSS.json
```

Perfect for:
- Data processing  
- Cost analytics  
- Debugging shopping logic  

---

## ▶️ Quick Start

### 1. Install Dependencies  
```bash
cd shopping
uv sync
```

### 2. Add Your Browser-Use API Key  
```bash
cp .env.example .env
```

Edit:
```
BROWSER_USE_API_KEY=your-key-here
```

### 3. Launch Chrome with Remote Debugging  
```bash
python launch_chrome_debug.py
```

Keep this window **open**.

---

## 🧪 Usage Examples

### Cheapest organic items
```bash
uv run main.py --items "milk, eggs, bread" --preference "organic"
```

### Cheapest overall
```bash
uv run main.py --items "apples, cheddar cheese, toothpaste"
```

---

## 🔄 Behind the Scenes: Execution Flow

1. Instacart store discovery  
2. Browser controlled via CDP  
3. AI-driven navigation, searching, filtering, sorting  
4. Preference ranking → tie-breaking via rating  
5. Substitution logic  
6. Pydantic validation  
7. Multi-store total cost comparison  
8. JSON export  

---

## 🧩 JSON Output Example

```json
{
  "store_name": "Safeway",
  "total_cost": 21.57,
  "items": [
    {
      "name": "Organic Whole Milk",
      "price": 5.99,
      "brand": "Horizon",
      "rating": 4.8,
      "in_stock": true,
      "notes": null,
      "url": "..."
    },
    {
      "name": "Wheat Bread (Substituted)",
      "price": 3.49,
      "brand": "Oroweat",
      "rating": 4.5,
      "in_stock": false,
      "notes": "Original organic bread was out of stock, substituted with Oroweat 100% whole wheat.",
      "url": "..."
    }
  ]
}
```

---

## 🎥 Reference Video  
**Setup and Demo:**  
https://www.youtube.com/watch?v=4xfdCCGYcuQ

---

## 🛠 Troubleshooting

### Chrome won’t launch  
Check your Chrome path in `launch_chrome_debug.py`.

### CDP connection error  
Ensure Chrome is running & port **9222** is not in use.

### Agent can’t locate items  
Instacart UI may have changed — update selectors or prompts.

---

