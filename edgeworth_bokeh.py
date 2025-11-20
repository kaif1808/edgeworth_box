import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, BoxZoomTool, ResetTool, PanTool, WheelZoomTool, SaveTool, NumeralTickFormatter
from bokeh.palettes import Spectral6, Turbo256
from scipy.optimize import minimize, brentq, minimize_scalar
import re
import warnings

# --- Configuration & Setup ---
st.set_page_config(
    layout="wide", 
    page_title="Edgeworth Box Simulator (Bokeh)",
    page_icon="📊"
)
warnings.filterwarnings('ignore')

# --- Helper Functions (Math) ---
def parse_latex_to_numpy(latex_str):
    if not latex_str: return "0"
    expr = latex_str.lower().replace("^", "**").replace(r"\cdot", "*")
    replacements = {
        r"\\ln": "np.log", r"\\log": "np.log", r"\\exp": "np.exp",
        r"\\sqrt": "np.sqrt", r"\\min": "np.minimum", r"\\max": "np.maximum",
        r"min": "np.minimum", r"max": "np.maximum",
    }
    for tex, py in replacements.items(): expr = re.sub(tex, py, expr)
    expr = expr.replace("{", "(").replace("}", ")")
    expr = re.sub(r'(\d)([xy])', r'\1*\2', expr)
    return expr

def evaluate_custom_utility(x, y, formula):
    try:
        env = {'x': x, 'y': y, 'np': np, 'abs': np.abs, 'log': np.log, 
               'exp': np.exp, 'sqrt': np.sqrt, 'minimum': np.minimum, 'maximum': np.maximum}
        return eval(parse_latex_to_numpy(formula), {"__builtins__": None}, env)
    except (SyntaxError, NameError, TypeError, ZeroDivisionError):
        return np.zeros_like(x) if isinstance(x, np.ndarray) else 0

def utility_func(x, y, u_type, params):
    x = np.maximum(x, 1e-9)
    y = np.maximum(y, 1e-9)

    if u_type == "Custom (Enter Formula)":
        return evaluate_custom_utility(x, y, params.get('formula', 'x*y'))

    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    a = params.get('a', 0.0)
    b = params.get('b', 0.0)
    
    if u_type == "Cobb-Douglas":
        return (x ** alpha) * (y ** beta)
    elif u_type == "Perfect Substitutes":
        return alpha * x + beta * y
    elif u_type == "Perfect Complements (Min)": 
        return np.minimum(alpha * x, beta * y)
    elif u_type == "Max Preferences (Convex)": 
        return np.maximum(alpha * x, beta * y)
    elif u_type == "Quasi-Linear (Shifted Product)": 
        return (x + a) * (y + b) 
    elif u_type == "Satiation (Bliss Point)": 
        return -1 * ((x - a)**2 + (y - b)**2)
    elif u_type == "Mixed Cobb-Douglas": 
        return x * (y ** alpha)
    return 0

def calculate_mrs(x, y, u_type, params):
    h = 1e-5
    u0 = utility_func(x, y, u_type, params)
    ux = (utility_func(x + h, y, u_type, params) - u0) / h
    uy = (utility_func(x, y + h, u_type, params) - u0) / h
    
    if abs(uy) < 1e-9:
        if abs(ux) < 1e-9: return 0 
        return np.inf
    return ux / uy

# --- Solver Logic ---
def get_demand(u_type, params, px, py, income, total_x_limit=None, total_y_limit=None):
    """Calculate optimal bundle (x, y) given prices and income."""
    alpha = params.get('alpha', 0.5)
    beta = params.get('beta', 0.5)
    
    if u_type in ["Cobb-Douglas", "Mixed Cobb-Douglas"]:
        if u_type == "Mixed Cobb-Douglas":
            eff_alpha, eff_beta = 1.0, alpha
        else:
            eff_alpha, eff_beta = alpha, beta
            
        x = (eff_alpha / (eff_alpha + eff_beta)) * income / px
        y = (eff_beta / (eff_alpha + eff_beta)) * income / py
        return x, y

    elif u_type == "Perfect Substitutes":
        mrs = alpha / beta
        price_ratio = px / py
        
        if price_ratio < mrs - 1e-6:
            return income / px, 0.0
        elif price_ratio > mrs + 1e-6:
            return 0.0, income / py
        else:
            return income / px, 0.0 

    elif u_type == "Perfect Complements (Min)":
        x = income / (px + py * (alpha / beta))
        y = (alpha / beta) * x
        return x, y

    elif u_type == "Quasi-Linear (Shifted Product)":
        a = params.get('a', 0.0)
        b = params.get('b', 0.0)
        I_eff = income + px*a + py*b
        
        X = I_eff / (2 * px)
        Y = I_eff / (2 * py)
        
        x = max(0, X - a)
        y = (income - px*x) / py
        return x, y

    if u_type == "Max Preferences (Convex)":
        x1, y1 = income / px, 0
        x2, y2 = 0, income / py
        u1 = utility_func(x1, y1, u_type, params)
        u2 = utility_func(x2, y2, u_type, params)
        return (x1, y1) if u1 >= u2 else (x2, y2)

    def obj(v): return -utility_func(v[0], v[1], u_type, params)
    def con_budget(v): return income - (px*v[0] + py*v[1])
    
    b_x = (0, total_x_limit) if total_x_limit else (0, None)
    b_y = (0, total_y_limit) if total_y_limit else (0, None)
    
    x0 = income / (2 * px)
    y0 = income / (2 * py)
    
    res = minimize(obj, [x0, y0], bounds=[b_x, b_y], constraints={'type':'ineq', 'fun':con_budget}, tol=1e-5)
    if res.success:
        return res.x[0], res.x[1]
    
    return x0, y0

def solve_walrasian_equilibrium(total_x, total_y, type_A, params_A, type_B, params_B, endow_A, endow_B):
    py = 1.0
    wAx, wAy = endow_A
    wBx, wBy = endow_B
    
    def excess_demand_x(px):
        if px <= 0: return 1e9 
        IA = px * wAx + py * wAy
        IB = px * wBx + py * wBy
        xA, yA = get_demand(type_A, params_A, px, py, IA, total_x, total_y)
        xB, yB = get_demand(type_B, params_B, px, py, IB, total_x, total_y)
        return (xA + xB) - total_x

    low, high = 0.01, 100.0
    try:
        px_eq = brentq(excess_demand_x, low, high, xtol=1e-4)
    except ValueError:
        res = minimize_scalar(lambda p: abs(excess_demand_x(p)), bounds=(0.01, 100.0), method='bounded')
        px_eq = res.x
    
    IA = px_eq * wAx + py * wAy
    xA, yA = get_demand(type_A, params_A, px_eq, py, IA, total_x, total_y)
    return px_eq, (xA, yA)

def solve_contract_curve(total_x, total_y, type_A, params_A, type_B, params_B, uA_w, uB_w, Z_B_min, Z_B_max):
    pareto_x, pareto_y, core_x, core_y = [], [], [], []
    if Z_B_max <= Z_B_min: return pareto_x, pareto_y, core_x, core_y

    steps = 50
    levels_B = np.linspace(Z_B_min, Z_B_max, steps)
    last_x = [total_x / 2, total_y / 2] 

    for ub_val in levels_B:
        def obj(v): return -utility_func(v[0], v[1], type_A, params_A)
        def con(v): return utility_func(total_x - v[0], total_y - v[1], type_B, params_B) - ub_val
        
        bnds = ((0, total_x), (0, total_y))
        res = minimize(obj, last_x, bounds=bnds, constraints={'type':'ineq', 'fun':con}, tol=1e-5)
        
        best_p = None
        best_u = -np.inf
        
        if res.success:
            best_p = res.x
            last_x = res.x
        else:
            starts = [[0, 0], [total_x, total_y], [0, total_y], [total_x, 0]]
            for s in starts:
                res_retry = minimize(obj, s, bounds=bnds, constraints={'type':'ineq', 'fun':con}, tol=1e-5)
                if res_retry.success:
                    ua = utility_func(res_retry.x[0], res_retry.x[1], type_A, params_A)
                    if ua > best_u:
                        best_u = ua
                        best_p = res_retry.x
                        last_x = res_retry.x

        if best_p is not None:
            ua = utility_func(best_p[0], best_p[1], type_A, params_A)
            ub_real = utility_func(total_x - best_p[0], total_y - best_p[1], type_B, params_B)
            
            if ub_real >= ub_val - 0.1: 
                pareto_x.append(best_p[0])
                pareto_y.append(best_p[1])
                if ua >= uA_w - 1e-3 and ub_val >= uB_w - 1e-3:
                    core_x.append(best_p[0])
                    core_y.append(best_p[1])

    if pareto_x:
        p_points = sorted(zip(pareto_x, pareto_y), key=lambda k: k[0])
        pareto_x, pareto_y = zip(*p_points)
        pareto_x, pareto_y = list(pareto_x), list(pareto_y)

    if core_x:
        c_points = sorted(zip(core_x, core_y), key=lambda k: k[0])
        core_x, core_y = zip(*c_points)
        core_x, core_y = list(core_x), list(core_y)

    return pareto_x, pareto_y, core_x, core_y

# --- Contour Helper ---
def compute_contours(X, Y, Z, levels):
    """
    Extract contour lines from grid data using matplotlib.
    Returns a list of dictionaries containing xs and ys for each contour segment.
    """
    contours = []
    fig, ax = plt.subplots()
    CS = ax.contour(X, Y, Z, levels=levels)
    
    for i, collection in enumerate(CS.collections):
        level = CS.levels[i]
        for path in collection.get_paths():
            vertices = path.vertices
            x = vertices[:, 0]
            y = vertices[:, 1]
            contours.append({
                'x': x.tolist(), 
                'y': y.tolist(), 
                'level': level
            })
            
    plt.close(fig)
    return contours

# --- Plotting Logic (Bokeh) ---
def get_theme_config(theme_name, dark_mode):
    if theme_name == "Modern Professional":
        return {
            "bg": "#1a1a1a" if dark_mode else "#ffffff",
            "grid": "#333" if dark_mode else "#e5e7eb",
            "text": "#e0e0e0" if dark_mode else "#374151",
            "A": "#d32f2f", 
            "B": "#1976d2",
            "Pareto": "#2e7d32",
            "Core": "#fbc02d",
            "Lens": "rgba(46, 125, 50, 0.08)",
            "EndowLineA": "#d32f2f",
            "EndowLineB": "#1976d2",
        }
    else: # Classic Textbook
        return {
            "bg": "#121212" if dark_mode else "#fcfcfc",
            "grid": "#444" if dark_mode else "#e0e0e0",
            "text": "white" if dark_mode else "black",
            "A": "#b40000",
            "B": "#0000b4",
            "Pareto": "#388e3c",
            "Core": "#ffa000",
            "Lens": "rgba(100, 100, 100, 0.1)",
            "EndowLineA": "#b40000",
            "EndowLineB": "#0000b4",
        }

def plot_edgeworth_box(Z_A, Z_B, x_vec, y_vec, total_x, total_y, 
                       pareto_x, pareto_y, core_x, core_y, 
                       uA_w, uB_w, endow_x, endow_y, 
                       settings, theme_config, we_data=None):
    
    colors = theme_config
    
    # Create Bokeh Figure
    p = figure(
        title="",
        x_range=(-0.5, total_x + 0.5),
        y_range=(-0.5, total_y + 0.5),
        match_aspect=True,
        tools=[PanTool(), WheelZoomTool(), ResetTool(), SaveTool(), HoverTool()],
        active_scroll="wheel_zoom",
        background_fill_color=colors["bg"],
        border_fill_color=colors["bg"],
        outline_line_color=colors["grid"]
    )
    p.grid.grid_line_color = colors["grid"]
    p.axis.axis_label_text_color = colors["text"]
    p.axis.major_label_text_color = colors["text"]
    p.title.text_color = colors["text"]
    p.xaxis.axis_label = "Good X (Agent A)"
    p.yaxis.axis_label = "Good Y (Agent A)"

    # 1. Exchange Lens (Approximate with high-res contour or points)
    # For true filled polygon, we'd need to extract the intersection. 
    # A simpler approach for Bokeh is to overlay points or use a contour fill approach.
    # Here, let's use a scatter overlay if enabled, but keep it light to avoid lag.
    if settings.get("show_lens", True):
         # Using image to show the lens area is efficient
        lens_mask = np.logical_and(Z_A >= uA_w - 1e-4, Z_B >= uB_w - 1e-4).astype(float)
        # Make it transparent where 0
        lens_img = np.zeros((lens_mask.shape[0], lens_mask.shape[1], 4), dtype=np.uint8)
        # Color: Greenish semi-transparent
        r, g, b = 46, 125, 50
        a = 40 # alpha
        lens_img[lens_mask > 0] = [r, g, b, a]
        
        p.image_rgba(image=[lens_img], x=0, y=0, dw=total_x, dh=total_y)

    # 2. Indifference Curves (Matplotlib extracted)
    X, Y = np.meshgrid(x_vec, y_vec)
    
    if settings.get("show_curves_A", True):
        n_curves_A = settings.get("n_curves", 20)
        levels_A = np.linspace(np.min(Z_A), np.max(Z_A), n_curves_A)
        contours_A = compute_contours(X, Y, Z_A, levels_A)
        
        xs_A = [c['x'] for c in contours_A]
        ys_A = [c['y'] for c in contours_A]
        p.multi_line(xs_A, ys_A, color=colors["A"], line_width=1, line_alpha=0.6, legend_label="Agent A IC")

    if settings.get("show_curves_B", True):
        n_curves_B = settings.get("n_curves", 20)
        levels_B = np.linspace(np.min(Z_B), np.max(Z_B), n_curves_B)
        contours_B = compute_contours(X, Y, Z_B, levels_B)
        
        xs_B = [c['x'] for c in contours_B]
        ys_B = [c['y'] for c in contours_B]
        p.multi_line(xs_B, ys_B, color=colors["B"], line_width=1, line_alpha=0.6, line_dash="dashed", legend_label="Agent B IC")

    # 3. Endowment ICs
    if settings.get("show_endow", True):
        # Agent A Endowment Curve
        contours_A_w = compute_contours(X, Y, Z_A, [uA_w])
        if contours_A_w:
            p.multi_line([c['x'] for c in contours_A_w], [c['y'] for c in contours_A_w], 
                         color=colors["EndowLineA"], line_width=2.5, legend_label="Start Utility A")
            
        # Agent B Endowment Curve
        contours_B_w = compute_contours(X, Y, Z_B, [uB_w])
        if contours_B_w:
            p.multi_line([c['x'] for c in contours_B_w], [c['y'] for c in contours_B_w], 
                         color=colors["EndowLineB"], line_width=2.5, line_dash="dashed", legend_label="Start Utility B")

    # 4. Pareto & Core
    if settings.get("show_pareto", True) and pareto_x:
        p.line(pareto_x, pareto_y, line_color=colors["Pareto"], line_width=3, legend_label="Pareto Set")
    
    if settings.get("show_core", True) and core_x:
        p.line(core_x, core_y, line_color=colors["Core"], line_width=6, legend_label="Core")

    # 5. Walrasian Equilibrium
    if settings.get("show_we", False) and we_data:
        px_eq, (xA_eq, yA_eq) = we_data
        
        # Budget Line
        x_range_line = np.array([0, total_x])
        y_line = endow_y - px_eq * (x_range_line - endow_x)
        # Clip for visual niceness (simple clip)
        p.line(x_range_line, y_line, line_color=colors["text"], line_width=2, line_dash="dashdot", legend_label=f"Budget (p={px_eq:.2f})")
        
        # WE Point
        p.scatter([xA_eq], [yA_eq], size=12, color="#9c27b0", marker="diamond", legend_label="Walrasian Eq.")

    # 6. Endowment Point
    if settings.get("show_endow", True):
        p.scatter([endow_x], [endow_y], size=10, color=colors["text"], marker="circle", legend_label="Endowment")

    p.legend.location = "top_right"
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.8
    
    return p

# --- Main App (UI) ---

# Initialize Session State for sliders if not exists
def init_state(key, default):
    if key not in st.session_state: st.session_state[key] = default

init_state("dim_x", 10.0)
init_state("dim_y", 10.0)
init_state("endow_x", 7.0)
init_state("endow_y", 6.0)

st.sidebar.header("Configuration")
theme_name = st.sidebar.selectbox("Theme", ["Modern Professional", "Classic Textbook"])
dark_mode = st.sidebar.checkbox("Dark Mode", False)

# Main Layout
col_config, col_viz = st.columns([1, 3])

with col_config:
    st.subheader("1. Environment")
    total_x = st.number_input("Total X", 1.0, 100.0, st.session_state["dim_x"])
    total_y = st.number_input("Total Y", 1.0, 100.0, st.session_state["dim_y"])
    
    st.subheader("2. Endowment")
    endow_x = st.slider("Agent A: X", 0.0, total_x, st.session_state["endow_x"])
    endow_y = st.slider("Agent A: Y", 0.0, total_y, st.session_state["endow_y"])
    
    endow_B_x = total_x - endow_x
    endow_B_y = total_y - endow_y
    
    st.subheader("3. Preferences")
    with st.expander("Agent A", expanded=True):
        type_A = st.selectbox("Type A", ["Cobb-Douglas", "Perfect Substitutes", "Perfect Complements (Min)", "Quasi-Linear (Shifted Product)", "Satiation (Bliss Point)"], index=0)
        params_A = {}
        if type_A == "Cobb-Douglas":
            params_A["alpha"] = st.slider("Alpha A", 0.1, 5.0, 1.0)
            params_A["beta"] = st.slider("Beta A", 0.1, 5.0, 1.0)
        elif type_A == "Perfect Substitutes":
            params_A["alpha"] = st.slider("Alpha A", 0.1, 5.0, 1.0)
            params_A["beta"] = st.slider("Beta A", 0.1, 5.0, 1.0)
        elif type_A == "Perfect Complements (Min)":
            params_A["alpha"] = st.slider("Alpha A", 0.1, 5.0, 1.0)
            params_A["beta"] = st.slider("Beta A", 0.1, 5.0, 1.0)
        elif type_A == "Quasi-Linear (Shifted Product)":
             params_A["a"] = st.slider("Shift X (a)", -5.0, 5.0, 0.0)
             params_A["b"] = st.slider("Shift Y (b)", -5.0, 5.0, 0.0)
        elif type_A == "Satiation (Bliss Point)":
             params_A["a"] = st.slider("Bliss X", 0.0, total_x, total_x/2)
             params_A["b"] = st.slider("Bliss Y", 0.0, total_y, total_y/2)

    with st.expander("Agent B", expanded=False):
        type_B = st.selectbox("Type B", ["Cobb-Douglas", "Perfect Substitutes", "Perfect Complements (Min)", "Quasi-Linear (Shifted Product)"], index=0)
        params_B = {}
        if type_B == "Cobb-Douglas":
            params_B["alpha"] = st.slider("Alpha B", 0.1, 5.0, 1.0)
            params_B["beta"] = st.slider("Beta B", 0.1, 5.0, 1.0)
        elif type_B == "Perfect Substitutes":
            params_B["alpha"] = st.slider("Alpha B", 0.1, 5.0, 1.0)
            params_B["beta"] = st.slider("Beta B", 0.1, 5.0, 1.0)
        elif type_B == "Perfect Complements (Min)":
            params_B["alpha"] = st.slider("Alpha B", 0.1, 5.0, 1.0)
            params_B["beta"] = st.slider("Beta B", 0.1, 5.0, 1.0)
        elif type_B == "Quasi-Linear (Shifted Product)":
             params_B["a"] = st.slider("Shift X (a) B", -5.0, 5.0, 0.0)
             params_B["b"] = st.slider("Shift Y (b) B", -5.0, 5.0, 0.0)

    st.subheader("4. View")
    vis_settings = {}
    vis_settings["show_lens"] = st.checkbox("Lens", True)
    vis_settings["show_pareto"] = st.checkbox("Pareto", True)
    vis_settings["show_core"] = st.checkbox("Core", True)
    vis_settings["show_endow"] = st.checkbox("Endowment", True)
    vis_settings["show_we"] = st.checkbox("Walrasian Eq.", False)
    vis_settings["n_curves"] = st.slider("Curve Density", 10, 50, 25)

# Calculation
N = 100
x_vec = np.linspace(0, total_x, N)
y_vec = np.linspace(0, total_y, N)
X, Y = np.meshgrid(x_vec, y_vec)

Z_A = utility_func(X, Y, type_A, params_A)
if isinstance(Z_A, (float, int)): Z_A = np.full_like(X, Z_A)

Z_B = utility_func(total_x - X, total_y - Y, type_B, params_B)
if isinstance(Z_B, (float, int)): Z_B = np.full_like(X, Z_B)

uA_w = utility_func(endow_x, endow_y, type_A, params_A)
uB_w = utility_func(endow_B_x, endow_B_y, type_B, params_B)

pareto_x, pareto_y, core_x, core_y = solve_contract_curve(
    total_x, total_y, type_A, params_A, type_B, params_B, uA_w, uB_w, np.min(Z_B), np.max(Z_B)
)

we_data = solve_walrasian_equilibrium(
    total_x, total_y, type_A, params_A, type_B, params_B, (endow_x, endow_y), (endow_B_x, endow_B_y)
)

# Visualization
with col_viz:
    theme_config = get_theme_config(theme_name, dark_mode)
    p = plot_edgeworth_box(Z_A, Z_B, x_vec, y_vec, total_x, total_y, 
                           pareto_x, pareto_y, core_x, core_y, 
                           uA_w, uB_w, endow_x, endow_y, 
                           vis_settings, theme_config, we_data)
    st.bokeh_chart(p, use_container_width=True)
    
    # Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Utility A", f"{uA_w:.2f}")
    m2.metric("Utility B", f"{uB_w:.2f}")
    
    if we_data:
        px, (eq_x, eq_y) = we_data
        m3.metric("Eq. Price Ratio", f"{px:.2f}")
        m4.metric("Eq. Allocation A", f"({eq_x:.2f}, {eq_y:.2f})")

