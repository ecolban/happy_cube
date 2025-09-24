from collections import defaultdict
from collections.abc import Iterable

from pieces import Piece, Orientations
from shapes import get_shape_slots


def check_solution(
        shape: list[tuple[int, int, int, int]],
        pieces: set[tuple[str, int]],
        tack_stitches: list[tuple[int, int]],
        solution: Iterable[tuple[int, str, int, str]],
) -> list[str]:
    errors = []
    covered_tiles = set(tile for tile, *_ in solution)
    uncovered_tile = next((tile for tile, _ in enumerate(shape) if tile not in covered_tiles), None)
    if uncovered_tile is not None:
        errors.append(f"Tile {uncovered_tile} has not been assigned any piece")
    piece_assignment = defaultdict(list)
    for tile, color, index, _ in solution:
        piece_assignment[(color, index)].append(tile)
    reused_piece = next((p for p, v in piece_assignment.items() if len(v) > 1), None)
    if reused_piece is not None:
        errors.append(f"Piece {reused_piece} is used more than once.")
    slots = get_shape_slots(shape, tack_stitches)
    covered_slots = defaultdict(list)
    for tile, color, index, orientation_str in solution:
        if (color, index) not in pieces:
            errors.append(f"The solution uses {(color, index)}, which is not in the pieces for this problem.")
        try:
            piece = Piece(color, index)
            piece.orientation = Orientations[orientation_str]
            for i, v in enumerate(piece.edge):
                if v == 1:
                    covered_slots[slots[16 * tile + i]].append(tile)
        except (IndexError, KeyError) as e:
            errors.append(e)
    uncovered_slot = next((slot for slot in slots if not covered_slots[slot]), None)
    if uncovered_slot is not None:
        tile, i = divmod(uncovered_slot, 16)
        errors.append(f"Slot {i} of tile {tile} is not covered by any piece.")
    collision = next((slot for slot, v in covered_slots.items() if len(v) > 1), None)
    if collision is not None:
        tile, i = divmod(collision, 16)
        a = ' and '.join(f"piece assigned to tile {tile}" for tile in covered_slots[collision])
        errors.append(f"Slot {i} of tile {tile} is covered by {a}")
    return errors
