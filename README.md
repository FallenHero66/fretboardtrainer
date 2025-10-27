# Fretboard Trainer
Fretboard Trainer helps you learn the layout of the guitar fretboard.

## How to practice
For beginners, decide on a string you want to practice on. You can toggle natural (7) tones or all (12) tones in the settings. <br>
Press the "Start Practice" button and play the displayed note in every position you can on the fretboard (between 1 and 2 positions, depending on whether you have 24 tabs or less)

This App was inspired Brandon D'Eon's technique on learning the fretboard: https://www.youtube.com/watch?v=7PMZWb6ZNJc

## Features
You can toggle between 6 and 7 strings, and between natural (7) tones or all (12) tones in the settings.<br>
Toggling the "Show/Hide Strings" button, the app also generates random strings you can practice on to make it even harder.<br>
After pressing "End practice", you receive a summary about your practice session. This helps tracking your progress.

## Tested on
- Pixel 7 Pro
- Pixel 7

## Screenshots:
<img src="/screenshots/Practice.png" width=400> <img src="/screenshots/Stats.png" width=400>

## How to build
Want to build the app yourself? Here's how:

On a linux system, run the following commands:

```
git pull https://github.com/FallenHero66/fretboardtrainer.git
python -m venv fretboard_venv # I suggest doing this outside of the fretboardtrainer folder, as otherwise your venv will be compiled into your .apk
source venv/bin/activate
cd fretboardtrainer
python -m pip install -e requirements.txt
buildozer android debug
```
You will then receive a .apk file in the bin folder.
