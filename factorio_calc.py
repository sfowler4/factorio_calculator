import tkinter as tk
import math
from tkinter import ttk
from collections import defaultdict

# === Assembler crafting speeds ===
assembler_speeds = {
    'Assembler 1': 0.5,
    'Assembler 2': 0.75,
    'Assembler 3': 1.25
}

# === Recipe Database ===
recipes = {
    'red_science': {
        'name': 'Red Science',
        'ingredients': {
            'iron_gear': 1,
            'copper_plate': 1
        },
        'time': 5.0
    },
    'green_science': {
        'name': 'Green Science',
        'ingredients': {
            'inserter': 1,
            'yellow_belt': 1
        },
        'time': 6.0
    },
    'inserter': {
        'name': 'Inserter',
        'ingredients': {
            'iron_plate': 1,
            'iron_gear': 1,
            'green_circuit': 1
        },
        'time': 0.5
    },
    'yellow_belt': {
        'name': 'Yellow Belt',
        'ingredients': {
            'iron_plate': 1,
            'iron_gear': 1
        },
        'time': 0.5
    },
    'iron_gear': {
        'name': 'Iron Gear',
        'ingredients': {
            'iron_plate': 2
        },
        'time': 0.5
    },
    'green_circuit': {
        'name': 'Green Circuit',
        'ingredients': {
            'iron_plate': 1,
            'copper_cable': 3
        },
        'time': 0.5
    },
    'copper_cable': {
        'name': 'Copper Cable',
        'ingredients': {
            'copper_plate': 1
        },
        'time': 0.5
    },
    'iron_plate': {
        'name': 'Iron Plate',
        'ingredients': {},
        'time': 3.5
    },
    'copper_plate': {
        'name': 'Copper Plate',
        'ingredients': {},
        'time': 3.5
    }
}

# === Recursive Calculation for Resource & Assembler Requirements ===
def calculate_requirements(target_item, rate_per_sec):
    item_rates = defaultdict(float)
    raw_resources = defaultdict(float)

    def expand(item, rate):
        if item not in recipes or not recipes[item]['ingredients']:
            raw_resources[item] += rate
            return

        item_rates[item] += rate
        for ingredient, amount in recipes[item]['ingredients'].items():
            expand(ingredient, rate * amount)

    expand(target_item, rate_per_sec)
    return item_rates, raw_resources

# === GUI App ===
class FactorioCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factorio Resource Calculator")

        # Item selection
        self.item_label = ttk.Label(root, text="Target Item:")
        self.item_label.grid(column=0, row=0, padx=5, pady=5)

        self.item_var = tk.StringVar()
        self.item_dropdown = ttk.Combobox(root, textvariable=self.item_var, state='readonly')
        self.item_dropdown['values'] = [item for item in recipes if recipes[item]['ingredients']]
        self.item_dropdown.current(0)
        self.item_dropdown.grid(column=1, row=0, padx=5, pady=5)

        # Rate input
        self.rate_label = ttk.Label(root, text="Items per second:")
        self.rate_label.grid(column=0, row=1, padx=5, pady=5)

        self.rate_entry = ttk.Entry(root)
        self.rate_entry.insert(0, "1.0")
        self.rate_entry.grid(column=1, row=1, padx=5, pady=5)

        # Assembler selection
        self.assembler_label = ttk.Label(root, text="Assembler Type:")
        self.assembler_label.grid(column=0, row=2, padx=5, pady=5)

        self.assembler_var = tk.StringVar()
        self.assembler_dropdown = ttk.Combobox(root, textvariable=self.assembler_var, state='readonly')
        self.assembler_dropdown['values'] = list(assembler_speeds.keys())
        self.assembler_dropdown.current(2)
        self.assembler_dropdown.grid(column=1, row=2, padx=5, pady=5)

        # Calculate button
        self.calc_button = ttk.Button(root, text="Calculate", command=self.calculate)
        self.calc_button.grid(column=0, row=3, columnspan=2, padx=5, pady=10)

        # Output display
        self.result_text = tk.Text(root, height=20, width=60, state='disabled')
        self.result_text.grid(column=0, row=4, columnspan=2, padx=5, pady=5)

    def calculate(self):
        item = self.item_var.get()
        assembler = self.assembler_var.get()
        try:
            rate = float(self.rate_entry.get())
        except ValueError:
            self.show_result("Please enter a valid number.")
            return

        if item not in recipes:
            self.show_result("Item not found in recipes.")
            return

        # Calculate rates and raw materials
        item_rates, raw_resources = calculate_requirements(item, rate)

        crafting_speed = assembler_speeds[assembler]
        output = f"To make {rate} {item}/sec with {assembler}:\n\n"

        # Show assembler counts for craftable items only
        output += "Assembler requirements:\n"
        for item_name, item_rate in sorted(item_rates.items()):
            if not recipes[item_name]['ingredients']:  # Skip raw resources
                continue
            recipe_time = recipes[item_name]['time']
            assemblers = math.ceil(item_rate * recipe_time / crafting_speed)
            output += f"  {assemblers} assembler(s) for {item_name} ({item_rate:.2f}/sec)\n"

        # # Show raw material needs
        output += "\nRaw inputs per second:\n"
        for res, amt in sorted(raw_resources.items()):
            output += f"  {amt:.2f} {res}/sec\n"

        self.show_result(output)

    def show_result(self, text):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state='disabled')

# === Launch the App ===
if __name__ == "__main__":
    root = tk.Tk()
    app = FactorioCalculatorApp(root)
    root.mainloop()
