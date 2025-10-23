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


CONFIG_FILE = "config.json"

# Notes sets
NOTES_12 = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTES_7 = ["C", "D", "E", "F", "G", "A", "H"]

# Strings for 6 and 7 string guitars
STRINGS_6 = ["6 - low E", "5 - A", "4 - D", "3 - G", "2 - B", "1 - high E"]
STRINGS_7 = ["7 - low B"] + STRINGS_6  # Adding a low B string for 7-string

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        # Defaults if no config file
        return {
            "string_count": 6,
            "notes_set": "all",  # "all" or "7"
            "show_string": True 
        }
    if "show_string" not in config:
        config["show_string"] = True

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

        # … your existing layout code …
        self.display = Label(
            text="",
            font_size=32,
            halign='center',
            valign='middle',
            color=(0,0,0,1),
            pos_hint={'center_x': 0.5, 'y': 0.15},
            markup=True
        )
        self.labelbox.add_widget(self.display)

        # Load saved preference
        self.show_string = self.config.get("show_string", True)

        # Create toggle button
        self.toggle_string_btn = ToggleButton(
            text="Hide String" if self.show_string else "Show String",
            state="down" if self.show_string else "normal",
            size_hint=(None, None),
            size=(dp(150), dp(50)),
            pos_hint={'center_x': 0.5, 'center_y': 0.3}
        )
        self.toggle_string_btn.bind(on_press=self.toggle_string)
        self.layout.add_widget(self.toggle_string_btn)

        # State variable
        self.show_string = True

        self.layout.add_widget(self.labelbox)

        button_size = dp(90)
        buttons_layout = BoxLayout(
            size_hint=(0.9, None),
            height=dp(100),  # overall height for the button row
            spacing=dp(10),
            pos_hint={'center_x': 0.5, 'y': 0.1}
        )
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

    #def update_bg(self, *args):
    #    self.bg_rect.pos = self.pos
    #    self.bg_rect.size = self.size
#
    #    # Calculate how many times to repeat the texture (adjust tiling scale)
    #    repeat_x = self.width / dp(256)   # each tile roughly 256dp wide
    #    repeat_y = self.height / dp(256)
#
    #    self.texture.uvsize = (repeat_x, -repeat_y)
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

    def toggle_string(self, instance):
        self.show_string = instance.state == "down"
        instance.text = "Hide String" if self.show_string else "Show String"

        # Update config and save
        self.config["show_string"] = self.show_string
        save_config(self.config)

        # Update the displayed label
        self.update_display()

    def start_practice(self, instance):
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

    def pick_new_note(self):
        self.current_string = random.choice(self.strings)
        self.current_note = random.choice(self.notes)
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

        #self.labelbox.display.text = (
        #    f"✅ Practice finished!\n"
        #    f"⏱ Total time: {self.format_time(total_time)}\n"
        #    f"🎯 Notes practiced: {self.note_count}\n"
        #    f"⚡ Average time/note: {avg_time:.2f} sec"
        #)

        

        self.manager.current = 'trainer'  # or your main screen name
        main_screen = self.manager.get_screen('trainer')

        main_screen.labelbox.display.text = (
            f"[size={int(sp(Window.width * 0.045))}]Practice finished![/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Total time: [b]{self.format_time(total_time)}[/b][/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Notes practiced: [b]{self.note_count}[/b][/size]\n"
            f"[size={int(sp(Window.width * 0.025))}]Average time/note: [b]{avg_time:.2f} sec[/b][/size]"
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

    def update_timer(self, dt):
        if self.start_time is None:
            return
        self.elapsed_time = time.time() - self.start_time
        self.update_display(timer_only=True)

    def update_display(self, timer_only=False):
        if not self.practicing:
            return
        string_lines = f"[size={int(sp(Window.width * 0.035))}]String[/size]\n[size={int(sp(Window.width * 0.07))}][b]{self.current_string}[/b][/size]\n" if self.show_string else ""

        time_str = self.format_time(self.elapsed_time)
        if timer_only:
            text = self.labelbox.display.text.split('\n', 1)[1] if '\n' in self.labelbox.display.text else ""
            self.labelbox.display.text = f"{time_str}\n{text}"
        else:
            #self.labelbox.display.text = f"⏱ {time_str}\nString: {self.current_string}\nNote: {self.current_note}"
            self.labelbox.display.text = (
                f"{time_str}"
                f"\n"
                f"{string_lines}"
                f"[size={int(sp(Window.width * 0.07))}][b]{self.current_note}[/b][/size]\n"
                f"[size={int(sp(Window.width * 0.035))}]Note[/size]"
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
        self.padding = 10
        self.spacing = 5
        self.size_hint = (0.9, None)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.75}

        # 🎨 Semi-transparent rounded background
        with self.canvas.before:
            Color(1, 1, 1, 0.7)
            self.bg_rect = Rectangle(radius=[15], pos=self.pos, size=self.size)

        # 🧩 Keep background in sync with layout
        self.bind(pos=self._update_bg, size=self._update_bg)

        # 🏷 Label that can grow vertically
        self.display = Label(
            text="Press Start to begin",
            color=(0, 0, 0, 1),
            font_size=32,
            halign='center',
            valign='middle',
            size_hint_y=None,
            markup=True
        )

        # Bind text and size changes to dynamically resize the box
        self.display.bind(texture_size=self._update_label_height)
        self.add_widget(self.display)

        # Initialize height properly
        self._update_label_height()

    def _update_label_height(self, *args):
        """Resize Label and Box height based on label content."""
        # Give label enough height for its text
        self.display.height = self.display.texture_size[1] + 20  # padding
        # Adjust total box height accordingly
        pad = self.padding[1] if isinstance(self.padding, (list, tuple)) else self.padding
        self.height = self.display.height + pad * 2
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
    #Window.size = (400, 800)
    GuitarTrainerApp().run()
