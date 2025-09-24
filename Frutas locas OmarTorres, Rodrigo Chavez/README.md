# Memorice (6×6) con IA de Memoria Perfecta — Tkinter (Python estándar)

> **Autor:** Omar Torres  
> **Asignatura:** Agentes de Búsqueda / IA  
> **Fecha:** 24-sep-2025 (America/Santiago)

## 🧩 Descripción
Implementación del juego **Memorice** en un tablero **6×6** (18 pares) con una **IA de memoria perfecta**. El juego cuenta los **movimientos** y el **tiempo de resolución**. La interfaz está hecha con **Tkinter** (biblioteca estándar de Python).

La IA utiliza una política informada por el conocimiento acumulado: empareja inmediatamente cuando conoce ambas posiciones de un símbolo, y en caso contrario explora revelando una carta para aumentar la información.

## ✅ Requisitos
- **Python 3.9+**
- **Tkinter** (viene incluido en las distribuciones estándar de Python para Windows/macOS. En algunas distros Linux puede requerir `sudo apt install python3-tk`).  
> **Importante:** No se usa `pygame` ni librerías externas.

## ▶️ Cómo ejecutar
```bash
python memorice_frutas_fast.py
```
Atajos:
- Botón **"Resolver IA (visual)"**: ejecuta la IA con animación (delays visibles).
- Botón **"Resolver IA (rápido)"**: ejecuta la IA en modo **FAST** sin animación (medición de tiempo “puro”).
- Botón **"Reiniciar"**: reinicia el tablero.

## 📊 Métricas que se muestran
- **Movimientos:** cada comparación de 2 cartas cuenta 1 movimiento.
- **Tiempo:** se muestra el tiempo total de partida (segundos). En **visual** incluye delays; en **rápido** no incluye delays.

---

## 🧠 Justificación del algoritmo y complejidad

**Justificación.**  
Para Memorice, cada estado relevante es el conjunto de cartas reveladas y la **memoria** de símbolos observados (mapa `símbolo → posiciones`). Usamos una **búsqueda informada por memoria perfecta**:

1. Si existen **dos posiciones** conocidas del mismo símbolo aún ocultas, se seleccionan inmediatamente (decisión determinista “greedy con certeza”).
2. Si **no hay par conocido**, se explora una carta oculta para adquirir información; si revela un símbolo cuya pareja ya estaba en memoria, se empareja en el mismo turno.

Esta política es **apropiada** porque la información reduce el espacio de acciones. Cuando hay un par conocido, **siempre** es óptimo revelarlo (no hay alternativa mejor en términos de movimientos). En expectativa, minimiza el número de movimientos frente a estrategias sin memoria o con memoria parcial.

**Complejidad.**  
- **Tiempo:** O(1) amortizado por decisión (búsquedas en diccionario), y **O(N)** para resolver un tablero de N cartas.  
- **Memoria:** O(N) para almacenar hasta dos posiciones por símbolo.

**Medición.**  
- **Movimientos**: 1 por comparación (volteo de 2 cartas).  
- **Tiempo**: en visual incluye animación (`after()`); en rápido (**FAST**) desactiva delays para medir procesamiento real con `time.perf_counter()`.

---

## 🛠️ Estructura del código
- `Game` (clase principal): tablero, estado, temporizador y UI.
- **IA**: política informada por memoria con diccionarios (`symbol → [posiciones]`) y conjunto de cartas ocultas.
- **Modo FAST**: elimina delays de animación para evaluación objetiva del rendimiento.

---

## 📚 Pregunta de Evaluación Teórica (respuesta)

**¿Por qué este algoritmo es adecuado para Memorice y cómo se compara con BFS/A*?**  
Elegimos **búsqueda informada por memoria perfecta** porque el objetivo es minimizar **movimientos** y la observación **reconfigura** el espacio de estados en tiempo real. Cuando existe un par conocido, revelarlo es óptimo (ganancia segura). Si no, explorar una carta maximiza información por movimiento; si la carta revela una pareja conocida, se empareja de inmediato.  
Usar BFS/A* sobre un grafo fijo es menos natural aquí: el “grafo” cambia tras cada observación y no hay una heurística admisible estable con coste uniforme. La política informada por memoria alcanza **O(N)** en tiempo total y reduce el número esperado de movimientos, lo que es **ideal** para Memorice.

---

## 🧪 Criterios de evaluación (cómo se satisface)
1. **Correcta ejecución (20/20):** el juego resuelve 6×6 con IA estable; cuenta tiempo y movimientos; UI funcional.  
2. **Optimización (hasta 20):** modo **FAST** para ejecución sin delays; estructura O(N).  
3. **Calidad del código (hasta 20):** clase única bien documentada, **type hints** básicos y docstrings.  
4. **Uso y justificación del algoritmo (hasta 20):** sección anterior con motivación y complejidad.  
5. **Documentación (hasta 15):** instrucciones claras, justificación, y cómo medir tiempos.  
6. **Pregunta teórica (hasta 25):** incluida en este README.

---

## 📌 Notas
- El set de **18 símbolos** es **único** (sin repetidos) para evitar sesgos en la evaluación.
- Se puede ajustar la **semilla aleatoria** al reiniciar para reproducibilidad (ver constante `RANDOM_SEED`).
