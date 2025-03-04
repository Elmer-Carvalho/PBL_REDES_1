import osmnx as ox
import matplotlib.pyplot as plt

# Coordenadas
veiculo = (-23.5505, -46.6333)
posto = (-23.5650, -46.6500)

# Centro entre os pontos
centro = ((veiculo[0] + posto[0]) / 2, (veiculo[1] + posto[1]) / 2)

try:
    # Configurar o OSMnx para verbosity
    ox.settings.log_console = True
    ox.settings.use_cache = True
    print(f"Centro: {centro}, Distância: 1000 metros")

    # Criar o grafo a partir de um ponto central
    print("Baixando o grafo...")
    G = ox.graph_from_point(centro, dist=1000, network_type="drive")  # Removido 'center='
    print("Grafo baixado com sucesso.")

    # Calcular a rota
    orig_node = ox.distance.nearest_nodes(G, veiculo[1], veiculo[0])
    dest_node = ox.distance.nearest_nodes(G, posto[1], posto[0])
    rota = ox.shortest_path(G, orig_node, dest_node, weight="length")
    print("Rota calculada:", rota)

    # Exibir e salvar o mapa
    fig, ax = ox.plot_graph_route(G, rota, route_color="r", route_linewidth=4, node_size=0, bgcolor="w")
    plt.savefig("mapa_teste.png")
    print("Mapa salvo como 'mapa_teste.png' no diretório atual.")
    plt.show()
except Exception as e:
    print(f"Erro ocorrido: {e}")