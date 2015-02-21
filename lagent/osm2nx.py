import networkx as nx
from osm import *
import geopy as geo
from geopy.distance import distance


def make_weighted(G):
    """
    A method for converting NetworkX graph with geo positions into a weighted NetworkX graph. The distance between points is
    inversely proportional to the distance between points.
    :return: weighted network in NetworkX format, maximum distance between two nodes
    """
    G = next(nx.connected_component_subgraphs(G))
    # For each edge, put (geographical distance * -1) as its weight. Calculate the largest distance beteen nodes
    max_distance = 0
    for u,v,d in G.edges(data=True):
        u_point = geo.Point(G.node[u]['data'].lat, G.node[u]['data'].lon)
        v_point = geo.Point(G.node[v]['data'].lat, G.node[v]['data'].lon)
        closeness = -(distance(u_point,v_point).kilometers)
        G[u][v]['weight'] = closeness

        if abs(closeness) > max_distance:
            max_distance = abs(closeness)

    # Add max distance to each of the weights. Thus, the higher the weight, the closer are two nodes physically.
    for u,v,d in G.edges(data=True):
        G[u][v]['weight'] += max_distance
    return G, max_distance

def simplify_by_degree(G, max_distance):
    """
    Simplify the graph. Remove every node where degree=2 and connect their neighbour nodes, making the roads straight.
    Thus, rather than describing the structure of the road, the network describes its connectivity.
    :param G: NetworkX graph created by the osm2nx method
    :param max_distance: max distance between two nodes in the network. Asked as a parameter to avoid repetitive iteration
    :return: Simplified network in NetworkX format
    """
    G_simple = G
    for n in G_simple.nodes():
        if G_simple.degree(n) == 2:

            # Find the weight for the new edge
            weight_uv_1 = G[n][G.neighbors(n)[0]]['weight'] - max_distance
            weight_uv_2 = G[n][G.neighbors(n)[1]]['weight'] - max_distance
            weight_new = weight_uv_1 + weight_uv_2 + max_distance

            G_simple.add_edge(G.neighbors(n)[0],G.neighbors(n)[1], weight=weight_new)
            G_simple.remove_node(n)

    print(G_simple.number_of_nodes())
    return G_simple


G = read_osm(download_osm(-2.8473, 56.3207, -2.7600, 56.3672))
G, max_distance = make_weighted(G)
G = simplify_by_degree(G,max_distance)





