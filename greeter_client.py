import logging
import grpc

def obter_stub():
    """Cria um canal e retorna o stub do gRPC."""
    try:
        channel = grpc.insecure_channel("localhost:50051")
        return pb2_grpc.CalculadoraStub(channel)
    except Exception as e:
        print(f"Erro de conexão com o servidor gRPC: {e}")
        return None

def rpc_somar(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.Somar(pb2.NumeroRequest(num1=num1, num2=num2))

def rpc_subtrair(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.Subtrair(pb2.NumeroRequest(num1=num1, num2=num2))

def rpc_multiplicar(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.Multiplicar(pb2.NumeroRequest(num1=num1, num2=num2))

def rpc_dividir(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.Dividir(pb2.NumeroRequest(num1=num1, num2=num2))

def rpc_calcular_potencia(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.CalcularPotencia(pb2.NumeroRequest(num1=num1, num2=num2))

def rpc_calcular_raiz_quadrada(num1):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.CalcularRaizQuadrada(pb2.RaizRequest(num=num1))

def rpc_somar_stream(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    def iterador():
        yield pb2.NumeroUnicoRequest(num=num1)
        yield pb2.NumeroUnicoRequest(num=num2)
    return stub.SomarStream(iterador())

def rpc_gerar_tabuada(num1):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    return stub.GerarTabuada(pb2.TabuadaRequest(num=num1))

def rpc_calcular_media_movel(num1, num2):
    stub = obter_stub()
    if not stub: raise ConnectionError("Servidor gRPC indisponível.")
    def iterador():
        yield pb2.NumeroUnicoRequest(num=num1)
        yield pb2.NumeroUnicoRequest(num=num2)
    return stub.CalcularMediaMovel(iterador())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)