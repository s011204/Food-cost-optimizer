import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import linprog
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="MacroMate", page_icon="💪", layout="wide")

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2d6a4f 0%, #40916c 50%, #52b788 100%);
        padding: 2rem 2rem 1.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2.4rem; }
    .main-header p  { margin: 0.4rem 0 0; opacity: .85; font-size: 1rem; }
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #0c5460;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
    }
    .result-header {
        background: linear-gradient(90deg, #40916c, #52b788);
        color: white;
        padding: 0.8rem 1.2rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .food-tag {
        display: inline-block;
        background: #e9f5ee;
        border: 1px solid #40916c;
        border-radius: 20px;
        padding: 0.2rem 0.7rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        color: #2d6a4f;
    }
</style>
""", unsafe_allow_html=True)

# ── Built-in sample foods ─────────────────────────────────────────────────────
SAMPLE_FOODS = pd.DataFrame([
    {"food": "Chicken Breast",  "calories": 165, "protein_g": 31,  "carbs_g": 0,  "fat_g": 3.6,  "fiber_g": 0,    "price_per_100g": 1.20},
    {"food": "Eggs",            "calories": 155, "protein_g": 13,  "carbs_g": 1.1,"fat_g": 11,   "fiber_g": 0,    "price_per_100g": 0.28},
    {"food": "Oats",            "calories": 389, "protein_g": 17,  "carbs_g": 66, "fat_g": 7,    "fiber_g": 10,   "price_per_100g": 0.15},
    {"food": "Brown Rice",      "calories": 216, "protein_g": 5,   "carbs_g": 45, "fat_g": 1.8,  "fiber_g": 3.5,  "price_per_100g": 0.12},
    {"food": "Broccoli",        "calories": 34,  "protein_g": 2.8, "carbs_g": 7,  "fat_g": 0.4,  "fiber_g": 2.6,  "price_per_100g": 0.40},
    {"food": "Spinach",         "calories": 23,  "protein_g": 2.9, "carbs_g": 3.6,"fat_g": 0.4,  "fiber_g": 2.2,  "price_per_100g": 0.45},
    {"food": "Sweet Potato",    "calories": 86,  "protein_g": 1.6, "carbs_g": 20, "fat_g": 0.1,  "fiber_g": 3,    "price_per_100g": 0.30},
    {"food": "Salmon",          "calories": 208, "protein_g": 20,  "carbs_g": 0,  "fat_g": 13,   "fiber_g": 0,    "price_per_100g": 2.50},
    {"food": "Tuna (canned)",   "calories": 116, "protein_g": 26,  "carbs_g": 0,  "fat_g": 1,    "fiber_g": 0,    "price_per_100g": 0.80},
    {"food": "Greek Yogurt",    "calories": 59,  "protein_g": 10,  "carbs_g": 3.6,"fat_g": 0.4,  "fiber_g": 0,    "price_per_100g": 0.60},
    {"food": "Lentils",         "calories": 116, "protein_g": 9,   "carbs_g": 20, "fat_g": 0.4,  "fiber_g": 7.9,  "price_per_100g": 0.18},
    {"food": "Black Beans",     "calories": 132, "protein_g": 8.9, "carbs_g": 24, "fat_g": 0.5,  "fiber_g": 8.7,  "price_per_100g": 0.20},
    {"food": "Almonds",         "calories": 579, "protein_g": 21,  "carbs_g": 22, "fat_g": 50,   "fiber_g": 12.5, "price_per_100g": 1.80},
    {"food": "Banana",          "calories": 89,  "protein_g": 1.1, "carbs_g": 23, "fat_g": 0.3,  "fiber_g": 2.6,  "price_per_100g": 0.20},
    {"food": "Whole Milk",      "calories": 61,  "protein_g": 3.2, "carbs_g": 4.8,"fat_g": 3.3,  "fiber_g": 0,    "price_per_100g": 0.10},
    {"food": "Cottage Cheese",  "calories": 98,  "protein_g": 11,  "carbs_g": 3.4,"fat_g": 4.3,  "fiber_g": 0,    "price_per_100g": 0.55},
    {"food": "Quinoa",          "calories": 120, "protein_g": 4.4, "carbs_g": 21, "fat_g": 1.9,  "fiber_g": 2.8,  "price_per_100g": 0.80},
    {"food": "Avocado",         "calories": 160, "protein_g": 2,   "carbs_g": 9,  "fat_g": 15,   "fiber_g": 6.7,  "price_per_100g": 0.90},
    {"food": "Pasta",           "calories": 371, "protein_g": 13,  "carbs_g": 74, "fat_g": 1.5,  "fiber_g": 3.2,  "price_per_100g": 0.14},
    {"food": "Beef (lean)",     "calories": 250, "protein_g": 26,  "carbs_g": 0,  "fat_g": 15,   "fiber_g": 0,    "price_per_100g": 1.80},
    {"food": "Tofu",            "calories": 76,  "protein_g": 8,   "carbs_g": 1.9,"fat_g": 4.8,  "fiber_g": 0.3,  "price_per_100g": 0.55},
    {"food": "Peanut Butter",   "calories": 588, "protein_g": 25,  "carbs_g": 20, "fat_g": 50,   "fiber_g": 6,    "price_per_100g": 0.45},
    {"food": "Whey Protein",    "calories": 400, "protein_g": 80,  "carbs_g": 8,  "fat_g": 4,    "fiber_g": 0,    "price_per_100g": 1.50},
    {"food": "Apple",           "calories": 52,  "protein_g": 0.3, "carbs_g": 14, "fat_g": 0.2,  "fiber_g": 2.4,  "price_per_100g": 0.35},
    {"food": "Olive Oil",       "calories": 884, "protein_g": 0,   "carbs_g": 0,  "fat_g": 100,  "fiber_g": 0,    "price_per_100g": 1.20},
])

# ── Goal definitions ──────────────────────────────────────────────────────────
GOALS = {
    "🏃 Sporty Student": {
        "description": "High protein on a tight budget — optimised for active students",
        "calories_min": 2200, "calories_max": 2800,
        "protein_min": 140,   "protein_max": 999,
        "carbs_min":   220,   "carbs_max":   400,
        "fat_min":     55,    "fat_max":     95,
        "fiber_min":   25,    "fiber_max":   999,
    },
    "💪 Muscle Building": {
        "description": "High protein & calorie surplus to support muscle growth",
        "calories_min": 2800, "calories_max": 3500,
        "protein_min": 180,   "protein_max": 999,
        "carbs_min":   300,   "carbs_max":   500,
        "fat_min":     70,    "fat_max":     120,
        "fiber_min":   25,    "fiber_max":   999,
    },
    "🔥 Weight Loss": {
        "description": "Calorie deficit with high protein to preserve muscle",
        "calories_min": 1200, "calories_max": 1600,
        "protein_min": 100,   "protein_max": 999,
        "carbs_min":   80,    "carbs_max":   160,
        "fat_min":     30,    "fat_max":     55,
        "fiber_min":   30,    "fiber_max":   999,
    },
    "🥗 Healthy Balanced": {
        "description": "Balanced macros for general health and wellbeing",
        "calories_min": 1800, "calories_max": 2200,
        "protein_min": 50,    "protein_max": 200,
        "carbs_min":   200,   "carbs_max":   300,
        "fat_min":     44,    "fat_max":     78,
        "fiber_min":   25,    "fiber_max":   999,
    },
    "🧘 Low Carb / Keto": {
        "description": "Very low carbs, high fat, moderate protein",
        "calories_min": 1600, "calories_max": 2200,
        "protein_min": 100,   "protein_max": 999,
        "carbs_min":   0,     "carbs_max":   50,
        "fat_min":     110,   "fat_max":     999,
        "fiber_min":   20,    "fiber_max":   999,
    },
}

# ── API helper ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def search_open_food_facts(query: str, max_results: int = 20) -> pd.DataFrame:
    try:
        resp = requests.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={
                "search_terms": query,
                "json": True,
                "page_size": max_results,
                "fields": "product_name,nutriments",
            },
            timeout=8,
        )
        products = resp.json().get("products", [])
    except Exception:
        return pd.DataFrame()

    rows = []
    for p in products:
        n    = p.get("nutriments", {})
        name = p.get("product_name", "").strip()
        cal  = n.get("energy-kcal_100g")
        pro  = n.get("proteins_100g")
        carb = n.get("carbohydrates_100g")
        fat  = n.get("fat_100g")
        fib  = n.get("fiber_100g", 0) or 0

        if not name or not all([cal, pro is not None, carb is not None, fat is not None]):
            continue
        if any(v < 0 for v in [cal, pro, carb, fat, fib]):
            continue

        rows.append({
            "food": name[:60],
            "calories": round(float(cal), 1),
            "protein_g": round(float(pro), 1),
            "carbs_g": round(float(carb), 1),
            "fat_g": round(float(fat), 1),
            "fiber_g": round(float(fib), 1),
            "price_per_100g": 0.0,
        })
    return pd.DataFrame(rows).drop_duplicates(subset="food").head(10)

# ── LP optimizer ──────────────────────────────────────────────────────────────
def optimize_diet(df: pd.DataFrame, goal: dict, max_portion: float = 8.0):
    n   = len(df)
    c   = df["price_per_100g"].values
    cal = df["calories"].values
    pro = df["protein_g"].values
    crb = df["carbs_g"].values
    fat = df["fat_g"].values
    fib = df["fiber_g"].values
    g   = goal

    A_ub = [
        -cal,  cal,
        -pro,  pro,
        -crb,  crb,
        -fat,  fat,
        -fib,  fib,
    ]
    b_ub = [
        -g["calories_min"], g["calories_max"],
        -g["protein_min"],  g["protein_max"],
        -g["carbs_min"],    g["carbs_max"],
        -g["fat_min"],      g["fat_max"],
        -g["fiber_min"],    g["fiber_max"],
    ]
    return linprog(c, A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                   bounds=[(0, max_portion)] * n, method="highs")

def build_result_df(df, x_vals, threshold=0.05):
    rows = []
    for i, row in df.iterrows():
        qty = x_vals[i]
        if qty < threshold:
            continue
        rows.append({
            "Food": row["food"],
            "Amount (g)": round(qty * 100, 1),
            "Calories": round(row["calories"] * qty, 1),
            "Protein (g)": round(row["protein_g"] * qty, 1),
            "Carbs (g)": round(row["carbs_g"] * qty, 1),
            "Fat (g)": round(row["fat_g"] * qty, 1),
            "Fiber (g)": round(row["fiber_g"] * qty, 1),
            "Cost (€)": round(row["price_per_100g"] * qty, 3),
        })
    return pd.DataFrame(rows)

# ── Session state init ────────────────────────────────────────────────────────
if "food_list" not in st.session_state:
    st.session_state.food_list = SAMPLE_FOODS.copy()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>💪 MacroMate</h1>
    <p>Find the cheapest daily meal plan that hits your nutritional goals — powered by linear programming + Open Food Facts.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    st.subheader("1. Choose your goal")
    goal_name = st.selectbox("Eating goal", list(GOALS.keys()))

    st.subheader("2. Max portion size")
    max_portion = st.slider("Max per food (100g servings/day)", 1, 20, 8,
                            help="Prevents the solver loading up on just one food.")

    st.subheader("3. Override targets (optional)")
    with st.expander("Customise nutritional targets"):
        goal_copy = dict(GOALS[goal_name])
        goal_copy["calories_min"] = st.number_input("Min calories",  value=goal_copy["calories_min"], step=50)
        goal_copy["calories_max"] = st.number_input("Max calories",  value=goal_copy["calories_max"], step=50)
        goal_copy["protein_min"]  = st.number_input("Min protein (g)", value=goal_copy["protein_min"], step=5)
        goal_copy["fat_max"]      = st.number_input("Max fat (g)",    value=goal_copy["fat_max"], step=5)
        goal_copy["carbs_max"]    = st.number_input("Max carbs (g)",  value=goal_copy["carbs_max"], step=10)
        goal_copy["fiber_min"]    = st.number_input("Min fiber (g)",  value=goal_copy["fiber_min"], step=2)
    selected_goal = goal_copy

    st.markdown("---")
    st.subheader("4. Upload your own CSV")
    uploaded = st.file_uploader("Optional — overrides the food list below", type=["csv"])
    if uploaded:
        try:
            up_df = pd.read_csv(uploaded)
            up_df.columns = up_df.columns.str.strip().str.lower().str.replace(" ", "_")
            st.session_state.food_list = up_df
            st.success(f"Loaded {len(up_df)} foods from CSV.")
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

    st.markdown("---")
    optimize_btn = st.button("🚀 Optimize!", use_container_width=True, type="primary")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_search, tab_list, tab_result = st.tabs(["🔍 Search Foods", "🥘 My Food List", "📊 Results"])

# ── Tab 1: Search Open Food Facts ─────────────────────────────────────────────
with tab_search:
    st.subheader("Search Open Food Facts")
    st.caption("Search any food and add it to your list. You'll need to enter the price manually.")

    col_q, col_btn = st.columns([4, 1])
    with col_q:
        query = st.text_input("Search food", placeholder="e.g. chicken breast, oats, protein bar…")
    with col_btn:
        st.write("")
        st.write("")
        search_btn = st.button("Search 🔎")

    if search_btn and query:
        with st.spinner("Fetching from Open Food Facts…"):
            results = search_open_food_facts(query)

        if results.empty:
            st.warning("No results found — try a different search term, or check your internet connection.")
        else:
            st.success(f"Found {len(results)} products. Set prices and add to your list.")
            for idx, row in results.iterrows():
                with st.expander(f"**{row['food']}** — {row['calories']:.0f} kcal | "
                                 f"P: {row['protein_g']}g | C: {row['carbs_g']}g | F: {row['fat_g']}g"):
                    price = st.number_input(
                        "Price per 100g (€)", min_value=0.0, value=0.50, step=0.05,
                        key=f"price_{idx}_{query}"
                    )
                    if st.button("➕ Add to my list", key=f"add_{idx}_{query}"):
                        new_row = row.to_dict()
                        new_row["price_per_100g"] = price
                        new_entry = pd.DataFrame([new_row])
                        st.session_state.food_list = pd.concat(
                            [st.session_state.food_list, new_entry], ignore_index=True
                        ).drop_duplicates(subset="food")
                        st.success(f"✅ Added {row['food']} at €{price}/100g")

# ── Tab 2: My Food List ───────────────────────────────────────────────────────
with tab_list:
    st.subheader(f"My Food List ({len(st.session_state.food_list)} items)")

    col_reset, col_dl = st.columns([1, 1])
    with col_reset:
        if st.button("🔄 Reset to sample foods"):
            st.session_state.food_list = SAMPLE_FOODS.copy()
            st.rerun()
    with col_dl:
        csv_dl = st.session_state.food_list.to_csv(index=False).encode()
        st.download_button("📥 Download as CSV", csv_dl, "my_foods.csv", "text/csv")

    # Editable price column
    st.caption("You can edit prices directly in the table below.")
    edited = st.data_editor(
        st.session_state.food_list,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "price_per_100g": st.column_config.NumberColumn("Price/100g (€)", format="€%.2f", min_value=0.0),
            "calories":       st.column_config.NumberColumn("Calories",        format="%.0f"),
            "protein_g":      st.column_config.NumberColumn("Protein (g)",     format="%.1f"),
            "carbs_g":        st.column_config.NumberColumn("Carbs (g)",       format="%.1f"),
            "fat_g":          st.column_config.NumberColumn("Fat (g)",         format="%.1f"),
            "fiber_g":        st.column_config.NumberColumn("Fiber (g)",       format="%.1f"),
        },
        hide_index=True,
    )
    st.session_state.food_list = edited

# ── Tab 3: Results ────────────────────────────────────────────────────────────
with tab_result:
    if not optimize_btn:
        st.markdown("""
        <div class="info-box">
            👈 Set your goal in the sidebar and hit <b>Optimize!</b> to get your cheapest meal plan.
        </div>
        """, unsafe_allow_html=True)
    else:
        df = st.session_state.food_list.reset_index(drop=True)

        # Check prices are set
        zero_price = df[df["price_per_100g"] <= 0]
        if len(zero_price) > 0:
            st.warning(f"⚠️ {len(zero_price)} foods have €0 price and will be treated as free — "
                       f"set prices in 'My Food List' for accurate results.")

        if len(df) < 3:
            st.error("Add at least 3 foods to your list before optimizing.")
        else:
            with st.spinner("Solving…"):
                res = optimize_diet(df, selected_goal, max_portion)

            if res.status == 0:
                result_df = build_result_df(df, res.x)

                st.markdown("""<div class="result-header">
                    <h3 style="margin:0">✅ Optimal plan found!</h3>
                </div>""", unsafe_allow_html=True)

                total_cost    = result_df["Cost (€)"].sum()
                total_cal     = result_df["Calories"].sum()
                total_protein = result_df["Protein (g)"].sum()
                total_carbs   = result_df["Carbs (g)"].sum()
                total_fat     = result_df["Fat (g)"].sum()
                total_fiber   = result_df["Fiber (g)"].sum()

                k1, k2, k3, k4, k5, k6 = st.columns(6)
                k1.metric("💰 Daily cost",  f"€{total_cost:.2f}")
                k2.metric("🔥 Calories",    f"{total_cal:.0f} kcal")
                k3.metric("🥩 Protein",     f"{total_protein:.0f} g")
                k4.metric("🌾 Carbs",       f"{total_carbs:.0f} g")
                k5.metric("🧈 Fat",         f"{total_fat:.0f} g")
                k6.metric("🌿 Fiber",       f"{total_fiber:.0f} g")

                st.markdown("---")
                st.subheader("📋 Daily food plan")
                st.dataframe(
                    result_df.style
                        .format({
                            "Amount (g)": "{:.0f}", "Calories": "{:.0f}",
                            "Protein (g)": "{:.1f}", "Carbs (g)": "{:.1f}",
                            "Fat (g)": "{:.1f}", "Fiber (g)": "{:.1f}",
                            "Cost (€)": "€{:.3f}",
                        })
                        .bar(subset=["Amount (g)"], color="#b7e4c7")
                        .bar(subset=["Cost (€)"],   color="#ffd6a5"),
                    use_container_width=True,
                )

                st.markdown("---")
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📅 Cost projection")
                    proj = pd.DataFrame({
                        "Period": ["Daily", "Weekly", "Monthly (30d)", "Yearly"],
                        "Cost": [total_cost, total_cost*7, total_cost*30, total_cost*365],
                    })
                    proj["Cost"] = proj["Cost"].map("€{:.2f}".format)
                    st.table(proj.set_index("Period"))

                with c2:
                    st.subheader("🍽️ Macro split")
                    macro_df = pd.DataFrame({
                        "Macro": ["Protein", "Carbs", "Fat"],
                        "Calories from macro": [total_protein*4, total_carbs*4, total_fat*9],
                    })
                    macro_df["% of total"] = (
                        macro_df["Calories from macro"] / macro_df["Calories from macro"].sum() * 100
                    ).round(1)
                    st.dataframe(macro_df.set_index("Macro"), use_container_width=True)

                csv_out = result_df.to_csv(index=False).encode()
                st.download_button("📥 Download meal plan", csv_out, "meal_plan.csv", "text/csv")

            elif res.status == 2:
                st.error("""
                ❌ **No feasible solution found.**

                The food list can't satisfy all constraints at once. Try:
                - Adding more foods (especially high-protein ones like chicken, tuna, whey)
                - Loosening the nutritional targets in the sidebar
                - Increasing the max portion size
                """)
            else:
                st.warning(f"Solver status {res.status}: {res.message}")