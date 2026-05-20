"""
janela.py
---------
Interface gráfica Tkinter — Cliente gRPC Calculadora.
Não faz nenhum cálculo: envia dados ao servidor e exibe o retorno.
"""

import tkinter as tk
from tkinter import messagebox
import grpc

import greeter_client as client


# ── Helpers de UI ─────────────────────────────────────────────────────────────

def obter_numeros(requer_dois=True):
    try:
        num1 = float(entry_num1.get())
        if requer_dois:
            num2 = float(entry_num2.get())
            return num1, num2
        return num1, None
    except ValueError:
        msg = ("Por favor, insira números válidos em ambos os campos."
               if requer_dois else
               "Por favor, insira um número válido no Campo 1.")
        messagebox.showerror("Erro de Entrada", msg)
        return None


def atualizar_tela(valor, nome_operacao):
    # Remove .0 de inteiros para exibição mais limpa
    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)
    label_resultado.config(text=f"Resultado: {valor}")
    label_historico.config(text=f"Último comando: {nome_operacao} (Calculado no Servidor)")


# ── Handlers dos botões ───────────────────────────────────────────────────────

def disparar_operacao_binaria(operacao):
    valores = obter_numeros(requer_dois=True)
    if valores is None:
        return
    num1, num2 = valores

    try:
        # Resultado vem em .valor (campo do proto Resultado)
        if operacao == 'somar':
            res = client.rpc_somar(num1, num2)
            atualizar_tela(res.valor, "Soma")
        elif operacao == 'subtrair':
            res = client.rpc_subtrair(num1, num2)
            atualizar_tela(res.valor, "Subtração")
        elif operacao == 'multiplicar':
            res = client.rpc_multiplicar(num1, num2)
            atualizar_tela(res.valor, "Multiplicação")
        elif operacao == 'dividir':
            res = client.rpc_dividir(num1, num2)
            atualizar_tela(res.valor, "Divisão")
        elif operacao == 'potencia':
            res = client.rpc_calcular_potencia(num1, num2)
            atualizar_tela(res.valor, "Potência")

    except grpc.RpcError as e:
        messagebox.showerror("Erro gRPC", e.details())
    except ConnectionError as e:
        messagebox.showerror("Erro de Conexão", str(e))


def disparar_raiz():
    valores = obter_numeros(requer_dois=False)
    if valores is None:
        return
    num1, _ = valores
    try:
        res = client.rpc_calcular_raiz_quadrada(num1)
        atualizar_tela(res.valor, "Raiz Quadrada")
    except grpc.RpcError as e:
        messagebox.showerror("Erro gRPC", e.details())
    except ConnectionError as e:
        messagebox.showerror("Erro de Conexão", str(e))


def disparar_somar_stream():
    valores = obter_numeros(requer_dois=True)
    if valores is None:
        return
    num1, num2 = valores
    try:
        res = client.rpc_somar_stream(num1, num2)
        # SomarStream retorna SomaTotal com campo .total
        atualizar_tela(res.total, "Soma em Stream")
    except grpc.RpcError as e:
        messagebox.showerror("Erro gRPC", e.details())
    except ConnectionError as e:
        messagebox.showerror("Erro de Conexão", str(e))


def disparar_tabuada():
    valores = obter_numeros(requer_dois=False)
    if valores is None:
        return
    num1, _ = valores
    try:
        respostas = client.rpc_gerar_tabuada(num1)
        # LinhaTabuada tem .multiplicador e .resultado
        n = int(num1)
        linhas = [
            f"{n} × {r.multiplicador} = {int(r.resultado) if r.resultado.is_integer() else r.resultado}"
            for r in respostas
        ]
        messagebox.showinfo(f"Tabuada do {n}", "\n".join(linhas))
        label_historico.config(text="Tabuada gerada inteiramente no servidor")
    except grpc.RpcError as e:
        messagebox.showerror("Erro gRPC", e.details())
    except ConnectionError as e:
        messagebox.showerror("Erro de Conexão", str(e))


def disparar_media_movel():
    valores = obter_numeros(requer_dois=True)
    if valores is None:
        return
    num1, num2 = valores
    try:
        res = client.rpc_calcular_media_movel(num1, num2)
        if res is None:
            messagebox.showerror("Erro", "Sem resposta do servidor.")
            return
        # MediaParcial tem .media e .contagem
        atualizar_tela(round(res.media, 4), f"Média Móvel (n={res.contagem})")
    except grpc.RpcError as e:
        messagebox.showerror("Erro gRPC", e.details())
    except ConnectionError as e:
        messagebox.showerror("Erro de Conexão", str(e))


def limpar():
    entry_num1.delete(0, tk.END)
    entry_num2.delete(0, tk.END)
    label_resultado.config(text="Resultado: -")
    label_historico.config(text="Último comando: nenhum")


# ── Construção da interface ───────────────────────────────────────────────────

def iniciar_interface():
    global entry_num1, entry_num2, label_resultado, label_historico

    root = tk.Tk()
    root.title("Cliente gRPC - Calculadora Distribuída")
    root.geometry("450x480")
    root.configure(bg="#f4f4f9")

    # Inputs
    frame_inputs = tk.Frame(root, bg="#f4f4f9", pady=10)
    frame_inputs.pack()

    tk.Label(frame_inputs, text="Número 1 (ou base):", bg="#f4f4f9",
             font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_num1 = tk.Entry(frame_inputs, font=("Arial", 12), width=15, justify="center")
    entry_num1.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Número 2 (ou exp):", bg="#f4f4f9",
             font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_num2 = tk.Entry(frame_inputs, font=("Arial", 12), width=15, justify="center")
    entry_num2.grid(row=1, column=1, padx=5, pady=5)

    # Resultado
    label_resultado = tk.Label(root, text="Resultado: -",
                                font=("Arial", 16, "bold"), bg="#f4f4f9",
                                fg="#2c3e50", pady=10)
    label_resultado.pack()

    label_historico = tk.Label(root, text="Último comando: nenhum",
                                font=("Arial", 9, "italic"), bg="#f4f4f9", fg="#7f8c8d")
    label_historico.pack(pady=5)

    # Botões
    frame_botoes = tk.Frame(root, bg="#f4f4f9", pady=10)
    frame_botoes.pack()

    eb = {"font": ("Arial", 11, "bold"), "width": 8,  "height": 2, "bg": "#3498db", "fg": "white", "relief": "flat"}
    ea = {"font": ("Arial", 10, "bold"), "width": 10, "height": 2, "bg": "#e67e22", "fg": "white", "relief": "flat"}
    es = {"font": ("Arial", 10, "bold"), "width": 12, "height": 2, "bg": "#9b59b6", "fg": "white", "relief": "flat"}
    el = {"font": ("Arial", 10, "bold"), "width": 12, "height": 2, "bg": "#e74c3c", "fg": "white", "relief": "flat"}

    tk.Button(frame_botoes, text="+",  command=lambda: disparar_operacao_binaria('somar'),      **eb).grid(row=0, column=0, padx=4, pady=4)
    tk.Button(frame_botoes, text="-",  command=lambda: disparar_operacao_binaria('subtrair'),   **eb).grid(row=0, column=1, padx=4, pady=4)
    tk.Button(frame_botoes, text="*",  command=lambda: disparar_operacao_binaria('multiplicar'),**eb).grid(row=0, column=2, padx=4, pady=4)
    tk.Button(frame_botoes, text="/",  command=lambda: disparar_operacao_binaria('dividir'),    **eb).grid(row=0, column=3, padx=4, pady=4)

    tk.Button(frame_botoes, text="Potência",     command=lambda: disparar_operacao_binaria('potencia'), **ea).grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="we")
    tk.Button(frame_botoes, text="Raiz Quadrada",command=disparar_raiz,                                 **ea).grid(row=1, column=2, columnspan=2, padx=4, pady=4, sticky="we")

    tk.Button(frame_botoes, text="Soma Stream",  command=disparar_somar_stream, **es).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="we")
    tk.Button(frame_botoes, text="Média Móvel",  command=disparar_media_movel,  **es).grid(row=2, column=2, columnspan=2, padx=4, pady=4, sticky="we")

    tk.Button(frame_botoes, text="Gerar Tabuada",command=disparar_tabuada, **es).grid(row=3, column=0, columnspan=2, padx=4, pady=4, sticky="we")
    tk.Button(frame_botoes, text="Limpar Tudo",  command=limpar,           **el).grid(row=3, column=2, columnspan=2, padx=4, pady=4, sticky="we")

    root.mainloop()


if __name__ == "__main__":
    iniciar_interface()
