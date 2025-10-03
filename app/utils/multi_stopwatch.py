from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button


class Stopwatch(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='horizontal', **kwargs)
        self.time = 0
        self.running = False

        self.label = Label(text='0.0', font_size=32)
        self.start_btn = Button(text='Start')
        self.pause_btn = Button(text='Pause')
        self.reset_btn = Button(text='Reset')

        self.add_widget(self.label)
        self.add_widget(self.start_btn)
        self.add_widget(self.pause_btn)
        self.add_widget(self.reset_btn)

        self.start_btn.bind(on_press=self.start)
        self.pause_btn.bind(on_press=self.pause)
        self.reset_btn.bind(on_press=self.reset)

    def update(self, dt):
        if self.running:
            self.time += dt
            self.label.text = f'{self.time:.1f}'

    def start(self, instance):
        if not self.running:
            self.running = True
            self._event = Clock.schedule_interval(self.update, 0.1)

    def pause(self, instance):
        self.running = False

    def reset(self, instance):
        self.running = False
        self.time = 0
        self.label.text = '0.0'


class MultiStopwatchApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Stopwatch())
        layout.add_widget(Stopwatch())
        return layout


if __name__ == '__main__':
    MultiStopwatchApp().run()
