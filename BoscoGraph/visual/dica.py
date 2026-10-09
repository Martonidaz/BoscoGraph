# Dica flutuante (tooltip): um texto curto que aparece quando o mouse para em cima de um controle.
# Serve para os botões com nome curto ("Sobre", a chave do tema sol/lua) explicarem o que fazem sem ocupar espaço.
#
# Uso: Dica(botao, "Abre a pasta onde os modelos são salvos")
# O texto também pode ser uma função (chamada na hora de mostrar), para dicas que mudam.

import tkinter as tk

ESPERA_EM_MILISSEGUNDOS = 500      # quanto tempo o mouse precisa ficar parado para a dica aparecer


class Dica:
    def __init__(self, componente, texto):
        self.componente = componente
        self.texto = texto
        self.janela = None
        self.agendamento = None
        componente.bind("<Enter>", self.agendar, add="+")       # add="+": não apaga outros "binds"
        componente.bind("<Leave>", self.esconder, add="+")
        componente.bind("<ButtonPress>", self.esconder, add="+")

    def agendar(self, evento=None):
        self.cancelar()
        self.agendamento = self.componente.after(ESPERA_EM_MILISSEGUNDOS, self.mostrar)

    def cancelar(self):
        if self.agendamento is not None:
            self.componente.after_cancel(self.agendamento)
            self.agendamento = None

    def mostrar(self):
        self.agendamento = None
        texto = self.texto() if callable(self.texto) else self.texto
        if not texto or self.janela is not None:
            return
        # Uma janelinha sem borda nem barra de título (overrideredirect), logo abaixo do controle
        self.janela = tk.Toplevel(self.componente)
        self.janela.wm_overrideredirect(True)
        x = self.componente.winfo_rootx() + 8
        y = self.componente.winfo_rooty() + self.componente.winfo_height() + 4
        self.janela.wm_geometry(f"+{x}+{y}")
        tk.Label(self.janela, text=texto, justify="left", wraplength=360, background="#fffbe6",
                 foreground="#1f2933", relief="solid", borderwidth=1, padx=6, pady=4).pack()

    def esconder(self, evento=None):
        self.cancelar()
        if self.janela is not None:
            self.janela.destroy()
            self.janela = None
