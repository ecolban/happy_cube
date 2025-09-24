# Happy Cubes - Part 1: Understanding shapes

This kata is the first in a series aimed at building a solver for Happy Cube puzzles.

## What is Happy Cubes

Happy Cubes is a 3D puzzle game where the goal is to assemble puzzle pieces into a cube (or other shapes).
Each piece is cut from a colored foam pad and can be represented as a 5×5 matrix of 1s and 0s:

- 1 = a small cubic unit (we’ll call it a _cubit_) is present.
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
to its **north**, **east**, **south**, **west** when folded into shape.

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

Each tile has 16 **slots** at its edges numbered clockwise starting from the northwest corner:

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

Note that two non-adjacent tiles may overlap at a corner only. This may happen if there is a tile `B` adjacent to `A`
and `D` where, e.g., `A[8]` overlaps `B[12]`, which overlaps `D[0]`.

Configuration of tiles where `A` and `D` overlap at a corner only:

```
A B
C D
```

**Shape slots:** We'll say that overlapping tile slots share the same _shape slot_.

Observe:

- Between 3 and 6 tiles overlap at **corner slots** (slots `0, 4, 8, 12`) depending on the shape.
- Exactly two tiles overlap at the remaining slots.

For example, a 6-tile cube has:

- 8 (= `6 * 4 / 3`) corner shape slots (one per cube vertex) -- 6 tiles with 4 corner slots each, with 3 tile slots
  sharing
  each shape slot
- 36 (= `6 * 12 / 2`) remaining shape slots (three per cube edge) -- 6 tiles with 12 non-corner slots each, with 2 tile
  slots
  sharing each shape slot

A 24-tile 2x2x2 cube (4 tiles per face) has:

- 26 corner shape slots, 8 of which have 3 overlapping tile slots (the ones at the cubes vertices) and the remaining 18
  have 4 overlapping tile slots. (This yields `8 * 3 + 18 * 4 = 24 * 4` corner tile slots.)
- 144 (= `24 * 12 / 2`) remaining slots.

### Tack stitches

(You may skip reading this section; its presence is only to warn people from becoming "too clever". The gist of it is
that there are shapes for which shape descriptions as described above, i.e., as a list of 4-tuples, are inadequate. Such
shapes will not be part of this kata.)

Not all overlaps in a shape come directly from tile adjacency. In some cases, additional overlaps arise that require
extra reasoning to detect.

To explain this, it helps to borrow terms from sewing:

- The intersection of two adjacent tiles is like a **seam**.
- Each pair of overlapping slots is a **stitch**.
- A stitch that is not part of a seam is a **tack stitch** (a reinforcing stitch that holds points together).

**Example 1.**  
Take two 6-tile cubes joined at a single vertex so that a corner slot from each cube overlap. Tile adjacency alone
would describe them as two detached cubes, but the “overlap” relation extends further: the shared vertex is a single
tack stitch, not explained by seams.

**Example 2.**  
Start with a 2×2×2 cube (4 tiles per face). Choose a vertex and “invert” the three tiles that meet there, pushing the
vertex into the cube’s interior. The result is a 2×2×2 cube with a 1×1×1 cube "carved out", as shown:

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

Here, three tile slots overlap at the cube’s center. Call this overlap **shape slot A** (the intersection of tiles 3,
7, and 8 in the figure).

If you repeat the inversion at the opposite vertex, another three tile slots will overlap at the cube's center. Let's
call this shape slot B (the intersection of tiles 10, 18, and 20 in the figure).

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

Since A and B occupy the same physical space (the center of the cube), they are actually the same shape slot —- but this
fact cannot be deduced from adjacency alone. It requires geometric reasoning. Their overlap is a tack stitch.

In this kata, _we will consider only shapes with seams (adjacency overlaps) only, not tack stitches._

---

### Challenge

Write a function:

```
get_shape_slots(shape: list[tuple[int, int, int, int]]) -> list[int]
  """Each distinct value in the returned list represents a shape slot 
  and the indices that hold that value are the tile slots that share 
  the shape slot."""
```

Input:

- `shape` is a list of 4-tuples (shape description) as shown above
- `len(shape) <= 36`
- `shape` can be assembled in 3D; no "Klein bottles" or such

Output:

If we call the return value `result`, then:

- `len(result) == 16 * len(shape)`
- for tile numbers `m` and `n` and slot numbers `i` and `j`, `result[16 * m + i] == result[16 * n + j]` if and only if
  slot `i` of tile `m` overlaps slot`j` of tile `n`.
- for all `k` in `result`, `0 ≤ k < N`, where `N` is the number of distinct values in `result` (`N` is also the number
  of shape slots)

