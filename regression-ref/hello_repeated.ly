\version "2.12.2"

\header {
    title = "Hello, world!"
    composer = "M. Foo"
}

melody = {
    \clef treble
    \key c \major
    \time 4/4

    \repeat volta 2 {
        a4 b4 c'4 d'4
    }
}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}