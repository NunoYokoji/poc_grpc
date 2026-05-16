# Calculadora Distribuída — gRPC (Python)

## Estrutura de arquivos

```
calculadora_grpc/
├── calculadora.proto          # Definição do serviço (fonte da verdade)
├── calculadora_pb2.py         # Stubs de mensagens  (gerado pelo protoc)
├── calculadora_pb2_grpc.py    # Stubs gRPC           (gerado pelo protoc)
├── servidor.py                # ← Implementação do servidor
└── README.md
```

## 1. Instalação

```bash
pip install grpcio grpcio-tools
```

## 2. Gerar (ou regenerar) os stubs

Sempre que `calculadora.proto` for alterado, regenere os stubs:

```bash
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    calculadora.proto
```

## 3. Executar o servidor

```bash
python servidor.py
```

Saída esperada:
```
✓ Servidor gRPC escutando na porta 50051 — pressione Ctrl+C para encerrar.
```

## 4. RPCs implementados

| RPC | Tipo | Descrição |
|---|---|---|
| `Somar` | Unary | Soma dois números |
| `Subtrair` | Unary | Subtrai dois números |
| `Multiplicar` | Unary | Multiplica dois números |
| `Dividir` | Unary | Divide (trata divisão por zero → `INVALID_ARGUMENT`) |
| `CalcularPotencia` | Unary | Calcula `a ^ b` |
| `CalcularRaizQuadrada` | Unary | Raiz quadrada (trata negativos → `INVALID_ARGUMENT`) |
| `SomarStream` | Client Streaming | Recebe N números e retorna a soma total |
| `GerarTabuada` | Server Streaming | Envia a tabuada do número (1×n a 10×n) |
| `CalcularMediaMovel` | Bidirectional | A cada número recebido, retorna a média parcial |

## 5. Testar com grpcurl (opcional)

```bash
# Unary — somar
grpcurl -plaintext -d '{"a": 10, "b": 5}' \
    localhost:50051 calculadora.Calculadora/Somar

# Server streaming — tabuada do 7
grpcurl -plaintext -d '{"numero": 7}' \
    localhost:50051 calculadora.Calculadora/GerarTabuada
```
