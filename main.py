import json
import random
import time
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
#from kivy.factory import Factory
from kivy.uix.screenmanager import Screen
from kivy.graphics import Rectangle, Color
from kivy.core.image import Image as CoreImage
from kivy.uix.button import Button
from kivy.properties import ListProperty
from kivy.metrics import dp,sp
from kivy.uix.anchorlayout import AnchorLayout

Builder.load_file("guitartrainer.kv")

class RoundedButton(Button):
    bg_color = ListProperty([0.2, 0.6, 0.9, 1])  # default color

class RoundedToggleButton(ToggleButton):
    bg_color = ListProperty([0.2, 0.6, 0.9, 1])  # default color

    def on_touch_down(self, touch):
        # If this button is already 'down', ignore further touches
        if self.state == "down":
            return False
        return super().on_touch_down(touch)

CONFIG_FILE = "config.json"

# Notes sets
NOTES_12 = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_7 = ["C", "D", "E", "F", "G", "A", "H"]
NOTES_POSITIONS=fretboard = {
    "E": {  # Low E string
        "E": 0, "F": 1, "F#": 2, "G": 3, "G#": 4, "A": 5, "A#": 6,
        "B": 7, "C": 8, "C#": 9, "D": 10, "D#": 11, "E (octave)": 12
    },
    "A": {  # A string
        "A": 0, "A#": 1, "B": 2, "C": 3, "C#": 4, "D": 5, "D#": 6,
        "E": 7, "F": 8, "F#": 9, "G": 10, "G#": 11, "A (octave)": 12
    },
    "D": {  # D string
        "D": 0, "D#": 1, "E": 2, "F": 3, "F#": 4, "G": 5, "G#": 6,
        "A": 7, "A#": 8, "B": 9, "C": 10, "C#": 11, "D (octave)": 12
    },
    "G": {  # G string
        "G": 0, "G#": 1, "A": 2, "A#": 3, "B": 4, "C": 5, "C#": 6,
        "D": 7, "D#": 8, "E": 9, "F": 10, "F#": 11, "G (octave)": 12
    },
    "B": {  # B string
        "B": 0, "C": 1, "C#": 2, "D": 3, "D#": 4, "E": 5, "F": 6,
        "F#": 7, "G": 8, "G#": 9, "A": 10, "A#": 11, "B (octave)": 12
    },
    # high E string identical to low E string
}

# Strings for 6 and 7 string guitars
STRINGS_6 = ["6 - low E", "5 - A", "4 - D", "3 - G", "2 - B", "1 - high E"]
STRINGS_7 = ["7 - low B"] + STRINGS_6  # Adding a low B string for 7-string

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except Exception:
        config = {
            "string_count": 6,
            "notes_set": "all",
            "show_string": True,
            "practice_mode": "random"   # NEW default
        }

    if "practice_mode" not in config:
        config["practice_mode"] = "random"
    return config

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


class TrainerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.practicing = False
        self.config = load_config()
        # Add background color/pattern
        self.texture = CoreImage("blueprint_pattern.png").texture
        self.texture.wrap = 'repeat'
        #self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        
        # Create a canvas rectangle with that texture
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(
                texture=self.texture,
                pos=self.pos,
                size=self.size
            )

        # Bind to screen resizing
        self.bind(pos=self.update_bg, size=self.update_bg)

        self.labelbox = LabelBox()

        # Load saved preference
        self.show_string = self.config.get("show_string", False)

        # Create toggle button
        mode = self.config['practice_mode']
        if mode == "random":
            togglebuttontext="Hide String" if self.show_string else "Show String"
        elif mode == "sequential":
            togglebuttontext="Hide Cheatsheet" if self.show_string else "Show Cheatsheet"
        
        self.toggle_string_btn = ToggleButton(
            text = togglebuttontext,
            state="down" if self.show_string else "normal",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.toggle_string_btn.bind(on_press=self.toggle_string)
        self.layout.add_widget(self.toggle_string_btn)


        button_size = dp(90)

        # --- Practice mode selection ---
        self.mode_labelbox = LabelBox()
        self.mode_labelbox.display.text ="Practice mode:"

        self.mode_box = BoxLayout(
            size_hint=(1, None),
            height=dp(60),
            spacing=dp(10),
            pos_hint={'center_x': 0.5, 'y': 0.5},
            padding=(dp(20), dp(5)),
        )
        self.mode_box.add_widget(self.mode_labelbox)

        self.random_mode_btn = RoundedToggleButton(
            text="Random",
            group="mode",
            state="down" if self.config['practice_mode'] == 'random' else "normal",
            on_press=lambda x: self.set_mode('random'),
        )
        self.seq_mode_btn = RoundedToggleButton(
            text="Sequential",
            group="mode",
            state="down" if self.config['practice_mode'] == 'sequential' else "normal",
            on_press=lambda x: self.set_mode('sequential'),
        )

        self.mode_box.add_widget(self.random_mode_btn)
        self.mode_box.add_widget(self.seq_mode_btn)

        buttons_layout = BoxLayout(
            size_hint=(0.9, None),
            height=dp(100),  # overall height for the button row
            spacing=dp(10),
            pos_hint={'center_x': 0.5, 'y': 0.1}
        )
        self.layout.add_widget(self.mode_box)
        self.layout.add_widget(buttons_layout)

        self.start_button = RoundedButton(text="Start\nPractice",disabled=False, bg_color=(0, 0.7, 0, 1), size=(button_size, button_size), halign="center", valign="middle")
        self.start_button.bind(on_press=self.start_practice)
        buttons_layout.add_widget(self.start_button)

        self.next_button = RoundedButton(text="Next\nNote", disabled=True, size=(button_size, button_size), halign="center", valign="middle")
        self.next_button.bind(on_press=self.next_note)
        buttons_layout.add_widget(self.next_button)

        self.stop_button = RoundedButton(text="Stop\nPractice", disabled=True, bg_color=(0.8, 0, 0, 1), size=(button_size, button_size), halign="center", valign="middle")
        self.stop_button.bind(on_press=self.stop_practice)
        buttons_layout.add_widget(self.stop_button)

        self.settings_button = RoundedButton(text="Settings", size=(button_size, button_size), halign="center", valign="middle")  
        self.settings_button.bind(on_press=self.go_to_settings)
        buttons_layout.add_widget(self.settings_button)
        # Initially hide Next & Stop
        self.next_button.opacity = 0
        self.next_button.disabled = True
        self.stop_button.opacity = 0
        self.stop_button.disabled = True
        
        # You’d apply the canvas trick or use a custom class to draw rounded rectangle.

        self.current_string = None
        self.current_note = None
        self.start_time = None
        self.note_count = 0
        self.elapsed_time = 0
        self.timer_event = None

        self.config = load_config()

        self.update_settings_dependent_data()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos

        img_ratio = self.texture.width / self.texture.height
        screen_ratio = self.width / self.height

        if screen_ratio > img_ratio:
            # Screen is wider → match height, crop sides
            new_height = self.height
            new_width = new_height * img_ratio
        else:
            # Screen is taller → match width, crop top/bottom
            new_width = self.width
            new_height = new_width / img_ratio

        self.bg_rect.size = (new_width, new_height)
        self.bg_rect.pos = (
            self.center_x - new_width / 2,
            self.center_y - new_height / 2
        )


    def update_settings_dependent_data(self):
        # Set strings and notes based on config
        if self.config["string_count"] == 6:
            self.strings = STRINGS_6
        else:
            self.strings = STRINGS_7

        if self.config["notes_set"] == "7":
            self.notes = NOTES_7
        else:
            self.notes = NOTES_12
        self.remaining_notes = []

    def toggle_string(self, instance):
        self.show_string = instance.state == "down"
        mode = self.config["practice_mode"]
        if mode == "random":
            instance.text = "Hide String" if self.show_string else "Show String"
        elif mode == "sequential":
            instance.text = "Hide Cheatsheet" if self.show_string else "Show Cheatsheet"

        # Update config and save
        self.config["show_string"] = self.show_string
        save_config(self.config)

        # Update the displayed label
        self.update_display()

    def set_mode(self, newmode):
        if newmode == "random":
            mode = "random" 
            self.toggle_string_btn.text = "Show String"
        elif newmode == "sequential":
            mode = "sequential"
            self.toggle_string_btn.text = "Show Cheatsheet"
        self.config["practice_mode"] = mode
        save_config(self.config)

    def start_practice(self, instance):
        if self.labelbox.parent is None:
            self.layout.add_widget(self.labelbox)
        self.layout.remove_widget(self.mode_box)

        # Reset session data
        self.practicing = True
        self.start_time = None
        self.note_count = 0
        self.elapsed_time = 0
        self.current_note = None
        self.current_string = None

        # hide start
        self.start_button.opacity = 0
        self.start_button.disabled = True
        self.settings_button.opacity = 0
        self.settings_button.disabled = True
        # show next & stop
        self.next_button.opacity = 1
        self.next_button.disabled = False
        self.stop_button.opacity = 1
        self.stop_button.disabled = False
        self.start_time = time.time()
        self.note_count = 0
        self.elapsed_time = 0
        self.start_button.disabled = True
        self.next_button.disabled = False
        self.stop_button.disabled = False
        self.pick_new_note()

        if self.timer_event:
            self.timer_event.cancel()
        self.timer_event = Clock.schedule_interval(self.update_timer, 1)

    def random_mode(self):
        self.current_string = random.choice(self.strings)
        self.current_note = random.choice(self.notes)

    def sequential_mode(self):
        if not hasattr(self, "seq_index"):
            self.seq_index = 0
        self.current_string = self.strings[self.seq_index % len(self.strings)]
        self.current_note = self.notes[self.seq_index % len(self.notes)]
        self.seq_index += 1

    def pick_new_note(self):
        if self.config["practice_mode"] == "random":
            if len(self.remaining_notes) == 0:
                self.remaining_notes = self.notes[:]
            self.current_string = random.choice(self.strings)
            self.current_note = random.choice(self.remaining_notes)
            self.remaining_notes.remove(self.current_note)
        elif self.config["practice_mode"] == "sequential":
            # Sequential mode — simple example cycling through notes
            self.sequential_mode()
        self.note_count += 1
        self.update_display()

    def next_note(self, instance):
        self.pick_new_note()


    def stop_practice(self, instance):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

        total_time = time.time() - self.start_time if self.start_time else 0
        avg_time = total_time / self.note_count if self.note_count else 0

        self.manager.current = 'trainer'  # or your main screen name
        main_screen = self.manager.get_screen('trainer')

        main_screen.labelbox.display.text = (
            f"[size={int(sp(Window.width * 0.045))}]Practice finished![/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Total time: [b]{self.format_time(total_time)}[/b][/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Notes practiced: [b]{self.note_count}[/b][/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Average time/note: [b]{avg_time:.2f} sec[/b][/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Mode: [b]{self.config['practice_mode']}[/b][/size]"
        )
        self.next_button.opacity = 0
        self.next_button.disabled = True
        self.stop_button.opacity = 0
        self.stop_button.disabled = True
        self.start_button.opacity = 1
        self.start_button.disabled = False
        self.settings_button.opacity = 1
        self.settings_button.disabled = False
        self.practicing = False
        self.settings_button.text = "Home"
        self.settings_button.unbind(on_press=self.go_to_settings)
        self.settings_button.bind(on_press=self.go_home)

    def go_home(self, instance):
        # Reset to trainer screen (home)
        self.manager.current = "trainer"

        # Restore Settings button back to normal for next session
        self.settings_button.text = "Settings"
        self.settings_button.unbind(on_press=self.go_home)
        self.settings_button.bind(on_press=self.go_to_settings)
        self.layout.remove_widget(self.labelbox)
        self.layout.add_widget(self.mode_box)

    def update_timer(self, dt):
        if self.start_time is None:
            return
        self.elapsed_time = time.time() - self.start_time
        self.update_display(timer_only=True)

    def update_display(self, timer_only=False):
        if not self.practicing:
            return
        string_lines = f"[size={int(sp(Window.width * 0.035))}]String[/size]\n[size={int(sp(Window.width * 0.07))}][b]{self.current_string}[/b][/size]\n" if self.show_string and self.config['practice_mode'] == "random" else ""
        
        time_str = self.format_time(self.elapsed_time)
        if timer_only:
            text = self.labelbox.display.text.split('\n', 1)[1] if '\n' in self.labelbox.display.text else ""
            self.labelbox.display.text = f"{time_str}\n{text}"
        else:
            if self.config['practice_mode']=="sequential" and self.show_string:
                tabsize = int(sp(Window.width * 0.03))
                if self.config['string_count'] == 6:
                    cheatsheet = (
                        f"---------------------------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['E'][self.current_note]}[/size]------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['B'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['G'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['D'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------------------\n"
                        f"---------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['A'][self.current_note]}[/size]------------------------------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['E'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------------------------------\n"
                    )
                else:
                    cheatsheet = (
                        f"---------------------------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['E'][self.current_note]}[/size]------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['B'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['G'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['D'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------------------\n"
                        f"---------------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['A'][self.current_note]}[/size]------------------------------------------------------------------------------------------------------------------\n"
                        f"----------------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['E'][self.current_note]}[/size]-----------------------------------------------------------------------------------------------------------------------\n"
                        f"-----------------------------------------------------------------------------------[size={tabsize}]{NOTES_POSITIONS['B'][self.current_note]}[/size]----------------------------------------------------------------------------------------------------------------------------\n"
                    )
            else:
                cheatsheet = ""
            self.labelbox.display.text = (
                f"{time_str}"
                f"\n"
                f"{string_lines}"
                f"[size={int(sp(Window.width * 0.07))}][b]{self.current_note}[/b][/size]\n"
                f"[size={int(sp(Window.width * 0.035))}]Note[/size]\n"
                f"{cheatsheet}"
            )

    @staticmethod
    def format_time(seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        hours = int(minutes // 60)
        minutes = int(minutes % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def go_to_settings(self, instance):
        self.manager.current = "settings"


class LabelBox(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (None, None)  # we'll control size manually
        self.padding = dp(15)
        self.spacing = dp(5)
        self.pos_hint = {'center_x': 0.5, 'top': 0.95}  # 5% gap from top
        self.display = Label(
            text="Ready to start",
            halign="center",
            valign="middle",
            markup=True,
            color=(0, 0, 0, 1)
        )
        self.display.bind(texture_size=self._update_label_height)
        self.add_widget(self.display)

        with self.canvas.before:
            Color(1, 1, 1, 0.7)  # semi-transparent white
            self.bg_rect = Rectangle(radius=[dp(15)])

        self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_label_height(self, *args):
        # Fit LabelBox height and width to content + padding
        label = self.display
        pad = self.padding[0] if isinstance(self.padding, (list, tuple)) else self.padding
        self.width = min(Window.width * 0.9, label.texture_size[0] + pad * 2)
        self.height = label.texture_size[1] + pad * 2
        self._update_bg()

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size




class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.root_layout = FloatLayout()
        self.add_widget(self.root_layout)


        self.layout = BoxLayout(
            orientation='vertical',
            size_hint=(1, 0.6),
            pos_hint={'center_x': 0.5, 'center_y': 0.75},
            spacing=dp(10),
            padding=dp(10)
        )
        self.root_layout.add_widget(self.layout)

        self.config = load_config()

        # Create toggle buttons first
        self.strings_6_btn = ToggleButton(text="6", group="strings", size_hint_x=None, width=100)
        self.strings_7_btn = ToggleButton(text="7", group="strings", size_hint_x=None, width=100)

        self.notes_7_btn = ToggleButton(text="7", group="notes", size_hint_x=None, width=100)
        self.notes_12_btn = ToggleButton(text="12", group="notes", size_hint_x=None, width=100)

        # Number of Strings Label
        lbl1 = Label(text="Select Number of Strings", font_size=20, size_hint_y=None, height=30,
                     halign='center', valign='middle')
        lbl1.bind(size=lambda instance, value: instance.setter('text_size')(instance, instance.size))
        self.layout.add_widget(lbl1)

        # Wrap strings toggles in centered AnchorLayout
        strings_layout = BoxLayout(size_hint_y=None, height=40, spacing=10, size_hint_x=None, width=210)
        strings_layout.add_widget(self.strings_6_btn)
        strings_layout.add_widget(self.strings_7_btn)
        strings_anchor = AnchorLayout(size_hint_y=None, height=40)
        strings_anchor.add_widget(strings_layout)
        self.layout.add_widget(strings_anchor)

        # Set initial state for strings toggle
        if self.config.get("string_count", 6) == 7:
            self.strings_7_btn.state = "down"
        else:
            self.strings_6_btn.state = "down"

        # Notes Set Label
        lbl2 = Label(text="Select Notes Set", font_size=20, size_hint_y=None, height=30,
                     halign='center', valign='middle')
        lbl2.bind(size=lambda instance, value: instance.setter('text_size')(instance, instance.size))
        self.layout.add_widget(lbl2)

        # Wrap notes toggles in centered AnchorLayout
        notes_layout = BoxLayout(size_hint_y=None, height=40, spacing=10, size_hint_x=None, width=210)
        notes_layout.add_widget(self.notes_7_btn)
        notes_layout.add_widget(self.notes_12_btn)
        notes_anchor = AnchorLayout(size_hint_y=None, height=40)
        notes_anchor.add_widget(notes_layout)
        self.layout.add_widget(notes_anchor)

        # Set initial state for notes toggle
        if self.config.get("notes_set", "all") == "12":
            self.notes_12_btn.state = "down"
        else:
            self.notes_7_btn.state = "down"

        # Save button centered and fixed width
        self.save_button = RoundedButton(text="Save and Back", size_hint=(None, None), size=(210, 50))
        self.save_button.pos_hint = {'center_x': 0.5}
        self.save_button.bind(on_press=self.save_and_back)
        self.layout.add_widget(self.save_button)

    def save_and_back(self, instance):
        self.config["string_count"] = 7 if self.strings_7_btn.state == "down" else 6
        self.config["notes_set"] = "12" if self.notes_12_btn.state == "down" else "7"
        save_config(self.config)

        trainer = self.manager.get_screen("trainer")
        trainer.config = self.config
        trainer.update_settings_dependent_data()

        self.manager.current = "trainer"


class GuitarTrainerApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TrainerScreen(name="trainer"))
        sm.add_widget(SettingsScreen(name="settings"))
        return sm


if __name__ == '__main__':
    #Window.size = (498, 1080)
    GuitarTrainerApp().run()
