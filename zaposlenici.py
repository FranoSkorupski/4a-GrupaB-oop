
# Korak 1: Osnovna (roditeljska) klasa Zaposlenik
class Zaposlenik:
    def __init__(self, ime, prezime, placa):
        # Pohranjujemo osnovne podatke o zaposleniku
        self.ime = ime
        self.prezime = prezime
        self.placa = placa

    def prikazi_info(self):
        # Ispis osnovnih informacija o zaposleniku
        print(f"Ime i prezime: {self.ime} {self.prezime}, Plaća: {self.placa} EUR")


# Korak 2: Izvedena klasa Programer (nasljeđuje Zaposlenik)
class Programer(Zaposlenik):
    def __init__(self, ime, prezime, placa, programski_jezici):
        # Pozivamo konstruktor roditeljske klase da postavi ime, prezime i plaću
        super().__init__(ime, prezime, placa)
        # Dodajemo novi atribut specifičan za programere
        self.programski_jezici = programski_jezici

    def prikazi_info(self):
        # Pozivamo metodu iz roditeljske klase kako bi se ispisali osnovni podaci
        super().prikazi_info()
        # Ispis dodatnih informacija - programskih jezika
        print("Programski jezici:", ", ".join(self.programski_jezici))


# Korak 3: Izvedena klasa Menadzer (nasljeđuje Zaposlenik)
class Menadzer(Zaposlenik):
    def __init__(self, ime, prezime, placa, tim):
        # Pozivamo konstruktor roditeljske klase
        super().__init__(ime, prezime, placa)
        # Dodajemo novi atribut specifičan za menadžere - lista članova tima
        self.tim = tim

    def prikazi_info(self):
        # Ispis osnovnih informacija (iz roditeljske klase)
        super().prikazi_info()
        # Ispis članova tima
        print("Tim:", ", ".join(self.tim))

    # Bonus: metoda za dodavanje novog člana tima
    def dodaj_clana_tima(self, novi_clan):
        # Dodaje novog člana u listu tima
        self.tim.append(novi_clan)
        print(f"Član '{novi_clan}' je dodan u tim {self.ime} {self.prezime}.")


# Korak 4: Testiranje

# Kreiranje objekata
z1 = Zaposlenik("Ana", "Anić", 1200)
p1 = Programer("Petar", "Perić", 1800, ["Python", "JavaScript"])
m1 = Menadzer("Iva", "Ivić", 2500, ["Ana Anić", "Petar Perić"])

# Pozivanje metoda za prikaz informacija
print("Podaci o zaposleniku")
z1.prikazi_info()

print("\nPodaci o programeru")
p1.prikazi_info()

print("\nPodaci o menadžeru")
m1.prikazi_info()

# Testiranje bonus metode
print("\nDodavanje novog člana u tim")
m1.dodaj_clana_tima("Luka Lukić")
m1.prikazi_info()