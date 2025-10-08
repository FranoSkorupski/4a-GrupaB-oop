class Ucenik:
    def __init__ (self, ime, prezime, razred):
        self.ime = ime
        self.prezime = prezime
        self.razred = razred

    def __str__(self):
        return f"{self.prezime} {self.ime} ({self.razred})"

import tkinter as tk

class EvidencijaApp:
    def __init__(self, root):

        self.ucenici = []
        self.odabrani_ucenik_index = None
        self.root = root
        # --- Struktura prozora ---
        self.root.title("Evidencija učenika")
        self.root.geometry("500x400")
        
        # --- Konfiguracija responzivnosti ---
        # Glavni prozor: daj "težinu" stupcu 0 i redu 1 (gdje je lista)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        
        # --- Okviri (Frames) za organizaciju ---
        # Okvir za formu (unos)
        unos_frame = tk.Frame(self.root, padx=10, pady=10)
        unos_frame.grid(row=0, column=0, sticky="EW") # Rasteže se horizontalno
        # Okvir za prikaz (lista)
        prikaz_frame = tk.Frame(self.root, padx=10, pady=10)
        prikaz_frame.grid(row=1, column=0, sticky="NSEW") # Rasteže se u svim smjerovima
        # Responzivnost unutar okvira za prikaz
        prikaz_frame.columnconfigure(0, weight=1)
        prikaz_frame.rowconfigure(0, weight=1)

        # --- Widgeti za unos ---
        # Ime
        tk.Label(unos_frame, text="Ime:").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.ime_entry = tk.Entry(unos_frame)
        self.ime_entry.grid(row=0, column=1, padx=5, pady=5, sticky="EW")
        # Prezime
        tk.Label(unos_frame, text="Prezime:").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.prezime_entry = tk.Entry(unos_frame)
        self.prezime_entry.grid(row=1, column=1, padx=5, pady=5, sticky="EW")
        # Razred
        tk.Label(unos_frame, text="Razred:").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.razred_entry = tk.Entry(unos_frame)
        self.razred_entry.grid(row=2, column=1, padx=5, pady=5, sticky="EW")
        # Gumbi
        self.dodaj_gumb = tk.Button(unos_frame, text="Dodaj učenika")
        self.dodaj_gumb.grid(row=3, column=0, padx=5, pady=10)
        self.spremi_gumb = tk.Button(unos_frame, text="Spremi izmjene")
        self.spremi_gumb.grid(row=3, column=1, padx=5, pady=10, sticky="W")


        
        # --- Widgeti za prikaz ---
        self.listbox = tk.Listbox(prikaz_frame)
        self.listbox.grid(row=0, column=0, sticky="NSEW")
        self.listbox.bind('<<ListboxSelect>>', self.artikl_odabran)
        # Scrollbar za listbox
        scrollbar = tk.Scrollbar(prikaz_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.listbox.config(yscrollcommand=scrollbar.set)

        tk.mainloop()
    
    def dodaj_ucenika(self):
        self.ime = self.ime_entry.get()
        self.prezime = self.prezime_entry.get()
        self.razred = self.razred_entry.get()

        if self.ime and self.prezime and self.razred:
            Ucenik = Ucenik(self.ime, self.prezime, self.razred)
            self.ucenici.append(Ucenik)

            self.entry.delete(0, 'end')
            osvjezi_prikaz()
            
    def osvjezi_prikaz(self):
        self.listbox.delete(0, tk.END)
        for ucenik in self.ucenici:
            self.listbox.insert(tk.END, ucenik)

    def odaberi_ucenika(self):
        odabrani_indeksi = self.listbox.curselection()
        if not odabrani_indeksi:
            return

        self.odabrani_ucenik_index = odabrani_indeksi[0]
        odabrani_ucenik = self.ucenici[self.odabrani_ucenik_index]

        self.ime_entry.delete(0,END)
        self.ime_entry.insert(0,odabrani_ucenik.ime)
        self.prezime_entry.delete(0,END)
        self.ime_entry.insert(0,odabrani_ucenik.prezime)
        self.razred_entry.delete(0,END)
        self.ime_entry.insert(0,odabrani_ucenik.razred)
        
    def spremi_izmjene(self):
        odabrani_indeksi = self.listbox.curselection()
        if not odabrani_indeksi:
            return

        self.odabrani_ucenik_index = odabrani_indeksi[0]
        odabrani_ucenik = self.ucenici[self.odabrani_ucenik_index]
        
        odabrani_ucenik.ime = self.ime_entry
        odabrani_ucenik.prezime = self.prezime_entry
        odabrani_ucenik.razred = self.razred_entry

        osvjezi_prikaz()
        
if __name__ == "__main__":
    root = tk.Tk()
    app = EvidencijaApp(root)
    root.mainloop()


        
