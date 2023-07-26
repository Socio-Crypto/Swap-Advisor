from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic import View
import json
from django.http import HttpResponse
from .services import get_routes
import heapq
import networkx as nx


class Graph:
    def __init__(self, ):
        self.graph = dict()

    def add_edge(self, node1, node2, cost, dex):
        if node1 not in self.graph:
            self.graph[node1] = dict()
        if node2 not in self.graph:
            self.graph[node2] = dict()
        # Ignore the edge if there is already edge with better cost
        if node2 in self.graph[node1] and self.graph[node1][node2][0] < cost:
            return
        self.graph[node1][node2] = (cost, dex)
        self.graph[node2][node1] = (cost, dex)

    def get_nodes(self):
        "Returns the nodes of the graph."
        return self.graph.keys()
    
    def get_neighbors(self, node):
        "Returns the neighbors of a node."
        return self.graph[node].keys()

    def get_cost(self, from_node, to_node):
        "Returns the cost of an edge between two nodes."
        return self.graph[from_node][to_node][0]

    def get_dex(self, from_node, to_node):
        return self.graph[from_node][to_node][1]

    def print_graph(self):
        for source, destination in self.graph.items():
            print(f"{source}-->{destination}")

##############
# Algorithm
##############
class DijkstraNodeState:
    def __init__(self, name):
        self.cost = float('inf')
        self.parent = None
        self.finished = False
        self.name = name

def dijkstra(graph, start_node, goal_node):
    nodes = {}
    for node in graph.get_nodes():
        nodes[node] = DijkstraNodeState(node)
    nodes[start_node].cost = 0
    queue = [(0, start_node)]
    while queue:
        cost, node = heapq.heappop(queue)
        if node == goal_node:
            break
        if nodes[node].finished:
            continue
        nodes[node].finished = True
        for neighbor in graph.get_neighbors(node):
            if nodes[neighbor].finished:
                continue
            new_cost = cost + graph.get_cost(node, neighbor)
            if new_cost < nodes[neighbor].cost:
                nodes[neighbor].cost = new_cost
                nodes[neighbor].parent = node
                heapq.heappush(queue, (new_cost, neighbor))
    path = []
    current = goal_node
    while nodes[current].parent:
        parent = nodes[current].parent
        dex = graph.get_dex(parent, current)
        path.append((parent, current, dex))
        current = nodes[current].parent
    path.reverse()
    return path

##############
# Main
##############
def print_path(path):
    routes = []
    for node1, node2, dex in path:
        routes.append(f"{node1}-->{node2} ({dex})")
        print(f"{node1}-->{node2} ({dex})")
    return routes

class SaveDataInJsonView(View):

    def get(self, request):
    
        networks = ['avalanche', 'polygon' , 'ethereum', 'bsc', 'optimism' , 'arbitrum']
        routes = []
        for network in networks:
            data = get_routes(network)
            with open(f'{network}.json', "w") as f:
                json.dump(data, f)

        return HttpResponse('The JSON files have been updated with new data!')


def networkx_path(paths, token_1, token_2):
    # Create an empty directed graph
    G = nx.DiGraph()

    # Add edges to the graph with their associated costs and identifiers
    for source, target, cost, dex in paths:
        G.add_edge(source, target, weight=cost, dex=dex)

    # Use Dijkstra's algorithm to find the best path from 'A' to 'E'
    best_path_nodes = nx.shortest_path(G, source=token_1, target=token_2, weight='weight')
    best_path_cost = nx.shortest_path_length(G, source=token_1, target=token_2, weight='weight')

    # Extract the dexs for the best path
    best_path_dexs = [(G[u][v]['dex']) for u, v in zip(best_path_nodes[:-1], best_path_nodes[1:])]

    return best_path_nodes, best_path_cost, best_path_dexs


def read_data_from_json(network):
    with open(f'{network}.json', 'r') as infile:
        routes = json.load(infile)
    output = []
    for entry in routes:
        if entry["symbol_in"] and entry["symbol_out"] is not None:
            token_in = entry["symbol_in"]
            token_out = entry["symbol_out"]
            avg_gas_used = entry["avg gas used"]
            platform = entry["platform"]
            output.append((token_in, token_out, avg_gas_used, platform))

    return output


def get_dijkstra_fr_algorithm(network_1_path, token_1, token_2):
    g = Graph()
    for node1, node2, cost, dex in network_1_path:
        g.add_edge(node1, node2, cost, dex)

    path = dijkstra(graph=g, start_node=token_1, goal_node=token_2)
    return print_path(path)


def find_path(request):
    if request.method == 'POST':
        context = {}
        network_1 = request.POST.get('bridge_network_1')
        network_2 = request.POST.get('bridge_network_2')
        token_1 = request.POST.get('bridge_token_1')
        token_2 = request.POST.get('bridge_token_2')

        network_1_path = read_data_from_json(network_1)
        network_2_path = read_data_from_json(network_2)

        # try:
        #     network_1_paths, b, c = networkx_path(network_1_path, token_1, 'axlUSDC')
        #     print(network_1_paths, b, c)
        # except: 
        #     pass
        # print('--------------------------------------------')
        # try:
        #     network_2_paths, d, e = networkx_path(network_2_path, 'axlUSDC', token_2)
        #     print(network_2_paths, d, e)
        # except:
        #     pass
        
        # network_1_paths, b, c = networkx_path(network_1_path, token_1, 'axlUSDC')
        # print(network_1_paths, b, c)
        # print('--------------------------------------------')
        # network_2_paths, d, e = networkx_path(network_2_path, 'axlUSDC', token_2)
        # print(network_2_paths, d, e)
        try:
            context['path_1'] = get_dijkstra_fr_algorithm(network_1_path, token_1, 'axlUSDC')
        except:
            context['path_1'] = f'There is no Path for {token_1}'
        try:
            context['path_2'] = get_dijkstra_fr_algorithm(network_2_path, 'axlUSDC', token_2)
        except:
            context['path_2'] = f'There is no Path for {token_2}'

        
        return JsonResponse(context , safe=False)

    return JsonResponse({'error': 'Invalid request'})
