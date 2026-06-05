#!/usr/bin/env python3
"""Interface graphique pour le calculateur d'empreinte carbone."""

import tkinter as tk
from tkinter import ttk, messagebox
from carbon_calculator import calculate_emissions


class CarbonCalculatorApp:
    """Application GUI pour le calcul d'empreinte carbone."""

    def __init__(self, root):
        self.root = root
        self.root.title("Calculateur d'Empreinte Carbone")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titre
        title = ttk.Label(
            main_frame,
            text="Calculateur d'Empreinte Carbone",
            font=("Helvetica", 16, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Label et input : Poids
        ttk.Label(main_frame, text="Poids (kg) :").grid(row=1, column=0, sticky=tk.W, pady=8)
        self.weight_var = tk.StringVar()
        weight_entry = ttk.Entry(main_frame, textvariable=self.weight_var, width=20)
        weight_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Label et input : Distance
        ttk.Label(main_frame, text="Distance (km) :").grid(row=2, column=0, sticky=tk.W, pady=8)
        self.distance_var = tk.StringVar()
        distance_entry = ttk.Entry(main_frame, textvariable=self.distance_var, width=20)
        distance_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Label et input : Facteur d'émission
        ttk.Label(main_frame, text="Facteur (g CO2e/t.km) :").grid(row=3, column=0, sticky=tk.W, pady=8)
        self.factor_choice_var = tk.StringVar(value="86 g")
        self.custom_factor_var = tk.StringVar()

        factor_options = ["86 g", "183 g", "1099 g", "Personnalisé"]
        factor_combo = ttk.Combobox(
            main_frame,
            textvariable=self.factor_choice_var,
            values=factor_options,
            state="readonly",
            width=18
        )
        factor_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10)
        factor_combo.bind("<<ComboboxSelected>>", self.on_factor_choice_changed)

        ttk.Label(main_frame, text="Valeur personnalisée :").grid(row=4, column=0, sticky=tk.W, pady=8)
        self.custom_factor_entry = ttk.Entry(main_frame, textvariable=self.custom_factor_var, width=20, state="disabled")
        self.custom_factor_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Boutons d'action
        calculate_button = ttk.Button(
            main_frame,
            text="Calculer",
            command=self.calculate
        )
        calculate_button.grid(row=5, column=0, sticky=tk.W, pady=20)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=20)

        # Bouton réinitialiser
        reset_button = ttk.Button(
            button_frame,
            text="Réinitialiser",
            command=self.reset
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton vider le cache
        clear_cache_button = ttk.Button(
            button_frame,
            text="Vider le cache",
            command=self.clear_cache
        )
        clear_cache_button.pack(side=tk.LEFT, padx=5)
        
        # Zone de résultat
        ttk.Label(main_frame, text="Résultat :", font=("Helvetica", 12, "bold")).grid(
            row=6, column=0, columnspan=2, sticky=tk.W, pady=(10, 5)
        )
        
        self.result_text = tk.Text(
            main_frame,
            height=8,
            width=50,
            wrap=tk.WORD,
            bg="white",
            font=("Courier", 10)
        )
        self.result_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar pour le texte
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Configuration de la grille
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0)
        main_frame.rowconfigure(7, weight=1)
    
    def calculate(self):
        """Effectue le calcul et affiche le résultat."""
        try:
            # Récupérer et valider les entrées
            weight_str = self.weight_var.get().strip().replace(',', '.')
            distance_str = self.distance_var.get().strip().replace(',', '.')
            
            if not weight_str or not distance_str:
                messagebox.showerror("Erreur", "Veuillez remplir le poids et la distance.")
                return
            
            weight_kg = float(weight_str)
            distance_km = float(distance_str)

            selected_factor = self.factor_choice_var.get()
            if selected_factor == "Personnalisé":
                factor_str = self.custom_factor_var.get().strip().replace(',', '.')
                if not factor_str:
                    messagebox.showerror("Erreur", "Veuillez saisir un facteur personnalisé.")
                    return
                factor = float(factor_str)
            else:
                factor = float(selected_factor.split()[0])

            if weight_kg < 0 or distance_km < 0 or factor < 0:
                messagebox.showerror("Erreur", "Les valeurs doivent être positives.")
                return
            
            # Calcul
            emissions_kg = calculate_emissions(weight_kg, distance_km, factor)
            emissions_g = emissions_kg * 1000
            weight_t = weight_kg / 1000.0
            
            # Afficher le résultat
            result_text = (
                f"Résultat : {emissions_kg:.2f} kg CO2e\n\n"
                f"Formule : {factor} g/t.km × {weight_t:.3f} t × {distance_km} km = {emissions_g:.0f} g CO2e"
            )
            
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result_text)
            self.result_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror(
                "Erreur",
                "Entrée invalide. Veuillez entrer des nombres valides.\n"
                "Utilisez '.' ou ',' pour les décimales."
            )
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

    def on_factor_choice_changed(self, event=None):
        """Active le champ personnalisé uniquement si l'utilisateur choisit Personnalisé."""
        if self.factor_choice_var.get() == "Personnalisé":
            self.custom_factor_entry.config(state="normal")
        else:
            self.custom_factor_entry.config(state="disabled")
            self.custom_factor_var.set("")
    
    def reset(self):
        """Réinitialise tous les champs."""
        self.weight_var.set("")
        self.distance_var.set("")
        self.factor_choice_var.set("86 g")
        self.custom_factor_var.set("")
        self.custom_factor_entry.config(state="disabled")
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
    
    def clear_cache(self):
        """Vide la zone de résultat."""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    app = CarbonCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
