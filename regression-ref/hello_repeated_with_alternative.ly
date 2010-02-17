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
        c'4 d'4 e'4 f'4
    }
    \alternative {
        { g'4 a'4 b'4 c''4 }
        { g'4 e'4 d'4 c'4 }
    }
}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}
