import networkx as nx

# Create a new graph
G = nx.DiGraph()

# Add the places (jobs) as nodes
G.add_node("Job 1", shape="circle")
G.add_node("Job 2", shape="circle")
G.add_node("Job 3", shape="circle")

# Add the transitions (machines) as nodes
G.add_node("Machine 1", shape="rectangle", label="9")
G.add_node("Machine 2", shape="rectangle", label="3")
G.add_node("Machine 3", shape="rectangle", label="6")

# Add the arcs (flow of jobs) as edges
G.add_edge("Job 1", "Machine 1")
G.add_edge("Machine 1", "Job 2")
G.add_edge("Job 2", "Machine 2")
G.add_edge("Machine 2", "Job 3")
G.add_edge("Job 3", "Machine 3")

# Draw the graph
nx.draw(G, with_labels=True)
