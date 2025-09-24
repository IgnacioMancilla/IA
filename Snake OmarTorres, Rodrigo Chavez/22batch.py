
import argparse, random, time
from collections import deque

# ---------------------
# Core (igual a tu agente)
# ---------------------
DIRS = [(0,1),(1,0),(0,-1),(-1,0)]  # E, S, O, N

def in_bounds(r, c, ROWS, COLS):
    return 0 <= r < ROWS and 0 <= c < COLS

def bfs_path(start, goal, blocked, ROWS, COLS):
    if start == goal:
        return [start]
    q = deque([start])
    prev = {start: None}
    seen = {start}
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS:
            nr, nc = r+dr, c+dc
            nxt = (nr, nc)
            if not in_bounds(nr, nc, ROWS, COLS) or nxt in blocked or nxt in seen:
                continue
            seen.add(nxt)
            prev[nxt] = (r, c)
            if nxt == goal:
                path = [nxt]
                while prev[path[-1]] is not None:
                    path.append(prev[path[-1]])
                path.reverse()
                if path and path[0] != start:
                    path = [start] + path
                return path
            q.append(nxt)
    return None

def next_move(head, body, apple, ROWS, COLS):
    blocked = set(body[:-1])  # deja la cola libre
    p = bfs_path(head, apple, blocked, ROWS, COLS)
    if p and len(p) >= 2:
        return p[1]
    tail = body[-1]
    p2 = bfs_path(head, tail, blocked, ROWS, COLS)
    if p2 and len(p2) >= 2:
        return p2[1]
    hr, hc = head
    for dr, dc in DIRS:
        nr, nc = hr+dr, hc+dc
        nxt = (nr, nc)
        if in_bounds(nr, nc, ROWS, COLS) and nxt not in blocked and nxt != head:
            return nxt
    return None

def spawn_apple(snake, ROWS, COLS, rnd):
    free = [(r,c) for r in range(ROWS) for c in range(COLS) if (r,c) not in snake]
    return rnd.choice(free) if free else None

def run_one(seed, ROWS, COLS, TARGET_APPLES, MAX_STEPS):
    rnd = random.Random(seed)
    mid_r, mid_c = ROWS//2, COLS//2
    snake = [(mid_r, mid_c), (mid_r, mid_c-1), (mid_r, mid_c-2)]
    apple = spawn_apple(snake, ROWS, COLS, rnd)

    apples = 0
    steps = 0
    t0 = time.perf_counter()

    while steps < MAX_STEPS:
        head = snake[0]
        mv = next_move(head, snake, apple, ROWS, COLS)
        if mv is None or not in_bounds(*mv, ROWS, COLS) or mv in snake[:-1]:
            elapsed = time.perf_counter() - t0
            return {"seed": seed, "apples": apples, "steps": steps, "time_s": elapsed, "result": "LOSE"}
        snake.insert(0, mv)
        ate = (mv == apple)
        if ate:
            apples += 1
            if apples >= TARGET_APPLES:
                elapsed = time.perf_counter() - t0
                return {"seed": seed, "apples": apples, "steps": steps, "time_s": elapsed, "result": "WIN"}
            apple = spawn_apple(snake, ROWS, COLS, rnd)
        else:
            snake.pop()
        steps += 1

    elapsed = time.perf_counter() - t0
    return {"seed": seed, "apples": apples, "steps": steps, "time_s": elapsed, "result": "TIMEOUT"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=10)
    ap.add_argument("--seed", type=int, default=1234, help="semilla base; por corrida uso seed+i")
    ap.add_argument("--rows", type=int, default=10)
    ap.add_argument("--cols", type=int, default=10)
    ap.add_argument("--target", type=int, default=35)
    ap.add_argument("--max-steps", type=int, default=5000)
    ap.add_argument("--csv", default="batch_results.csv")
    ap.add_argument("--md", default="batch_table.md")
    args = ap.parse_args()

    ROWS, COLS = args.rows, args.cols
    TARGET_APPLES = args.target
    MAX_STEPS = args.max_steps

    results = []
    wins = 0
    apples_sum = 0
    steps_sum = 0
    time_sum = 0.0

    for i in range(args.runs):
        s = args.seed + i
        r = run_one(s, ROWS, COLS, TARGET_APPLES, MAX_STEPS)
        results.append(r)
        if r["result"] == "WIN":
            wins += 1
        apples_sum += r["apples"]
        steps_sum += r["steps"]
        time_sum += r["time_s"]

    # CSV
    with open(args.csv, "w", encoding="utf-8") as f:
        f.write("run,seed,apples,steps,time_s,result\n")
        for idx, r in enumerate(results, 1):
            f.write(f"{idx},{r['seed']},{r['apples']},{r['steps']},{r['time_s']:.4f},{r['result']}\n")
        f.write(f"#summary,,avg_apples,avg_steps,avg_time_s,win_rate\n")
        avg_ap = apples_sum/len(results) if results else 0
        avg_st = steps_sum/len(results) if results else 0
        avg_tm = time_sum/len(results) if results else 0.0
        win_rate = wins/len(results) if results else 0.0
        f.write(f"#summary,,{avg_ap:.2f},{avg_st:.2f},{avg_tm:.3f},{win_rate:.2%}\n")

    # Markdown
    with open(args.md, "w", encoding="utf-8") as f:
        f.write("| # | Seed | Manzanas | Pasos | Tiempo (s) | Resultado |\n")
        f.write("|---|------|----------|------:|-----------:|-----------|\n")
        for idx, r in enumerate(results, 1):
            f.write(f"| {idx} | {r['seed']} | {r['apples']} | {r['steps']} | {r['time_s']:.2f} | {r['result']} |\n")
        f.write("\n**Resumen**  \n")
        f.write(f"- Promedio manzanas: **{avg_ap:.2f}**  \n")
        f.write(f"- Promedio pasos: **{avg_st:.2f}**  \n")
        f.write(f"- Promedio tiempo: **{avg_tm:.2f}s**  \n")
        f.write(f"- % de victorias (35/35): **{win_rate:.2%}**  \n")

    print(f"Listo. CSV: {args.csv} | MD: {args.md} | wins: {wins}/{len(results)}")

if __name__ == "__main__":
    main()
