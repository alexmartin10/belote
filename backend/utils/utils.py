def argmax(lst: list) -> int:
    return max(range(len(lst)), key=lambda i: lst[i])

def argmin(lst: list) -> int:
    return min(range(len(lst)), key=lambda i: lst[i])