import tkinter as tk
from tkinter import ttk
import csv
import requests


# Vytvoření hlavního okna
screen = tk.Tk()
screen.title("Currency Converter")
screen.geometry("600x400")
screen.resizable(False, False)

# Nastavení sloupců tak, aby se rovnoměrně roztahovaly
screen.columnconfigure(0, weight=1)
screen.columnconfigure(1, weight=1)

converted_amount_label = None  

def submit():
    try:
        amount = float(amount_entry.get())  # Získání částky z Entry
        currency_from = currency_combobox_from.get()  # Získání měny z Combobox
        currency_to = currency_combobox_to.get()
        print(currency_from, currency_to, amount)

    except ValueError:
        amount_entry.delete(0, tk.END)
        error_message = tk.Label(screen, text="Enter a valid amount", font=("Arial", 20, "bold"), fg="red")
        error_message.grid(row=5, column=0, columnspan=2, pady=10)
        screen.after(1000, error_message.destroy)

    url = "https://www.cnb.cz/cs/financni-trhy/devizovy-trh/kurzy-devizoveho-trhu/kurzy-devizoveho-trhu/denni_kurz.txt?date=02.04.2025"
    response = requests.get(url)

    if response.status_code == 200:
        # Získání textových dat z odpovědi
        data = response.text

        # Zápis textu do souboru
        with open("currency_rate.txt", "w", encoding="utf-8") as file:
            file.write(data)

        print("Data byla úspěšně uložena do currency_rate.txt")
        calculate_conversion(amount, currency_from, currency_to)
    else:
        print(f"Chyba při stahování dat, status code: {response.status_code}")

def read_data():
    file_path = "currency_rate.txt"

    # Načtení dat z textového souboru
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    data = []
    for line in lines[2:]:
        # Předpokládám, že data jsou oddělena tabulátory nebo mezerami
        line = line.strip()
        if line:
            parts = line.split("|")  # Změňte podle formátu dat v souboru
            data.append({
                "země": parts[0],
                "měna": parts[1],
                "množství": parts[2],
                "kód": parts[3],
                "kurz": float(parts[4].replace(",", ".")) 
            })
    return data
    

def calculate_conversion(amount, currency_from, currency_to):
    global converted_amount_label
    currency_data = read_data()
    

    # Inicializace proměnných pro kurzy
    from_currency_rate = None
    to_currency_rate = None
    
    print(currency_from)
    print(currency_to)

    # Procházení dat a hledání příslušných kurzů
    for row in currency_data:
        if row["kód"] == currency_from:
            from_currency_rate = row["kurz"]
        elif row["kód"] == currency_to:
            to_currency_rate = row["kurz"]

    # Pokud nejsou nalezeny kurzy pro obě měny, vypíšeme chybu
    if from_currency_rate is None:
        from_currency_rate = "CZK"
    if to_currency_rate is None:
        to_currency_rate = "CZK"
    # Výpočet konverze
    if currency_to == currency_from:
        converted_amount = amount

    elif currency_from != "CZK" and currency_to != "CZK":
        # Pokud ani jedna měna není CZK, použijeme oba kurzy
        converted_amount = amount * from_currency_rate / to_currency_rate

    else:
        if currency_from == "CZK":
            # Pokud je zdrojová měna CZK
            converted_amount = amount / to_currency_rate
        else:
            # Pokud je cílová měna CZK
            converted_amount = amount * from_currency_rate

    if converted_amount_label is not None:
        converted_amount_label.destroy()
    # Zobrazení výsledku
    converted_amount_label = tk.Label(screen, text=f"{amount} {currency_from} = {converted_amount:.2f} {currency_to}", font=("Arial", 20))
    converted_amount_label.grid(row=5, column=0, columnspan=2, pady=10, padx=20)



# Nadpis
label = tk.Label(screen, text="Currency Converter", font=("Times New Roman", 40))
label.grid(row=0, column=0, columnspan=2, pady=20, sticky="ew")

# Seznam měn
currencies = []
for row in read_data():
    currencies.append(row["kód"])
currencies.append("CZK")

# Výběr zdrojové měny
currency_from_label = tk.Label(screen, text="From Currency:")
currency_from_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
selected_currency_from = tk.StringVar()
currency_combobox_from = ttk.Combobox(screen, textvariable=selected_currency_from, values=currencies, state="readonly")
currency_combobox_from.grid(row=1, column=1, padx=10, pady=10, sticky="w")
currency_combobox_from.current(0)  

# Výběr cílové měny
currency_to_label = tk.Label(screen, text="To Currency:")
currency_to_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
selected_currency_to = tk.StringVar()  
currency_combobox_to = ttk.Combobox(screen, textvariable=selected_currency_to, values=currencies, state="readonly")
currency_combobox_to.grid(row=2, column=1, padx=10, pady=10, sticky="w")
currency_combobox_to.current(0)  

# Pole pro zadání částky
amount_label = tk.Label(screen, text="Amount:")
amount_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
amount_entry = tk.Entry(screen)
amount_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

# Submit button
submit_btn = tk.Button(screen, text="Převést", command=submit, font=("Arial", 20, "bold"), padx=20, pady=10)
submit_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

# Spuštění hlavní smyčky Tkinteru
screen.mainloop()
