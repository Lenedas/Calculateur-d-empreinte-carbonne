#!/usr/bin/env python3
"""Interface graphique pour le calculateur d'empreinte carbone."""

import tkinter as tk
from tkinter import ttk, messagebox
import urllib.request
import urllib.parse
import json
import threading
from carbon_calculator import calculate_emissions


class CarbonCalculatorApp:
    """Application GUI pour le calcul d'empreinte carbone."""

    def __init__(self, root):
        self.root = root
        self.root.title("Calculateur d'Empreinte Carbone")
        self.root.geometry("560x620")
        self.root.configure(bg="#f0f0f0")
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Frame principal
        main_frame = ttk.Frame(root, padding="8")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titre
        title = ttk.Label(
            main_frame,
            text="Calculateur d'Empreinte Carbone",
            font=("Helvetica", 16, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=10)
        
        # ── Séparateur ──────────────────────────────────────────
        sep_top = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        sep_top.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 4))

        # ── Section itinéraire ───────────────────────────────────
        route_header = ttk.Label(
            main_frame,
            text="📍 Calcul de la distance par itinéraire",
            font=("Helvetica", 11, "bold")
        )
        route_header.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(4, 6))

        ttk.Label(main_frame, text="Départ :").grid(row=3, column=0, sticky=tk.W, pady=4)
        self.origin_var = tk.StringVar()
        origin_entry = ttk.Entry(main_frame, textvariable=self.origin_var, width=20)
        origin_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=10)

        ttk.Label(main_frame, text="Arrivée :").grid(row=4, column=0, sticky=tk.W, pady=4)
        self.destination_var = tk.StringVar()
        dest_entry = ttk.Entry(main_frame, textvariable=self.destination_var, width=20)
        dest_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), padx=10)

        self.route_status_var = tk.StringVar(value="")
        route_status_label = ttk.Label(
            main_frame, textvariable=self.route_status_var,
            foreground="#555555", font=("Helvetica", 9, "italic")
        )
        route_status_label.grid(row=5, column=1, sticky=tk.W, padx=10)

        route_btn = ttk.Button(
            main_frame,
            text="🔍 Obtenir la distance",
            command=self.fetch_distance_async
        )
        route_btn.grid(row=3, column=2, rowspan=2, padx=(0, 6), pady=4, sticky=tk.NS)

        sep_bot = ttk.Separator(main_frame, orient=tk.HORIZONTAL)
        sep_bot.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(6, 4))

        # ── Section calcul ───────────────────────────────────────
        calc_header = ttk.Label(
            main_frame,
            text="🧮 Paramètres de calcul",
            font=("Helvetica", 11, "bold")
        )
        calc_header.grid(row=7, column=0, columnspan=3, sticky=tk.W, pady=(4, 6))

        # Label et input : Poids + sélection d'unité (kg / t)
        self.unit_var = tk.StringVar(value="kg")
        self.weight_label = ttk.Label(main_frame, text="Poids (kg) :")
        self.weight_label.grid(row=8, column=0, sticky=tk.W, pady=8)

        self.weight_var = tk.StringVar()
        weight_frame = ttk.Frame(main_frame)
        weight_frame.grid(row=8, column=1, sticky=(tk.W, tk.E), padx=10)

        weight_entry = ttk.Entry(weight_frame, textvariable=self.weight_var, width=13)
        weight_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        unit_combo = ttk.Combobox(
            weight_frame,
            textvariable=self.unit_var,
            values=["kg", "t"],
            state="readonly",
            width=3
        )
        unit_combo.pack(side=tk.LEFT, padx=(6, 0))
        unit_combo.bind("<<ComboboxSelected>>", self.on_unit_changed)
        
        # Label et input : Distance
        ttk.Label(main_frame, text="Distance (km) :").grid(row=9, column=0, sticky=tk.W, pady=8)
        self.distance_var = tk.StringVar()
        distance_entry = ttk.Entry(main_frame, textvariable=self.distance_var, width=20)
        distance_entry.grid(row=9, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Label et input : Facteur d'émission
        ttk.Label(main_frame, text="Facteur (g CO2e/t.km) :").grid(row=10, column=0, sticky=tk.W, pady=8)
        self.factor_choice_var = tk.StringVar(value="86 g")
        self.custom_factor_var = tk.StringVar()

        factor_options = ["86 g Marchandise diverse/longue distance", "183 g frigorifique", "1099 g Express", "Personnalisé"]
        factor_combo = ttk.Combobox(
            main_frame,
            textvariable=self.factor_choice_var,
            values=factor_options,
            state="readonly",
            width=18
        )
        factor_combo.grid(row=10, column=1, sticky=(tk.W, tk.E), padx=10)
        factor_combo.bind("<<ComboboxSelected>>", self.on_factor_choice_changed)

        ttk.Label(main_frame, text="Valeur personnalisée :").grid(row=11, column=0, sticky=tk.W, pady=8)
        self.custom_factor_entry = ttk.Entry(main_frame, textvariable=self.custom_factor_var, width=20, state="disabled")
        self.custom_factor_entry.grid(row=11, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Boutons d'action
        calculate_button = ttk.Button(
            main_frame,
            text="Calculer",
            command=self.calculate
        )
        calculate_button.grid(row=12, column=0, sticky=tk.W, pady=20)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=1, sticky=(tk.W, tk.E), pady=20)

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
            row=13, column=0, columnspan=2, sticky=tk.W, pady=(10, 5)
        )
        
        self.result_text = tk.Text(
            main_frame,
            height=8,
            width=50,
            wrap=tk.WORD,
            bg="white",
            font=("Courier", 10)
        )
        self.result_text.grid(row=14, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbar pour le texte
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        scrollbar.grid(row=14, column=2, sticky=(tk.N, tk.S))
        self.result_text.config(yscrollcommand=scrollbar.set)
        
        # Configuration de la grille
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=0)
        main_frame.rowconfigure(14, weight=1)
    
    def fetch_distance_async(self):
        """Lance le calcul de distance dans un thread pour ne pas bloquer l'UI."""
        origin = self.origin_var.get().strip()
        destination = self.destination_var.get().strip()
        if not origin or not destination:
            messagebox.showerror("Erreur", "Veuillez saisir un lieu de départ et d'arrivée.")
            return
        self.route_status_var.set("⏳ Recherche en cours…")
        t = threading.Thread(target=self._fetch_distance_thread, args=(origin, destination), daemon=True)
        t.start()

    def _fetch_distance_thread(self, origin: str, destination: str):
        """Appel réseau (OpenRouteService) dans un thread secondaire."""
        try:
            def geocode(place: str):
                params = urllib.parse.urlencode({"q": place, "format": "json", "limit": 1})
                url = f"https://nominatim.openstreetmap.org/search?{params}"
                req = urllib.request.Request(url, headers={"User-Agent": "CarbonCalculatorApp/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode())
                if not data:
                    raise ValueError(f"Lieu introuvable : {place!r}")
                return float(data[0]["lon"]), float(data[0]["lat"])

            lon1, lat1 = geocode(origin)
            lon2, lat2 = geocode(destination)

            ors_url = "https://api.openrouteservice.org/v2/directions/driving-hgv"
            body = json.dumps({
                "coordinates": [[lon1, lat1], [lon2, lat2]],
                "units": "km"
            }).encode()
            req = urllib.request.Request(
                ors_url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6IjdiNWI4YjAxNGY5ZTRlNzQ5NDgxMjdkZDFjNDM5YTU1IiwiaCI6Im11cm11cjY0In0=",
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode())

            distance_km = result["routes"][0]["summary"]["distance"]
            self.root.after(0, self._on_distance_received, round(distance_km, 1))

        except Exception as e:
            self.root.after(0, self._on_distance_error, str(e))

    def _on_distance_received(self, distance_km: float):
        """Appelé dans le thread principal une fois la distance obtenue."""
        self.distance_var.set(str(distance_km))
        self.route_status_var.set(f"✅ Distance routière : {distance_km} km")

    def _on_distance_error(self, error_msg: str):
        """Appelé dans le thread principal en cas d'erreur."""
        self.route_status_var.set("❌ Erreur lors du calcul")
        messagebox.showerror(
            "Erreur de géolocalisation",
            f"Impossible de calculer la distance :\n{error_msg}\n\n"
            "Vérifiez les noms des lieux et votre connexion internet."
        )

    def calculate(self):
        """Effectue le calcul et affiche le résultat."""
        try:
            # Récupérer et valider les entrées
            weight_str = self.weight_var.get().strip().replace(',', '.')
            distance_str = self.distance_var.get().strip().replace(',', '.')
            
            if not weight_str or not distance_str:
                messagebox.showerror("Erreur", "Veuillez remplir le poids et la distance.")
                return
            
            weight_input = float(weight_str)
            # Convertir en kg si l'utilisateur a saisi en tonnes
            if self.unit_var.get() == 't':
                weight_kg = weight_input * 1000.0
            else:
                weight_kg = weight_input
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

            # Préparer l'affichage de la formule selon l'unité choisie
            if self.unit_var.get() == 't':
                # l'utilisateur a saisi en tonnes
                weight_display = f"{weight_input:.3f} t"
                formula = f"{factor} g/t.km × {weight_input:.3f} t × {distance_km} km = {emissions_g:.0f} g CO2e"
            else:
                # l'utilisateur a saisi en kg
                weight_t = weight_kg / 1000.0
                weight_display = f"{weight_input:.0f} kg ({weight_t:.3f} t)"
                formula = f"{factor} g/t.km × {weight_t:.3f} t × {distance_km} km = {emissions_g:.0f} g CO2e"

            # Afficher le résultat
            result_text = (
                f"Résultat : {emissions_kg:.2f} kg CO2e\n\n"
                f"Entrée : {weight_display}\n"
                f"Formule : {formula}"
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

    def on_unit_changed(self, event=None):
        """Met à jour le label du poids quand l'utilisateur change l'unité."""
        unit = self.unit_var.get()
        if unit == 't':
            self.weight_label.config(text="Poids (t) :")
        else:
            self.weight_label.config(text="Poids (kg) :")
    
    def reset(self):
        """Réinitialise tous les champs."""
        self.origin_var.set("")
        self.destination_var.set("")
        self.route_status_var.set("")
        self.weight_var.set("")
        self.distance_var.set("")
        self.factor_choice_var.set("86 g")
        self.custom_factor_var.set("")
        self.custom_factor_entry.config(state="disabled")
        self.unit_var.set("kg")
        self.weight_label.config(text="Poids (kg) :")
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
