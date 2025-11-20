import streamlit as st

def init_session_state():
    """Initialize the session state with default values."""
    
    # Dimensions
    if "total_x" not in st.session_state:
        st.session_state["total_x"] = 10.0
    if "total_y" not in st.session_state:
        st.session_state["total_y"] = 10.0
        
    # Endowments (Agent A)
    if "endow_x" not in st.session_state:
        st.session_state["endow_x"] = 5.0
    if "endow_y" not in st.session_state:
        st.session_state["endow_y"] = 5.0
        
    # Agent A Preferences
    if "type_A" not in st.session_state:
        st.session_state["type_A"] = "Cobb-Douglas"
    if "params_A" not in st.session_state:
        st.session_state["params_A"] = {"alpha": 1.0, "beta": 1.0}
        
    # Agent B Preferences
    if "type_B" not in st.session_state:
        st.session_state["type_B"] = "Cobb-Douglas"
    if "params_B" not in st.session_state:
        st.session_state["params_B"] = {"alpha": 1.0, "beta": 1.0}
        
    # Visual Settings
    if "theme_name" not in st.session_state:
        st.session_state["theme_name"] = "Modern Professional"
    if "dark_mode" not in st.session_state:
        st.session_state["dark_mode"] = False
    if "vis_settings" not in st.session_state:
        st.session_state["vis_settings"] = {
            "show_endow": True,
            "show_core": True,
            "show_pareto": True,
            "show_lens": True,
            "show_curves_A": True,
            "show_curves_B": True,
            "line_mode": False,
            "show_we": False,
            "style_A": "solid",
            "style_B": "dot",
            "ic_mode": "Auto (Density)",
            "n_curves": 30,
            "n_curves_A": 10,
            "n_curves_B": 10
        }

def reset_to_baseline():
    """Reset all state variables to their default values."""
    st.session_state["total_x"] = 10.0
    st.session_state["total_y"] = 10.0
    st.session_state["endow_x"] = 5.0
    st.session_state["endow_y"] = 5.0
    st.session_state["type_A"] = "Cobb-Douglas"
    st.session_state["params_A"] = {"alpha": 1.0, "beta": 1.0}
    st.session_state["type_B"] = "Cobb-Douglas"
    st.session_state["params_B"] = {"alpha": 1.0, "beta": 1.0}
    # We don't necessarily reset visual settings on baseline reset, but we could.
    # For now, let's keep visual settings as is.