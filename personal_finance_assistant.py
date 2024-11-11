import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ListProperty, StringProperty
import cohere
import json
from datetime import datetime
import os

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
print("Cohere API Key", COHERE_API_KEY)

# Initialize Cohere client
co = cohere.Client("oddRPfeNXM0Rq3ohAjRKlMcLWFuUdBXCvZzVOosA")
# Custom styling defined in the Builder
Builder.load_string('''
<StyledButton>:
    background_color: 0, 0, 0, 0
    canvas.before:
        Color:
            rgba: (0.13, 0.59, 0.95, 1) if not self.state == 'down' else (0.09, 0.47, 0.82, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(10)]
    font_size: '16sp'
    bold: True
    color: 1, 1, 1, 1
    size_hint_y: None
    height: dp(50)
    padding: dp(15), dp(10)

<StyledTextInput>:
    background_normal: ''
    background_color: 0.95, 0.95, 0.95, 1
    foreground_color: 0, 0, 0, 1
    cursor_color: 0.3, 0.3, 0.3, 1
    font_size: '16sp'
    padding: dp(15)
    multiline: False

<StyledLabel>:
    font_size: '18sp'
    color: 0.2, 0.2, 0.2, 1
    size_hint_y: None
    height: dp(40)
    halign: 'left'
    valign: 'middle'
    text_size: self.size
''')

class StyledButton(Button):
    pass

class StyledTextInput(TextInput):
    pass

class StyledLabel(Label):
    pass

class FinanceAssistant(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        
        # Set up basic window properties
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Initialize data structures
        self.expenses = []
        self.load_expenses()
        
        # Set up the UI
        self.setup_ui()
    
    def setup_ui(self):
        # App header
        header = BoxLayout(size_hint_y=None, height=dp(80), padding=[0, dp(10)])
        header.add_widget(StyledLabel(text="Personal Finance Assistant", font_size='28sp', bold=True))
        self.add_widget(header)
        
        # Tabs for navigation
        tab_buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        self.advice_btn = StyledButton(text="Get Advice", on_press=self.show_advice_section)
        self.expense_btn = StyledButton(text="Track Expenses", on_press=self.show_expense_section)
        self.goals_btn = StyledButton(text="Financial Goals", on_press=self.show_goals_section)
        
        tab_buttons.add_widget(self.advice_btn)
        tab_buttons.add_widget(self.expense_btn)
        tab_buttons.add_widget(self.goals_btn)
        self.add_widget(tab_buttons)
        
        # Main content area
        self.content_layout = BoxLayout(orientation='vertical', spacing=dp(15))
        self.add_widget(self.content_layout)
        
        # Display default section
        self.show_advice_section(None)

    def show_advice_section(self, instance):
        self.content_layout.clear_widgets()
        advice_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        advice_layout.add_widget(StyledLabel(text="Ask for Financial Advice", bold=True))
        
        # Input area for asking questions
        self.query_input = StyledTextInput(hint_text="Enter your question...")
        advice_layout.add_widget(self.query_input)
        
        # Get advice button
        submit_btn = StyledButton(text="Get Advice", on_press=self.get_financial_advice)
        advice_layout.add_widget(submit_btn)
        
        # Display area for advice response
        self.response_label = Label(text="Your advice will appear here...", color=(0.3, 0.3, 0.3, 1))
        advice_layout.add_widget(self.response_label)
        
        self.content_layout.add_widget(advice_layout)

    def show_expense_section(self, instance):
        self.content_layout.clear_widgets()
        expense_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Input fields for adding expenses
        self.expense_amount = StyledTextInput(hint_text="Amount ($)")
        self.expense_category = StyledTextInput(hint_text="Category")
        add_expense_btn = StyledButton(text="Add Expense", on_press=self.add_expense)
        
        expense_layout.add_widget(StyledLabel(text="Add New Expense"))
        expense_layout.add_widget(self.expense_amount)
        expense_layout.add_widget(self.expense_category)
        expense_layout.add_widget(add_expense_btn)
        
        # Expense list
        self.expense_list_label = Label(text="No expenses recorded.", color=(0.3, 0.3, 0.3, 1))
        expense_layout.add_widget(self.expense_list_label)
        
        self.content_layout.add_widget(expense_layout)

    def show_goals_section(self, instance):
        self.content_layout.clear_widgets()
        goals_layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Input fields for adding goals
        self.goal_description = StyledTextInput(hint_text="Goal description")
        self.goal_amount = StyledTextInput(hint_text="Target amount ($)")
        add_goal_btn = StyledButton(text="Set Goal", on_press=self.add_goal)
        
        goals_layout.add_widget(StyledLabel(text="Set Financial Goals"))
        goals_layout.add_widget(self.goal_description)
        goals_layout.add_widget(self.goal_amount)
        goals_layout.add_widget(add_goal_btn)
        
        self.content_layout.add_widget(goals_layout)

    def get_financial_advice(self, instance):
        if not co:
            self.response_label.text = "Cohere API key is missing."
            return

        query = self.query_input.text
        if not query:
            self.response_label.text = "Please enter a question first."
            return

        # Call Cohere API
        self.response_label.text = "Fetching advice..."
        try:
            response = co.generate(
                model='command-r-plus-08-2024',  # You can use 'xlarge' or other models depending on your access
                prompt=f"Provide financial advice for the following question:\n{query}",
                max_tokens=50,   # Adjust based on advice length needed
                temperature=0.5  # Adjust temperature for creativity in response
            )
            advice = response.generations[0].text.strip() if response.generations else "No response received."
            self.response_label.text = advice

        except Exception as e:
            self.response_label.text = f"Error fetching advice: {str(e)}"
        
    def add_expense(self, instance):
        try:
            amount = float(self.expense_amount.text)
            category = self.expense_category.text
            
            if amount and category:
                self.expenses.append({
                    'amount': amount,
                    'category': category,
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                self.expense_amount.text = ''
                self.expense_category.text = ''
                self.update_expense_list()
        except ValueError:
            self.expense_list_label.text = "Please enter a valid amount."

    def update_expense_list(self):
        if self.expenses:
            expense_text = "\n".join([f"{exp['date']} - ${exp['amount']} ({exp['category']})" for exp in self.expenses])
            self.expense_list_label.text = expense_text
        else:
            self.expense_list_label.text = "No expenses recorded yet."

    def add_goal(self, instance):
        goal_desc = self.goal_description.text
        try:
            goal_amount = float(self.goal_amount.text)
            if goal_desc and goal_amount:
                # Append goal logic here (not implemented)
                self.goal_description.text = ''
                self.goal_amount.text = ''
        except ValueError:
            pass

    def load_expenses(self):
        if os.path.exists("expenses.json"):
            with open("expenses.json", "r") as f:
                self.expenses = json.load(f)

    def save_expenses(self):
        with open("expenses.json", "w") as f:
            json.dump(self.expenses, f)

class FinanceApp(App):
    def build(self):
        return FinanceAssistant()

if __name__ == '__main__':
    FinanceApp().run()
