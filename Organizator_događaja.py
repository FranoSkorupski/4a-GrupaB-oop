import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from tkinter import ttk
import xml.etree.ElementTree as ET
from datetime import datetime
import re

# ---------- Klase ----------

class Dogadjaj:
    def __init__(self, naziv, datum, lokacija):
        self.naziv = naziv
        self.datum = datum
        self.lokacija = lokacija
        self.prijave = []

    def dodaj_prijavu(self, prijava):
        self.prijave.append(prijava)

    def broj_prijava(self):
        return len(self.prijave)

    def to_xml(self):
        elem = ET.Element(self.__class__.__name__)
        ET.SubElement(elem, "naziv").text = self.naziv
        ET.SubElement(elem, "datum").text = self.datum
        ET.SubElement(elem, "lokacija").text = self.lokacija
        prijave_elem = ET.SubElement(elem, "prijave")
        for p in self.prijave:
            prij_elem = ET.SubElement(prijave_elem, "Prijava")
            prij_elem.text = p.ime
        return elem

    @staticmethod
    def from_xml(elem):
        if elem.tag == "Predavanje":
            dog = Predavanje(elem.find("naziv").text,
                             elem.find("datum").text,
                             elem.find("lokacija").text,
                             elem.find("predavac").text)
        elif elem.tag == "Radionica":
            dog = Radionica(elem.find("naziv").text,
                            elem.find("datum").text,
                            elem.find("lokacija").text,
                            int(elem.find("max_mjesta").text))
        else:
            return None

        prijave_elem = elem.find("prijave")
        if prijave_elem is not None:
            for prij_elem in prijave_elem.findall("Prijava"):
                dog.dodaj_prijavu(Prijava(prij_elem.text))
        return dog


class Predavanje(Dogadjaj):
    def __init__(self, naziv, datum, lokacija, predavac):
        super().__init__(naziv, datum, lokacija)
        self.predavac = predavac

    def to_xml(self):
        elem = super().to_xml()
        ET.SubElement(elem, "predavac").text = self.predavac
        return elem

    def __str__(self):
        return f"[Predavanje] {self.naziv} - predavač: {self.predavac} ({self.datum}, {self.lokacija})"


class Radionica(Dogadjaj):
    def __init__(self, naziv, datum, lokacija, max_mjesta):
        super().__init__(naziv, datum, lokacija)
        self.max_mjesta = max_mjesta

    def slobodna_mjesta(self):
        return self.max_mjesta - len(self.prijave)

    def to_xml(self):
        elem = super().to_xml()
        ET.SubElement(elem, "max_mjesta").text = str(self.max_mjesta)
        return elem

    def __str__(self):
        return f"[Radionica] {self.naziv} ({self.datum}, {self.lokacija}) - slobodno: {self.slobodna_mjesta()}"


class Prijava:
    def __init__(self, ime):
        self.ime = ime


# ---------- GUI ----------

def prebroji_slova(s: str) -> int:
    # prebrojavanje Unicode slova u stringu
    return sum(1 for ch in s if ch.isalpha())

def tocan_format_datuma(s: str) -> bool:
    # provjera formata DD.MM.YYYY i jeli pravi datum
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', s):
        return False
    try:
        datetime.strptime(s, "%d.%m.%Y")
        return True
    except ValueError:
        return False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Planerko v1.0")
        self.geometry("750x520")
        self.configure(bg="#e6f2ff")

        self.dogadjaji = []

        self.postavi_stil()
        self.stvori_menu()
        self.stvori_widgete()
        self.stvori_statusnu_traku()

    # ---------- Stil ----------
    def postavi_stil(self):
        stil = ttk.Style(self)
        try:
            stil.theme_use("clam")
        except Exception:
            pass
        stil.configure("TFrame", background="#b7d7f8")
        stil.configure("TButton", background="#0066cc", foreground="white", font=("Segoe UI", 10, "bold"))
        stil.map("TButton", background=[("active", "#004d99")])
        stil.configure("TLabel", background="#b7d7f8", foreground="dark blue", font=("Segoe UI", 10, "bold"))
        stil.configure("TRadiobutton", background="#b7d7f8", foreground="dark blue", font=("Segoe UI", 10, "bold")) 

    # ---------- Menu ----------
    def stvori_menu(self):
        menu_traka = tk.Menu(self)
        datoteka_menu = tk.Menu(menu_traka, tearoff=0)
        datoteka_menu.add_command(label="Spremi", command=self.spremi_xml)
        datoteka_menu.add_command(label="Učitaj", command=self.ucitaj_xml)
        datoteka_menu.add_separator()
        datoteka_menu.add_command(label="Izlaz", command=self.quit)
        menu_traka.add_cascade(label="Datoteka", menu=datoteka_menu)

        informacije_menu = tk.Menu(menu_traka, tearoff=0)
        informacije_menu.add_command(label="O aplikaciji", command=self.informacije_o_aplikaciji)
        menu_traka.add_cascade(label="Informacije", menu=informacije_menu)

        self.config(menu=menu_traka)

    # ---------- Widgeti ----------
    def stvori_widgete(self):
        frame = ttk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        widgeti = tk.Frame(frame, bg="#b7d7f8")
        widgeti.place(relx=0.5, rely=0, anchor="n")

        ttk.Label(widgeti, text="Naziv:").grid(row=0, column=0, sticky="e")
        self.entry_naziv = ttk.Entry(widgeti, width=35)
        self.entry_naziv.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(widgeti, text="Datum (DD.MM.YYYY):").grid(row=1, column=0, sticky="e")
        self.entry_datum = ttk.Entry(widgeti, width=35)
        self.entry_datum.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(widgeti, text="Lokacija:").grid(row=2, column=0, sticky="e")
        self.entry_lokacija = ttk.Entry(widgeti, width=35)
        self.entry_lokacija.grid(row=2, column=1, padx=5, pady=5)

        self.tip_dogadjaja = tk.StringVar(value="Predavanje")
        ttk.Radiobutton(widgeti, text="Predavanje", variable=self.tip_dogadjaja, value="Predavanje", command=self.promjena_prema_tipu).grid(row=0, column=2, padx=10)
        ttk.Radiobutton(widgeti, text="Radionica", variable=self.tip_dogadjaja, value="Radionica", command=self.promjena_prema_tipu).grid(row=1, column=2)

        self.label_extra = ttk.Label(widgeti, text="Predavač:")
        self.label_extra.grid(row=3, column=0, sticky="e")
        self.entry_extra = ttk.Entry(widgeti, width=35)
        self.entry_extra.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(widgeti, text="Dodaj događaj", command=self.dodaj_dogadjaj).grid(row=4, column=1, pady=10)

        self.listbox = tk.Listbox(widgeti, width=90, height=15, bg="#f9fcff", fg="#003366", font=("Consolas", 10))
        self.listbox.grid(row=5, column=0, columnspan=3, pady=10)
        ttk.Button(widgeti, text="Prijava na događaj", command=self.prijava_na_dogadjaj).grid(row=6, column=1)

    def promjena_prema_tipu(self):
        tip = self.tip_dogadjaja.get()
        if tip == "Predavanje":
            self.label_extra.config(text="Predavač:")
            self.entry_extra.delete(0, tk.END)
        else:
            self.label_extra.config(text="Max mjesta:")
            self.entry_extra.delete(0, tk.END)

    # ---------- Statusna traka ----------
    def stvori_statusnu_traku(self):
        self.status = tk.StringVar()
        self.status.set("Program spreman za rad")
        status_bar = tk.Label(self, textvariable=self.status, bg="#cce6ff", fg="#003366", bd=1, relief=tk.SUNKEN, anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Provjera unosa ----------
    def Provjeri_unos(self, naziv, datum, lokacija, tip, extra):
        # naziv najmanje 3 slova
        if prebroji_slova(naziv) < 3:
            messagebox.showerror("Neispravan unos", "Naziv mora sadržavati najmanje 3 slova.")
            return False
        # datum formata DD.MM.YYYY
        if not tocan_format_datuma(datum):
            messagebox.showerror("Neispravan unos", "Datum mora biti u obliku DD.MM.YYYY i biti valjan datum.")
            return False
        # lokacija najmanje 3 slova
        if prebroji_slova(lokacija) < 3:
            messagebox.showerror("Neispravan unos", "Lokacija mora sadržavati najmanje 3 slova.")
            return False
        # varijabla extra ovisna o tipu događaja
        if tip == "Predavanje":
            if prebroji_slova(extra) < 3:
                messagebox.showerror("Neispravan unos", "Ime predavača mora sadržavati najmanje 3 slova.")
                return False
        else:  # ako je radionica, extra mora biti isključivo broj
            if not re.fullmatch(r'\d+', extra):
                messagebox.showerror("Neispravan unos", "Max mjesta mora biti pozitivan cijeli broj.")
                return False
            if int(extra) <= 0:
                messagebox.showerror("Neispravan unos", "Max mjesta mora biti veće od 0.")
                return False
        return True

    # ---------- Funkcionalnost ----------
    def dodaj_dogadjaj(self):
        try:
            naziv = self.entry_naziv.get().strip()
            datum = self.entry_datum.get().strip()
            lokacija = self.entry_lokacija.get().strip()
            tip = self.tip_dogadjaja.get()
            extra = self.entry_extra.get().strip()

            if not self.Provjeri_unos(naziv, datum, lokacija, tip, extra):
                return

            if tip == "Predavanje":
                dog = Predavanje(naziv, datum, lokacija, extra)
            else:
                max_mj = int(extra)
                dog = Radionica(naziv, datum, lokacija, max_mj)

            self.dogadjaji.append(dog)
            self.osvjezi_listbox()
            self.status.set(f"Dodan novi događaj: {naziv}")
        except Exception as e:
            messagebox.showerror("Greška", f"Pogreška prilikom dodavanja događaja: {e}")

    def osvjezi_listbox(self):
        self.listbox.delete(0, tk.END)
        for d in self.dogadjaji:
            tekst = str(d)
            if isinstance(d, Radionica) and d.slobodna_mjesta() == 0:
                tekst += " [POPUNJENO]"
            self.listbox.insert(tk.END, tekst)

    def prijava_na_dogadjaj(self):
        indeks = self.listbox.curselection()
        if not indeks:
            messagebox.showwarning("Upozorenje", "Odaberite događaj.")
            return
        dog = self.dogadjaji[indeks[0]]

        ime = simpledialog.askstring("Prijava", "Unesite ime sudionika:")
        if not ime:
            return
        ime = ime.strip()
        if prebroji_slova(ime) < 3:
            messagebox.showerror("Neispravan unos", "Ime sudionika mora sadržavati najmanje 3 slova.")
            return
        
        if isinstance(dog, Radionica) and dog.slobodna_mjesta() <= 0:
            messagebox.showinfo("Obavijest", "Radionica je popunjena!")
            return
        dog.dodaj_prijavu(Prijava(ime))
        self.osvjezi_listbox()
        self.status.set(f"{ime} prijavljen na događaj: {dog.naziv}")

    # ---------- Spremanje / učitavanje ----------
    def spremi_xml(self):
        path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML datoteke", "*.xml")])
        if not path:
            return
        root = ET.Element("Dogadjaji")
        for d in self.dogadjaji:
            root.append(d.to_xml())
        tree = ET.ElementTree(root)
        try:
            tree.write(path, encoding="utf-8", xml_declaration=True)
            self.status.set(f"Podaci spremljeni u {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Neuspjelo spremanje: {e}")

    def ucitaj_xml(self):
        path = filedialog.askopenfilename(filetypes=[("XML datoteke", "*.xml")])
        if not path:
            return
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            self.dogadjaji = []
            for elem in root:
                dog = Dogadjaj.from_xml(elem)
                if dog:
                    self.dogadjaji.append(dog)
            self.osvjezi_listbox()
            self.status.set(f"Podaci učitani iz {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Neuspjelo učitavanje: {e}")

    # ---------- Prozor o aplikaciji ----------
    def informacije_o_aplikaciji(self):
        info = tk.Toplevel(self)
        info.title("O aplikaciji")
        info.geometry("500x400")
        info.configure(bg="#003366")

        logo = r"""
 ██████╗ ██╗      █████╗ ███╗   ██╗███████╗██████╗ ██╗  ██╗ ██████╗ 
██╔══██╗██║     ██╔══██╗████╗  ██║██╔════╝██╔══██╗██║ ██╔╝██╔═══██╗
██████╔╝██║     ███████║██╔██╗ ██║█████╗  ██████╔╝█████╔╝ ██║   ██║
██╔═══╝ ██║     ██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗██╔═██╗ ██║   ██║
██║     ███████╗██║  ██║██║ ╚████║███████╗██║  ██║██║  ██╗╚██████╔╝
╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 

        """

        tk.Label(info, text=logo, font=("Consolas", 8), fg="#00ccff", bg="#003366", justify="center").pack(pady=10)
        tk.Label(info, text="Planerko", font=("Segoe UI", 14, "bold"), fg="white", bg="#003366").pack()
        tk.Label(info, text="Aplikacija za upravljanje događajima\nVerzija 1.0 (2025)", fg="#99ccff", bg="#003366",
                 font=("Segoe UI", 11)).pack(pady=5)
        tk.Label(info, text="Autor: Frano Skorupski", fg="#b3daff", bg="#003366", font=("Segoe UI", 10)).pack(pady=5)

        ttk.Button(info, text="Zatvori", command=info.destroy).pack(pady=15)


# ---------- Pokretanje ----------
if __name__ == "__main__":
    app = App()
    app.mainloop()
