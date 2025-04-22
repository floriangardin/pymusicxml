#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #
#  This file is part of SCAMP (Suite for Computer-Assisted Music in Python)                      #
#  Copyright © 2020 Marc Evanstein <marc@marcevanstein.com>.                                     #
#                                                                                                #
#  This program is free software: you can redistribute it and/or modify it under the terms of    #
#  the GNU General Public License as published by the Free Software Foundation, either version   #
#  3 of the License, or (at your option) any later version.                                      #
#                                                                                                #
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;     #
#  without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.     #
#  See the GNU General Public License for more details.                                          #
#                                                                                                #
#  You should have received a copy of the GNU General Public License along with this program.    #
#  If not, see <http://www.gnu.org/licenses/>.                                                   #
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++  #

from pymusicxml import *


Score([
    PartGroup([
        Part("Oboe", [
            Measure([
                Chord(["G#4", "b4", "d5"], 1.5, notations=StartMultiGliss((None, 1, 2))),
                GraceChord(["C5", "eb5", "G5"], 0.5, stemless=True, notations=StopMultiGliss((1, None, 2))),
                BeamedGroup([
                    Note("f#4", 0.25),
                    Note("A#4", 0.25)
                ]),
                Chord(["Cs4", "Ab4"], 1.0, directions=Dynamic("LOUD")),
                Rest(1.0)
            ], time_signature=(4, 4), directions_with_displacements=[
                (Dynamic("mf"), 0),
                (MetronomeMark(1.5, 80), 0),
                (TextAnnotation("rit.", italic=True), 1.0),
                (MetronomeMark(1.0, 60), 3.5)
            ]),
            Measure([
                Tuplet([
                    Note("c5", 0.5),
                    Note("bb4", 0.25),
                    Note("a4", 0.25),
                    Note("b4", 0.25),
                ], (5, 4)),
                Note("f4", 2, directions=TextAnnotation("with gusto!")),
                Rest(1)
            ], clef="mezzo-soprano", barline="end", key="d-flat, f#, gx, cbb"),
            Measure([
                Note("e5", 1, directions=[StartHairpin("crescendo")]),
                Note("g5", 1, directions=[StartDashes(text="sim.")], notations=[TrillMark()]),
                Note("f5", 1, directions=[StopDashes(), StopHairpin()], notations=[StartTrill()]),
                Note("d5", 1, notations=[StopTrill()])
            ]),
            Measure([
                Rest(4)
            ])
        ]),
        Part("Bb Clarinet", [
            Measure([
                Tuplet([
                    Note("c5", 0.5),
                    Note("bb4", 0.25, notehead="x"),
                    Note("a4", 0.25),
                    Note("b4", 0.25),
                ], (5, 4)),
                Note("f4", 2),
                Rest(1)
            ], time_signature=(4, 4), key="F# dorian", transpose=Transpose(-2, -1)),
            Measure([
                Note("d5", 1.5, directions=[StartBracket(text="roguishly")]),
                BeamedGroup([
                    Note("f#4", 0.25),
                    Note("A#4", 0.25)
                ]),
                Chord(["Cs4", "Ab4"], 1.0, directions=[StopBracket(line_end="down")]),
                Rest(1.0)
            ], barline="end"),
            Measure([
                Note("a4", 1, directions=[StartHairpin("diminuendo")]),
                BeamedGroup([
                    Note("b4", 0.5, notations=[StartSlur()]),
                    Note("c5", 0.5),
                    Note("d5", 0.5),
                    Note("e5", 0.5, notations=[StopSlur()])
                ]),
                Note("d5", 0.5, directions=[StopHairpin()], notations=[StartGliss(3)]),
                Note("g5", 0.5, notations=[StopGliss(3)])
            ]),
            Measure([
                Rest(4)
            ])
        ]),
        Part("Violin", [
            Measure([
                Note("e5", 1, notations=[Mordent()]),
                Note("g5", 1, notations=[Turn()]),
                Note("a5", 1, notations=[Schleifer()]),
                Note("d5", 1, notations=[Tremolo(3)])
            ], time_signature=(4, 4)),
            Measure([
                BeamedGroup([
                    Note("a4", 0.5, notations=[UpBow()]),
                    Note("b4", 0.5, notations=[DownBow()]),
                    Note("c5", 0.5, notations=[UpBow()]),
                    Note("d5", 0.5, notations=[DownBow()])
                ]),
                Note("e5", 1, notations=[Harmonic()]),
                Note("a4", 1, notations=[OpenString()]),
            ], barline="end"),
            Measure([
                Chord(["e4", "g4", "c5"], 1, notations=[Arpeggiate()]),
                Chord(["f4", "a4", "d5"], 1, notations=[NonArpeggiate()]),
                BeamedGroup([
                    Note("g4", 0.5, notations=[Tremolo(2)]),
                    Note("a4", 0.5, notations=[Tremolo(2)])
                ]),
                Note("b4", 1, notations=[Harmonic(), UpBow()])
            ]),
            Measure([
                BeamedGroup([
                    Note("c5", 0.5, notations=[Harmonic(), OpenString()]),
                    Note("d5", 0.5, notations=[DownBow()]),
                    Note("e5", 0.5, notations=[UpBow()]),
                    Note("f5", 0.5, notations=[DownBow(), Tremolo(1)])
                ]),
                Chord(["g4", "b4", "d5"], 0.5, notations=[Arpeggiate(), Mordent()]),
                Chord(["a4", "c5", "e5"], 0.5, notations=[NonArpeggiate(), Turn()]),
                Note("g5", 1, notations=[Schleifer(), OpenString()])
            ], barline="end")
        ])
    ]),
    Part("Bassoon", [
        Measure([
            BarRest(4, directions=[StartPedal(),
                                   Harmony("D", -1, "dominant", use_symbols=True, degrees=[Degree(13, -1)])])
        ], time_signature=(4, 4), clef="bass"),
        Measure([
            [
                BeamedGroup([
                    Rest(0.5),
                    Note("d4", 0.5, notehead="open mi", notations=[StartGliss(1), StartSlur()]),
                    Note("Eb4", 0.5, notations=[StopGliss(1), StartGliss(2)]),
                    Note("F4", 0.5, notations=[StopGliss(2), StopSlur()]),
                ]),
                Note("Eb4", 2.0)
            ],
            None,
            [
                Rest(1.0),
                Note("c4", 2.0),
                Note("Eb3", 0.5, directions=StopPedal()),
                Rest(0.5)
            ]
        ], barline="end"),
        Measure([
            Note("C3", 1, directions=[StartPedal()]),
            BeamedGroup([
                Note("G3", 0.5, directions=[StartDashes(text="tenuto")]),
                Note("F3", 0.5),
                Note("E3", 0.5),
                Note("D3", 0.5, directions=[StopDashes()])
            ]),
            Chord(["C3", "G3"], 0.5, directions=[ChangePedal()]),
            Note("B2", 0.5, directions=[StartHairpin("crescendo")])
        ]),
        Measure([
            Note("A2", 1, directions=[StopHairpin()]),
            Chord(["G2", "D3", "G3"], 1, notations=[StartMultiGliss((1, None, 2))]),
            Chord(["E2", "B2", "E3"], 1, notations=[StopMultiGliss((1, None, 2))]),
            Note("C2", 1, directions=[StopPedal()])
        ], barline="end")
    ])
], title="Directly Created MusicXML", composer="HTMLvis").export_to_file("DirectExampleAllFeatures.musicxml")

