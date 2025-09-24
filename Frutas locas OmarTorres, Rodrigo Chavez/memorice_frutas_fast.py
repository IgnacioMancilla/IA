# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
import random
import time
from typing import Dict, List, Optional, Tuple

# =====================
# Configuración
# =====================
ROWS, COLS = 6, 6
PAIRS = (ROWS * COLS) // 2
CARD_SIZE = 72
PADDING = 12
FONT = ("Segoe UI Emoji", 28)
BG = "#0b1220"
CELL = "#0f172a"
FG = "#e2e8f0"
ACCENT = "#22c55e"
GRID = "#0c1a2e"

# Delays (ms) solo para modo visual
DELAY_FLIP = 250
DELAY_CHECK = 350

# Lista de 18 símbolos únicos
SYMBOLS = ["🍎","🍐","🍊","🍋","🍌","🍉","🍇","🍓","🥭","🍍","🥝","🍒","🍑","🍈","🥥","🥑","🍏","🫐"]

# Semilla reproducible (None para aleatorio cada vez)
RANDOM_SEED: Optional[int] = None

Position = Tuple[int, int]

class Game:
    """Juego Memorice 6x6 con IA de memoria perfecta (Tkinter)."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Memorice 6x6 — IA de memoria perfecta (Tkinter)")
        self.root.configure(bg=BG)

        # Estado principal
        self.board: List[List[str]] = []
        self.revealed: Dict[Position, bool] = {}
        self.locked: Dict[Position, bool] = {}
        self.buttons: Dict[Position, tk.Button] = {}
        self.moves: int = 0
        self.start_ts: float = 0.0
        self.end_ts: float = 0.0
        self.fast_mode: bool = False
        self.ia_running: bool = False

        # Memoria de la IA: símbolo -> lista de posiciones vistas (máximo 2)
        self.memory: Dict[str, List[Position]] = {}

        # UI
        top = tk.Frame(self.root, bg=BG)
        top.pack(padx=PADDING, pady=(PADDING, 6), fill="x")

        self.lbl_moves = tk.Label(top, text="Movimientos: 0", fg=FG, bg=BG, font=("Segoe UI", 11))
        self.lbl_moves.pack(side="left")

        self.lbl_time = tk.Label(top, text="Tiempo: 0.00 s", fg=FG, bg=BG, font=("Segoe UI", 11))
        self.lbl_time.pack(side="left", padx=12)

        tk.Button(top, text="Resolver IA (visual)", command=self.solve_visual).pack(side="right", padx=4)
        tk.Button(top, text="Resolver IA (rápido)", command=self.solve_fast).pack(side="right", padx=4)
        tk.Button(top, text="Reiniciar", command=self.reset).pack(side="right", padx=4)

        grid = tk.Frame(self.root, bg=BG)
        grid.pack(padx=PADDING, pady=PADDING)

        # Crear botones
        for r in range(ROWS):
            for c in range(COLS):
                btn = tk.Button(
                    grid, text="",
                    width=3, height=1,
                    font=FONT, relief="flat",
                    bg=CELL, fg=FG, activebackground=CELL, activeforeground=FG,
                    command=lambda rr=r, cc=c: self.flip((rr, cc))
                )
                btn.grid(row=r, column=c, padx=3, pady=3, ipadx=8, ipady=8)
                self.buttons[(r, c)] = btn

        self.reset()
        self._tick()  # Temporizador UI

    # ---------- Utilidades de estado ----------

    def new_board(self) -> List[List[str]]:
        """Crea un tablero 6x6 con 18 pares (símbolos únicos duplicados)."""
        if len(SYMBOLS) < PAIRS:
            raise ValueError("Se requieren al menos 18 símbolos únicos.")
        pool = SYMBOLS[:PAIRS] * 2
        if RANDOM_SEED is not None:
            random.seed(RANDOM_SEED)
        random.shuffle(pool)
        return [pool[i*COLS:(i+1)*COLS] for i in range(ROWS)]

    def all_revealed(self) -> bool:
        """True si todas las cartas están emparejadas (bloqueadas)."""
        return all(self.locked.get((r, c), False) for r in range(ROWS) for c in range(COLS))

    def flip(self, pos: Position) -> None:
        """Manejo de clic humano (opcional). No se usa durante la resolución automática."""
        if self.locked.get(pos, False) or self.ia_running:
            return
        self._reveal(pos)
        self._human_flow(pos)

    def _human_flow(self, pos: Position) -> None:
        """Flujo simple si un humano juega (para pruebas)."""
        opened = [p for p, v in self.revealed.items() if v and not self.locked.get(p, False)]
        if len(opened) == 2:
            a, b = opened
            self.moves += 1
            self._update_moves()
            self.root.after(DELAY_CHECK, lambda: self._check_pair(a, b))

    def _reveal(self, pos: Position) -> None:
        """Revela una carta y actualiza la memoria de la IA."""
        if self.revealed.get(pos, False) or self.locked.get(pos, False):
            return
        r, c = pos
        sym = self.board[r][c]
        self.revealed[pos] = True
        self.buttons[pos]["text"] = sym
        self.buttons[pos]["bg"] = GRID

        # Memorizar
        lst = self.memory.setdefault(sym, [])
        if pos not in lst:
            lst.append(pos)
        # Mantener máximo 2 posiciones
        if len(lst) > 2:
            self.memory[sym] = lst[-2:]

    def _hide(self, pos: Position) -> None:
        """Oculta una carta (si no está emparejada)."""
        if self.locked.get(pos, False):
            return
        self.revealed[pos] = False
        self.buttons[pos]["text"] = ""
        self.buttons[pos]["bg"] = CELL

    def _lock(self, a: Position, b: Position) -> None:
        """Bloquea (empareja) dos posiciones."""
        self.locked[a] = True
        self.locked[b] = True
        self.buttons[a]["bg"] = ACCENT
        self.buttons[b]["bg"] = ACCENT

    def _check_pair(self, a: Position, b: Position) -> None:
        """Comprueba si a y b forman par; actualiza estado/estilos."""
        ra, ca = a
        rb, cb = b
        if self.board[ra][ca] == self.board[rb][cb]:
            self._lock(a, b)
        else:
            self._hide(a)
            self._hide(b)

        if self.all_revealed():
            self.end_ts = time.perf_counter()
            self.ia_running = False
            elapsed = self.end_ts - self.start_ts
            messagebox.showinfo("Completado", f"¡Resuelto!\nMovimientos: {self.moves}\nTiempo: {elapsed:.2f} s")

    def _update_moves(self) -> None:
        self.lbl_moves.config(text=f"Movimientos: {self.moves}")

    def _tick(self) -> None:
        """Actualiza label de tiempo en loop."""
        elapsed = (time.perf_counter() - self.start_ts) if self.start_ts and not self.end_ts else (self.end_ts - self.start_ts if self.end_ts else 0.0)
        self.lbl_time.config(text=f"Tiempo: {elapsed:.2f} s")
        self.root.after(60, self._tick)

    # ---------- Control general ----------

    def reset(self) -> None:
        """Reinicia tablero y métricas."""
        self.board = self.new_board()
        self.revealed.clear()
        self.locked.clear()
        self.memory.clear()
        self.moves = 0
        self._update_moves()
        self.start_ts = time.perf_counter()
        self.end_ts = 0.0
        self.ia_running = False
        # Reset UI
        for r in range(ROWS):
            for c in range(COLS):
                self._hide((r, c))

    # ---------- IA: Memoria perfecta ----------

    def solve_visual(self) -> None:
        """Ejecuta la IA con animación (delays visibles)."""
        if self.ia_running:
            return
        self.fast_mode = False
        self.ia_running = True
        self.start_ts = time.perf_counter()
        self._ia_step()

    def solve_fast(self) -> None:
        """Ejecuta la IA sin animación (modo FAST)."""
        if self.ia_running:
            return
        self.fast_mode = True
        self.ia_running = True
        self.start_ts = time.perf_counter()

        # Bucle sin delays
        while not self.all_revealed():
            a, b = self._ia_pick_two()
            self._reveal(a)
            self._reveal(b)
            self.moves += 1
            self._update_moves()
            # En fast, comprobación inmediata
            self._check_pair(a, b)
            # Evitar que el messagebox corte el loop prematuramente
            if not self.ia_running:
                break

        # Si no mostró messagebox (por fast), asegurar fin
        if self.all_revealed() and self.ia_running:
            self.end_ts = time.perf_counter()
            self.ia_running = False
            elapsed = self.end_ts - self.start_ts
            messagebox.showinfo("Completado (rápido)", f"¡Resuelto!\nMovimientos: {self.moves}\nTiempo: {elapsed:.2f} s")

    def _ia_step(self) -> None:
        """Un paso de IA en modo visual con delays."""
        if self.all_revealed():
            self.end_ts = time.perf_counter()
            self.ia_running = False
            elapsed = self.end_ts - self.start_ts
            messagebox.showinfo("Completado", f"¡Resuelto!\nMovimientos: {self.moves}\nTiempo: {elapsed:.2f} s")
            return

        a, b = self._ia_pick_two()

        # Mostrar a, luego b, luego comprobar
        self._reveal(a)
        self.root.after(DELAY_FLIP, lambda: self._reveal(b))
        def _after_both():
            self.moves += 1
            self._update_moves()
            self._check_pair(a, b)
            # Siguiente paso si sigue corriendo
            if self.ia_running:
                self.root.after(DELAY_CHECK, self._ia_step)
        self.root.after(DELAY_FLIP + DELAY_CHECK, _after_both)

    def _ia_pick_two(self) -> Tuple[Position, Position]:
        """Selecciona dos posiciones siguiendo la política informada por memoria."""
        # 1) Si existe un par conocido oculto, tomarlo
        for sym, lst in self.memory.items():
            pair = [p for p in lst if not self.locked.get(p, False)]
            if len(pair) >= 2:
                return pair[0], pair[1]

        # 3) Si no hay par conocido: explorar una carta oculta aleatoria
        hidden: List[Position] = [(r, c) for r in range(ROWS) for c in range(COLS)
                                  if not self.revealed.get((r, c), False) and not self.locked.get((r, c), False)]
        if not hidden:
            return (0, 0), (0, 1)

        a = random.choice(hidden)

        # Tomar b: si conocemos la pareja de 'a', usarla; si no, otra oculta
        ra, ca = a
        sym_a = self.board[ra][ca]
        known = [p for p in self.memory.get(sym_a, []) if p != a and not self.locked.get(p, False)]

        if known:
            b = known[0]
        else:
            hidden2 = [p for p in hidden if p != a]
            b = random.choice(hidden2) if hidden2 else a
        return a, b


def main() -> None:
    root = tk.Tk()
    Game(root)
    root.mainloop()


if __name__ == "__main__":
    main()
