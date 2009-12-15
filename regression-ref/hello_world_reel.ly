\version "2.12.2"

\header {
  title = "Hello, world!"
  composer = "M. Foo"
  meter = "Reel"
}

melody = \relative c' {
  \clef treble
  \key c \major
  \time 2/2

  a4 b c d
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}
