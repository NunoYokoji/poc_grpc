import tkinter as tk
from tkinter import messagebox
import grpc

import greeter_client as client

# --- Funções de Validação e Tela ---
def obter_numeros(requer_dois=True):
    try:
        num1 = float(entry_num1.get())
        if requer_dois:
            num2 = float(entry_num2.get())
            return num1, num2
        return num1, None
    except ValueError:
        msg = "Por favor, insira números válidos em ambos os campos." if requer_dois else "Por favor, insira um número válido no Campo 1."
        messagebox.showerror("Erro de Entrada", msg)
        return None

def atualizar_tela(resultado_remoto, nome_operacao):
    # O cliente apenas formata visualmente o número recebido (ex: remove .0 se for inteiro)
    if isinstance(resultado_remoto, (int, float)) and resultado_remoto.is_integer():
        resultado_remoto = int(resultado_remoto)
        
    label_resultado.config(text=f"Resultado: {resultado_remoto}")
    label_historico.config(text=f"Último comando: {nome_operacao} (Calculado no Servidor)")

# --- Handlers dos Botões (Pontes puras para o gRPC) ---
def disparar_operacao_binaria(operacao):
    valores = obter_numeros(requer_dois=True)
    if valores is None: return
    num1, num2 = valores

    try:
        # O cliente NÃO faz contas. Ele envia os dados, recebe a resposta 
        # e exibe o atributo vindo do servidor (.resultado)
        if operacao == 'somar':
            res = client.rpc_somar(num1, num2)
            atualizar_tela(res.resultado, "Soma")
        elif operacao == 'subtrair':
            res = client.rpc_subtrair(num1, num2)
            atualizar_tela(res.resultado, "Subtração")
        elif operacao == 'multiplicar':
            res = client.rpc_multiplicar(num1, num2)
            atualizar_tela(res.resultado, "Multiplicação")
        elif operacao == 'dividir':
            res = client.rpc_dividir(num1, num2)
            atualizar_tela(res.resultado, "Divisão")
        elif operacao == 'potencia':
            res = client.rpc_calcular_potencia(num1, num2)
            atualizar_tela(res.resultado, "Potência")
            
    except (grpc.RpcError, ConnectionError) as e:
        messagebox.showerror("Erro gRPC", str(e.details() if hasattr(e, 'details') else e))

def disparar_raiz():
    valores = obter_numeros(requer_dois=False)
    if valores is None: return
    num1, _ = valores
    try:
        res = client.rpc_calcular_raiz_quadrada(num1)
        atualizar_tela(res.resultado, "Raiz Quadrada")
    except (grpc.RpcError, ConnectionError) as e:
        messagebox.showerror("Erro gRPC", str(e.details() if hasattr(e, 'details') else e))

def disparar_somar_stream():
    valores = obter_numeros(requer_dois=True)
    if valores is None: return
    num1, num2 = valores
    try:
        res = client.rpc_somar_stream(num1, num2)
        atualizar_tela(res.resultado, "Soma em Stream")
    except (grpc.RpcError, ConnectionError) as e:
        messagebox.showerror("Erro gRPC", str(e.details() if hasattr(e, 'details') else e))

def disparar_tabuada():
    valores = obter_numeros(requer_dois=False)
    if valores is None: return
    num1, _ = valores
    try:
        respostas_stream = client.rpc_gerar_tabuada(num1)
        # O servidor envia as linhas prontas. O cliente apenas agrupa o texto.
        linhas = [resposta.linha for resposta in respostas_stream]
        messagebox.showinfo(f"Tabuada do {num1}", "\n".join(linhas))
        label_historico.config(text="Tabuada gerada inteiramente no servidor")
    except (grpc.RpcError, ConnectionError) as e:
        messagebox.showerror("Erro gRPC", str(e.details() if hasattr(e, 'details') else e))

def disparar_media_movel():
    valores = obter_numeros(requer_dois=True)
    if valores is None: return
    num1, num2 = valores
    try:
        res = client.rpc_calcular_media_movel(num1, num2)
        atualizar_tela(res.resultado, "Média Móvel")
    except (grpc.RpcError, ConnectionError) as e:
        messagebox.showerror("Erro gRPC", str(e.details() if hasattr(e, 'details') else e))

def limpar():
    entry_num1.delete(0, tk.END)
    entry_num2.delete(0, tk.END)
    label_resultado.config(text="Resultado: -")
    label_historico.config(text="Último comando: nenhum")

# --- Construção da Interface (O resto do layout permanece igual) ---
def iniciar_interface():
    global entry_num1, entry_num2, label_resultado, label_historico
    
    root = tk.Tk()
    root.title("Cliente gRPC - Calculadora Pura")
    root.geometry("450x480")
    root.configure(bg="#f4f4f9")

    frame_inputs = tk.Frame(root, bg="#f4f4f9", pady=10)
    frame_inputs.pack()

    tk.Label(frame_inputs, text="Número 1 (ou base):", bg="#f4f4f9", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, pady=5, sticky="e")
    entry_num1 = tk.Entry(frame_inputs, font=("Arial", 12), width=15, justify="center")
    entry_num1.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_inputs, text="Número 2 (ou pot):", bg="#f4f4f9", font=("Arial", 10, "bold")).grid(row=1, column=0, padx=5, pady=5, sticky="e")
    entry_num2 = tk.Entry(frame_inputs, font=("Arial", 12), width=15, justify="center")
    entry_num2.grid(row=1, column=1, padx=5, pady=5)

    label_resultado = tk.Label(root, text="Resultado: -", font=("Arial", 16, "bold"), bg="#f4f4f9", fg="#2c3e50", pady=10)
    label_resultado.pack()

    label_historico = tk.Label(root, text="Último comando: nenhum", font=("Arial", 9, "italic"), bg="#f4f4f9", fg="#7f8c8d")
    label_historico.pack(pady=5)

    frame_botoes = tk.Frame(root, bg="#f4f4f9", pady=10)
    frame_botoes.pack()

    estilo_basico = {"font": ("Arial", 11, "bold"), "width": 8, "height": 2, "bg": "#3498db", "fg": "white", "relief": "flat"}
    estilo_avancado = {"font": ("Arial", 10, "bold"), "width": 10, "height": 2, "bg": "#e67e22", "fg": "white", "relief": "flat"}
    estilo_streams = {"font": ("Arial", 10, "bold"), "width": 12, "height": 2, "bg": "#9b59b6", "fg": "white", "relief": "flat"}
    estilo_limpar = {"font": ("Arial", 10, "bold"), "width": 12, "height": 2, "bg": "#e74c3c", "fg": "white", "relief": "flat"}

    tk.Button(frame_botoes, text="+", command=lambda: disparar_operacao_binaria('somar'), **estilo_basico).grid(row=0, column=0, padx=4, pady=4)
    tk.Button(frame_botoes, text="-", command=lambda: disparar_operacao_binaria('subtrair'), **estilo_basico).grid(row=0, column=1, padx=4, pady=4)
    tk.Button(frame_botoes, text="*", command=lambda: disparar_operacao_binaria('multiplicar'), **estilo_basico).grid(row=0, column=2, padx=4, pady=4)
    tk.Button(frame_botoes, text="/", command=lambda: disparar_operacao_binaria('dividir'), **estilo_basico).grid(row=0, column=3, padx=4, pady=4)

    tk.Button(frame_botoes, text="Potência", command=lambda: disparar_operacao_binaria('potencia'), **estilo_avancado).grid(row=1, column=0, columnspan=2, padx=4, pady=4, sticky="we")
    tk.Button(frame_botoes, text="Raiz Quadrada", command=disparar_raiz, **estilo_avancado).grid(row=1, column=2, columnspan=2, padx=4, pady=4, sticky="we")

    tk.Button(frame_botoes, text="SomarStream", command=disparar_somar_stream, **estilo_streams).grid(row=2, column=0, columnspan=2, padx=4, pady=4, sticky="we")
    tk.Button(frame_botoes, text="Média Móvel", command=disparar_media_movel, **estilo_streams).grid(row=2, column=2, columnspan=2, padx=4, pady=4, sticky="we")

    tk.Button(frame_botoes, text="Gerar Tabuada", command=disparar_tabuada, **estilo_streams).grid(row=3, column=0, columnspan=2, padx=4, pady=4, sticky="we")
    tk.Button(frame_botoes, text="Limpar Tudo", command=limpar, **estilo_limpar).grid(row=3, column=2, columnspan=2, padx=4, pady=4, sticky="we")

    root.mainloop()

if __name__ == "__main__":
    iniciar_interface()