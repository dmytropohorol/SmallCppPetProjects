def partitions(n, max_part=None, prefix=()):
    """
    Generate all partitions of n into natural addends in non-increasing order.
    Example for n=4 returns tuples:
    (4), (3,1), (2,2), (2,1,1), (1,1,1,1)
    """
    if n == 0:
        yield prefix
        return
    if max_part is None:
        max_part = n
    # Try the next addend from larger to smaller, not exceeding the previous one
    # to avoid duplicates caused by order.
    for x in range(min(max_part, n), 0, -1):
        yield from partitions(n - x, x, prefix + (x,))


def print_partitions(n):
    # All partitions
    all_parts = list(partitions(n))
    print(f"All partitions of {n} into natural addends (order ignored):")
    for p in all_parts:
        print(" + ".join(map(str, p)))
    print(f"Total: {len(all_parts)}\n")

    # Partitions with exactly 3 addends (if the task requires exactly 3)
    parts_k3 = [p for p in all_parts if len(p) == 3]
    print(f"Partitions of {n} into EXACTLY 3 natural addends:")
    if parts_k3:
        for p in parts_k3:
            print(" + ".join(map(str, p)))
    else:
        print("None.")
    print(f"Total (k=3): {len(parts_k3)}")


def main():
    try:
        n = int(input("Enter n (3..7): ").strip())
    except ValueError:
        print("Error: please enter an integer.")
        return

    if not (3 <= n <= 7):
        print("Error: n must be in the range 3..7.")
        return

    print_partitions(n)


if __name__ == "__main__":
    main()