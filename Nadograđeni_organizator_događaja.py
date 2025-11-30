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
        
        # pretvoriti datum u datetime objekt (ako je valjan)
        try:
            self._datum_obj = datetime.strptime(self.datum, "%d.%m.%Y")
        except Exception:
            self._datum_obj = None

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
        self.max_mjesta = int(max_mjesta)

    def slobodna_mjesta(self):
        return max(0, self.max_mjesta - len(self.prijave))

    def to_xml(self):
        elem = super().to_xml()
        ET.SubElement(elem, "max_mjesta").text = str(self.max_mjesta)
        return elem

    def __str__(self):
        return f"[Radionica] {self.naziv} ({self.datum}, {self.lokacija}) - slobodno: {self.slobodna_mjesta()}"


class Prijava:
    def __init__(self, ime):
        self.ime = ime

class EventManager:

    def __init__(self):
        self.dogadjaji: list[Dogadjaj] = []

    def dodaj_dogadjaj(self, dog: Dogadjaj):
        self.dogadjaji.append(dog)

    def obrisi_dogadjaj(self, event_id: int):
        self.dogadjaji = [d for d in self.dogadjaji if d.id != event_id]

    def spremi_xml(self, path: str):
        root = ET.Element("Dogadjaji")
        for d in self.dogadjaji:
            root.append(d.to_xml())
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def ucitaj_xml(self, path: str):
        tree = ET.parse(path)
        root = tree.getroot()
        self.dogadjaji = []
        for elem in root:
            dog = Dogadjaj.from_xml(elem)
            if dog:
                # ensure parsed date is set
                try:
                    dog._datum_obj = datetime.strptime(dog.datum, "%d.%m.%Y")
                except Exception:
                    dog._datum_obj = None
                self.dogadjaji.append(dog)

# ---------- Provjera unosa ----------

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

# ---------- GUI ----------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Planerko v1.0")
        self.geometry("900x600")
        self.configure(bg="#e6f2ff")

        self.manager = EventManager()
        self.sort_state = {}

        self.stvori_stil()
        self.stvori_meni()
        self.stvori_widgete()
        self.stvori_statusnu_traku()

    def stvori_stil(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("TButton", background="#0066cc", foreground="white", font=("Segoe UI", 10, "bold"))
        style.map("TButton", background=[("active", "#004d99")])
        style.configure("TLabel", background="#e6f2ff", font=("Segoe UI", 10))
        style.configure("Treeview", rowheight=22)

    def stvori_meni(self):
        menu_bar = tk.Menu(self)
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Spremi", command=self.spremi)
        file_menu.add_command(label="Učitaj", command=self.ucitaj)
        file_menu.add_separator()
        file_menu.add_command(label="Izlaz", command=self.quit)
        menu_bar.add_cascade(label="Datoteka", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="O aplikaciji", command=self.informacije_o_aplikaciji)
        menu_bar.add_cascade(label="Pomoć", menu=help_menu)

        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Izvještaj", command=self.show_report)
        menu_bar.add_cascade(label="Alati", menu=tools_menu)

        self.config(menu=menu_bar)

    def stvori_widgete(self):
        top_frame = tk.Frame(self, bg="#99ccff", bd=0)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        inner = ttk.Frame(top_frame)
        inner.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(inner, text="Naziv:").grid(row=0, column=0, sticky="e")
        self.entry_naziv = ttk.Entry(inner, width=35)
        self.entry_naziv.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(inner, text="Datum (DD.MM.YYYY):").grid(row=1, column=0, sticky="e")
        self.entry_datum = ttk.Entry(inner, width=35)
        self.entry_datum.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(inner, text="Lokacija:").grid(row=2, column=0, sticky="e")
        self.entry_lokacija = ttk.Entry(inner, width=35)
        self.entry_lokacija.grid(row=2, column=1, padx=5, pady=5)

        self.var_tip = tk.StringVar(value="Predavanje")
        ttk.Radiobutton(inner, text="Predavanje", variable=self.var_tip, value="Predavanje", command=self.on_tip_change).grid(row=0, column=2, padx=10)
        ttk.Radiobutton(inner, text="Radionica", variable=self.var_tip, value="Radionica", command=self.on_tip_change).grid(row=1, column=2)

        self.label_extra = ttk.Label(inner, text="Predavač / Max mjesta:")
        self.label_extra.grid(row=3, column=0, sticky="e")
        self.entry_extra = ttk.Entry(inner, width=35)
        self.entry_extra.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(inner, text="Dodaj događaj", command=self.dodaj_dogadjaj).grid(row=4, column=1, pady=10)

        search_frame = ttk.Frame(self)
        search_frame.pack(fill=tk.X, padx=12, pady=(0,6))
        ttk.Label(search_frame, text="Pretraži:").pack(side=tk.LEFT, padx=(0,6))
        self.search_var = tk.StringVar()
        ent_search = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        ent_search.pack(side=tk.LEFT)
        ent_search.bind("<KeyRelease>", lambda e: self.refresh_treeview())
        ttk.Button(search_frame, text="Očisti", command=self.clear_search).pack(side=tk.LEFT, padx=6)

        cols = ("tip", "naziv", "datum", "lokacija", "extra", "prijave")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", selectmode="browse", height=15)
        self.tree.heading("tip", text="Tip", command=lambda: self.sort_by("tip"))
        self.tree.heading("naziv", text="Naziv", command=lambda: self.sort_by("naziv"))
        self.tree.heading("datum", text="Datum", command=lambda: self.sort_by("datum"))
        self.tree.heading("lokacija", text="Lokacija", command=lambda: self.sort_by("lokacija"))
        self.tree.heading("extra", text="Predavač / Max mjesta", command=lambda: self.sort_by("extra"))
        self.tree.heading("prijave", text="Prijavljeni", command=lambda: self.sort_by("prijave"))

        self.tree.column("tip", width=90, anchor="w")
        self.tree.column("naziv", width=280, anchor="w")
        self.tree.column("datum", width=110, anchor="center")
        self.tree.column("lokacija", width=160, anchor="w")
        self.tree.column("extra", width=160, anchor="w")
        self.tree.column("prijave", width=80, anchor="center")

        self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)
        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.tree.tag_configure("puna", background="#ffd6d6")  # svjetlocrvena pozadina za popunjene

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill=tk.X, padx=12, pady=(0,10))
        ttk.Button(bottom_frame, text="Prijava na događaj", command=self.prijava_na_dogadjaj).pack(side=tk.LEFT)
        ttk.Button(bottom_frame, text="Obriši događaj", command=self.delete_selected_event).pack(side=tk.LEFT, padx=6)

    def on_tip_change(self):
        tip = self.var_tip.get()
        if tip == "Predavanje":
            self.label_extra.config(text="Predavač:")
            self.entry_extra.delete(0, tk.END)
        else:
            self.label_extra.config(text="Max mjesta:")
            self.entry_extra.delete(0, tk.END)

    def clear_search(self):
        self.search_var.set("")
        self.refresh_treeview()

    def stvori_statusnu_traku(self):
        self.status = tk.StringVar()
        self.status.set("Spreman")
        status_bar = tk.Label(self, textvariable=self.status, bg="#cce6ff", fg="#003366", bd=1, relief=tk.SUNKEN, anchor="w")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ---------- Provjera unosa ----------
    def validate_inputs(self, naziv, datum, lokacija, tip, extra):
        # naziv najmanje 3 slova
        if prebroji_slova(naziv) < 3:
            messagebox.showerror("Neispravan unos", "Naziv mora sadržavati najmanje 3 slova.")
            return False
        # datum format DD.MM.YYYY
        if not tocan_format_datuma(datum):
            messagebox.showerror("Neispravan unos", "Datum mora biti u obliku DD.MM.YYYY i biti valjan datum.")
            return False
        # lokacija najmanje 3 slova
        if prebroji_slova(lokacija) < 3:
            messagebox.showerror("Neispravan unos", "Lokacija mora sadržavati najmanje 3 slova.")
            return False
        # extra ovisno o tipu
        if tip == "Predavanje":
            if prebroji_slova(extra) < 3:
                messagebox.showerror("Neispravan unos", "Ime predavača mora sadržavati najmanje 3 slova.")
                return False
        else:  # Radionica -> extra mora biti isključivo broj
            if not re.fullmatch(r'\d+', extra):
                messagebox.showerror("Neispravan unos", "Max mjesta mora biti pozitivan cijeli broj.")
                return False
            if int(extra) <= 0:
                messagebox.showerror("Neispravan unos", "Max mjesta mora biti veće od 0.")
                return False
        return True

    # ---------- Dodavanje događaja ----------
    def dodaj_dogadjaj(self):
        try:
            naziv = self.entry_naziv.get().strip()
            datum = self.entry_datum.get().strip()
            lokacija = self.entry_lokacija.get().strip()
            tip = self.var_tip.get()
            extra = self.entry_extra.get().strip()

            if not self.validate_inputs(naziv, datum, lokacija, tip, extra):
                return

            if tip == "Predavanje":
                dog = Predavanje(naziv, datum, lokacija, extra)
            else:
                max_mj = int(extra)
                dog = Radionica(naziv, datum, lokacija, max_mj)

            self.manager.dodaj_dogadjaj(dog)
            # osvježi treeview (umjesto listbox)
            self.refresh_treeview()
            self.status.set(f"Dodan novi događaj: {naziv}")
        except ValueError as e:
            messagebox.showerror("Greška", str(e))

    # ---------- Treeview refresh / prikaz ----------
    def refresh_treeview(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        q = self.search_var.get().strip().lower()

        for d in self.manager.dogadjaji:

            if q:
                predv = getattr(d, "predavac", "") if isinstance(d, Predavanje) else ""
                if q not in d.naziv.lower() and q not in d.lokacija.lower() and q not in predv.lower():
                    continue

            tip = "Predavanje" if isinstance(d, Predavanje) else "Radionica"
            extra = getattr(d, "predavac", "") if isinstance(d, Predavanje) else str(getattr(d, "max_mjesta", ""))
            if isinstance(d, Predavanje):
                info = f"{d.broj_prijava()} prijavljeno"
            else:
                preostalo = d.slobodna_mjesta()
                info = f"{d.broj_prijava()}/{d.max_mjesta} prijavljeno (preostalo {preostalo})"
            tags = ()
            if isinstance(d, Radionica) and d.slobodna_mjesta() == 0:
                tags = ("puna",)
            iid = str(id(d))
            self.tree.insert("", "end", iid=iid, values=(tip, d.naziv, d.datum, d.lokacija, extra, info), tags=tags)


    # ---------- sortiranje ----------
    def sort_by(self, column):

        reverse = self.sort_state.get(column, False)
        def key_fn(d):
            if column == "tip":
                return 0 if isinstance(d, Predavanje) else 1
            if column == "naziv":
                return d.naziv.lower()
            if column == "datum":
                return getattr(d, "_datum_obj", datetime.min) or datetime.min
            if column == "lokacija":
                return d.lokacija.lower()
            if column == "extra":
                if isinstance(d, Predavanje):
                    return d.predavac.lower()
                else:
                    return str(d.max_mjesta)
            if column == "prijave":
                return d.broj_prijava()
            return d.naziv.lower()
        self.manager.dogadjaji.sort(key=key_fn, reverse=reverse)
        self.sort_state[column] = not reverse
        self.refresh_treeview()

    # ---------- prijava na događaj ----------
    def prijava_na_dogadjaj(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite događaj.")
            return
        iid = sel[0]
        # pronadi događaj po id-u
        target = None
        for d in self.manager.dogadjaji:
            if str(id(d)) == iid:
                target = d
                break
        if not target:
            messagebox.showerror("Greška", "Događaj nije pronađen.")
            return

        ime = simpledialog.askstring("Prijava", "Unesite ime sudionika (min 3 slova):")
        if ime is None:
            return
        ime = ime.strip()
        if prebroji_slova(ime) < 3:
            messagebox.showerror("Neispravan unos", "Ime sudionika mora sadržavati najmanje 3 slova.")
            return
        if isinstance(target, Radionica) and target.slobodna_mjesta() <= 0:
            messagebox.showinfo("Obavijest", "Radionica je popunjena!")
            return
        target.dodaj_prijavu(Prijava(ime))
        self.refresh_treeview()
        self.status.set(f"{ime} prijavljen na {target.naziv}")

    # ---------- brisanje događaja ----------
    def delete_selected_event(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Upozorenje", "Odaberite događaj za brisanje.")
            return
        iid = sel[0]

        for d in list(self.manager.dogadjaji):
            if str(id(d)) == iid:
                if not messagebox.askyesno("Potvrda", f"Jeste li sigurni da želite obrisati '{d.naziv}'?"):
                    return
                self.manager.dogadjaji.remove(d)
                self.refresh_treeview()
                self.status.set(f"Događaj {d.naziv} obrisan.")
                return

    # ---------- dvoklik za uredjivanje ----------
    def on_tree_double_click(self, event):
        item = self.tree.focus()
        if not item:
            return
        iid = item
        target = None
        for d in self.manager.dogadjaji:
            if str(id(d)) == iid:
                target = d
                break
        if not target:
            return
        self.open_edit_window(target)


    def open_edit_window(self, d):
        win = tk.Toplevel(self)
        win.title("Uredi događaj")
        win.geometry("520x420")

        frm = ttk.Frame(win, padding=10)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Naziv:").grid(row=0, column=0, sticky="e")
        e_n = ttk.Entry(frm, width=40); e_n.grid(row=0, column=1, pady=4); e_n.insert(0, d.naziv)

        ttk.Label(frm, text="Datum (DD.MM.YYYY):").grid(row=1, column=0, sticky="e")
        e_d = ttk.Entry(frm, width=20); e_d.grid(row=1, column=1, pady=4); e_d.insert(0, d.datum)

        ttk.Label(frm, text="Lokacija:").grid(row=2, column=0, sticky="e")
        e_l = ttk.Entry(frm, width=30); e_l.grid(row=2, column=1, pady=4); e_l.insert(0, d.lokacija)

        lbl_extra = ttk.Label(frm, text="Predavač / Max mjesta:")
        lbl_extra.grid(row=3, column=0, sticky="e")
        e_x = ttk.Entry(frm, width=30); e_x.grid(row=3, column=1, pady=4)
        e_x.insert(0, getattr(d, "predavac", str(getattr(d, "max_mjesta", ""))))

        ttk.Label(frm, text="Prijavljeni:").grid(row=4, column=0, sticky="ne", pady=(8,0))
        lb = tk.Listbox(frm, height=6)
        lb.grid(row=4, column=1, sticky="we", pady=(8,0))
        for p in d.prijave:
            lb.insert(tk.END, p.ime)

        def remove_participant():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Upozorenje", "Odaberite sudionika za uklanjanje.")
                return
            name = lb.get(sel[0])
            d.prijave = [p for p in d.prijave if p.ime != name]
            lb.delete(sel[0])
            self.refresh_treeview()
            self.status.set(f"Sudionik {name} uklonjen iz {d.naziv}")

        ttk.Button(frm, text="Ukloni sudionika", command=remove_participant).grid(row=5, column=1, sticky="w", pady=6)

        def save_changes():
            new_n = e_n.get().strip()
            new_d = e_d.get().strip()
            new_l = e_l.get().strip()
            new_x = e_x.get().strip()

            if prebroji_slova(new_n) < 3:
                messagebox.showerror("Greška", "Naziv mora imati najmanje 3 slova.")
                return
            if not tocan_format_datuma(new_d):
                messagebox.showerror("Greška", "Datum nije ispravan.")
                return
            if prebroji_slova(new_l) < 3:
                messagebox.showerror("Greška", "Lokacija mora imati najmanje 3 slova.")
                return
            if isinstance(d, Predavanje):
                if prebroji_slova(new_x) < 3:
                    messagebox.showerror("Greška", "Ime predavača mora imati najmanje 3 slova.")
                    return
                d.predavac = new_x
            elif isinstance(d, Radionica):
                if not re.fullmatch(r'\d+', new_x) or int(new_x) <= 0:
                    messagebox.showerror("Greška", "Max mjesta mora biti pozitivan cijeli broj.")
                    return
                d.max_mjesta = int(new_x)
            d.naziv = new_n
            d.datum = new_d
            try:
                d._datum_obj = datetime.strptime(new_d, "%d.%m.%Y")
            except Exception:
                d._datum_obj = None
            d.lokacija = new_l
            self.refresh_treeview()
            self.status.set(f"Događaj {d.naziv} ažuriran.")
            win.destroy()

        ttk.Button(frm, text="Spremi izmjene", command=save_changes).grid(row=6, column=1, pady=8, sticky="e")
        ttk.Button(frm, text="Obriši događaj", command=lambda: (self._delete_from_edit(d, win))).grid(row=6, column=0, pady=8, sticky="w")

    def _delete_from_edit(self, d: Dogadjaj, win: tk.Toplevel):
        if not messagebox.askyesno("Potvrda", f"Jeste li sigurni da želite obrisati '{d.naziv}'?"):
            return
        self.manager.obrisi_dogadjaj(d.id)
        self.refresh_treeview()
        self.status.set(f"Događaj {d.naziv} obrisan.")
        win.destroy()

    # ---------- Spremanje / učitavanje ----------
    def spremi(self):
        path = filedialog.asksaveasfilename(defaultextension=".xml", filetypes=[("XML files", "*.xml")], initialfile="events.xml")
        if not path:
            return
        try:
            self.manager.spremi_xml(path)
            self.status.set(f"Spremio: {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Neuspjelo spremanje: {e}")

    def ucitaj(self):
        path = filedialog.askopenfilename(filetypes=[("XML files", "*.xml")])
        if not path:
            return
        try:
            self.manager.ucitaj_xml(path)
            self.refresh_treeview()
            self.status.set(f"Učitano: {path}")
        except Exception as e:
            messagebox.showerror("Greška", f"Neuspjelo učitavanje: {e}")

    # ---------- Izvještaj ----------
    def show_report(self):
        total = len(self.manager.dogadjaji)
        upcoming = sum(1 for d in self.manager.dogadjaji if getattr(d, "_datum_obj", None) and d._datum_obj.date() >= datetime.now().date())
        most_popular = None
        maxp = -1
        for d in self.manager.dogadjaji:
            if d.broj_prijava() > maxp:
                maxp = d.broj_prijava()
                most_popular = d
        txt = f"Ukupno događaja: {total}\nBroj budućih događaja: {upcoming}\n"
        if most_popular:
            txt += f"Najpopularniji događaj: {most_popular.naziv} ({most_popular.broj_prijava()} prijava)\n"
        else:
            txt += "Najpopularniji događaj: -\n"
        win = tk.Toplevel(self)
        win.title("Izvještaj")
        ttk.Label(win, text=txt, padding=10, justify="left").pack()
        ttk.Button(win, text="Zatvori", command=win.destroy).pack(pady=6)
    
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
