# Happy Cubes - Part 2: Understanding pieces

This kata is the second in a series aimed at building a solver for Happy Cube puzzles. First part
is [here](https://www.codewars.com/kata/68e20fd1c4cf24cbff647000/python). This description relies heavily on a good
understanding of the concepts introduced in that kata.

## Pieces

A Happy Cubes set consist of 6 colored pads with six pieces cut out of each.
To illustrate, the blue pad looks like this:

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
This allows two pieces to be assembled either lying flat next to each other or at a 90° angle.

An enum class is provided as part of the preloaded code.

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

Each member of the `Pads` class has a value that is an 11-by-15 multiline string of digits 0 through 7 (when ignoring
extraneous whitespace). Each digit represents a cubit and the value of the digit identifies
the piece it belongs to. The surrounding frame is marked by `'0'`'s, which we will ignore. Piece 1 consists of the part
of the pad that has the digit `'1'`, piece 2 the part of the pad that has `'2'`'s, and so on.

Side note: If you want to have some more fun, you can write a function that creates a box drawing from the pads as shown
above. However, that's [another kata](https://www.codewars.com/kata/5ff11422d118f10008d988ea). 😀

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

When a piece is assigned to a tile, its top edge shall align with the tile's north edge. The slots that a piece
covers when assigned to a tile depends on its orientation. For example, when `BLUE[2]` with the `R0` orientation is
assigned to a tile, it covers tile slots 2, 6, 9, 13, and 14, whereas with the `F2` orientation, it covers tile slots 3,
6, 10, 14, and 15.
---

The challenge in this kata is to determine which shape slots are covered when assigning a piece with a given orientation
to one of the shape's tiles. The shape is defined by a possible output of the `get_shape_slots` function defined
in [Part 1](https://www.codewars.com/kata/68e20fd1c4cf24cbff647000/python) of this kata series, which provides a
numbering and orientation of the tiles as well as a numbering of the shape slots.

#### Challenge

Write a function

```Python
def get_covered_shape_slots(
        tile: int,
        color: str,
        piece_num: int,
        orientation: str,
        slot_map: list[int],
) -> list[int]:
    pass
```

**Input**

- `tile` is an integer identifying a tile
- `color` is the name of one of the `Pads` members, i.e., `'BLUE'`, `'GREEN'`, `'PINK'`, `'PURPLE'`, `'RED'`,
  or `'YELLOW'`. It's used to identify a pad.
- `piece_num` is a number between 1 and 6 identifying one of the pad's pieces. Together, `color` and `piece_num`
  identify a piece
- `orientation` is a string identifying one of the eight possible orientations `'R0'`, `'R1'`, ..., `'F3'`
- `slot_map` is a possible output of `get_shape_slots` applied to a shape description; it is a list of length
  `16 * N`, where `N`, `0 <= N <= 36`, is the number of tiles in the shape, and `slot_map[16 * n + i]` is the shape slot
  number corresponding to tile slot `i` of tile `n`.

**Output**

The function shall return a list sorted in ascending order of the shape slot numbers covered when assigning the given
piece with the given orientation to the given tile.

---
Happy coding!