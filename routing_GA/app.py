import streamlit as st
import pandas as pd
import time
import numpy as np
import logic

st.set_page_config(page_title="Route GA Optimizer", layout="wide", page_icon="🗺️")

@st.cache_data
def load_excel_data(file_path_or_buffer):
    """Loads and caches the excel file to prevent unnecessary re-reads using Streamlit's caching mechanism."""
    return logic.load_data(file_path_or_buffer)

def main():
    st.title("🛣️ Routing Optimization Simulator (GA)")
    st.markdown("Find the shortest path using a Genetic Algorithm. Upload your data, edit the nodes/paths, adjust GA parameters, and run the optimization!")

    # --- Sidebar: File Upload & Sample Data ---
    st.sidebar.header("📁 1. Data Input")
    uploaded_file = st.sidebar.file_uploader("Upload route_inputs.xlsx", type=['xlsx'])
    
    use_sample = st.sidebar.button("Load Sample Data")
    
    # Store whether we are using sample data in session state so it persists
    if use_sample:
        st.session_state.use_sample = True
        
    if uploaded_file is None and not st.session_state.get('use_sample', False):
        st.info("Please upload an Excel file from the sidebar or click 'Load Sample Data' to begin. (e.g., `route_inputs.xlsx` expected to have 'nodes' and 'paths' sheets)")
        st.stop()
        
    try:
        # Determine which file to load
        if uploaded_file is not None:
            file_to_load = uploaded_file
            st.session_state.use_sample = False # Reset if a file is actually uploaded
        else:
            # GitHubや別環境で動かすために「相対パス（このファイルと同じフォルダ）」を指定します
            file_to_load = 'route_inputs_example.xlsx'
            
        nodes_df_raw, paths_df_raw = load_excel_data(file_to_load)
        
        # Initialize session state for editable DataFrames if not exists, preventing re-runs from overwriting edits
        if 'nodes_df' not in st.session_state:
            st.session_state.nodes_df = nodes_df_raw.copy()
        if 'paths_df' not in st.session_state:
            st.session_state.paths_df = paths_df_raw.copy()
            
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        st.stop()

    # --- Sidebar: GA Parameters ---
    st.sidebar.header("⚙️ 2. GA Parameters")
    
    max_num_iteration = st.sidebar.number_input("Max Iterations", min_value=10, max_value=2000, value=500, step=10)
    population_size = st.sidebar.number_input("Population Size", min_value=10, max_value=500, value=100, step=10)
    mutation_probability = st.sidebar.slider("Mutation Probability", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
    elit_ratio = st.sidebar.slider("Elitism Ratio", min_value=0.0, max_value=1.0, value=0.10, step=0.01)
    parents_portion = st.sidebar.slider("Parents Portion", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
    max_iter_no_improv = st.sidebar.number_input("Max Iter. without Improv.", min_value=10, max_value=1000, value=100, step=10)

    st.session_state.ga_params = {
        'max_num_iteration': max_num_iteration,
        'population_size': population_size,
        'mutation_probability': mutation_probability,
        'elit_ratio': elit_ratio,
        'parents_portion': parents_portion,
        'crossover_type': 'uniform',
        'max_iteration_without_improv': max_iter_no_improv
    }

    # --- Sidebar: Execution ---
    st.sidebar.header("🚀 3. Optimization Engine")
    run_pressed = st.sidebar.button("▶️ Run Genetic Algorithm", type="primary")

    if run_pressed:
        with st.spinner("Optimizing route using Geneticalgorithm2..."):
            try:
                start_time = time.time()
                # Pass data and params to pure logic layer
                model = logic.run_optimization(
                    st.session_state.nodes_df, 
                    st.session_state.paths_df, 
                    st.session_state.ga_params
                )
                end_time = time.time()
                
                # Extract results
                st.session_state.best_variable = model.result.variable
                st.session_state.best_score = model.result.score
                st.session_state.run_history = model.report
                st.session_state.comp_time = end_time - start_time
                st.session_state.success = True
            except Exception as e:
                st.sidebar.error(f"Optimization failed: {e}")
                st.session_state.success = False

    # --- Main Area: Data Editor & Path Visualization ---
    st.header("📊 Network Data & Preview")
    st.markdown("You can edit the distance or the node relationships directly in the tables below. The changes are immediately reflected in the preview map below.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nodes")
        edited_nodes = st.data_editor(st.session_state.nodes_df, num_rows="dynamic", key="editor_nodes", width='stretch')
        st.session_state.nodes_df = edited_nodes
    with col2:
        st.subheader("Paths (Edges)")
        edited_paths = st.data_editor(st.session_state.paths_df, num_rows="dynamic", key="editor_paths", width='stretch')
        st.session_state.paths_df = edited_paths

    st.subheader("Initial Network Preview")
    with st.spinner("Drawing network preview..."):
        try:
            # We pass an array of zeros to highlight nothing initially since we haven't solved it
            dummy_selected = np.zeros(len(st.session_state.paths_df))
            fig_preview = logic.plot_network(
                st.session_state.nodes_df, 
                st.session_state.paths_df, 
                dummy_selected
            )
            st.pyplot(fig_preview)
        except Exception as e:
            st.error(f"Could not render graph preview: {e}")

    # --- Main Area: Dashboard ---
    if st.session_state.get('success', False):
        st.success("Optimization completed successfully!")
        st.header("🏁 Results Dashboard")
        
        # Metrics
        m1, m2 = st.columns(2)
        m1.metric("Optimal Distance (Score)", float(st.session_state.best_score))
        m2.metric("Computation Time", f"{st.session_state.comp_time:.2f} s")
        
        # Selected Paths Table
        st.subheader("Selected Route Sequence")
        paths_df = st.session_state.paths_df.copy()
        
        # Prevent crash if length somehow differs due to dynamic rows
        if len(paths_df) == len(st.session_state.best_variable):
            paths_df['activated'] = st.session_state.best_variable
            selected_paths = paths_df[paths_df['activated'] == 1].copy()
            selected_paths['activated'] = selected_paths['activated'].astype(int)
            st.dataframe(selected_paths, width='stretch')
        else:
            st.error("Length mismatch between path definitions and GA variables. Did you add/remove paths without restarting?")
        
        # Visualizations
        st.header("📈 Optimization Visualizations")
        
        st.subheader("Optimized Network Topology")
        with st.spinner("Drawing network graph..."):
            try:
                fig_optimal = logic.plot_network(
                    st.session_state.nodes_df, 
                    st.session_state.paths_df, 
                    st.session_state.best_variable
                )
                st.pyplot(fig_optimal)
            except Exception as e:
                st.error(f"Could not render graph: {e}")
                
        st.subheader("Fitness Convergence")
        # Create a simple dataframe for the line chart
        if isinstance(st.session_state.run_history, list):
            history_df = pd.DataFrame(st.session_state.run_history, columns=["Best Score"])
            st.line_chart(history_df)
        else:
            st.info("No report history returned by GA.")

if __name__ == "__main__":
    main()
