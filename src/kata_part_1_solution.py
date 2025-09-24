def get_shape_slots(tiles: list[tuple[int, int, int, int]]) -> list[int]:
    num_tiles = len(tiles)
    res = list(range(num_tiles * 16))

    def find(i):
        if res[i] == i:
            return i
        root = find(res[i])
        res[i] = root
        return root

    def union(i, j):
        i = find(i)
        j = find(j)
        if i != j:
            res[i] = j

    for tile1, neighbors in enumerate(tiles):
        for edge1, tile2 in enumerate(neighbors):
            if tile2 > tile1:
                edge2 = next(i for i, v in enumerate(tiles[tile2]) if v == tile1)
                for i in range(5):
                    slot1 = 16 * tile1 + (4 * edge1 + i) % 16
                    slot2 = 16 * tile2 + (4 * edge2 + 4 - i) % 16
                    union(slot1, slot2)

    for i in range(len(res)):
        find(i)

    m, n = {}, 0
    for i, v in enumerate(res):
        if v not in m:
            m[v] = n
            n += 1
        res[i] = m[v]

    return res
