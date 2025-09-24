# Happy Cubes

## Pieces

A Happy Cubes set consist of 6 colored pads with six pieces cut out of each.
To illustrate, the blue pad looks like this:

**Example 1:**

<pre style="font-family: Menlo, monospace">
 ┌────────────────────────────────────────────┐ 
 │        ┌──┐  ┌──┐  ┌──┐     ┌──┐  ┌──┐     │ 
 │     ┌──┘  └──┘  ├──┘  └──┬──┘  └──┘  │     │ 
 │     │        ┌──┘        └──┐        └──┐  │ 
 │  ┌──┘        │           ┌──┘           │  │ 
 │  │     ┌──┐  └──┬─────┐  ├─────┐  ┌─────┤  │ 
 │  ├─────┘  └─────┤     └──┤     └──┘  ┌──┘  │ 
 │  └──┐        ┌──┘        └──┐        │     │ 
 │  ┌──┘        └──┐        ┌──┘        └──┐  │ 
 │  └──┐  ┌──┐  ┌──┘     ┌──┤  ┌──┐  ┌──┐  │  │ 
 │     └──┘  └──┴────────┘  └──┘  └──┘  └──┘  │ 
 └────────────────────────────────────────────┘ 
 </pre>

The thickness of the pads equals the width and height of the small cubit units, or _cubits_, that make up the pieces.
This allows two pieces to be assembled either lying flat next to each other or at a 90° angle. Each piece fits into a
5-by-5 cubits square, so, if you want, you can represent a piece by a 5 x 5 matrix of 0's an 1's, where a 1 represents
the presence of a cubit and a 0 represents the absence of a cubit.

An enum class is provided as part of the preloaded code:

```Python
from enum import Enum


class Pads(Enum):
    BLUE = """
    000000000000000
    000101020030300
    001111222333300
    001112222233330
    011112222333330
    011411552663660
    044444555666600
    004445555566600
    044444555666660
    004045550606060
    000000000000000
    """
    GREEN = """..."""
    PINK = """..."""
    PURPLE = """..."""
    RED = """..."""
    YELLOW = """..."""
```

Each member of the `Pads` class has a value that, when ignoring extraneous whitespace, is an 11-by-15 multiline string
of digits 0 through 7. Each digit represents a cubit and the value of the digit identifies the piece it belongs to. The
surrounding frame is marked by `'0'`'s, which we will ignore. Piece 1 consists of the part of the pad that has the
digit `'1'`, piece 2 the part of the pad that has `'2'`'s, and so on.

A piece can be oriented in 8 different ways, which we identify as follows:

1. `'R0'` = the piece in its original form
2. `'R1'` = `'R0'` rotated 90° clockwise
3. `'R2'` = `'R0'` rotated 180°
4. `'R3'` = `'R0'` rotated 90° counter-clockwise
5. `'F0'` = `'R0'` flipped about the vertical axis (mirror left-right)
6. `'F1'` = `'F0'` then 90° clockwise
7. `'F2'` = `'F0'` then 180°
8. `'F3'` = `'F0'` then 90° counter-clockwise

To illustrate this by an example, here are the eight orientations of `BLUE[2]` (piece 2 of `Pads.BLUE`):

**Example 2:**

<pre style="font-family: Menlo, monospace">
  R0                R1                R2                R3
        ┌──┐           ┌─────┐           ┌──┐                 ┌──┐  
     ┌──┘  └──┐        │     └──┐        │  └────────┐     ┌──┘  └─────┐ 
  ┌──┘        └──┐     │        └──┐  ┌──┘           │  ┌──┘        ┌──┘  
  │           ┌──┘  ┌──┘        ┌──┘  └──┐        ┌──┘  └──┐        │   
  └────────┐  │     └─────┐  ┌──┘        └──┐  ┌──┘        └──┐     │  
           └──┘           └──┘              └──┘              └─────┘  

  F0                F1                F2                F3
        ┌──┐              ┌──┐                 ┌──┐           ┌─────┐         
     ┌──┘  └──┐     ┌─────┘  └──┐     ┌────────┘  │        ┌──┘     │         
  ┌──┘        └──┐  └──┐        └──┐  │           └──┐  ┌──┘        │            
  └──┐           │     │        ┌──┘  └──┐        ┌──┘  └──┐        └──┐            
     │  ┌────────┘     │     ┌──┘        └──┐  ┌──┘        └──┐  ┌─────┘         
     └──┘              └─────┘              └──┘              └──┘      
 </pre>

Some pieces may not have eight distinct orientations due to symmetries.

## Shapes

Pieces can be assembled into various shapes.

**Example 3:** Using the pieces from a single pad, it is possible to assemble
them into a small cube where one piece is placed on each of the cubes faces.

### Tiles

In order to describe a shape, we introduce the notion of a _tile_. A _tile_ is a square where one can place a piece. We
can think of a tile as a 5x5 square of _slots_. When we place a piece on a tile, the piece's cubits cover a subset of
the slots.

**Example 4:** A tile with a piece assigned to it covering 14 of its 25 slots.

<pre style="font-family: Menlo, monospace">

   ░░ ░░ ██ ░░ ░░ 
   ░░ ██ ██ ██ ░░ 
   ██ ██ ██ ██ ██ 
   ██ ██ ██ ██ ░░ 
   ░░ ░░ ░░ ██ ░░ 

</pre>

Since all pieces have the cubits at the 3x3 square at their centre present, we only care about the slots along a tile's
edges. In order to reference those slots (e.g., in error messages), we number them from 0 to 15, starting at the
north-west corner and moving clockwise.

```
     0  1  2  3  4
    15     N     5
    14 W       E 6
    13     S     7
    12 11 10  9  8
```

When a piece is assigned to a tile, its top edge shall align with the tile's north edge. The slots that a piece
covers when assigned to a tile depends on its orientation. For example, when `BLUE[2]` with the `R0` orientation is
assigned to a tile (left part of figure below), it covers tile slots 2, 6, 9, 13, and 14, whereas with the `F2`
orientation (right part of figure below), it covers tile slots 3, 6, 10, 14, and 15.

<pre style="font-family: Menlo, monospace">

   ░░ ░░ ██ ░░ ░░       ░░ ░░ ░░ ██ ░░
   ░░ ██ ██ ██ ░░       ██ ██ ██ ██ ░░
   ██ ██ ██ ██ ██       ██ ██ ██ ██ ██
   ██ ██ ██ ██ ░░       ░░ ██ ██ ██ ░░
   ░░ ░░ ░░ ██ ░░       ░░ ░░ ██ ░░ ░░

</pre>

### Shape descriptions

A shape assembled from `P` pieces has `P` tiles. To describe the shape we number the tiles `0, 1, ..., P - 1` and select
one edge of each tile as its North edge. Then we can describe a shape by an array of 4-tuples of length `P` such that
the tuple at index `i` are the tile numbers of the tiles to north, east, south, and west of tile number `i`.

**Example 5:**

The small cube from Example 3 has six tiles; one for each of the cubes six faces. Assume we unfold the cube and lay out
the tiles as follows:

```
   0
 1 2 3
   4
   5
```

Let the top edge of each tile as it appears in the figure be the North edge. When we fold the tiles back into a cube,
Tile 0 has Tile 5 to its north, Tile 3 to its east, Tile 2 to its south and Tile 1 to its west. This is captured by the
4-tuple `(5, 3, 2, 1)`.If we complete this for each tile, we get the following shape description:

```
[
  (5, 3, 2, 1),
  (0, 2, 4, 5),
  (1, 3, 4, 1),
  (0, 5, 4, 2),
  (2, 3, 5, 1),
  (4, 3, 0, 1)
]
```

**Example 6:**

We can lay out the tiles of a 2x1x1 prism as follows:

```
   0 1
 2 3 4 5
   6 7
   8 9
```

When choosing the top edge of each tile as they appear in the figure above as the North edge, we end up with the
following description:

```
[
  (8, 1, 3, 2),
  (9, 5, 4, 0),
  (0, 3, 6, 8),
  (0, 4, 6, 2),
  (1, 5, 7, 3),
  (1, 9, 7, 4),
  (3, 7, 8, 2),
  (4, 5, 9, 6),
  (6, 9, 0, 2),
  (7, 5, 1, 8)
]
```

Note that a description depends on the choice of the tile numbering and choice of the North edge of each tile.

> Since adjacent pieces mesh into each other, adjacent tiles overlap at their adjacent edges.

**Example 7**
Assume Tile 1 has Tile 2 to its east and Tile 2 has Tile 1 to its north (in the figure below, Tile 1's North edge is up,
whereas Tile 2's North edge is left). When assigning `BLUE[2]` with `R2` orientation to Tile 1, Tile 2's slots 2 and 3
are covered because Tile 1's slots `4, 5, 6, 7, 8 `  overlap Tile 2's slots `4, 3, 2, 1, 0` respectively.

<pre style="font-family: Menlo, monospace">
  ├────Tile 1────┤
   ░░ ██ ░░ ░░ ░░ ░░ ░░ ░░ ░░
   ░░ ██ ██ ██ ██ ░░ ░░ ░░ ░░
   ██ ██ ██ ██ ██ ░░ ░░ ░░ ░░
   ░░ ██ ██ ██ ░░ ░░ ░░ ░░ ░░
   ░░ ░░ ██ ░░ ░░ ░░ ░░ ░░ ░░
              ├────Tile 2────┤
</pre>

Note that slot overlap is a transitive relation; if slot `a` overlaps slot `b`, and slot `b` overlaps slot `c`, then
slot `a` overlaps slot `c`. This implies that not only adjacent tiles overlap. In fact, up to 6 tiles may overlap
at a given corner.

---

#### Challenge

Given a shape description and a set of pieces, assign a piece with an orientation to each tile of the shape such that
each slot is covered exactly once. To be more precise:

Write a function

```Python
def solve(
        shape: list[tuple[int, int, int, int]],
        pieces: list[tuple[str, int]],
        hints: list[tuple[int, str, int, str]] | None = None,
) -> list[tuple[int, str, int, str]]:
    pass
```

**Input**

- `shape` is a shape description given as a list of 4-tuples as shown under section "Shape descriptions"
- `pieces` is a list of distinct pairs `(color, i)` where `color` is the name of one of the members of the
  preloaded `Pads` enum and `i` is the piece number of a piece of that pad. `pieces` may contain more pieces than what
  is needed for a solution.
- `hints` is an optional argument. When present it is a partial solution given as a list of
  4-tuples `(tile_number, color, piece_number, orientation)`, where
    - `tile_number` is the number of a tile
    - `color` and `piece_number` identify a piece
    - `orientation` is one of the 8 orientations (`'R0', ..., 'F3'`)
- There exists at least one solution for any given input.

**Output**

- The output shall be a list of 4-tuples `(tile_number, color, piece_number, orientation)`, where,
  each tuple denotes which piece and orientation is assigned to which tile:
    - `tile_number` is the number of the tile
    - `color` and `piece_number` identify the piece
    - `orientation` is one of the 8 orientations (`'R0', ..., 'F3'`), which identifies the piece's orientation
- Any piece assigned to a tile must be included in the given `pieces`
- Exactly one piece and orientation shall be assigned to each tile in the given `shape`
- The same piece cannot be assigned to more than one tile
- Each tile slot must be covered by exactly one piece
- When `hints` is given, the solution must be consistent with `hints`, i.e., each tuple in `hints` must appear in the
  output.

---
Happy coding!