from collections import defaultdict
from collections.abc import Iterable

from happy_cube_solver import PieceSpec, SolutionSpec, get_edge, Orientations


def check_solution(
        shape: list[tuple[int, int, int, int]],
        pieces: Iterable[PieceSpec],
        hints: list[tuple[int, str, int, str]] | None,
        solution: SolutionSpec,
        tack_stitches: list[tuple[int, int]] | None = None,
) -> list[str]:

    def get_shape_slots() -> list[int]:
        num_tiles = len(shape)
        res = list(range(num_tiles * 16))

        def find(i_):
            if res[i_] == i_:
                return i_
            root = find(res[i_])
            res[i_] = root
            return root

        def union(i_, j):
            i_ = find(i_)
            j = find(j)
            if i_ != j:
                res[i_] = j

        for tile1, neighbors in enumerate(shape):
            for edge1, tile2 in enumerate(neighbors):
                if tile2 > tile1:
                    edge2 = next(i_ for i_, v in enumerate(shape[tile2]) if v == tile1)
                    for i_ in range(5):
                        slot1 = 16 * tile1 + (4 * edge1 + i_) % 16
                        slot2 = 16 * tile2 + (4 * edge2 + 4 - i_) % 16
                        union(slot1, slot2)
        if tack_stitches:
            for s1, s2 in tack_stitches:
                union(s1, s2)

        for i_ in range(len(res)):
            find(i_)

        return res

    errors = []
    covered_tiles = set(tile for tile, *_ in solution)
    uncovered_tiles = set(range(len(shape))) - covered_tiles
    for uncovered_tile in uncovered_tiles:
        errors.append(f"No piece has been assigned to tile {uncovered_tile}.")
    piece_assignment = defaultdict(list)
    for tile, pad, index, _ in solution:
        piece_assignment[(pad, index)].append(tile)
    reused_pieces = (p for p, v in piece_assignment.items() if len(v) > 1)
    for reused_piece in reused_pieces:
        errors.append(f"Piece {reused_piece} is used more than once.")
    slots = get_shape_slots()
    covered_slots = defaultdict(list)
    for tile, pad, index, orientation_str in solution:
        if (pad, index) not in pieces:
            errors.append(f"The solution uses {(pad, index)}, which is not in the pieces for this problem.")
        try:
            edge = Orientations[orientation_str].apply_to(get_edge(pad, index))
            for i, v in enumerate(edge):
                if v == 1:
                    covered_slots[slots[16 * tile + i]].append((pad, index, tile))
        except (IndexError, KeyError) as e:
            errors.append(e)
    uncovered_slots = (slot for slot in set(slots) if not covered_slots[slot])
    for uncovered_slot in uncovered_slots:
        tile, i = divmod(uncovered_slot, 16)
        errors.append(f"Slot {i} of tile {tile} is not covered by any piece.")
    collision_slots = (slot for slot, v in covered_slots.items() if len(v) > 1)
    for slot in collision_slots:
        a = ' and '.join(
            f"piece {(color, index)} assigned to tile {tile}" for color, index, tile in covered_slots[slot])
        tile, i = divmod(slot, 16)
        errors.append(f"Slot {i} of tile {tile} is covered by {a}")

    if hints and not set(hints) <= set(solution):
        errors.append("The solution is not an extension of the hints")
    return errors
