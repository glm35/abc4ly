\version "2.12.2"

\header {
  title = "Hello, world!"
  composer = "M. Foo"
}

melody = \relative c' {
  \clef treble
  \key c \major
  \time 6/8

  a4 b c d
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}