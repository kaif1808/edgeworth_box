import streamlit as st
import numpy as np
import ui.state
import ui.sidebar
import core.economics as eco

# 1. Page Config
st.set_page_config(
    layout="wide", 
    page_title="Edgeworth Box Simulator",
    page_icon="📊"
)

# 2. Initialize State
ui.state.init_session_state()

# 3. Render Sidebar
ui.sidebar.render_sidebar()

# 4. Main Content
st.title("Edgeworth Box Simulator")
st.markdown("Interactive tool for analyzing exchange efficiency, contract curves, and the core.")

# Retrieve State
total_x = st.session_state["total_x"]
total_y = st.session_state["total_y"]
endow_A = (st.session_state["endow_x"], st.session_state["endow_y"])
endow_B = (total_x - endow_A[0], total_y - endow_A[1])

type_A = st.session_state["type_A"]
params_A = st.session_state["params_A"]
type_B = st.session_state["type_B"]
params_B = st.session_state["params_B"]

# --- Calculations ---

# Utility at Endowment
uA_w = eco.utility_func(endow_A[0], endow_A[1], type_A, params_A)
uB_w = eco.utility_func(endow_B[0], endow_B[1], type_B, params_B)

# MRS at Endowment
mrs_A = eco.calculate_mrs(endow_A[0], endow_A[1], type_A, params_A)
mrs_B = eco.calculate_mrs(endow_B[0], endow_B[1], type_B, params_B)

# Walrasian Equilibrium
we_data = eco.solve_walrasian_equilibrium(
    total_x, total_y, type_A, params_A, type_B, params_B, endow_A, endow_B
)

# Contract Curve Calculation
# We need a rough estimate of Z_B min/max to guide the contract curve solver
N = 50 
x_vec = np.linspace(0, total_x, N)
y_vec = np.linspace(0, total_y, N)
X, Y = np.meshgrid(x_vec, y_vec)

try:
    Z_B = eco.utility_func(total_x - X, total_y - Y, type_B, params_B)
    z_b_min, z_b_max = np.min(Z_B), np.max(Z_B)
except:
    z_b_min, z_b_max = 0, 100

pareto_x, pareto_y, core_x, core_y = eco.solve_contract_curve(
    total_x, total_y, type_A, params_A, type_B, params_B, uA_w, uB_w, z_b_min, z_b_max
)

# --- Display Results ---

st.subheader("📊 Economic Analysis (Phase 2 Verification)")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Utility A (at ω)", f"{uA_w:.2f}")
c2.metric("Utility B (at ω)", f"{uB_w:.2f}")
c3.metric("MRS A", f"{mrs_A:.2f}" if not np.isinf(mrs_A) else "∞")
c4.metric("MRS B", f"{mrs_B:.2f}" if not np.isinf(mrs_B) else "∞")

st.markdown("---")
st.subheader("⚖️ Walrasian Equilibrium")
if we_data:
    px_eq, (xA_eq, yA_eq) = we_data
    cw1, cw2, cw3 = st.columns(3)
    cw1.metric("Eq. Price Ratio (Px/Py)", f"{px_eq:.2f}")
    cw2.metric("Agent A Allocation", f"({xA_eq:.2f}, {yA_eq:.2f})")
    
    net_x = xA_eq - endow_A[0]
    trade_dir = "Buys" if net_x > 0 else "Sells"
    cw3.metric(f"Agent A Trade", f"{trade_dir} {abs(net_x):.2f} X")

st.markdown("---")
st.subheader("📈 Contract Curve Stats")
st.write(f"Pareto Points Found: {len(pareto_x)}")
st.write(f"Core Points Found: {len(core_x)}")