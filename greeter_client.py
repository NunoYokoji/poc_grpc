"""
greeter_client.py
-----------------
Camada de comunicação gRPC — chamada pelo janela.py.
Cada função abre um canal, chama o RPC correspondente e retorna a resposta.
"""

import grpc
import calculadora_pb2 as pb2
import calculadora_pb2_grpc as pb2_grpc


def _stub():
    """Cria canal e retorna stub. Lança ConnectionError se indisponível."""
    try:
        channel = grpc.insecure_channel("localhost:50051")
        return pb2_grpc.CalculadoraStub(channel), channel
    except Exception as e:
        raise ConnectionError(f"Erro de conexão com o servidor gRPC: {e}")


# ── Unary RPCs ────────────────────────────────────────────────────────────────

def rpc_somar(num1, num2):
    stub, _ = _stub()
    return stub.Somar(pb2.DoisNumeros(a=num1, b=num2))

def rpc_subtrair(num1, num2):
    stub, _ = _stub()
    return stub.Subtrair(pb2.DoisNumeros(a=num1, b=num2))

def rpc_multiplicar(num1, num2):
    stub, _ = _stub()
    return stub.Multiplicar(pb2.DoisNumeros(a=num1, b=num2))

def rpc_dividir(num1, num2):
    stub, _ = _stub()
    return stub.Dividir(pb2.DoisNumeros(a=num1, b=num2))

def rpc_calcular_potencia(num1, num2):
    stub, _ = _stub()
    return stub.CalcularPotencia(pb2.DoisNumeros(a=num1, b=num2))

def rpc_calcular_raiz_quadrada(num1):
    stub, _ = _stub()
    return stub.CalcularRaizQuadrada(pb2.NumeroUnico(numero=num1))

# ── Client Streaming ──────────────────────────────────────────────────────────

def rpc_somar_stream(num1, num2):
    stub, _ = _stub()
    def iterador():
        yield pb2.NumeroStream(numero=num1)
        yield pb2.NumeroStream(numero=num2)
    return stub.SomarStream(iterador())

# ── Server Streaming ──────────────────────────────────────────────────────────

def rpc_gerar_tabuada(num1):
    stub, _ = _stub()
    # Retorna o iterador de LinhaTabuada (cada item tem .multiplicador e .resultado)
    return stub.GerarTabuada(pb2.EntradaTabuada(numero=int(num1)))

# ── Bidirectional Streaming ───────────────────────────────────────────────────

def rpc_calcular_media_movel(num1, num2):
    stub, _ = _stub()
    def iterador():
        yield pb2.NumeroStream(numero=num1)
        yield pb2.NumeroStream(numero=num2)
    # Retorna iterador de MediaParcial — pegamos o último (média final)
    ultimo = None
    for resp in stub.CalcularMediaMovel(iterador()):
        ultimo = resp
    return ultimo
