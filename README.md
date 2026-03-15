# Routing Optimization Simulator (GA) 🗺️

This project is an interactive web application that visualizes and simulates the Shortest Path Problem using a **Genetic Algorithm (GA)**. It is built entirely in Python using **Streamlit** for the frontend dashboard and `geneticalgorithm2` / `networkx` for the backend logic.

## 🌟 Features

1. **Interactive Data Editor**: Upload your Excel definition file (`nodes` and `paths` sheets) or click **"Load Sample Data"** to try it out immediately without downloading anything. You can edit the distances and relationships directly in the browser!
2. **GA Hyperparameter Tuning**: Adjust parameters like Max Iterations, Population Size, and Mutation Probability using intuitive sliders.
3. **Execution & Evaluation**: Instantly run the Genetic Algorithm engine and view Key Performance Indicators (KPIs) like total calculated distance and computation time.
4. **Visualizations**: 
   - **Network Topology**: View the initial graph, and see the finalized optimal route dynamically highlighted in red using NetworkX & Matplotlib.
   - **Fitness Convergence**: See the GA's problem-solving history as a line chart mapping the best fitness score across generations.

## 🔧 Architecture / Separation of Concerns (Spec-Driven)

This project was developed strictly adhering to the **Spec Kit** methodology (spec-driven development):
- **`logic.py`**: Pure logic handler. Contains Excel parsing, definition of the mathematical constraints (Fitness functions with penalty values for origin/destination rules), and graph rendering logic.
- **`app.py`**: Presentation layer. Only manages the `st.session_state` and UI elements, isolating them from the optimization math to dramatically reduce unnecessary Streamlit re-runs.

## 🚀 How to Run Locally

If you wish to clone and run this application on your local machine:

1. Clone this repository
```bash
git clone https://github.com/takashi-sugawara/Udemy-Optimization-Routing-GA-App.git
cd Udemy-Optimization-Routing-GA-App/routing_GA
```

2. Install the required dependencies
```bash
pip install -r requirements.txt
```

3. Run the Streamlit app
```bash
streamlit run app.py
```

## 📂 Repository Structure
* `routing_GA/app.py`: Streamlit User Interface.
* `routing_GA/logic.py`: Optimization and visualization engines.
* `routing_GA/route_inputs_example.xlsx`: Sample mapping data (automatically loaded via side menu).
* `routing_GA/requirements.txt`: Project dependencies list.
