\version "2.12.2"

\header {
    title = "Yellow Tinker"
    meter = "Reel"
}

melody = {
    \clef treble
    \key a \mixolydian
    \time 2/2

    \repeat volta 2 {
        e'8 a'8 a'8 a'8 e'8 fis'8 g'8 fis'8 |
        e'8 a'8 a'8 a'8 e''8 a'8 cis''8 a'8 |
        e'8 a'8 a'8 a'8 e'8 d'8 e'8 fis'8 |
        g'4 b'16 a'16 g'8 c''8 g'8 b'8 g'8
    }
    a'4 e''8 a'8 fis''8 a'8 e''8 a'8 |
    a'8 a'8 e''4 d''8 b'8 g'8 b'8 |
    a'4 e''8 a'8 fis''8 a'8 e''4 |
    d''4 b'8 g'8 d'8 g'8 b'8 g'8 |
    a'4 e''8 a'8 fis''8 a'8 e''8 a'8 |
    a'8 a'8 e''4 d''8 b'8 g'8 b'8 |
    e''8 e''8 e''8 fis''8 g''8 g''8 g''8 e''8 |
    d''4 b'8 g'8 d'8 g'8 b'8 g'8 |
}

\score {
    \new Staff \melody
    \layout { }
    \midi { }
}
