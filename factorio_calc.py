import tkinter as tk
import math
import yaml
from tkinter import ttk
from collections import defaultdict

# Assembler crafting speeds
assembler_speeds = {
    'Assembler 1': 0.5,
    'Assembler 2': 0.75,
    'Assembler 3': 1.25
}

# List of oils made in different processes
output_to_recipe = {
  "petroleum_gas": "basic_oil_processing",
  "heavy_oil": "advanced_oil_processing",
  "light_oil": "advanced_oil_processing"
}

# Open yaml file that holds recipes, helps to keep code clean
with open("recipes.yaml", "r") as f:
    recipes = yaml.safe_load(f)

# Recursive Calculation for Resource & Assembler Requirements
def calculate_requirements(target_item, rate_per_sec):
    item_rates = defaultdict(float)
    raw_resources = defaultdict(float)

    def expand(item, rate):
        if item not in recipes or not recipes[item]['ingredients']:
            raw_resources[item] += rate
            return

        output_amount = recipes[item].get('output', 1)
        crafts_per_sec = rate / output_amount
        item_rates[item] += crafts_per_sec

        for ingredient, amount in recipes[item]['ingredients'].items():
            expand(ingredient, crafts_per_sec * amount)

    expand(target_item, rate_per_sec)
    return item_rates, raw_resources

# GUI App
class FactorioCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Factorio Resource Calculator")

        # Item selection
        self.item_label = ttk.Label(root, text="Target Item:")
        self.item_label.grid(column=0, row=0, padx=5, pady=5)

        # Build a display name to item key mapping
        self.display_name_to_key = {
            recipes[key].get('name', key): key
            for key in recipes
            if recipes[key]['ingredients']  # only craftable items
        }

        self.item_var = tk.StringVar()
        self.item_dropdown = ttk.Combobox(root, textvariable=self.item_var, state='readonly')
        self.item_dropdown['values'] = list(self.display_name_to_key.keys())
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
        display_name = self.item_var.get()
        item = self.display_name_to_key.get(display_name)
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

        display_name = recipes[item].get("name", item)
        output = f"To make {rate} {display_name}/sec with {assembler}:\n\n"

        # Show assembler counts for craftable items only
        output += "Assembler requirements:\n"
        for item_name, item_rate in sorted(item_rates.items()):
            if not recipes[item_name]['ingredients']:  # Skip raw resources
                continue
            recipe_time = recipes[item_name]['time']
            assemblers = math.ceil(item_rate * recipe_time / crafting_speed)
            machine_type = recipes[item_name].get('machine', 'assembler')
            display_name = recipes[item_name].get("name", item_name)
            output += f"  {assemblers} {machine_type}(s) for {display_name} ({item_rate:.2f}/sec)\n"

        # Show raw material needs
        output += "\nRaw inputs per second:\n"
        for res, amt in sorted(raw_resources.items()):
            display_name = recipes[res].get("name", res) if res in recipes else res 
            output += f"  {amt:.2f} {display_name}/sec\n"

        self.show_result(output)

    def show_result(self, text):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.config(state='disabled')

# Launch the App
if __name__ == "__main__":
    root = tk.Tk()
    app = FactorioCalculatorApp(root)
    root.mainloop()
