import streamlit as st
from ui.state import reset_to_baseline

def dual_input(label, min_val, max_val, state_key, step=0.1):
    """
    A helper to render a slider and number input that stay in sync.
    Updates st.session_state[state_key].
    """
    # Ensure the state key exists
    if state_key not in st.session_state:
        return

    current_val = st.session_state[state_key]
    
    # Widget keys
    k_slider = f"{state_key}_slider"
    k_num = f"{state_key}_num"

    # Initialize widget states if not present or if out of sync with main state
    if k_slider not in st.session_state or st.session_state[k_slider] != current_val:
        st.session_state[k_slider] = current_val
    if k_num not in st.session_state or st.session_state[k_num] != current_val:
        st.session_state[k_num] = current_val

    def update_from_slider():
        st.session_state[state_key] = st.session_state[k_slider]
        st.session_state[k_num] = st.session_state[k_slider]

    def update_from_num():
        st.session_state[state_key] = st.session_state[k_num]
        st.session_state[k_slider] = st.session_state[k_num]
        
    def increment():
        new_val = min(max_val, st.session_state[state_key] + step)
        st.session_state[state_key] = new_val
        st.session_state[k_slider] = new_val
        st.session_state[k_num] = new_val

    def decrement():
        new_val = max(min_val, st.session_state[state_key] - step)
        st.session_state[state_key] = new_val
        st.session_state[k_slider] = new_val
        st.session_state[k_num] = new_val

    st.markdown(f"**{label}**")
    c1, c2, c3, c4 = st.columns([0.15, 0.45, 0.25, 0.15])
    
    with c1: st.button("➖", key=f"dec_{state_key}", on_click=decrement)
    with c2: st.slider("", min_value=float(min_val), max_value=float(max_val), key=k_slider, step=step, on_change=update_from_slider, label_visibility="collapsed")
    with c3: st.number_input("", min_value=float(min_val), max_value=float(max_val), key=k_num, step=step, format="%.2f", on_change=update_from_num, label_visibility="collapsed")
    with c4: st.button("➕", key=f"inc_{state_key}", on_click=increment)

def render_param_input(label, param_key, params_dict, min_v, max_v, key_suffix):
    """
    Helper to render inputs for utility parameters.
    Updates the params_dict in place.
    """
    val = float(params_dict.get(param_key, 1.0 if param_key in ['alpha', 'beta'] else 0.0))
    k = f"param_{key_suffix}_{param_key}"
    
    st.markdown(f"<small>{label}</small>", unsafe_allow_html=True)
    col1, col2 = st.columns([0.7, 0.3])
    
    # We use the slider as the primary input for simplicity here
    new_val = col1.slider("", min_value=float(min_v), max_value=float(max_v), value=val, step=0.1, key=f"{k}_slider", label_visibility="collapsed")
    col2.number_input("", value=new_val, key=f"{k}_num", disabled=True, label_visibility="collapsed")
    
    params_dict[param_key] = new_val

def render_agent_config(agent_name):
    prefix = f"_{agent_name}" # e.g. _A
    key_type = f"type{prefix}" # type_A
    key_params = f"params{prefix}" # params_A
    
    with st.sidebar.expander(f"👤 Agent {agent_name} Preferences", expanded=False):
        opts = ["Cobb-Douglas", "Perfect Substitutes", "Perfect Complements (Min)", 
                "Max Preferences (Convex)", "Quasi-Linear (Shifted Product)", 
                "Mixed Cobb-Douglas", "Satiation (Bliss Point)", "Custom (Enter Formula)"]
        
        current_type = st.session_state.get(key_type, "Cobb-Douglas")
        
        # Update type
        new_type = st.selectbox(f"Utility Type", opts, index=opts.index(current_type) if current_type in opts else 0, key=f"select_{key_type}")
        if new_type != current_type:
            st.session_state[key_type] = new_type
            st.rerun()

        # Params handling
        params = st.session_state.get(key_params, {})
        
        if new_type == "Custom (Enter Formula)":
            val = st.text_input("Formula", value=params.get('formula', 'x*y'), key=f"formula{prefix}")
            params['formula'] = val
        elif new_type == "Satiation (Bliss Point)":
            render_param_input("Bliss Point X", "a", params, -50.0, 50.0, prefix)
            render_param_input("Bliss Point Y", "b", params, -50.0, 50.0, prefix)
        elif new_type == "Quasi-Linear (Shifted Product)":
            render_param_input("Shift Parameter X", "a", params, -50.0, 50.0, prefix)
            render_param_input("Shift Parameter Y", "b", params, -50.0, 50.0, prefix)
        else:
            # Alpha/Beta
            render_param_input("Alpha (α)", "alpha", params, 0.1, 10.0, prefix)
            if new_type != "Mixed Cobb-Douglas":
                render_param_input("Beta (β)", "beta", params, 0.1, 10.0, prefix)

def render_visual_settings():
    with st.sidebar.expander("🎨 Visual Settings", expanded=False):
        vis = st.session_state["vis_settings"]
        
        st.session_state["theme_name"] = st.radio("Theme", ["Modern Professional", "Classic Textbook"], index=0 if st.session_state.get("theme_name") == "Modern Professional" else 1)
        st.session_state["dark_mode"] = st.checkbox("Dark Mode", value=st.session_state.get("dark_mode", False))
        
        st.markdown("---")
        vis["show_endow"] = st.checkbox("Show Endowment", value=vis.get("show_endow", True))
        vis["show_core"] = st.checkbox("Show Core", value=vis.get("show_core", True))
        vis["show_pareto"] = st.checkbox("Show Pareto Set", value=vis.get("show_pareto", True))
        vis["show_lens"] = st.checkbox("Shade Exchange Lens", value=vis.get("show_lens", True))
        vis["show_curves_A"] = st.checkbox("Show Curves (Agent A)", value=vis.get("show_curves_A", True))
        vis["show_curves_B"] = st.checkbox("Show Curves (Agent B)", value=vis.get("show_curves_B", True))
        vis["line_mode"] = st.checkbox("Connect Pareto Points", value=vis.get("line_mode", False))
        vis["show_we"] = st.checkbox("Show Walrasian Equilibrium", value=vis.get("show_we", False))
        
        st.markdown("**Line Styles**")
        c1, c2 = st.columns(2)
        style_map = {"Solid": "solid", "Dotted": "dot", "Dashed": "dash"}
        rev_map = {v: k for k, v in style_map.items()}
        
        sA = c1.selectbox("Agent A", ["Solid", "Dotted", "Dashed"], index=["Solid", "Dotted", "Dashed"].index(rev_map.get(vis.get("style_A", "solid"), "Solid")), key="style_sel_A")
        sB = c2.selectbox("Agent B", ["Solid", "Dotted", "Dashed"], index=["Solid", "Dotted", "Dashed"].index(rev_map.get(vis.get("style_B", "dot"), "Dotted")), key="style_sel_B")
        vis["style_A"] = style_map[sA]
        vis["style_B"] = style_map[sB]
        
        st.markdown("**Curve Density**")
        ic_mode = st.radio("Mode", ["Auto", "Manual"], horizontal=True, label_visibility="collapsed", index=0 if vis.get("ic_mode") == "Auto (Density)" else 1)
        vis["ic_mode"] = "Auto (Density)" if ic_mode == "Auto" else "Manual"
        
        if ic_mode == "Auto":
            vis["n_curves"] = st.slider("Density", 10, 100, vis.get("n_curves", 30))
        else:
            c1, c2 = st.columns(2)
            vis["n_curves_A"] = c1.number_input("N (A)", 1, 50, vis.get("n_curves_A", 10))
            vis["n_curves_B"] = c2.number_input("N (B)", 1, 50, vis.get("n_curves_B", 10))

def render_sidebar():
    st.sidebar.header("⚙️ Configuration")

    if st.sidebar.button("Reset to Baseline"):
        reset_to_baseline()
        st.rerun()

    # Dimensions & Endowment
    with st.sidebar.expander("📦 Dimensions & Endowment", expanded=True):
        dual_input("Total Good X", 1.0, 100.0, "total_x", 1.0)
        dual_input("Total Good Y", 1.0, 100.0, "total_y", 1.0)
        
        st.markdown("---")
        st.markdown("**Agent A Endowment**")
        
        # Clamp endowment if totals changed
        total_x = st.session_state["total_x"]
        total_y = st.session_state["total_y"]
        
        if st.session_state["endow_x"] > total_x: st.session_state["endow_x"] = total_x
        if st.session_state["endow_y"] > total_y: st.session_state["endow_y"] = total_y
        
        dual_input("ω_x", 0.0, total_x, "endow_x", 0.1)
        dual_input("ω_y", 0.0, total_y, "endow_y", 0.1)

    # Agent Preferences
    render_agent_config("A")
    render_agent_config("B")

    # Visual Settings
    render_visual_settings()