import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager

from envs import *
from kivycalendar import CalendarWidget
from utils import *


def attempt_connect_or_init():
    connection_failed = False
    # If can connect to DB
    try:
        conn, cursor = connect_to_postgres(
            POSTGRES_HOST,
            POSTGRES_DB,
            POSTGRES_PORT,
            POSTGRES_USER,
            POSTGRES_PASSWORD
            )
        print('Connection successful')
    except:
        connection_error('Failed to connect to DB')
        return False, False

    # If can find schema
    if not connection_failed:
        try:
            schema_exists = check_schema_exists(cursor, BABEANIE_SCHEMA)
            print('Schema found')
        except:
            close_connection_to_postgres(conn)
            connection_error('Failed to find schema')
            return False, False

    if (not connection_failed) and (schema_exists):
        table_exists = check_table_exists(cursor, BABEANIE_SCHEMA, TABLE_NAME)
        if not table_exists:
            print('Table does not exist')
            try:
                create_empty_task_table(conn, cursor, BABEANIE_SCHEMA, TABLE_NAME)
                print('Table created')
            except:
                close_connection_to_postgres(conn)
                connection_error('Failed to create table')
                return False, False
        print('Existing table found')
    return conn, cursor


# def edit_task():

    

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text='BaBeanie', font_size=40, pos_hint={'y': .4}))
        layout = BoxLayout(orientation='vertical', pos_hint={'x': .25, 'y': .25})
        
        self.calendar_button = Button(text='Calendar', size_hint=(None, None), size=(400, 100))
        self.calendar_button.bind(on_release=self.go_to_calendar)
        self.upcoming_tasks_button = Button(text='Upcoming Tasks', size_hint=(None, None), size=(400, 100))
        self.upcoming_tasks_button.bind(on_release=self.go_to_upcoming_tasks)
        self.edit_tasks_button = Button(text='Edit Tasks', size_hint=(None, None), size=(400, 100))
        self.edit_tasks_button.bind(on_release=self.go_to_edit_tasks)
        layout.add_widget(self.calendar_button)
        layout.add_widget(self.upcoming_tasks_button)
        layout.add_widget(self.edit_tasks_button)
        self.add_widget(layout)

    def go_to_calendar(self, instance):
        self.manager.current = 'calendar'

    def go_to_upcoming_tasks(self, instance):
        self.manager.get_screen('upcoming_tasks')# .update_task_list()
        self.manager.current = 'upcoming_tasks'

    def go_to_edit_tasks(self, instance):
        self.manager.current = 'edit_tasks'

class CalendarScreen(Screen):
    # Number on each day of number of tasks on that day
    # Click into same type of screen as upcoming 

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        # self.add_widget(Label(text='Calendar', font_size=40))
        
        # Create a DatePicker widget
        self.date_picker = CalendarWidget()
        
        back_button = Button(text='Back', size_hint=(None, None), size=(200, 50))
        back_button.bind(on_release=self.go_to_menu)
        
        layout.add_widget(self.date_picker)
        layout.add_widget(back_button)
        
        self.add_widget(layout)

    def go_to_menu(self, instance):
        self.manager.current = 'menu'

class UpcomingTasksScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.task_list_label = Label(text='Upcoming Tasks', font_size=20, size_hint=(1, 0.2))
        back_button = Button(text='Back', size_hint=(None, None), size=(200, 50))
        back_button.bind(on_release=self.go_to_menu)
        self.layout = None  # Initialize the layout as None
        self.button_list = []  # Initialize an empty list for buttons

    def on_enter(self):
        # This method is called when the screen is displayed
        self.layout = self.generate_buttons()
        self.add_widget(self.layout)

    def on_leave(self):
        # This method is called when the screen is left
        self.remove_widget(self.layout)

    def go_to_menu(self, instance):
        self.manager.current = 'menu'

    def generate_buttons(self):
        # Generate buttons dynamically
        layout = BoxLayout(orientation='vertical')
        button_list = []

        # Create a ScrollView to contain the buttons
        scroll_view = ScrollView()

        buttons_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        buttons_container.bind(minimum_height=buttons_container.setter('height'))

        task_list_label = Label(text='Upcoming Tasks', font_size=20, size_hint=(1, 0.2))
        layout.add_widget(task_list_label)

        for i in range(1, 21):  # Generate 20 buttons (example with more buttons)
            button = Button(text=f"Button {i}", size_hint_y=None, height=50)
            button.bind(on_release=self.button_callback)
            button_list.append(button)
            buttons_container.add_widget(button)

        scroll_view.add_widget(buttons_container)
        layout.add_widget(scroll_view)

        back_button = Button(text='Back', size_hint=(None, None), size=(200, 50))
        back_button.bind(on_release=self.go_to_menu)
        layout.add_widget(back_button)

        return layout

    def button_callback(self, instance):
        # Define the callback function for button click
        print(f"Button clicked: {instance.text}")

class EditTasksScreen(Screen):
    # Categorize tasks for easier edits
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.add_widget(Label(text='babeanie', font_size=40))
        back_button = Button(text='Back', size_hint=(None, None), size=(200, 50))
        back_button.bind(on_release=self.go_to_menu)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def go_to_menu(self, instance):
        self.manager.current = 'menu'

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        menu_screen = MenuScreen(name='menu')
        calendar_screen = CalendarScreen(name='calendar')
        upcoming_tasks_screen = UpcomingTasksScreen(name='upcoming_tasks')
        edit_tasks_screen = EditTasksScreen(name='edit_tasks')
        sm.add_widget(menu_screen)
        sm.add_widget(calendar_screen)
        sm.add_widget(upcoming_tasks_screen)
        sm.add_widget(edit_tasks_screen)
        return sm

myApp = MyApp()
myApp.run()