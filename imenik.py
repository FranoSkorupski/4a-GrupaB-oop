import tkinter as tk
import csv

#Korak 1
class Kontakt:
    def __init__(self, ime, email, telefon):
        self.ime = ime
        self.email = email
        self.telefon = telefon

    def __str__(self):
        return f"{self.ime} {self.email} {self.telefon}"


#Koraci 2 i 3
class ImenikApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Jednostavni digitalni imenik")
        self.root.geometry("500x400")

        self.kontakti = []

        #Konfiguracija responzivnosti
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        #Gornji okvir (unos kontakta)
        unos_frame = tk.Frame(self.root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW")

        tk.Label(unos_frame, text="Ime:").grid(row=0, column=0, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, sticky="EW")

        tk.Label(unos_frame, text="Email:").grid(row=1, column=0, sticky="W")
        self.email_entry = tk.Entry(unos_frame)
        self.email_entry.grid(row=1, column=1, sticky="EW")

        tk.Label(unos_frame, text="Telefon:").grid(row=2, column=0, sticky="W")
        self.telefon_entry = tk.Entry(unos_frame)
        self.telefon_entry.grid(row=2, column=1, sticky="EW")

        unos_frame.columnconfigure(1, weight=1)

        #Gumbi
        tk.Button(unos_frame, text="Dodaj kontakt", command=self.dodaj_kontakt).grid(row=3, column=0, pady=10, sticky="EW")
        tk.Button(unos_frame, text="Obriši kontakt", command=self.obrisi_kontakt).grid(row=3, column=1, pady=10, sticky="EW")

        #Donji okvir (prikaz kontakata)
        prikaz_frame = tk.Frame(self.root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW")

        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)

        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")

        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

        #Donji gumbi (spremanje i učitavanje)
        donji_frame = tk.Frame(self.root, padx=10, pady=5)
        donji_frame.grid(row=2, column=0, sticky="EW")

        tk.Button(donji_frame, text="Spremi kontakte", command=self.spremi_u_csv).grid(row=0, column=0, padx=5)
        tk.Button(donji_frame, text="Učitaj kontakte", command=self.ucitaj_iz_csv).grid(row=0, column=1, padx=5)

        #Automatski učitaj kontakte pri pokretanju
        self.ucitaj_iz_csv()

    #Metode
    def dodaj_kontakt(self):
        ime = self.ime_entry.get().strip()
        email = self.email_entry.get().strip()
        telefon = self.telefon_entry.get().strip()

        #Provjera unosa
        
        if not (ime and email and telefon):
            print("Unesite sve podatke!")
            return

        if len(ime) <= 2:
            print("Ime mora imat barem 3 slova")
            return
        
        if "@" not in email:
            print("Email ne sadrzava potreban @ znak")
            return

        if ".com" not in email and ".skole.hr" not in email and ".hr" not in email:
            print("Email ne sardži potrebne znakove")
            return

        if not ((telefon.replace(" ","")).isdigit() and len(telefon.replace(" ","")) == 10):
            print("Broj mobitela mora sadržavati 10 znamenki")
            return
        
        kontakt = Kontakt(ime, email, telefon)
        self.kontakti.append(kontakt)
        self.osvjezi_prikaz()
        self.ocisti_unos()

    def obrisi_kontakt(self):
        odabrani = self.listbox.curselection()
        if not odabrani:
            print("Odaberite kontakt za brisanje.")
            return
        indeks = odabrani[0]
        self.kontakti.pop(indeks)
        self.osvjezi_prikaz()

    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for k in self.kontakti:
            self.listbox.insert(tk.END, str(k))

    def ocisti_unos(self):
        self.ime_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.telefon_entry.delete(0, tk.END)

    def spremi_u_csv(self):
        with open("kontakti.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for k in self.kontakti:
                writer.writerow([k.ime, k.email, k.telefon])
        print("Kontakti su spremljeni u CSV datoteku.")

    def ucitaj_iz_csv(self):
        try:
            with open("kontakti.csv", "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                self.kontakti = [Kontakt(ime, email, telefon) for ime, email, telefon in reader]
            print("Kontakti učitani iz CSV datoteke.")
        except FileNotFoundError:
            print("Datoteka ne postoji")
            self.kontakti = []
        self.osvjezi_prikaz()


#Pokretanje aplikacije
if __name__ == "__main__":
    root = tk.Tk()
    app = ImenikApp(root)
    root.mainloop()
