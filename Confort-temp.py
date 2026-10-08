import csv
import math
import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class TableApp(ctk.CTkToplevel):
    def __init__(self, config_window, size):
        super().__init__(config_window)
        self.config_window = config_window
        self.title("Ajout des données")
        self.geometry("800x700")

        self.size = size
        self.entries = []
        self.history_window = None
        self.result_window = None

        self.create_table()
        self.create_bottom_section()

        # Rendre la fenêtre prioritaire et capturer la fermeture
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def create_table(self):
        top_label = ctk.CTkLabel(self, text="Données du bâtiment", font=("Arial", 20, "bold"))
        top_label.pack(pady=10)

        table_frame = ctk.CTkFrame(self)
        table_frame.pack(pady=10)

        labels = [
            "Température externe (°C)",
            "Température interne (°C)",
            "Isolement (0:bien 1:moyen 2:mal)",
            "Humidité (%)",
            "Occupation (0:non 1:oui)"
        ]

        for i, label_text in enumerate(labels):
            label = ctk.CTkLabel(table_frame, text=label_text, width=200)
            label.grid(row=i, column=0, padx=10, pady=5)

            entry = ctk.CTkEntry(table_frame, width=200)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries.append(entry)

    def create_bottom_section(self):
        bottom_frame = ctk.CTkFrame(self)
        bottom_frame.pack(pady=20)

        self.save_button = ctk.CTkButton(bottom_frame, text="Analyser", command=self.save_and_run)
        self.save_button.grid(row=0, column=0, padx=10, pady=5)

        self.view_button = ctk.CTkButton(bottom_frame, text="Résultat", command=self.view_result)
        self.view_button.grid(row=0, column=1, padx=10, pady=5)

        self.return_button = ctk.CTkButton(bottom_frame, text="Nouvelle analyse", command=self.return_to_config)
        self.return_button.grid(row=1, column=1, padx=10, pady=5)

        self.history_button = ctk.CTkButton(bottom_frame, text="Afficher historique", command=self.view_history)
        self.history_button.grid(row=1, column=0, padx=10, pady=5)

    def view_history(self):
        try:
            with open("historique.csv", "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                rows = list(reader)

            if not rows:
                messagebox.showinfo("Historique", "Aucune donnée trouvée.")
                return

            if self.history_window is None or not self.history_window.winfo_exists():
                self.history_window = ctk.CTkToplevel(self)
                self.history_window.title("Historique des analyses")
                self.history_window.geometry("700x500")

                for row in rows:
                    line = " | ".join(row)
                    label = ctk.CTkLabel(self.history_window, text=line, anchor="w", wraplength=680, justify="left")
                    label.pack(pady=2)

            self.history_window.lift()
            self.history_window.focus()

        except FileNotFoundError:
            messagebox.showerror("Erreur", "Le fichier historique.csv est introuvable.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

    def return_to_config(self):
        self.destroy()
        self.config_window.deiconify()

    def on_close(self):
        self.destroy()
        self.config_window.destroy()

    def save_and_run(self):
        data = [entry.get().strip() for entry in self.entries]

        if not all(data):
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs.")
            return

        try:
            T_ext = float(data[0])
            T_int = float(data[1])
            iso = data[2]
            hum = float(data[3])
            occ = data[4]
        except ValueError:
            messagebox.showerror("Erreur", "Températures et humidité doivent être numériques.")
            return

        formatted_lines = [
            f"Température externe : {T_ext} °C",
            f"Température interne : {T_int} °C",
            f"Isolement : {iso}",
            f"Humidité : {hum} %",
            f"Occupation : {'Oui' if occ == '1' else 'Non'}"
        ]

        if occ == "0":
            formatted_lines.append("Chauffage & ventilation: éteint")
            v = "Chauffage & ventilation: éteint"
            tp = "N/A"
        else:
            k_values = {"0": 0.05, "1": 0.1, "2": 0.2}
            k = k_values.get(iso, 0.1)
            T_confort = 20
            t_min = 5
            t_hr = t_min / 60

            if 19 <= T_int <= 23:
                formatted_lines.append("Température actuelle optimale.")
                tp = "ideale"
            else:
                T_initiale_calc = (T_confort - T_ext) / math.exp(-k * t_hr) + T_ext
                formatted_lines.append(
                    f"Pour atteindre {T_confort}°C après {t_min} minutes mettre la température à : {T_initiale_calc:.2f}°C"
                )
                tp = f"{T_initiale_calc:.2f}°C"

            if hum > 60:
                v = "Ventilation : activé"
            elif hum < 40:
                v = "Humidificateur : activé"
            else:
                v = "Humidité : idéale"

            formatted_lines.append(f"{v}")

        try:
            with open("RESULTAT.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(formatted_lines))

            summary_line = f"{v} | Température : {tp}"
            with open("historique.csv", "a", encoding="utf-8", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(data + [summary_line])

            messagebox.showinfo("Succès", "Analyse enregistrée avec succès.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")

    def view_result(self):
        try:
            with open("RESULTAT.txt", "r", encoding="utf-8") as file:
                lines = file.readlines()

            if self.result_window is None or not self.result_window.winfo_exists():
                self.result_window = ctk.CTkToplevel(self)
                self.result_window.title("Résultat")
                self.result_window.geometry("400x500")

                for line in lines:
                    label = ctk.CTkLabel(self.result_window, text=line.strip(), width=380, anchor="w")
                    label.pack(pady=5)

            self.result_window.lift()
            self.result_window.focus()

        except FileNotFoundError:
            messagebox.showerror("Erreur", "Le fichier RESULTAT.txt n'a pas été trouvé.")
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur s'est produite : {e}")


class ConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Accueil")
        self.geometry("400x250")

        self.submit_button = ctk.CTkButton(self, text="Commencer", command=self.create_table)
        self.submit_button.pack(pady=20)

    def create_table(self):
        self.withdraw()
        TableApp(self, 5)


if __name__ == "__main__":
    config_app = ConfigApp()
    config_app.mainloop()