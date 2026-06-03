#!/usr/bin/env python3
"""Calculateur d'empreinte carbone pour transport (g CO2e / t.km).
Formule utilisée : émissions (g) = facteur (g CO2e / t.km) * poids (t) * distance (km)
Le résultat est affiché en kg CO2e.

Exemple : 86 g/t.km * 15 t * 221 km = 285090 g = 285.09 kg CO2e
"""


def calculate_emissions(weight_kg: float, distance_km: float, factor_g_per_tkm: float = 86.0) -> float:
    """Retourne les émissions en kilogrammes CO2e.

    weight_kg : poids en kilogrammes
    distance_km : distance en kilomètres
    factor_g_per_tkm : facteur d'émission en grammes CO2e par tonne-kilomètre
    """
    weight_t = weight_kg / 1000.0
    emissions_g = factor_g_per_tkm * weight_t * distance_km
    emissions_kg = emissions_g / 1000.0
    return emissions_kg


def main():
    print("Calculateur d'empreinte carbone — transport (g CO2e / t.km)")
    try:
        w_raw = input("Poids (kg) : ").strip()
        d_raw = input("Distance (km) : ").strip()
        weight_kg = float(w_raw.replace(',', '.'))
        distance_km = float(d_raw.replace(',', '.'))
    except ValueError:
        print("Entrée invalide. Veuillez entrer des nombres (ex : 15000 pour 15 t).")
        return

    use_default = input("Utiliser le facteur par défaut 86 g CO2e/t.km ? (O/n) : ").strip().lower()
    if use_default in ('n', 'no', 'non'):
        try:
            factor_raw = input("Entrez le facteur (g CO2e / t.km) : ").strip()
            factor = float(factor_raw.replace(',', '.'))
        except ValueError:
            print("Entrée invalide, utilisation du facteur par défaut (86 g/t.km).")
            factor = 86.0
    else:
        factor = 86.0

    emissions_kg = calculate_emissions(weight_kg, distance_km, factor)

    print(f"\nRésultat : {emissions_kg:.2f} kg CO2e")
    emissions_g = emissions_kg * 1000
    print(f"Formule : {factor} g/t.km × {weight_kg/1000:.3f} t × {distance_km} km = {emissions_g:.0f} g CO2e = {emissions_kg:.2f} kg CO2e")


if __name__ == '__main__':
    main()
