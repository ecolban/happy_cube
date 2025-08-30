# Happy Cubes - Part 1: Understanding shapes

This kata is the first in a series aimed at building a solver for Happy Cube puzzles.

## What is Happy Cubes

Happy Cubes is a 3D puzzle game where the goal is to assemble puzzle pieces into a cube (or other shapes).
Each piece is cut from a colored foam pad and can be represented as a 5×5 matrix of 1s and 0s:

- 1 = a small cubic unit (we’ll call it a cubit) is present.
- 0 = no cubit in that position.

Example:

```
[[0, 0, 1, 0, 1],
 [0, 1, 1, 1, 1],
 [1, 1, 1, 1, 0],
 [1, 1, 1, 1, 1],
 [0, 1, 0, 1, 0]]
```

This corresponds to a puzzle piece that looks roughly like this:

```
      ┌──┐  ┌──┐
   ┌──┘  └──┘  │
┌──┘        ┌──┘
│           └──┐
└──┐  ┌──┐  ┌──┘
   └──┘  └──┘
```

Key points:

- The 3×3 central block of cubits is always present.
- Only edge cubits may be missing.
- Because each cubit is a cube (height, width, and thickness are the same), pieces that fit together flat will also fit
  at right angles — enabling 3D assembly.

## Shapes

### Describing shapes

A **tile** is the spot in a shape where a single puzzle piece fits.

For a 6-tile cube:

- There are 6 tiles (one per face).
- We can “unfold” the cube and number the tiles starting from 0, for example:

```
     0
   1 2 3
     4
     5
```

We assign a **North edge** to each tile (e.g., the top edge in this layout). Then for each tile, we note which tiles lie
to its **North**, **East**, **South**, **West** when folded into shape.

Example: The neighbors of tiles in ascending order are given by the following list.

```
[
 (5, 3, 2, 1),
 (0, 2, 4, 5),
 (0, 3, 4, 1),
 (0, 5, 4, 2),
 (2, 3, 5, 1),
 (4, 3, 0, 1),
]
```

This list of 4-tuples is the **shape description**.

> The same shape can have many valid descriptions depending on tile numbering and North edge choices.

### Slots

Each tile has 16 cubit **slots** at its edges numbered clockwise starting from the northwest corner:

```
     0  1  2  3  4
    15     N     5
    14 W       E 6
    13     S     7
    12 11 10  9  8
```

We'll use the notation `A[i]` to refer to slot `i` of tile `A`.

In a shape, tile slots of adjacent tiles **overlap**:

- Example (see figure below): If Tile A’s east edge is adjacent to Tile B’s north edge, then:
    - `A[4]` overlaps `B[4]`
    - `A[5]` overlaps `B[3]`
    - `A[6]` overlaps `B[2]`
    - `A[7]` overlaps `B[1]`
    - `A[8]` overlaps `B[0]`

```
     0  1  2  3  4|4  5  6  7  8
    15     N     5|3     E     9
    14 W       E 6|2 N      S 10
    13     S     7|1     W    11
    12 11 10  9  8|0 15 14 13 12
```

Overlapping tile slots are the same **shape slot**. Mathematically speaking, shape slots are equivalence classes of tile
slots with respect to the “overlaps” relation.

Observe:

- Between 3 and 6 tiles overlap at **corner slots** (slots `0, 4, 8, 12`) depending on the shape.
- Exactly two tiles overlap at the remaining slots.

For example, a 6-tile cube has:

- 8 (= `6 * 4 / 3`) corner slots (one per vertex).
- 36 (= `6 * 12 / 2`) remaining slots (three per cube edge).

A 24-tile 2x2x2 cube (4 tiles per face) has:

- 26 corner slots, 8 of which have 3 overlapping tile slots (the ones at the cubes vertices) and the remaining 18 have 4
  overlapping tile slots. (This yields `8 * 3 + 18 * 4 = 24 * 4` corner tile slots.)
- 144 (= `24 * 12 / 2`) remaining slots.

#### Special shapes

Some shapes cannot be described by tile adjacency alone, because additional overlaps arise.

For example, consider two 6-tile cubes joined at a single vertex, so that one corner slot from each cube overlaps. The
shape description in terms of tile adjacency is the same as for two detached cubes, but the "overlap" relation has been
extended beyond what adjacency dictates.

A more interesting case comes from modifying a 2×2×2 cube (a cube with 4 tiles on each face). Choose one vertex and
"invert" the three tiles meeting at that vertex, effectively pushing the vertex into the interior of the cube. The
result is a 2×2×2 cube with a 1×1×1 cube carved out at one vertex, as shown below. In this configuration, three tile
slots overlap at the cube’s center. Let's call this shape slot A (the intersection of tiles 3, 7, and 8 in the figure).

```
           +------------------+                         +------------------+
          /  0          1    / \                       /  0          1    / \
         /                  /   \                     /                  /   \
        /                  /   9 \                   /        +---------+   9 \
       /  2         3     /       \                 /  2     / \   3     \     \
      /                  /         \               /        /   \         \     \
     +------------------+   8    15 +     ==>     +--------+  7  +---------+  15 + 
      \  6         7     \         /               \  6     \  /   8      /     /
       \                  \       /                 \        \/          /     /
        \                  \  14 /                   \        +---------+  14 / 
         \  12       13     \   /                     \  12       13     \   /
          \                  \ /                       \                  \ /
           +------------------+                         +------------------+

```

If you repeat the inversion at the opposite vertex, another three tile slots will overlap at the center. Let's call this
shape slot B (the intersection of tiles 10, 18, and 20 in the figure).

```
           +-------------------+                        +-------------------+
          / \   4          5    \                      / \   4          5    \
         /   \                   \                    /   \                   \ 
        /  22 \                   \                  /  22 +---------+         \ 
       /       \  10        11     \                /     /  10     / \   11    \ 
      /         \                   \              /     /         /   \         \
     +  23   20  +-------------------+     ==>     +  23 +--------+ 18  +---------+ 
      \         /  18         16    /               \     \        \   /   16    / 
       \       /                   /                 \     \   20   \ /         / 
        \  21 /                   /                   \  21 + -------+         / 
         \   /                   /                     \   /                  /
          \ /   19        17    /                       \ /   19       17    / 
           +-------------------+                         +-----------------+

```

The fact that shape slot A and shape slot B are the same shape slot because they occupy the center of the cube does
not follow from tile adjacency alone and requires additional geometric reasoning to detect.

We will not include special shapes like these in this kata.

### Challenge 1

Write:

```
get_shape_slots(shape: list[tuple[int, int, int, int]]) -> list[int]
```

Input:

- `shape` is a list of 4-tuples (shape description) as shown above
- `len(shape) <= 36`
- `shape` can be assembled in 3D; no "Klein bottles" or such
- `shape` is not special,

Output:

If we call the return value `result`, then:

- `len(result) == 16 * len(shape)`
- `result[16 * m + i] == result[16 * n + j]` if and only if slot `i` of tile number `m` overlaps slot`j` of tile
  number `n`.
- For all `k` in `result`, `0 ≤ k < 16 * N`
