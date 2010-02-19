\version "2.12.2"

\header {
    title = "Hello, triplets!"
    composer = "M. Foo"
}

melody = {
    \clef treble
    \key c \major
    \time 4/4

    \times 2/3 { c'8 d'8 e'8 } f'4 g'4 a'4 |
}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}
