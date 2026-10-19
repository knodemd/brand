# Graphic elements

The building blocks to design anything new with the system.

- `Patterns/`: node field, cell screen, mark repeat, SVG and PNG.
- `Alphabet/`: every Knode Block and Knode Line character as its own SVG (currentColor);
  punctuation is named by code point (`U+002E.svg` is the full stop).
- `Grid/`: the construction of the mark on its 10 × 25 grid, and the radius rule
  (every corner, convex or concave, is half a cell).

Anything new: draw it on the cell grid, round every corner with half a cell, and it belongs to Knode.
