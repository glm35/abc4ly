\version "2.12.2"

\header {
  title = "Hello, world!"
  composer = "M. Foo"
}

melody = {
  \clef treble
  \key c \major
  \time 4/4

  a4 b c d
}

\score {
  \new Staff \melody
  \layout { }
  \midi { }
}
