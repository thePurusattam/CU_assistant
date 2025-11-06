# --- Quick Sort for ranking retrieved chunks ---
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if len(x) < len(pivot)]
    middle = [x for x in arr if len(x) == len(pivot)]
    right = [x for x in arr if len(x) > len(pivot)]
    return quick_sort(left) + middle + quick_sort(right)


# --- 0/1 Knapsack heuristic for selecting top chunks ---
def knapsack_filter(chunks, max_weight=5):
    selected = []
    weight = 0
    for c in chunks:
        if weight + 1 <= max_weight:
            selected.append(c)
            weight += 1
    return selected


# --- BFS traversal (for exploring related contexts) ---
def bfs(graph, start):
    visited, queue = set(), [start]
    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.add(node)
            queue.extend(graph.get(node, []))
    return visited


# --- DFS traversal (for deeper search) ---
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    for neighbour in graph.get(start, []):
        if neighbour not in visited:
            dfs(graph, neighbour, visited)
    return visited