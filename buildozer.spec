[app]
# (str) Title of your application
title = Fretboard Trainer

# (str) Package name (no spaces or special chars)
package.name = fretboardtrainer

# (str) Package domain (must be unique)
package.domain = org.fretboardtrainer

# (str) Source code directory (where main.py lives)
source.dir = .

# (list) Include these file types in the APK
source.include_exts = py, kv, png, jpg, json, wav

# (optional) include additional folders (if you add assets later)
# source.include_patterns = assets/*, images/*, *.kv, *.json

# (str) Application version
version = 0.1

# (list) Python packages required
requirements = python3, kivy, pillow

# (str) Entry point file (defaults to main.py)
entrypoint = main.py

# (list) Supported orientations
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# (int) Target Android API (set to the latest installed in your SDK)
android.api = 35

# (int) Minimum supported API
android.minapi = 21

# (list) Architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Use the SDL2 bootstrap (modern Kivy bootstrap)
android.bootstrap = sdl2

# (bool) Allow Android to back up app data
android.allow_backup = True

# (list) Permissions – not required for now
android.permissions =

# (str) Presplash color (optional)
android.presplash_color = #000000

# (bool) Copy Python libs instead of packaging as libpymodules.so
android.copy_libs = 1

# (str) Format of debug build
android.debug_artifact = apk

# (list) Patterns to exclude
exclude_patterns = tests/*, test/*, __pycache__/*

android.wakelock = True

[buildozer]
# (int) Log level (0 = errors only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
