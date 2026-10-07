#!/usr/bin/env python3
"""
🐍 La Culebrita Hambrienta: versión con interfaz gráfica 🍎
DFS (culebrita loca) vs. BFS (culebrita olfateadora), animados en una ventana.

Cómo usarlo:
  - Botones DFS / BFS: la culebrita sale a buscar la manzana (se anima paso a paso).
  - Clic en una casilla: pone o quita una roca 🪨 (¡diseña tu propio laberinto!).
  - "Aleatorio": genera un laberinto nuevo. "Reiniciar": limpia los rastros.
  - Deslizador: controla qué tan rápido se arrastra la culebrita.
"""

import random
import tkinter as tk
from collections import deque


# Laberinto inicial (mismo de la versión de terminal)

LABERINTO_INICIAL = [
    "S......",
    ".#####.",
    ".....#.",
    "####.#.",
    ".......",
    ".#####.",
    "......F",
]

TAM = 72  # tamaño de cada casilla en píxeles
MOVIMIENTOS = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # abajo, derecha, arriba, izquierda

COLORES = {
    "pasto": "#a8e6a1",
    "pasto_alt": "#9ddc96",
    "roca": "#6b6b6b",
    "explorada": "#9ec9ff",
    "camino": "#ffe066",
    "borde": "#5c8f56",
}


# ---------------------------------------------------------------------------
# Algoritmos (como generadores, para poder animarlos paso a paso)
# Cada uno produce ("explorar", casilla) por cada casilla que visita y, al final,
# ("camino", lista_de_casillas) o ("camino", None) si no hay forma de llegar.
# ---------------------------------------------------------------------------
def vecinos(grid, pos):
    """Casillas vecinas por donde la culebrita SÍ puede arrastrarse."""
    f, c = pos
    for df, dc in MOVIMIENTOS:
        nf, nc = f + df, c + dc
        if 0 <= nf < len(grid) and 0 <= nc < len(grid[0]) and grid[nf][nc] != "#":
            yield (nf, nc)


def dfs_pasos(grid, inicio, meta):
    """
    DFS con PILA: la culebrita se vuelve LOCA 🌀. Se lanza de frente lo más lejos
    que puede, hasta chocar con una roca, y solo entonces da reversa. Va a ciegas,
    así que llega, pero casi siempre por un camino larguísimo.
    """
    pila = [(inicio, [inicio])]
    visitadas = set()
    while pila:
        pos, camino = pila.pop()  # Saca la ÚLTIMA apilada: sigue de frente
        if pos in visitadas:
            continue
        visitadas.add(pos)
        yield ("explorar", pos)
        if pos == meta:  #ÑAM!
            yield ("camino", camino)
            return
        for v in vecinos(grid, pos):
            if v not in visitadas:
                pila.append((v, camino + [v]))
    yield ("camino", None)


def bfs_pasos(grid, inicio, meta):
    """
    BFS con COLA: la culebrita OLFATEADORA 🌊. Huele por capas (1 paso, 2 pasos,
    3 pasos...) como una onda en el agua, así que la primera vez que huele la
    manzana ya va por el camino MÁS CORTO.
    """
    cola = deque([(inicio, [inicio])])
    visitadas = {inicio}
    while cola:
        pos, camino = cola.popleft()  #Saca la MÁS ANTIGUA: avanza por capas
        yield ("explorar", pos)
        if pos == meta: 
            yield ("camino", camino)
            return
        for v in vecinos(grid, pos):
            if v not in visitadas:
                visitadas.add(v)
                cola.append((v, camino + [v]))
    yield ("camino", None)



#La ventana

class AventuraCulebrita:
    def __init__(self, root):
        self.root = root
        root.title("🐍 La Aventura de la Culebrita 🍎")
        root.resizable(False, False)

        self.grid = [list(fila) for fila in LABERINTO_INICIAL]
        self.filas, self.cols = len(self.grid), len(self.grid[0])
        self.inicio, self.meta = self._buscar("S"), self._buscar("F")

        self.explorada, self.camino = set(), []
        self.cabeza = None            # dónde va la cabeza durante la animación
        self.generador = None
        self.trabajo = None           # id del after() pendiente
        self.resultados = {}          # {"DFS": pasos, "BFS": pasos}
        self.nombre_actual = ""

        tk.Label(root, text="🐍 La Aventura de la Culebrita 🍎",
                 font=("Helvetica", 16, "bold")).pack(pady=(10, 0))
        tk.Label(root, text="Clic en una casilla para poner/quitar rocas 🪨",
                 font=("Helvetica", 10)).pack()

        self.canvas = tk.Canvas(root, width=self.cols * TAM, height=self.filas * TAM,
                                highlightthickness=0)
        self.canvas.pack(padx=12, pady=8)
        self.canvas.bind("<Button-1>", self.al_hacer_clic)

        barra = tk.Frame(root)
        barra.pack(pady=4)
        tk.Button(barra, text="🌀 DFS (Loca)", width=14,
                  command=lambda: self.ejecutar("DFS")).grid(row=0, column=0, padx=4)
        tk.Button(barra, text="🌊 BFS (Olfateadora)", width=18,
                  command=lambda: self.ejecutar("BFS")).grid(row=0, column=1, padx=4)
        tk.Button(barra, text="🔄 Reiniciar", width=12,
                  command=self.reiniciar).grid(row=0, column=2, padx=4)
        tk.Button(barra, text="🎲 Aleatorio", width=12,
                  command=self.aleatorio).grid(row=0, column=3, padx=4)

        vel = tk.Frame(root)
        vel.pack()
        tk.Label(vel, text="Velocidad:").pack(side="left")
        self.velocidad = tk.Scale(vel, from_=1, to=10, orient="horizontal", length=180)
        self.velocidad.set(6)
        self.velocidad.pack(side="left")

        self.estado = tk.Label(root, text="Elige un algoritmo para empezar.",
                               font=("Helvetica", 11))
        self.estado.pack(pady=(6, 2))
        self.comparacion = tk.Label(root, text="", font=("Helvetica", 11, "bold"))
        self.comparacion.pack(pady=(0, 10))

        self.dibujar()

    #utilidades 
    def _buscar(self, letra):
        for f, fila in enumerate(self.grid):
            for c, celda in enumerate(fila):
                if celda == letra:
                    return (f, c)

    def _retraso(self):
        # Velocidad 1 = lento (400 ms), velocidad 10 = rápido (20 ms)
        return int(420 - self.velocidad.get() * 40)

    def _cancelar(self):
        if self.trabajo is not None:
            self.root.after_cancel(self.trabajo)
            self.trabajo = None
        self.generador = None

    #dibujo 
    def dibujar(self):
        self.canvas.delete("all")
        for f in range(self.filas):
            for c in range(self.cols):
                x, y = c * TAM, f * TAM
                pos = (f, c)
                if self.grid[f][c] == "#":
                    color = COLORES["roca"]
                elif pos in self.camino:
                    color = COLORES["camino"]
                elif pos in self.explorada:
                    color = COLORES["explorada"]
                else:
                    color = COLORES["pasto"] if (f + c) % 2 == 0 else COLORES["pasto_alt"]
                self.canvas.create_rectangle(x, y, x + TAM, y + TAM, fill=color,
                                             outline=COLORES["borde"])
                centro = (x + TAM // 2, y + TAM // 2)
                if self.grid[f][c] == "#":
                    self.canvas.create_text(*centro, text="🪨", font=("Helvetica", 28))
                elif pos == self.meta:
                    self.canvas.create_text(*centro, text="🍎", font=("Helvetica", 32))
        # La culebrita (en su posición inicial o donde va la cabeza)
        f, c = self.cabeza or self.inicio
        self.canvas.create_text(c * TAM + TAM // 2, f * TAM + TAM // 2,
                                text="🐍", font=("Helvetica", 32))

    #interacción 
    def al_hacer_clic(self, evento):
        if self.generador is not None:  # no tocar rocas mientras la culebrita corre
            return
        f, c = evento.y // TAM, evento.x // TAM
        if not (0 <= f < self.filas and 0 <= c < self.cols):
            return
        if (f, c) in (self.inicio, self.meta):
            return
        self.grid[f][c] = "." if self.grid[f][c] == "#" else "#"
        self.reiniciar(borrar_resultados=True)

    def reiniciar(self, borrar_resultados=False):
        self._cancelar()
        self.explorada, self.camino, self.cabeza = set(), [], None
        if borrar_resultados:
            self.resultados = {}
            self.comparacion.config(text="")
        self.estado.config(text="Elige un algoritmo para empezar.")
        self.dibujar()

    def aleatorio(self):
        for f in range(self.filas):
            for c in range(self.cols):
                if (f, c) in (self.inicio, self.meta):
                    continue
                self.grid[f][c] = "#" if random.random() < 0.28 else "."
        self.reiniciar(borrar_resultados=True)

    #animación 
    def ejecutar(self, nombre):
        self.reiniciar()
        self.nombre_actual = nombre
        algoritmo = dfs_pasos if nombre == "DFS" else bfs_pasos
        self.generador = algoritmo(self.grid, self.inicio, self.meta)
        self.estado.config(text=f"{nombre}: la culebrita está explorando... 👃")
        self._paso_exploracion()

    def _paso_exploracion(self):
        try:
            tipo, dato = next(self.generador)
        except StopIteration:
            return
        if tipo == "explorar":
            self.explorada.add(dato)
            self.cabeza = dato
            self.dibujar()
            self.estado.config(
                text=f"{self.nombre_actual}: casillas exploradas = {len(self.explorada)}")
            self.trabajo = self.root.after(self._retraso(), self._paso_exploracion)
        else:  # "camino": terminó de explorar
            if dato is None:
                self.generador = None
                self.cabeza = None
                self.dibujar()
                self.estado.config(text=f"{self.nombre_actual}: ¡no hay camino! 😢 La culebrita se quedó con hambre.")
                return
            self.ruta = dato
            self.indice = 0
            self.estado.config(text=f"{self.nombre_actual}: ¡manzana a la vista! Siguiendo el rastro...")
            self.trabajo = self.root.after(self._retraso(), self._paso_camino)

    def _paso_camino(self):
        if self.indice < len(self.ruta):
            self.camino.append(self.ruta[self.indice])
            self.cabeza = self.ruta[self.indice]
            self.indice += 1
            self.dibujar()
            self.trabajo = self.root.after(self._retraso(), self._paso_camino)
            return
        # ¡Llegó!
        pasos = len(self.ruta) - 1
        self.resultados[self.nombre_actual] = pasos
        self.generador, self.trabajo = None, None
        self.estado.config(
            text=f"{self.nombre_actual}: ¡ÑAM! 🍎 {pasos} pasos, {len(self.explorada)} casillas exploradas.")
        partes = [f"{k}: {v} pasos" for k, v in self.resultados.items()]
        texto = "  |  ".join(partes)
        if len(self.resultados) == 2:
            extra = self.resultados["DFS"] - self.resultados["BFS"]
            if extra > 0:
                texto += f"   →   ¡DFS dio {extra} pasos de más! 🥴"
            else:
                texto += "   →   ¡Empate de caminos!"
        self.comparacion.config(text=texto)


if __name__ == "__main__":
    ventana = tk.Tk()
    AventuraCulebrita(ventana)
    ventana.mainloop()