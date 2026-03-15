import random
import numpy as np
import pandas as pd
from geneticalgorithm2 import geneticalgorithm2 as ga
import matplotlib.pyplot as plt
import networkx as nx
from typing import Tuple, Dict, Any, Callable

# Fix for Python 3.12 compatibility with geneticalgorithm2
_old_randint = random.randint
random.randint = lambda a, b: _old_randint(int(a), int(b))

def load_data(file_path_or_buffer) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads nodes and paths data from an Excel file."""
    nodes = pd.read_excel(file_path_or_buffer, sheet_name='nodes')
    paths = pd.read_excel(file_path_or_buffer, sheet_name='paths')
    return nodes, paths

def create_fitness_function(nodes: pd.DataFrame, paths: pd.DataFrame) -> Callable[[np.ndarray], float]:
    """Creates and returns the fitness function (with penalties) based on the current nodes and paths DataFrames."""
    def f(x: np.ndarray) -> float:
        pen = 0

        # constraint sum(x) == 1 (origin)
        origin_nodes = nodes[nodes['description'] == 'origin']
        if not origin_nodes.empty:
            node_origin = int(origin_nodes.iloc[0]['node'])
            out_paths = paths.index[paths['node_from'] == node_origin]
            sum_out = sum([x[p] for p in out_paths])
            if sum_out != 1:
                pen += 1000000 * np.abs(sum_out - 1)

        # constraint sum(x) == 1 (destination)
        dest_nodes = nodes[nodes['description'] == 'destination']
        if not dest_nodes.empty:
            node_destination = int(dest_nodes.iloc[0]['node'])
            in_paths = paths.index[paths['node_to'] == node_destination]
            sum_in = sum([x[p] for p in in_paths])
            if sum_in != 1:
                pen += 1000000 * np.abs(sum_in - 1)

        # constraint sum(x, in) == sum(x, out)
        middle_nodes = nodes[nodes['description'] == 'middle point']['node']
        for node in middle_nodes:
            sum_in = sum([x[p] for p in paths.index[paths['node_to'] == node]])
            sum_out = sum([x[p] for p in paths.index[paths['node_from'] == node]])
            if sum_in != sum_out:
                pen += 1000000 * np.abs(sum_in - sum_out)

        # objective function and return
        objFun = sum([x[p] * paths['distance'].iloc[p] for p in paths.index])
        return objFun + pen
    
    return f

def run_optimization(nodes: pd.DataFrame, paths: pd.DataFrame, params: Dict[str, Any]) -> Any:
    """Runs the genetic algorithm optimization and returns the trained model result."""
    nVars = len(paths)
    varbounds = [[0, 1]] * nVars
    vartype = tuple(['int'] * nVars)
    
    f = create_fitness_function(nodes, paths)
    
    # We create the GA model
    model = ga(dimension=nVars,
               variable_type=vartype,
               variable_boundaries=varbounds,
               algorithm_parameters=params)
    
    # We run the GA model using our fitness function
    model.run(function=f)
    return model

def plot_network(nodes: pd.DataFrame, paths: pd.DataFrame, selected_paths_array: np.ndarray) -> plt.Figure:
    """Plots the network graph using NetworkX and Matplotlib. 
    Selected paths are highlighted in red."""
    G = nx.DiGraph()
    
    # Add nodes to graph
    for _, row in nodes.iterrows():
        node_id = row['node']
        desc = row['description']
        color = 'lightblue'
        if desc == 'origin':
            color = 'lightgreen'
        elif desc == 'destination':
            color = 'salmon'
        G.add_node(node_id, desc=desc, color=color)
        
    # Add edges to graph
    edge_colors = []
    edge_widths = []
    for idx, row in paths.iterrows():
        u = row['node_from']
        v = row['node_to']
        dist = row['distance']
        is_selected = selected_paths_array[idx] == 1
        
        G.add_edge(u, v, weight=dist)
        
        if is_selected:
            edge_colors.append('red')
            edge_widths.append(3.0)
        else:
            edge_colors.append('gray')
            edge_widths.append(1.0)
            
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Position nodes using spring layout with a fixed seed for visual consistency
    pos = nx.spring_layout(G, seed=42)
    
    node_colors = [data['color'] for _, data in G.nodes(data=True)]
    
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=600, edgecolors='black')
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=10, font_weight="bold")
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths, arrowsize=20)
    
    # Add distance labels onto the plotted edges
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, font_size=8)
    
    ax.set_title("Routing Network Topology\n(Red: Optimal Path, Green: Origin, Salmon: Destination)", fontsize=14)
    ax.axis("off")
    fig.tight_layout()
    
    return fig
