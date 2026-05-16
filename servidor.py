"""
Servidor gRPC — Calculadora Distribuída
=======================================
Baseado no padrão do repositório oficial:
  grpc/grpc/examples/python/helloworld/greeter_server.py

Estrutura idêntica ao helloworld:
  - ThreadPoolExecutor como executor do servidor
  - server.add_insecure_port para escuta na porta 50051
  - server.start() + server.wait_for_termination()

Para executar:
    pip install grpcio grpcio-tools
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. calculadora.proto
    python servidor.py
"""

from concurrent import futures
import logging
import math

import grpc
import calculadora_pb2
import calculadora_pb2_grpc

# ── Constante de porta (igual ao helloworld) ──────────────────────────────────
PORT = "50051"


# ══════════════════════════════════════════════════════════════════════════════
#  Implementação do Servicer
# ══════════════════════════════════════════════════════════════════════════════

class CalculadoraServicer(calculadora_pb2_grpc.CalculadoraServicer):
    """
    Implementa todos os RPCs definidos em calculadora.proto.

    Tipos de RPC cobertos:
      • Unary             — Somar, Subtrair, Multiplicar, Dividir,
                            CalcularPotencia, CalcularRaizQuadrada
      • Client Streaming  — SomarStream
      • Server Streaming  — GerarTabuada
      • Bidirectional     — CalcularMediaMovel
    """

    # ── Helpers internos ──────────────────────────────────────────────────────

    def _abortar(self, context, codigo, msg):
        """Aborta o RPC com um código de status e mensagem de erro."""
        logging.warning("[ERRO] %s", msg)
        context.abort(codigo, msg)

    # ── Unary RPCs ────────────────────────────────────────────────────────────

    def Somar(self, request, context):
        """Recebe dois números e retorna a soma."""
        resultado = request.a + request.b
        logging.info("Somar(%g, %g) = %g", request.a, request.b, resultado)
        return calculadora_pb2.Resultado(valor=resultado)

    def Subtrair(self, request, context):
        """Recebe dois números e retorna a diferença."""
        resultado = request.a - request.b
        logging.info("Subtrair(%g, %g) = %g", request.a, request.b, resultado)
        return calculadora_pb2.Resultado(valor=resultado)

    def Multiplicar(self, request, context):
        """Recebe dois números e retorna o produto."""
        resultado = request.a * request.b
        logging.info("Multiplicar(%g, %g) = %g", request.a, request.b, resultado)
        return calculadora_pb2.Resultado(valor=resultado)

    def Dividir(self, request, context):
        """
        Recebe dois números e retorna o quociente.
        Retorna INVALID_ARGUMENT se o divisor for zero.
        """
        if request.b == 0:
            self._abortar(
                context,
                grpc.StatusCode.INVALID_ARGUMENT,
                "Divisão por zero não é permitida.",
            )
            return calculadora_pb2.Resultado()

        resultado = request.a / request.b
        logging.info("Dividir(%g, %g) = %g", request.a, request.b, resultado)
        return calculadora_pb2.Resultado(valor=resultado)

    def CalcularPotencia(self, request, context):
        """Recebe base (a) e expoente (b) e retorna a ** b."""
        resultado = request.a ** request.b
        logging.info("Potencia(%g ^ %g) = %g", request.a, request.b, resultado)
        return calculadora_pb2.Resultado(valor=resultado)

    def CalcularRaizQuadrada(self, request, context):
        """
        Recebe um número e retorna sua raiz quadrada.
        Retorna INVALID_ARGUMENT para números negativos.
        """
        if request.numero < 0:
            self._abortar(
                context,
                grpc.StatusCode.INVALID_ARGUMENT,
                f"Não é possível calcular a raiz quadrada de {request.numero} (número negativo).",
            )
            return calculadora_pb2.Resultado()

        resultado = math.sqrt(request.numero)
        logging.info("RaizQuadrada(%g) = %g", request.numero, resultado)
        return calculadora_pb2.Resultado(valor=resultado)

    # ── Client Streaming RPC ──────────────────────────────────────────────────

    def SomarStream(self, request_iterator, context):
        """
        Recebe um stream de números do cliente e retorna a soma total.
        O cliente envia quantos números quiser e encerra o stream.
        """
        total = 0.0
        contagem = 0

        for req in request_iterator:
            total += req.numero
            contagem += 1
            logging.info("  [SomarStream] recebido: %g (acumulado: %g)", req.numero, total)

        logging.info("SomarStream concluído: %d números, soma = %g", contagem, total)
        return calculadora_pb2.SomaTotal(total=total)

    # ── Server Streaming RPC ──────────────────────────────────────────────────

    def GerarTabuada(self, request, context):
        """
        Recebe um número e envia de volta um stream com a tabuada (1 × n a 10 × n),
        uma linha por vez.
        """
        n = request.numero
        logging.info("GerarTabuada(%d): iniciando stream", n)

        for multiplicador in range(1, 11):
            resultado = n * multiplicador
            logging.info("  [GerarTabuada] %d × %d = %d", n, multiplicador, resultado)
            yield calculadora_pb2.LinhaTabuada(
                multiplicador=multiplicador,
                resultado=float(resultado),
            )

        logging.info("GerarTabuada(%d): stream encerrado", n)

    # ── Bidirectional Streaming RPC ───────────────────────────────────────────

    def CalcularMediaMovel(self, request_iterator, context):
        """
        Recebe um stream de números e, a cada novo número recebido, envia
        de volta a média parcial e a contagem atual.
        """
        soma = 0.0
        contagem = 0

        for req in request_iterator:
            soma += req.numero
            contagem += 1
            media = soma / contagem

            logging.info(
                "  [MediaMovel] novo=%g | soma=%g | n=%d | média=%.4f",
                req.numero, soma, contagem, media,
            )

            yield calculadora_pb2.MediaParcial(
                media=media,
                contagem=contagem,
            )

        logging.info("CalcularMediaMovel concluído: %d números processados", contagem)


# ══════════════════════════════════════════════════════════════════════════════
#  Inicialização do servidor  (padrão helloworld)
# ══════════════════════════════════════════════════════════════════════════════

def serve():
    """Configura e inicia o servidor gRPC."""
    # ThreadPoolExecutor com 10 workers — igual ao helloworld
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Registra o servicer no servidor
    calculadora_pb2_grpc.add_CalculadoraServicer_to_server(
        CalculadoraServicer(), server
    )

    # Porta insegura (sem TLS) — suficiente para fins didáticos
    server.add_insecure_port("[::]:" + PORT)

    server.start()
    logging.info("Servidor Calculadora iniciado na porta %s", PORT)
    print(f"✓ Servidor gRPC escutando na porta {PORT} — pressione Ctrl+C para encerrar.")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("Encerrando servidor...")
        server.stop(grace=5)   # aguarda 5 s para RPCs em andamento finalizarem
        print("\n✗ Servidor encerrado.")


# ══════════════════════════════════════════════════════════════════════════════
#  Entry-point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    serve()
