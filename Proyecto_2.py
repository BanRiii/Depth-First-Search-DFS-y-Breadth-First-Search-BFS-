"""
🐍 La Aventura de la Culebrita Hambrienta 🍎
Búsqueda en Profundidad (DFS) vs. Búsqueda en Amplitud (BFS) en un laberinto.

Leyenda:
    S = Culebrita (inicio)      F = Manzana (final)
    . = Pasto libre             # = Roca / muro
    ~ = Rastro de la culebrita
"""

from collections import deque

# Apariencia: cambia a True si tu terminal soporta emojis

USAR_EMOJIS = False

if USAR_EMOJIS:
    SIMBOLOS = {"S": "🐍", "F": "🍎", ".": "🟩", "#": "🪨", "~": "🟨"}
else:
    SIMBOLOS = {"S": "S", "F": "F", ".": ".", "#": "#", "~": "~"}

# El laberinto (7x7): la culebrita empieza arriba a la izquierda y la
# manzana la espera abajo a la derecha. Hay rocas por todos lados
LABERINTO = [
    "S......",
    ".#####.",
    ".....#.",
    "####.#.",
    ".......",
    ".#####.",
    "......F",
]

# Movimientos posibles: abajo, derecha, arriba, izquierda
MOVIMIENTOS = [(1, 0), (0, 1), (-1, 0), (0, -1)]


def encontrar(laberinto, letra):
    """Busca una letra en el laberinto y devuelve su posición (fila, columna)."""
    for f, fila in enumerate(laberinto):
        for c, celda in enumerate(fila):
            if celda == letra:
                return (f, c)
    raise ValueError(f"No encontré la letra {letra} en el laberinto 😵")


def vecinos(laberinto, pos):
    """Devuelve las casillas vecinas por donde la culebrita SÍ puede arrastrarse."""
    f, c = pos
    for df, dc in MOVIMIENTOS:
        nf, nc = f + df, c + dc
        dentro = 0 <= nf < len(laberinto) and 0 <= nc < len(laberinto[0])
        if dentro and laberinto[nf][nc] != "#":  # las rocas no se atraviesan 🪨
            yield (nf, nc)


#DFS: la Culebrita Loca
def buscar_manzana_dfs(laberinto):
    """
    Búsqueda en Profundidad (DFS), usando una PILA (LIFO).

    Es como si la culebrita se volviera loca: ¡se lanza en línea recta lo más
    lejos que puede, hasta chocar con una roca, y solo entonces da marcha atrás
    para probar otro camino! Va a ciegas, sin olfatear nada. Puede llegar a la
    manzana, sí, pero muchas veces por un camino larguísimo y lleno de vueltas.

    Devuelve (camino, casillas_exploradas). El camino NO es necesariamente el
    más corto.
    """
    inicio = encontrar(laberinto, "S")
    meta = encontrar(laberinto, "F")

    pila = [(inicio, [inicio])]  # (posición, camino recorrido hasta aquí)
    visitadas = set()
    exploradas = 0

    while pila:
        pos, camino = pila.pop() #Saca la ÚLTIMA casilla apilada: sigue de frente
        if pos in visitadas:
            continue
        visitadas.add(pos)
        exploradas += 1

        if pos == meta:  #Encontró la manzana
            return camino, exploradas

        # Apilamos los vecinos; el último en entrar será el primero en explorarse
        for vecino in vecinos(laberinto, pos):
            if vecino not in visitadas:
                pila.append((vecino, camino + [vecino]))

    return None, exploradas  #Sin manzana hoy


# 🌊 BFS: la Culebrita Olfateadora
def buscar_manzana_bfs(laberinto):
    """
    Búsqueda en Amplitud (BFS), usando una COLA (FIFO).

    Aquí la culebrita es mucho más lista: se queda quietecita y olfatea
    metódicamente todo a su alrededor, primero las casillas a 1 paso, luego las
    de 2 pasos, luego las de 3... expandiéndose como la onda que deja una
    piedrita en un estanque. Como revisa todo por capas, la primera vez que
    huele la manzana es garantizado que llegó por el CAMINO MÁS CORTO.

    Devuelve (camino, casillas_exploradas).
    """
    inicio = encontrar(laberinto, "S")
    meta = encontrar(laberinto, "F")

    cola = deque([(inicio, [inicio])])  # (posición, camino recorrido hasta aquí)
    visitadas = {inicio}
    exploradas = 0

    while cola:
        pos, camino = cola.popleft()  #Saca la casilla MÁS ANTIGUA: va por capas
        exploradas += 1

        if pos == meta:  #Manzana encontrada
            return camino, exploradas

        for vecino in vecinos(laberinto, pos):
            if vecino not in visitadas:
                visitadas.add(vecino)  #Marcamos al encolar para no oler dos veces
                cola.append((vecino, camino + [vecino]))

    return None, exploradas  #Sin manzana hoy


#Utilidades para imprimir
def imprimir_laberinto(laberinto, camino=None):
    """Imprime el laberinto; si hay camino, dibuja el rastro con '~'."""
    rastro = set(camino) if camino else set()
    for f, fila in enumerate(laberinto):
        linea = ""
        for c, celda in enumerate(fila):
            if (f, c) in rastro and celda not in ("S", "F"):
                celda = "~"  # El rastro baboso de la culebrita 🐌 (perdón, 🐍)
            linea += SIMBOLOS[celda] + ("" if USAR_EMOJIS else " ")
        print(linea)


def mostrar_resultado(nombre, camino, exploradas):
    if camino is None:
        print(f"{nombre}: ¡La culebrita se quedó con hambre! 😢")
        return
    print(f"{nombre}: ¡Manzana devorada! 🍎")
    print(f"  Pasos del camino : {len(camino) - 1}")
    print(f"  Casillas exploradas: {exploradas}\n")


# Se inicia la aventura 
def main():
    print("=" * 50)
    print("🐍  LA AVENTURA DE LA CULEBRITA HAMBRIENTA  🍎")
    print("=" * 50)

    print("\n📍 El laberinto original (S = culebrita, F = manzana, # = roca):\n")
    imprimir_laberinto(LABERINTO)

    # --- DFS ---
    print("\n" + "-" * 50)
    print("🌀 Intento 1: La Culebrita LOCA (DFS)")
    print("-" * 50)
    camino_dfs, exp_dfs = buscar_manzana_dfs(LABERINTO)
    mostrar_resultado("DFS", camino_dfs, exp_dfs)
    if camino_dfs:
        imprimir_laberinto(LABERINTO, camino_dfs)

    #BFS 
    print("\n" + "-" * 50)
    print("🌊 Intento 2: La Culebrita OLFATEADORA (BFS)")
    print("-" * 50)
    camino_bfs, exp_bfs = buscar_manzana_bfs(LABERINTO)
    mostrar_resultado("BFS", camino_bfs, exp_bfs)
    if camino_bfs:
        imprimir_laberinto(LABERINTO, camino_bfs)

    #Comparación final 
    if camino_dfs and camino_bfs:
        print("\n" + "=" * 50)
        print("🏆 Veredicto final")
        print("=" * 50)
        print(f"DFS: {len(camino_dfs) - 1} pasos | BFS: {len(camino_bfs) - 1} pasos")
        if len(camino_dfs) > len(camino_bfs):
            extra = len(camino_dfs) - len(camino_bfs)
            print(f"La culebrita loca dio {extra} pasos de más. ¡Qué mareo! 🥴")
        else:
            print("¡Esta vez ambas culebritas coincidieron en el camino!")
        print("Moraleja: DFS llega, pero BFS garantiza el camino más corto. 🐍✨")


if __name__ == "__main__":
    main()