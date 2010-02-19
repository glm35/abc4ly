\version "2.12.2"

\header {
    title = "Hello, world!"
    composer = "M. Foo"
}

melody = {
    \clef treble
    \key c \major
    \time 4/4

    c'4 d'4 r4 e'4
}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}
