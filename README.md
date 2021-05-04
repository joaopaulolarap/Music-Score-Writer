# Basic Score Writer 

This is a messy and simple score writer I created for fun and to practice some concepts. The score is constructed on a pixel level logic, with the symbols being sets of coordinates of which pixels (relatively to an origin point at the symbol image file) should be colored black. It isn't finished, but it is possible to create scores for basic melodies, as shown in the example image. 

#### Considerations:

- The logic of coloring some parts/elements, such as the note connection bars, might be unintelligible for it is nearly arbitrary.
- The notes, pauses, key signature and time signature should be given in the 'WRITE' section at the end of the score-writer code.
- There are no exceptions (thus nor exception handling) in the code, as it is very informal. If values out of bounds are given, it would result in errors.
- Some connection bars may come out wrong.
- I'm not an expert in music, so I did what I could with what I knew and learned by searching.
- It is possible to create only one page.
- Most certainly, there are infinitely better ways to do what I did, and some methods may be unnecessary and too badly writen.