import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Menu
from PIL import Image, ImageTk
import csv
import os

class PokemonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon Collection Manager")

        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Définir les colonnes pour le Treeview, sans la colonne "Sprite"
        columns = ("ID", "Name", "Game", "Level", "Nature", "Ability", "Method")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Définir les en-têtes et colonnes pour le Treeview
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, minwidth=100)

        # Boutons pour charger le CSV et ajouter un Pokémon
        self.load_button = tk.Button(self.root, text="Load CSV", command=self.load_csv)
        self.load_button.pack()

        self.add_button = tk.Button(self.root, text="Add Pokémon", command=self.add_pokemon)
        self.add_button.pack()

        # Gestion des événements pour le clic droit et double-clic
        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Définir le chemin du fichier CSV et charger les données
        self.csv_file = "pokemon_collection.csv"
        self.pokemon_data = []
        self.sprite_images = {}  # Dictionnaire pour stocker les images
        self.load_csv()

        self.pokemon_dict = self.load_pokemon_dict()

        # Menu contextuel pour la modification et la suppression des Pokémon
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Modify", command=self.modify_pokemon)
        self.context_menu.add_command(label="Delete", command=self.delete_pokemon)

    def load_pokemon_dict(self):
        pokemon_dict = {}
        try:
            with open("pokemon_id_name.csv", mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    pokemon_dict[row[0]] = row[1]
        except FileNotFoundError:
            messagebox.showerror("Error", "pokemon_id_name.csv file not found.")
        return pokemon_dict

    def load_csv(self):
        if os.path.exists(self.csv_file):
            try:
                with open(self.csv_file, mode='r') as file:
                    reader = csv.DictReader(file)
                    self.pokemon_data = []
                    for row in reader:
                        if "Method" not in row:
                            row["Method"] = ""  # Ajouter la colonne "Method" si elle manque
                        self.pokemon_data.append(row)

                    self.tree.delete(*self.tree.get_children())
                    for row in self.pokemon_data:
                        sprite_path = f"sprites/{row['ID']}.png"
                        sprite_image = self.load_sprite(sprite_path)
                        self.sprite_images[row['ID']] = sprite_image
                        self.tree.insert("", tk.END, values=(row['ID'], row['Name'], row["Game"], row["Level"], row["Nature"], row["Ability"], row["Method"]), image=self.sprite_images.get(row['ID']))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV file: {e}")
        else:
            with open(self.csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Name", "Sprite", "isShiny", "Game", "Save", "Evolution",
                                "Gender", "Forme majeur", "Forme mineur", "PID", "Ball", "Level",
                                "IVs", "EVs", "Nature", "Ability", "Date", "Location", "Note", "Method"])

    def save_csv(self):
        with open(self.csv_file, mode='w', newline='') as file:
            fieldnames = ["ID", "Name", "Sprite", "isShiny", "Game", "Save", "Evolution",
                          "Gender", "Forme majeur", "Forme mineur", "PID", "Ball", "Level",
                          "IVs", "EVs", "Nature", "Ability", "Date", "Location", "Note", "Method"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.pokemon_data)

    def load_sprite(self, path):
        if os.path.exists(path):
            print(f"Loading sprite: {path}")  # Débogage: afficher le chemin du sprite
            img = Image.open(path)
            img = img.resize((96, 96), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            return img
        else:
            print(f"Sprite not found: {path}")  # Débogage: afficher les erreurs
        return None

    def add_pokemon(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add Pokémon")

        # Ajouter un canvas pour permettre le défilement
        canvas = tk.Canvas(add_window)
        scrollbar = tk.Scrollbar(add_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Fonction pour redimensionner le canvas
        def on_frame_configure(canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: on_frame_configure(canvas)
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        labels = ["ID", "Name", "Sprite", "isShiny", "Game", "Save", "Evolution", "Gender", "Forme majeur", "Forme mineur", "PID", "Ball", "Level", "IVs", "EVs", "Nature", "Ability", "Date", "Location", "Note", "Method"]

        entries = {}
        for i, label in enumerate(labels):
            tk.Label(scrollable_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(scrollable_frame)
            entry.grid(row=i, column=1, sticky=tk.W)
            entries[label] = entry

        def on_id_or_name_change(event=None):
            id_entry = entries["ID"].get()
            name_entry = entries["Name"].get()
            if event.widget == entries["ID"] and id_entry in self.pokemon_dict:
                entries["Name"].delete(0, tk.END)
                entries["Name"].insert(0, self.pokemon_dict[id_entry])
            elif event.widget == entries["Name"] and name_entry in self.pokemon_dict.values():
                for key, value in self.pokemon_dict.items():
                    if value == name_entry:
                        entries["ID"].delete(0, tk.END)
                        entries["ID"].insert(0, key)
                        break

        entries["ID"].bind("<KeyRelease>", on_id_or_name_change)
        entries["Name"].bind("<KeyRelease>", on_id_or_name_change)

        def submit():
            new_pokemon = {label: entries[label].get() for label in labels}
            self.pokemon_data.append(new_pokemon)
            sprite_path = f"sprites/{new_pokemon['ID']}.png"
            sprite_image = self.load_sprite(sprite_path)
            self.sprite_images[new_pokemon['ID']] = sprite_image
            self.tree.insert("", tk.END, values=(new_pokemon["ID"], new_pokemon["Name"], new_pokemon["Game"], new_pokemon["Level"], new_pokemon["Nature"], new_pokemon["Ability"], new_pokemon["Method"]), image=sprite_image)
            self.save_csv()
            add_window.destroy()

        submit_button = tk.Button(scrollable_frame, text="Submit", command=submit)
        submit_button.grid(row=len(labels), columnspan=2)

    def show_context_menu(self, event):
        try:
            self.context_menu.post(event.x_root, event.y_root)
        except IndexError:
            pass

    def delete_pokemon(self):
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, "values")

        self.pokemon_data = [row for row in self.pokemon_data if row["ID"] != item_values[0]]
        self.tree.delete(selected_item)
        self.save_csv()

    def modify_pokemon(self):
        selected_item = self.tree.selection()[0]
        item_values = self.tree.item(selected_item, "values")

        modify_window = tk.Toplevel(self.root)
        modify_window.title("Modify Pokémon")

        # Ajouter un canvas pour permettre le défilement
        canvas = tk.Canvas(modify_window)
        scrollbar = tk.Scrollbar(modify_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        # Fonction pour redimensionner le canvas
        def on_frame_configure(canvas):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind(
            "<Configure>",
            lambda e: on_frame_configure(canvas)
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        labels = ["ID", "Name", "Sprite", "isShiny", "Game", "Save", "Evolution", "Gender", "Forme majeur", "Forme mineur", "PID", "Ball", "Level", "IVs", "EVs", "Nature", "Ability", "Date", "Location", "Note", "Method"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(scrollable_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W)
            entry = tk.Entry(scrollable_frame)
            if i < len(item_values):
                entry.insert(0, item_values[i])
            entry.grid(row=i, column=1, sticky=tk.W)
            entries[label] = entry

        def submit():
            new_values = {label: entries[label].get() for label in labels}
            for row in self.pokemon_data:
                if row["ID"] == item_values[0]:
                    row.update(new_values)
            sprite_path = f"sprites/{new_values['ID']}.png"
            sprite_image = self.load_sprite(sprite_path)
            self.sprite_images[new_values['ID']] = sprite_image
            self.tree.item(selected_item, values=(new_values["ID"], new_values["Name"], new_values["Game"], new_values["Level"], new_values["Nature"], new_values["Ability"], new_values["Method"]), image=sprite_image)
            self.save_csv()
            modify_window.destroy()

        submit_button = tk.Button(scrollable_frame, text="Submit", command=submit)
        submit_button.grid(row=len(labels), columnspan=2)

    def on_item_double_click(self, event):
        item_id = self.tree.selection()[0]
        item_values = self.tree.item(item_id, "values")
        self.show_pokemon_details(item_values)

    def show_pokemon_details(self, item_values):
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Details of {item_values[1]}")

        labels = ["Sprite", "ID", "Name", "Game", "Level", "Nature", "Ability", "Method", "isShiny", "Save", "Evolution", "Gender", "Forme majeur", "Forme mineur", "PID", "Ball", "IVs", "EVs", "Date", "Location", "Note"]

        sprite_path = f"sprites/{item_values[0]}.png"
        if os.path.exists(sprite_path):
            img = Image.open(sprite_path)
            img = img.resize((96, 96), Image.Resampling.LANCZOS)
            img = ImageTk.PhotoImage(img)
            sprite_label = tk.Label(detail_window, image=img)
            sprite_label.image = img  # Garder une référence pour éviter la collecte des ordures
            sprite_label.grid(row=0, column=2, rowspan=len(labels))

        for i, label in enumerate(labels):
            tk.Label(detail_window, text=f"{label}:").grid(row=i, column=0, sticky=tk.W)
            tk.Label(detail_window, text=item_values[i] if i < len(item_values) else "N/A").grid(row=i, column=1, sticky=tk.W)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokemonApp(root)
    root.mainloop()