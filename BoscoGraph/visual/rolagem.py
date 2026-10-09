# Um quadro que rola: se o conteúdo não cabe na altura (janela pequena ou letras grandes), aparece a barra
# de rolagem à direita e a roda do mouse rola o conteúdo. Se cabe, a barra some.
#
# O Tkinter não tem um quadro que rola pronto. O jeito de sempre é este:
#   QuadroRolavel (Frame)
#     ├── Canvas  -> a "janela" por onde o conteúdo aparece (o Canvas sabe rolar)
#     │     └── conteudo (Frame, dentro do Canvas com create_window) -> onde ficam os componentes
#     └── Scrollbar -> ligada ao Canvas
# Uso:
#   quadro = QuadroRolavel(pai, app, fundo="#ffffff")
#   ttk.Label(quadro.conteudo, text="...").pack()      # os componentes vão no "conteudo"
#   quadro.ligar_roda()                                 # depois de criar os componentes: a roda do mouse rola

import tkinter as tk
from tkinter import ttk

MASCARA_DO_CTRL = 0x0004            # o bit do Ctrl no "state" do evento (Ctrl + roda é o zoom, não rola)


class QuadroRolavel(tk.Frame):
    # largura_do_conteudo=True: o quadro pede a largura que o conteúdo precisa (não encolhe o conteúdo)
    def __init__(self, pai, app, fundo, largura_do_conteudo=True, **opcoes):
        super().__init__(pai, bg=fundo, **opcoes)
        self.app = app
        self.largura_do_conteudo = largura_do_conteudo
        self.canvas = tk.Canvas(self, bg=fundo, highlightthickness=0, bd=0, yscrollincrement=20)
        self.barra = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.barra.set)
        self.conteudo = tk.Frame(self.canvas, bg=fundo)
        self.janela = self.canvas.create_window(0, 0, window=self.conteudo, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.barra_aparecendo = False
        self.conteudo.bind("<Configure>", lambda evento: self.ajustar())
        self.canvas.bind("<Configure>", lambda evento: self.ajustar())

    # Depois de qualquer mudança de tamanho: a área que rola, a largura do conteúdo e a barra
    def ajustar(self):
        largura_pedida = self.conteudo.winfo_reqwidth()
        altura_pedida = self.conteudo.winfo_reqheight()
        if self.largura_do_conteudo and int(self.canvas.cget("width")) != largura_pedida:
            self.canvas.configure(width=largura_pedida)
        largura = max(self.canvas.winfo_width(), largura_pedida if self.largura_do_conteudo else 1)
        self.canvas.itemconfigure(self.janela, width=largura)
        self.canvas.configure(scrollregion=(0, 0, largura, altura_pedida))
        precisa = altura_pedida > self.canvas.winfo_height() > 1
        if precisa and not self.barra_aparecendo:
            self.barra.pack(side="right", fill="y", before=self.canvas)
            self.barra_aparecendo = True
        elif not precisa and self.barra_aparecendo:
            self.barra.pack_forget()
            self.barra_aparecendo = False
            self.canvas.yview_moveto(0)

    # A roda do mouse em cima de qualquer componente do conteúdo rola o quadro (menos nas caixas que
    # rolam sozinhas, como as de texto e as tabelas: nelas a roda rola a própria caixa)
    def ligar_roda(self, componente=None):
        if componente is None:
            componente = self
        if isinstance(componente, (tk.Text, tk.Listbox, ttk.Treeview)):
            return
        for evento in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            componente.bind(evento, self.rolar, add="+")
        for filho in componente.winfo_children():
            self.ligar_roda(filho)

    def rolar(self, evento):
        if evento.state & MASCARA_DO_CTRL:
            return None                     # Ctrl + roda: é o zoom (o aplicativo cuida)
        if not self.barra_aparecendo:
            return None
        if evento.num == 4:
            passos = -1
        elif evento.num == 5:
            passos = 1
        elif evento.delta > 0:
            passos = -1
        else:
            passos = 1
        self.canvas.yview_scroll(passos * 2, "units")
        return "break"

    # Rola até o componente aparecer (por exemplo, o grupo que acabou de abrir na sanfona)
    def mostrar(self, componente):
        self.update_idletasks()
        altura_total = self.conteudo.winfo_reqheight()
        if altura_total <= 0:
            return
        topo = componente.winfo_rooty() - self.conteudo.winfo_rooty()
        fundo = topo + componente.winfo_height()
        visivel_de = self.canvas.canvasy(0)
        visivel_ate = visivel_de + self.canvas.winfo_height()
        if topo < visivel_de:
            self.canvas.yview_moveto(topo / altura_total)
        elif fundo > visivel_ate:
            self.canvas.yview_moveto(max(0, fundo - self.canvas.winfo_height()) / altura_total)
