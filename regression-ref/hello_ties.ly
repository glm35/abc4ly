\version "2.12.2"

\header {
    title = "Hello, world!"
    composer = "M. Foo"
}

melody = {
    \clef treble
    \key c \major
    \time 4/4

    c'2 ~ c'4 d'4 ~ |
    d'2 e'2 |
}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}
