import tkinter as tk

#Faza1
class Ucenik:
    def __init__(self, ime, prezime, razred):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self):
        return f"{self.prezime} {self.ime}, {self.razred}"


#Faza2
class EvidencijaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Evidencija učenika")
        self.root.geometry("500x400")

        self.ucenici = []
        self.odabrani_ucenik_index = None

        #Konfiguracija responzivnosti glavnog prozora
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        #Okviri
        unos_frame = tk.Frame(self.root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW")

        prikaz_frame = tk.Frame(self.root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW")

        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)

        #Entry polja i labeli
        tk.Label(unos_frame, text="Ime:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Prezime:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.prezime_entry = tk.Entry(unos_frame)
        self.prezime_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")

        tk.Label(unos_frame, text="Razred:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.razred_entry = tk.Entry(unos_frame)
        self.razred_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")

        #Gumbi
        self.dodaj_gumb = tk.Button(unos_frame, text="Dodaj učenika", command=self.dodaj_ucenika)
        self.dodaj_gumb.grid(row=3, column=0, padx=5, pady=10, sticky="EW")

        self.spremi_gumb = tk.Button(unos_frame, text="Spremi izmjene", command=self.spremi_izmjene)
        self.spremi_gumb.grid(row=3, column=1, padx=5, pady=10, sticky="EW")

        unos_frame.columnconfigure(1, weight=1)

        #Listbox i scrollbar
        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")
        self.listbox.bind('<<ListboxSelect>>', self.odaberi_ucenika)

        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

#Faza 3 - metode

    #Dodavanje učenika u listu
    def dodaj_ucenika(self):
        ime = self.ime_entry.get().strip()
        prezime = self.prezime_entry.get().strip()
        razred = self.razred_entry.get().strip()

        if not (ime and prezime and razred):
            print("Unesite sve podatke")
            return

        novi = Ucenik(ime, prezime, razred)
        self.ucenici.append(novi)
        self.osvjezi_prikaz()
        self.ocisti_unos()

    #Osvježavanje prikaza u listboxu
    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for ucenik in self.ucenici:
            self.listbox.insert(tk.END, str(ucenik))

    #Metoda koja se poziva kada je učenik odabran
    def odaberi_ucenika(self, event):
        odabrani_indeksi = self.listbox.curselection()
        if not odabrani_indeksi:
            return

        self.odabrani_ucenik_index = odabrani_indeksi[0]
        u = self.ucenici[self.odabrani_ucenik_index]

        self.ime_entry.delete(0, tk.END)
        self.ime_entry.insert(0, u.ime)
        self.prezime_entry.delete(0, tk.END)
        self.prezime_entry.insert(0, u.prezime)
        self.razred_entry.delete(0, tk.END)
        self.razred_entry.insert(0, u.razred)
        
    #Spremanje izmjena
    def spremi_izmjene(self):
        if self.odabrani_ucenik_index is None:
           print("Nije odabran učenik.")
           return

        u = self.ucenici[self.odabrani_ucenik_index]
        u.ime = self.ime_entry.get().strip()
        u.prezime = self.prezime_entry.get().strip()
        u.razred = self.razred_entry.get().strip()

        self.osvjezi_prikaz()
        self.ocisti_unos()
        self.odabrani_ucenik_index = None

    #Čišćenje entry polja
    def ocisti_unos(self):
        self.ime_entry.delete(0, tk.END)
        self.prezime_entry.delete(0, tk.END)
        self.razred_entry.delete(0, tk.END)

#Pokretanje prozora
if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()
