import tkinter as tk
from tkinter import messagebox
from collections import deque
import random, time

# =====================
# Config (igual al anterior estilo)
# =====================
ROWS, COLS = 10, 10
TARGET_APPLES = 35           # meta
CELL = 36                    # tamaño celda px
MARGIN = 14                  # borde
BG_BOARD = "#0b1220"
BG_CELL  = "#0f172a"
GRID     = "#0c1a2e"
APPLE    = "#f43f5e"
S_HEAD   = "#22c55e"
S_BODY   = "#16a34a"

# Velocidad (ms entre pasos) — default (mantiene tu valor anterior)
DEFAULT_SPEED = 90

# =====================
# Utilidades BFS
# =====================
DIRS = [(0,1),(1,0),(0,-1),(-1,0)]  # E, S, O, N

def in_bounds(r, c):
    """True si (r,c) está dentro del tablero."""
    return 0 <= r < ROWS and 0 <= c < COLS

def bfs_path(start, goal, blocked):
    """BFS clásico: shortest path en grilla sin pesos. Devuelve lista de celdas (incluye goal) o None."""
    if start == goal:
        return [start]
    q = deque([start])
    prev = {start: None}
    seen = {start}
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS:  # orden estable (como tu versión)
            nr, nc = r+dr, c+dc
            nxt = (nr, nc)
            if not in_bounds(nr, nc) or nxt in blocked or nxt in seen:
                continue
            seen.add(nxt)
            prev[nxt] = (r, c)
            if nxt == goal:
                # reconstruir
                path = [nxt]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                path.reverse()
                # garantiza que arranque en start
                if path and path[0] != start:
                    path = [start] + path
                return path
            q.append(nxt)
    return None

def next_move(head, body, apple):
    """
    Política del agente (igual a la tuya, explicitada):
      1) BFS hacia la manzana (bloqueando body[:-1] para dejar la cola libre).
      2) Si no hay, BFS hacia la cola (gana tiempo/espacio).
      3) Si no hay, movimiento seguro cualquiera.
    """
    blocked = set(body[:-1])  # dejar cola libre es clave en Snake
    # 1) camino óptimo a la manzana
    p = bfs_path(head, apple, blocked)
    if p and len(p) >= 2:
        return p[1]
    # 2) camino a la cola
    tail = body[-1]
    p2 = bfs_path(head, tail, blocked)
    if p2 and len(p2) >= 2:
        return p2[1]
    # 3) movimiento seguro
    hr, hc = head
    for dr, dc in DIRS:
        nr, nc = hr+dr, hc+dc
        nxt = (nr, nc)
        if in_bounds(nr, nc) and nxt not in blocked and nxt != head:
            return nxt
    return None

# =====================
# Juego + UI (mismo look & feel, solo agregamos Speed/Seed minimalistas)
# =====================
class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Snake BFS 10x10")
        self.root.configure(bg=BG_BOARD)

        # Estado
        self.speed_ms = DEFAULT_SPEED
        self.running = False
        self.timer = None
        self.apples = 0
        self.steps = 0
        self.t0 = None
        self.seed_value = None

        # Canvas (mismas dimensiones y colores)
        w = MARGIN*2 + COLS*CELL
        h = MARGIN*2 + ROWS*CELL
        self.cv = tk.Canvas(self.root, width=w, height=h, bg=BG_BOARD, highlightthickness=0)
        self.cv.grid(row=0, column=0, rowspan=6, padx=10, pady=10)

        # Botones estilo simple (como antes)
        self.btn_start = tk.Button(self.root, text="Start", command=self.on_start)
        self.btn_pause = tk.Button(self.root, text="Pause", command=self.on_pause)
        self.btn_reset = tk.Button(self.root, text="Reset", command=self.on_reset)
        self.btn_start.grid(row=0, column=1, sticky="ew", padx=6, pady=4)
        self.btn_pause.grid(row=1, column=1, sticky="ew", padx=6, pady=4)
        self.btn_reset.grid(row=2, column=1, sticky="ew", padx=6, pady=4)

        # Speed (Scale) — minimal, sin ttk, respetando estética
        tk.Label(self.root, text="Speed (ms)", fg="white", bg=BG_BOARD).grid(row=3, column=1, sticky="w", padx=6)
        self.speed_scale = tk.Scale(self.root, from_=20, to=300, orient="horizontal",
                                    bg=BG_BOARD, fg="white", highlightthickness=0,
                                    troughcolor=GRID, command=self._on_speed)
        self.speed_scale.set(self.speed_ms)
        self.speed_scale.grid(row=4, column=1, sticky="ew", padx=6, pady=2)

        # Seed (Entry) — Enter para aplicar
        tk.Label(self.root, text="Seed", fg="white", bg=BG_BOARD).grid(row=5, column=1, sticky="w", padx=6)
        self.seed_entry = tk.Entry(self.root)
        self.seed_entry.grid(row=6, column=1, sticky="ew", padx=6, pady=(0,6))
        self.seed_entry.bind("<Return>", self._on_seed)

        # Inicia partida
        self.new_game()
        self.draw()

    # ---------- Controles ----------
    def _on_speed(self, val):
        try:
            self.speed_ms = int(float(val))
        except ValueError:
            pass

    def _on_seed(self, _evt=None):
        s = self.seed_entry.get().strip()
        self.seed_value = int(s) if s.isdigit() else (s if s else None)
        self.on_reset()

    def on_start(self):
        if not self.running:
            self.running = True
            if self.t0 is None:
                self.t0 = time.perf_counter()
            self.tick()

    def on_pause(self):
        self.running = False
        if self.timer is not None:
            try:
                self.root.after_cancel(self.timer)
            except Exception:
                pass
            self.timer = None

    def on_reset(self):
        self.on_pause()
        self.new_game()
        self.draw()

    # ---------- Lógica ----------
    def new_game(self):
        # Semilla reproducible si la fijaste
        if self.seed_value is not None:
            random.seed(self.seed_value)
        else:
            random.seed()

        mid_r, mid_c = ROWS//2, COLS//2
        self.snake = [(mid_r, mid_c), (mid_r, mid_c-1), (mid_r, mid_c-2)]
        self.apples = 0
        self.steps = 0
        self.t0 = None
        self.running = False
        self.apple = None
        self.spawn_apple()

    def spawn_apple(self):
        free = [(r,c) for r in range(ROWS) for c in range(COLS) if (r,c) not in self.snake]
        self.apple = random.choice(free) if free else None

    def tick(self):
        if not self.running:
            return
        head = self.snake[0]
        mv = next_move(head, self.snake, self.apple)
        if mv is None or not in_bounds(*mv) or mv in self.snake[:-1]:
            return self.end_game("LOSE")

        # mover
        self.snake.insert(0, mv)
        ate = (mv == self.apple)
        if ate:
            self.apples += 1
            if self.apples >= TARGET_APPLES:
                self.draw()
                return self.end_game("WIN")
            self.spawn_apple()
        else:
            self.snake.pop()

        self.steps += 1
        self.draw()
        self.timer = self.root.after(self.speed_ms, self.tick)

    def end_game(self, result):
        self.on_pause()
        elapsed = time.perf_counter() - self.t0 if self.t0 else 0.0
        messagebox.showinfo("Resultado",
                            f"Resultado: {result}\n"
                            f"Manzanas: {self.apples}\n"
                            f"Pasos: {self.steps}\n"
                            f"Tiempo: {elapsed:.2f}s")

    # ---------- Render ----------
    def draw(self):
        self.cv.delete("all")
        # fondo + grid (igual al look anterior)
        for r in range(ROWS):
            for c in range(COLS):
                x1 = MARGIN + c*CELL
                y1 = MARGIN + r*CELL
                x2 = x1 + CELL - 1
                y2 = y1 + CELL - 1
                self.cv.create_rectangle(x1, y1, x2, y2, fill=BG_CELL, outline=GRID)

        # manzana
        if self.apple:
            ar, ac = self.apple
            ax1 = MARGIN + ac*CELL
            ay1 = MARGIN + ar*CELL
            self.cv.create_rectangle(ax1, ay1, ax1+CELL-1, ay1+CELL-1, fill=APPLE, outline="")

        # serpiente
        for i, (r, c) in enumerate(self.snake):
            x1 = MARGIN + c*CELL
            y1 = MARGIN + r*CELL
            color = S_HEAD if i == 0 else S_BODY
            self.cv.create_rectangle(x1, y1, x1+CELL-1, y1+CELL-1, fill=color, outline="")

def main():
    App().root.mainloop()

if __name__ == "__main__":
    main()
