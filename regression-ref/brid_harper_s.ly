\version "2.12.2"

\header {
  title = "Br\'id Harper's"
  meter = "Jig"
}

melody = {
  \clef treble
  \key e \minor
  \time 6/8

  \repeat volta 2 {
    g'8    e'8    fis'8    g'4    a'8    |
    b'8    e''8    e''8    d''8    b'8    d''8    |
    e''8    d''8    b'8    a'8    g'8    a'8    |
    b'8    g'8    e'8    a'8    fis'8    d'8    |
    g'8    e'8    fis'8    g'4    a'8    |
    b'8    e''8    e''8    d''8    b'8    d''8    |
    e''8    d''8    b'8    a'8    g'8    a'8    |
    b'8    g'8    e'8    e'4.
  }
  \repeat volta 2 {
    g''4    g''8    fis''8    e''8    d''8    |   
    e''4    e''8    d''8    b'8    a'8    |
    g'4    g'8    a'8    b'8    c''8    |
    b'8    g'8    e'8    e'8    g'8    e'8    |
    d'8    b8    d'8    e'8    g'8    c''8    |
    b'8    d''8    b'8    g''4    d''8    |
    e''8    d''8    b'8    a'8    g'8    a'8    |
    b'8    g'8    e'8    e'4.
  }   
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}
