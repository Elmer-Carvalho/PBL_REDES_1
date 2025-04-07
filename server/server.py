import socket
import json
import threading
import selectors
import sys
import traceback
from controller import route_request
from utils.time_utils import get_current_timestamp
from station_monitor import StationMonitor  # Importa o monitor

class Server:
    def __init__(self, host='0.0.0.0', port=8888, max_connections=100):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.selector = selectors.DefaultSelector()
        self.running = False
        self.monitor = StationMonitor()  # Instancia o monitor

    def start(self):
        """Inicializa e executa o servidor."""
        try:
            # Inicia o monitoramento de postos
            self.monitor.start()

            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_connections)
            self.server_socket.setblocking(False)
            
            self.selector.register(self.server_socket, selectors.EVENT_READ, data=None)
            
            self.running = True
            print(f"Servidor iniciado em {self.host}:{self.port}")
            
            while self.running:
                events = self.selector.select(timeout=1)
                for key, mask in events:
                    if key.data is None:
                        self._accept_connection(key.fileobj)
                    else:
                        self._handle_client_data(key, mask)
                        
        except KeyboardInterrupt:
            print("Servidor interrompido pelo usuário")
        except Exception as e:
            print(f"Erro no servidor: {e}")
            traceback.print_exc()
        finally:
            self.stop()
    
    def stop(self):
        """Encerra o servidor de forma segura."""
        print("Encerrando servidor...")
        self.running = False
        self.monitor.stop()  # Para o monitoramento
        
        for key in list(self.selector.get_map().values()):
            try:
                self.selector.unregister(key.fileobj)
                key.fileobj.close()
            except:
                pass
                
        self.selector.close()
        print("Servidor encerrado")

    # (Métodos _accept_connection, _handle_client_data, _check_complete_json, _process_message, _close_connection permanecem iguais)

if __name__ == "__main__":
    port = 8888
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Porta inválida: {sys.argv[1]}. Usando porta padrão 8888.")
    
    server = Server(port=port)
    server.start()
    