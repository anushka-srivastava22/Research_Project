import sys
import argparse
import matplotlib.pyplot as plt
import networkx as nx

from Node import *


def plotandinput():
    class SpaceTimeGraph:
        def __init__(self, nodes, time_slots, snapshots):
            self.nodes = nodes
            self.time_slots = time_slots
            self.snapshots = snapshots
            self.layers = len(snapshots) + 1  # K + 1 layers

            # Initialize space-time graph as an empty graph
            self.graph = nx.DiGraph()

        def add_spatial_links(self):
            for t in range(len(self.snapshots)):
                snapshot = self.snapshots[t]
                # Iterate through each edge in the snapshot
                for edge in snapshot:
                    source, target, weight = edge
                    # Add the original edge and its reverse
                    self.graph.add_edge(
                        (t, source), (t + 1, target), weight=weight)
    #                 print(self.graph.nodes)

        def add_temporal_links(self):
            for layer in range(self.layers - 1):
                for node in self.nodes:
                    # Add temporal links between consecutive layers
                    self.graph.add_edge((layer, str(layer)+node),
                                        (layer + 1, str(layer+1)+node))
    #         print(self.graph.nodes)

        def visualize_graph(self):
            # Calculate the position of nodes
            pos = {}
            for layer in range(self.layers):
                for idx, node in enumerate(self.nodes):
                    pos[(layer, str(layer)+node)] = (layer, idx)

            # Draw the graph with the specified properties
            nx.draw(self.graph, pos, with_labels=True, node_size=1000, node_color='lightblue',
                    font_size=10, edge_color='black', arrows=True, arrowstyle='-|>')

            # Draw edge labels with the weights of the edges
            edge_labels = nx.get_edge_attributes(self.graph, 'weight')
            nx.draw_networkx_edge_labels(
                self.graph, pos, edge_labels=edge_labels)

            # Add plot title and labels
            plt.title('Space-Time Graph')
            plt.xlabel('Time')
            plt.ylabel('Nodes')
            plt.xticks(range(self.layers))

            # Add x-axis and y-axis lines
            # x-axis at y = -0.5
            plt.axhline(y=-0.5, color='black', linewidth=0.5)
            # y-axis at x = -0.5
            plt.axvline(x=-0.5, color='black', linewidth=0.5)

            # Show the plot grid
            plt.grid(True)
            plt.show()

    # Example usage
    nodes = ['v5', 'v4', 'v3', 'v2', 'v1']
    time_slots = 3

    # Snapshots represented as lists of edges with weights
    # Define the snapshot data
    snapshots = [
        # Time interval 1
        [
            ['v1', 'v2', 2],
            ['v3', 'v4', 1],
            ['v4', 'v5', 4]

        ],
        # Time interval 2
        [
            ['v3', 'v5', 1],
            ['v1', 'v3', 2]
        ],
        # Time interval 3
        [
            ['v3', 'v1', 1],
            ['v4', 'v5', 3]
        ],
        # Time interval 4
        [
            ['v1', 'v3', 4],
            ['v2', 'v5', 4]
        ],
    ]
    # print(snapshots)

    # Ensure bidirectional connections
    # For each snapshot, add the reverse of each connection automatically
    for i, snapshot in enumerate(snapshots):
        new_snapshot = []
        for edge in snapshot:
            source, target, weight = edge
            # Add original edge
            new_snapshot.append(edge)
            # Add reverse edge
            new_snapshot.append([target, source, weight])
        snapshots[i] = new_snapshot

    # To normalise the snapshot data
    normalise_snapshot = []
    timeinterval = 0
    for snapshot in snapshots:
        normalise_edges = []
        for edge in snapshot:
            normalise_edge = []
            source, target, weight = edge
            normalise_edge.append(str(timeinterval) + source)
            normalise_edge.append(str(timeinterval+1)+target)
            normalise_edge.append(weight)
            normalise_edges.append(normalise_edge)
        timeinterval = timeinterval+1
        normalise_snapshot.append(normalise_edges)

    snapshots = normalise_snapshot

    # Mapping nodes to numeric value
    mapper = {}
    nodeNum = 1
    for time in range(len(nodes)):
        for layer in range(1, len(nodes)+1):
            mapper[str(time)+'v'+str(layer)] = nodeNum
            nodeNum += 1

    # Convert the snapshot data to the required format (FromNode, ToNode, Weight)
    snapshot_data = []
    for snapshot in snapshots:
        for edge in snapshot:
            source, target, weight = edge
            snapshot_data.append((source, target, weight))

 # Write the snapshot data to a text file
    with open("input.txt", "w") as f:
        id = 1
        f.write("{}\n".format(len(nodes)*len(nodes)))
        for edge in snapshot_data:
            source, target, weight = edge
            f.write("{},{},{},{}\n".format(
                id, mapper[source], mapper[target], weight))
            id += 1
        for time in range(len(nodes)-1):
            for layer in range(1, len(nodes)+1):
                f.write("{},{},{},{}\n".format(
                    id, mapper[str(time)+'v'+str(layer)], mapper[str(time+1)+'v'+str(layer)], 0))
                id += 1

    print("Snapshot data has been prepared and saved to 'input.txt'.")
    # Initialize space-time graph and visualize
    space_time_graph = SpaceTimeGraph(nodes, time_slots, snapshots)
    space_time_graph.add_spatial_links()
    space_time_graph.add_temporal_links()
    space_time_graph.visualize_graph()
    return mapper


def kspmain(mapper):

    # Parse the command line searching for a single string argument of the file to open
    parser = argparse.ArgumentParser(description='KSP Project')
    parser.add_argument('--infile', dest='file_in', default="input.txt",
                        help='File to process network from and find KSP for')
    parser.add_argument('--k', dest='k', type=int, default='4',
                        help='Number of K shortest paths to find')
    parser.add_argument('--source', dest='source', type=int,
                        default='1', help='Index of starting node')
    parser.add_argument('--sink', dest='sink', type=int, default='-1',
                        help='Index of sink node, defaults to last node')

    args = parser.parse_args()

    # Project Parts 1 and 2
    # Open the file and build a network of nodes with edges
    print("ECE 643 Project Part 1 and 2")
    nodes = build_table(args.file_in)

    # If sink was not explicitly specified, assign it to the last node
    if args.sink == -1:
        args.sink = len(nodes)

    # Project Part 3
    # Run djikstra from each node (except the sink node) to each other node
    print("\nECE 643 Project Part 3")
    for i in range(len(nodes)-1):
        for j in range(len(nodes)):
            if i != j:
                shortestPath = dijkstraImpl(nodes, i, j)
                if shortestPath != -1:
                    print("Searching for shortest path from " +
                          str(i+1) + " to " + str(j+1))
                    shortestPath.printPath()
                    print(" -> ".join(list(filter(lambda x: mapper[x] == (i.index + 1), mapper))[
                        0] for i in shortestPath.nodes))
                # else:
                #     print("No path found")

    # Project Part 4
    # print(mapper)
    # Run Yens KSP algorithm to find the 3 shortest paths
    print("\nProject Part 4")
    KSPs = yensImpl(nodes, args.source-1, args.sink-1, args.k)
    print("\n\nResults of searching for " + str(args.k) +
          " shortest paths from " + str(args.source) + " to " + str(args.sink))
    if KSPs is not None:
        for i, ksp in enumerate(KSPs):
            print("Found KSP " + str(i+1))
            ksp.printPath()
            print(" -> ".join(list(filter(lambda x: mapper[x] == (i.index + 1), mapper))[
                  0] for i in ksp.nodes))

        for i in range(len(KSPs), args.k):
            print("Not enough paths to find KSP " + str(i+1))


# Takes an input file as an argument and builds a Node/Edge structure


def build_table(file_in):

    # Open the file as readonly
    with open(file_in, 'r') as f:
        # The first line of the file is a single integer for number of Nodes
        for i in f.readline().split():
            numNodes = int(i)
        # print(numNodes)

        # Create a list of Nodes
        nodes = [Node(i) for i in range(numNodes)]

        # Read the rest of the file and create edges
        # Each line contain 4 integers, comma separated
        # ID,FromNode,ToNode,Weight'
        # But! Nodes are 1-indexed, so subtract 1 internally
        for line in f.readlines():
            ID, FromNode, ToNode, Weight = [int(i) for i in line.split(",")]
            FromNode = FromNode - 1
            ToNode = ToNode - 1
            # print (ID, FromNode, ToNode, Weight)
            # The data structure uses unidirectional links, so create an edge in each direction
            nodes[FromNode].addEdge(ToNode, Weight)
            # nodes[ToNode].addEdge(FromNode, Weight);
    # End the "with" statement, which closes the file

    # Print an adjacency/weight matrix
    print("   " + "".join(' {} '.format(i+1) for i in range(numNodes)))
    print("  " + "".join('___' for _ in range(numNodes)))
    for i in range(numNodes):
        adjacency = []
        for j in range(numNodes):
            if i == j:
                adjacency.append('-')
                continue
            distance = nodes[i].hasEdgeTo(j)
            if distance == -1:
                adjacency.append('X')
            else:
                adjacency.append(distance)
        print(str(i+1) + " | " + "".join('{}  '.format(k) for k in adjacency))

    return nodes


# Implementation of Dijkstra's algorithm
# Arguments:
#   nodes: A list of nodes created by the build_table function above
#   fromNode: integer of the starting Node
#   toNode: integer of the Node to find the shortest path to
def dijkstraImpl(nodes, fromNode, toNode):
    # Create a list of visited nodes initialized with the starting node
    visited = [nodes[fromNode]]
    # cost_list is a list potential nodes to visit and paths to them
    cost_list = []
    # Initialize some variables
    # current_node: The node which edges will be checked from and evaluated for lower costs
    # current_path: The Path (essentially a list of nodes) that was traversed to get to the current node
    # 				Keep track of and store the current_path in the cost_list structure because the lowest
    # cost edge to traverse next may not originate from the current_node
    current_node = nodes[fromNode]
    current_path = Path(nodes[fromNode])

    # Continue to search nodes until we reach the destination
    while current_node.index != toNode:
        # Find connections from the current Node and assign costs
        for edge in current_node.getEdgesFrom():
            # print("Checking edge from " + str(edge.fromNode) + " to " + str(edge.toNode))
            # If the visited list does not have any instances of the toNode for this edge
            if not any(n_visited.index == edge.toNode for n_visited in visited):
                # Search for a cost entry for this node
                for idx, (n_cost, p_cost) in enumerate(cost_list):
                    if n_cost.index == edge.toNode:
                        # Compute total cost and update if less than
                        if current_path.getPathCost() + edge.weight < p_cost.getPathCost():
                            # Create a potential path to this node to update the cost_list entry with
                            candidatePath = Path(current_path)
                            candidatePath.addNode(nodes[edge.toNode])
                            # Use the idx variable from enumerate loop to update the correct cost_list entry
                            cost_list[idx] = (n_cost, candidatePath)
                        # Having found a matching cost_list entry, exit the search
                        break
                else:
                    # The else statement will not be executed if a break was triggered
                    # If no cost entry was found, add to the cost table
                    # Note: This is equivalent to the cost having been infinity
                    # Create a potential path to this node to insert into the cost_list
                    candidatePath = Path(current_path)
                    candidatePath.addNode(nodes[edge.toNode])
                    cost_list.append((nodes[edge.toNode], candidatePath))

            # End the if statement checking the visited list
        # End the for statement iterating through edges from current node

        # If cost_list is empty at this point, no valid path exists to the destination
        if (len(cost_list) == 0):
            # print("All path options exhausted, no valid path exists")
            break
        # Pick a new node!
        # Sort cost_list by the path cost of the Path component
        cost_list.sort(key=lambda cost: cost[1].getPathCost())
        # Pop the first entry in the now sorted list
        # Update the current_node and current_path variables from that entry
        (current_node, current_path) = cost_list.pop(0)
        # print("Selected a new node to visit: " + str(current_node.index) + ", it had a cost of " + str(current_path.getPathCost()))
        # current_path.printPath();

        # Add this node to the visited list
        visited.append(current_node)

    # Repeat the while statement
    else:
        # When the while statement exits normally, we have found the final path
        # print("Final path picked: ")
        return current_path

    # If the while statement exited from a break, the else will not be executed
    # Need to return a NULL here as no shortest path exists
    return -1


# Implementation of Yen's algorithm for finding K shortest paths in a network
# Uses Dijkstra implemented above for shortest path calculation
# Returns a list of Path variables.
# Implemented based on the pseudo-code from "http://en.wikipedia.org/wiki/Yen%27s_algorithm"
# Arguments:
#   nodes: A list of nodes created by the build_table function above
#   fromNode: integer of the starting Node
#   toNode: integer of the Node to find the shortest path to
# numPaths: how many shortest paths to find
def yensImpl(nodes, fromNode, toNode, numPaths):
    # Create an empty list of paths that will be returned and a list of potential paths
    Apaths = []
    Bpaths = []
    # First find the 1st shortest path using Dijkstra
    Apaths.append(dijkstraImpl(nodes, fromNode, toNode))

    if Apaths and Apaths[0] != -1:
        # Loop to find the remaining k shortest paths
        for k in range(1, numPaths):

            # Loop through all but the last node in the previous lowest-cost path
            for i, spurNode in enumerate(Apaths[k-1][:-1]):
                rootPath = Path(Apaths[k-1][:i+1])
                # rootPath.printPath()

                # Check the previous shortest paths and compare to rootPath
                # Break any edges at the end of the rootPath if it coincides with a
                # previous shortest path
                for testPath in Apaths:
                    if rootPath[:] == testPath[:i+1]:
                        spurNode.breakEdge(testPath[i+1].index)

                # For each node rootPathNode in rootPath except spurNode:
                #   remove rootPathNode from Graph

                # Calculate the spur path from the spur node to the sink
                spurPath = dijkstraImpl(nodes, spurNode.index, toNode)
                # Fix any edges that were broken
                spurNode.fixEdges()

                if spurPath == -1:
                    # No valid path exists, skip to next node
                    continue

                totalPath = rootPath + spurPath
    # Need to check if spurPath already exists in B
                if not any(totalPath[:] == bpath[:] for bpath in Bpaths):
                    # print("Adding a path to Bpaths:")
                    # totalPath.printPath()
                    Bpaths.append(totalPath)
                else:
                    print("Not adding a path to Bpaths because it already existed:")
                    totalPath.printPath()

            # If Bpaths is empty, no more possible paths exist, so exit
            if len(Bpaths) == 0:
                break
            # Sort the list of candidate paths
            Bpaths.sort(key=lambda item: item.getPathCost())
            # Move the lowest path cost from B to A
            Apaths.append(Bpaths.pop(0))
            print("Found shortest path " + str(k+1) + ": ")
            Apaths[k].printPath()

        return Apaths


# Execute the main function when called from command line
if __name__ == "__main__":
    mapper = plotandinput()
    kspmain(mapper)
    print("Done with program")
