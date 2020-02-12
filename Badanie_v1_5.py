import Tkinter
from Tkinter import *
import math, random, threading, time, smbus, datetime
import sys
import RPi.GPIO as GPIO
import PID
import VL53L0X
#import gyro
import Queue
import Adafruit_ADS1x15
class StripChart:


    def __init__(self, root):
        global gf
        gf = self.makeGraph(root)
        self.cf = self.makeControls(root)
        gf.pack()
        self.cf.pack()
        
        #self.Reset()

    def makeGraph(self, frame):
        self.sw = 1015
        self.h = 400
        self.top = 2
        gf = Canvas(frame, width=self.sw, height=self.h+10,
                    bg="#002", bd=0, highlightthickness=0)
        return(gf)
    def makeControls(self, frame):
        cf = Frame(frame, borderwidth=2, relief="raised")
        Label(cf, text="Wyswietl wykres:", justify=RIGHT).grid(column=2, row=2, sticky=E)

        self.zmienna_wyswietl = IntVar()
        self.zmienna_wyswietl.set(1)
        Radiobutton(cf, text="x(t)", variable=self.zmienna_wyswietl, value=1, command=self.przelacznik_wyswietl).grid(column=4, row=2)
        Radiobutton(cf, text="V(t)", variable=self.zmienna_wyswietl, value=2, command=self.przelacznik_wyswietl).grid(column=6, row=2)
        Radiobutton(cf, text="alfa(t)", variable=self.zmienna_wyswietl, value=3, command=self.przelacznik_wyswietl).grid(column=8, row=2)
        Label(cf, text=" ").grid(column=6, row=4)

        Label(cf, text="Rejestracja pomiarow:", justify=RIGHT).grid(column=2, row=6, sticky=E)

        self.rejestracja = IntVar()
        Checkbutton(cf, text="      ", variable=self.rejestracja, command=self.rejestr).grid(column=4, row=6)
        
        self.zatrzymaj_uklad = Button(cf, fg="darkred", bg="tomato", text="ZATRZYMAJ UKLAD", command=self.zakoncz_rejestracje)
        self.zatrzymaj_uklad.grid(column=2, row=26, sticky=W)
        self.zatrzymaj_uklad.grid_remove()

        Label(cf, text=" ").grid(column=6, row=10)

        Label(cf, text="Wybor regulatora:", justify=RIGHT).grid(column=2, row=12, sticky=E)
       
        self.var = IntVar()
        self.var.set(1)
        Radiobutton(cf, text="PID", variable=self.var, value=1, command=self.przelacznik_radiobutton).grid(column=4, row=12)
        Radiobutton(cf, text="LQR", variable=self.var, value=2, command=self.przelacznik_radiobutton).grid(column=6, row=12)
        Label(cf, text=" ").grid(column=6, row=14)

        Label(cf, text="Parametry regulatora:").grid(column=6, row=16, sticky=W)

        self.label_p = Label(cf, text="P (Kp): ", justify=RIGHT)
        self.label_p.grid(column=4, row=18, sticky=E)
        
        self.pid_p = Entry(cf, bg="white")
        self.pid_p.insert(0, "4.5")
        self.pid_p.grid(column=6, row=18)

        self.label_i = Label(cf, text="I   (Ki): ", justify=RIGHT)
        self.label_i.grid(column=4, row=20, sticky=E)
        
        self.pid_i = Entry(cf, bg="white")
        self.pid_i.insert(0, "1.38")
        self.pid_i.grid(column=6, row=20)

        self.label_d = Label(cf, text="D (Kd): ", justify=RIGHT)
        self.label_d.grid(column=4, row=22, sticky=E)

        self.pid_d = Entry(cf, bg="white")
        self.pid_d.insert(0, "3.65")
        self.pid_d.grid(column=6, row=22)
        Label(cf, text=" ").grid(column=6, row=23)

        Label(cf, text="Pozycja docelowa kulki:", justify=RIGHT).grid(column=4, row=24)
        self.poz_docel = Entry(cf, bg="white")
        self.poz_docel.insert(0, "20.0")
        self.poz_docel.grid(column=6, row=24)
        Label(cf, text="                                    ").grid(column=8, row=25)

        self.start_ukladu = Button(cf, text="   START UKLADU   ", fg="darkgreen", bg="lime", command=self.ustaw_parametry)
        self.start_ukladu.grid(column=8, row=26, sticky=E)
        self.start_ukladu.grid_remove()
        self.poziomowanie = Button(cf, text="POZIOMUJ", fg="white", bg="darkgrey", command=self.poziomuj)
        self.poziomowanie.grid(column=4, row=26)
        self.wciaganie = Button(cf, text=" /\ ", repeatdelay=1, repeatinterval=1, fg="blue", bg="white", command=self.wciagaj)
        self.wciaganie.grid(column=6, row=26, sticky=W)
        self.opuszczanie = Button(cf, text=" \/ ", repeatdelay=1, repeatinterval=1, fg="blue", bg="white", command=self.opuszczaj)
        self.opuszczanie.grid(column=2, row=26, sticky=E)
        self.uwaga = Label(cf, text="Uwaga: Przed rozpoczeciem pracy nalezy ustawic pochylnie poziomo, nastepnie wcisnac przycisk POZIOMUJ")
        self.uwaga.grid(row=28, column=2, columnspan=8)
        return (cf)
    def wciagaj(self):
        GPIO.setmode(GPIO.BCM)
        pin1 = 17
        pin2 = 22
        pin3 = 23
        pin4 = 24
        czas = 0.001
        global kat_silnik
        GPIO.setup(pin1,GPIO.OUT)
        GPIO.setup(pin2,GPIO.OUT)
        GPIO.setup(pin3,GPIO.OUT)
        GPIO.setup(pin4,GPIO.OUT)
        
        GPIO.output(pin1, 1)
        GPIO.output(pin3, 1)
        GPIO.output(pin2, 0)       
        GPIO.output(pin4, 0)
        time.sleep(czas)

        GPIO.output(pin3, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin2, 0)
        GPIO.output(pin4, 0)
        time.sleep(czas)

        GPIO.output(pin2, 1)
        GPIO.output(pin3, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin4, 0)
        time.sleep(czas)

        GPIO.output(pin2, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin3, 0)
        GPIO.output(pin4, 0)
        time.sleep(czas)

        GPIO.output(pin2, 1)
        GPIO.output(pin4, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin3, 0)
        time.sleep(czas)

        GPIO.output(pin4, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin2, 0)
        GPIO.output(pin3, 0)
        time.sleep(czas)

        GPIO.output(pin1, 1)
        GPIO.output(pin4, 1)
        GPIO.output(pin2, 0)
        GPIO.output(pin3, 0)
        time.sleep(czas)

        GPIO.output(pin1, 1)
        GPIO.output(pin2, 0)
        GPIO.output(pin3, 0)
        GPIO.output(pin4, 0)
        try:
            kat_silnik = kat_silnik + 8
        except:
            kat_silnik = 0
        print kat_silnik
        GPIO.cleanup()
    def opuszczaj(self):
        GPIO.setmode(GPIO.BCM)
        pin1 = 17
        pin2 = 22
        pin3 = 23
        pin4 = 24
        czas = 0.001
        global kat_silnik
        GPIO.setup(pin1,GPIO.OUT)
        GPIO.setup(pin2,GPIO.OUT)
        GPIO.setup(pin3,GPIO.OUT)
        GPIO.setup(pin4,GPIO.OUT)

        GPIO.output(pin1, 1)
        GPIO.output(pin2, 0)
        GPIO.output(pin3, 0)
        GPIO.output(pin4, 0)    

        GPIO.output(pin1, 1)
        GPIO.output(pin4, 1)
        GPIO.output(pin2, 0)
        GPIO.output(pin3, 0)    
        time.sleep(czas)

        GPIO.output(pin4, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin2, 0)
        GPIO.output(pin3, 0)    
        time.sleep(czas)

        GPIO.output(pin2, 1)
        GPIO.output(pin4, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin3, 0)    
        time.sleep(czas)

        GPIO.output(pin2, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin3, 0)
        GPIO.output(pin4, 0)    
        time.sleep(czas)

        GPIO.output(pin2, 1)
        GPIO.output(pin3, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin4, 0)    
        time.sleep(czas)

        GPIO.output(pin3, 1)
        GPIO.output(pin1, 0)
        GPIO.output(pin2, 0)
        GPIO.output(pin4, 0)    
        time.sleep(czas)
        
        GPIO.output(pin1, 1)
        GPIO.output(pin3, 1)
        GPIO.output(pin2, 0)       
        GPIO.output(pin4, 0)    
        time.sleep(czas)
        try:
            kat_silnik = kat_silnik - 8
        except:
            kat_silnik = 0
        print kat_silnik
        GPIO.cleanup()

    def poziomuj(self):
        self.start_ukladu.grid()
        global kat_silnik
        kat_silnik = 0
        ##ZAPISYWANIE DO PLIKU
    def rejestr(self):
        global rejestracja
        rejestracja = self.rejestracja.get()
        if rejestracja == 1:
            
            print "reje=", rejestracja
            global data
            data = time.strftime("pomiary/%H_%M_%S___%d_%m.txt")

            try:
                plik = open(data, 'a')
                plik.write("Badanie regulatora PID \n")
                plik.write("t(s) x(cm) V(cm/s) alfa(*) wyjscie_PID(*) \n")
                plik.close()
            except:
                pass
            
    def przelacznik_wyswietl(self):
        global wyswietl
        wyswietl = self.zmienna_wyswietl.get()
        
        print "abcs"
        if wyswietl == 1:
            gf.delete("all")
    
            y = 7
            while y < 70:
                linie_poziome = y * 6
                linie_poziome = linie_poziome - 420
                linie_poziome = -linie_poziome
                gf.create_line(0, linie_poziome, 960, linie_poziome,
                               fill="dimgray", width=1)
                y = y + 1
            x = 0
            while x <= 950:
                gf.create_line(x, 0, x, 390, fill="mediumblue", width=1)
                x = x + 10
    
            y=0
            while y < 70:
                linie_poziome = y * 6
                linie_poziome = linie_poziome - 420
                linie_poziome = -linie_poziome
                gf.create_line(0, linie_poziome, 960, linie_poziome,
                               fill="white", width=1)
                gf.create_text(980, linie_poziome,
                               text=(y, "cm"), fill="yellow")
                y = y + 10

            x = 50
            while x <= 950:
                gf.create_line(x, 0, x, 390, fill="cyan", width=1)
                sekundy = x/10
                gf.create_text(x, 400, text=(sekundy, "s"),
                               fill="yellow", tags="sekundy")
                x = x + 50
##            print self.wartosc4
##            poz_docel_wykres = self.wartosc4 * 6
##            poz_docel_wykres = poz_docel_wykres - 420
##            poz_docel_wykres = -poz_docel_wykres
##            gf.create_line(0, poz_docel_wykres, 960, poz_docel_wykres,
##                           fill="green", width=3, tags="linia_poz_docel")
        if wyswietl == 2:
            gf.delete("all")
            y = 5
            while y < 70:
                linie_poziome = y * 12
                linie_poziome = linie_poziome - 420
                linie_poziome = -linie_poziome
                gf.create_line(0, linie_poziome, 960, linie_poziome,
                               fill="dimgray", width=1)
                y = y + 1
            x = 0
            while x <= 950:
                gf.create_line(x, 0, x, 390, fill="mediumblue", width=1)
                x = x + 10
            x = 50
            y = 0
            while y < 70:
                linie_poziome = y * 6
                linie_poziome = linie_poziome - 420
                linie_poziome = -linie_poziome
                gf.create_line(0, linie_poziome, 960, linie_poziome,
                               fill="white", width=1)
                gf.create_text(985, linie_poziome,
                               text=(y/2-5, "cm/s"), fill="yellow")
                y = y + 10
            
            while x <= 950:
                gf.create_line(x, 0, x, 390, fill="cyan", width=1)
                sekundy = x/10
                gf.create_text(x, 400, text=(sekundy, "s"),
                               fill="yellow", tags="sekundy")
                x = x + 50
        if wyswietl == 3:
            gf.delete("all")
            y = 3
            while y < 70:
                linie_poziome = y * 12
                linie_poziome = linie_poziome - 420
                linie_poziome = -linie_poziome
                gf.create_line(0, linie_poziome, 960, linie_poziome,
                               fill="dimgray", width=1)
                y = y + 1
            x = 0
            while x <= 950:
                gf.create_line(x, 0, x, 390, fill="mediumblue", width=1)
                x = x + 10
            x = 50
            y = 0
            while y < 70:
                linie_poziome = y * 6
                linie_poziome = linie_poziome - 420
                linie_poziome = -linie_poziome
                gf.create_line(0, linie_poziome, 960, linie_poziome,
                               fill="white", width=1)
                gf.create_text(980, linie_poziome,
                               text=(y/10-4, "*"), fill="yellow")
                y = y + 10
            
            while x <= 950:
                gf.create_line(x, 0, x, 390, fill="cyan", width=1)
                sekundy = x/10
                gf.create_text(x, 400, text=(sekundy, "s"),
                               fill="yellow", tags="sekundy")
                x = x + 50

    def rozpocznij_rejestracje(self):
        self.y = 1
        for t in threading.enumerate():
            if t.name == "_abc_":
                print("already running")
                return
        threading.Thread(target=self.silnik_krokowy, name="_abc_").start()

    def zakoncz_rejestracje(self):
        kolejka_zadan_obliczeniaPID.queue.clear()
        kolejka_zadan_obliczeniaPID.put(None)
        kolejka_zadan_obliczeniaPID.put(None)
        kolejka_zadan_obliczeniaPID.put(None)
        kolejka_zadan_obliczeniaPID.put(None)
        print "KONIEC 3"
        self.start_ukladu.config(text="   START UKLADU   ", fg="darkgreen", bg="lime")
        self.zatrzymaj_uklad.grid_remove()
        self.poziomowanie.grid()
        self.wciaganie.grid()
        self.opuszczanie.grid()
        self.uwaga.config(text="Mozna teraz bezpiecznie zamknac program")
        tof.stop_ranging()
    def Run(self):
        self.go = 1
        for t in threading.enumerate():
            if t.name == "_gen_":
                print("already running")
                return
        threading.Thread(target=self.do_start, name="_gen_").start()

##    def Stop(self):
##        self.go = 0
##        for t in threading.enumerate():
##            if t.name == "_gen_":
##                t.join()
##        
##
##    def Reset(self):
##        self.Stop()
##        self.clearstrip(self.gf.p, '#345')

    def przelacznik_radiobutton(self):
        self.pid_p.delete(0, END)
        self.pid_i.delete(0, END)
        self.pid_d.delete(0, END)

        self.pid_p.config(bg="white", fg="black")
        self.pid_i.config(bg="white", fg="black")
        self.pid_d.config(bg="white", fg="black")

        self.wartosc = self.var.get()
        
        if self.wartosc == 1:
            self.label_p.config(text="P:")
            self.label_i.config(text="I :")
            self.label_d.config(text="D:")
        else:
            self.label_p.config(text="K1:")
            self.label_i.config(text="K2:")
            self.label_d.config(text="K3:")

    def ustaw_parametry(self):
        self.poziomowanie.grid_remove()
        self.wciaganie.grid_remove()
        self.opuszczanie.grid_remove()
        self.uwaga.config(text="Uwaga: Przed zamknieciem okna programu nalezy ZATRZYMAC UKLAD")
        self.zatrzymaj_uklad.grid()
        self.start_ukladu.config(text="ZMIEN PARAMETRY", fg="darkblue", bg="yellow")
        global rejestracja
        rejestracja = self.rejestracja.get()
        global kat_silnik

        try:
            wartosc1 = float(self.pid_p.get())
            self.pid_p.config(bg="white", fg="black")
            sprawdz1 = 1
        except ValueError:
            sprawdz1 = 0
            self.pid_p.delete(0, END)
            self.pid_p.insert(0, "BLEDNA WARTOSC")
            self.pid_p.config(bg="red", fg="yellow")
        try: 
            wartosc2 = float(self.pid_i.get())
            self.pid_i.config(bg="white", fg="black")
            sprawdz2 = 1
        except ValueError:
            sprawdz2 = 0
            self.pid_i.delete(0, END)
            self.pid_i.insert(0, "BLEDNA WARTOSC")
            self.pid_i.config(bg="red", fg="yellow")
        try:
            wartosc3 = float(self.pid_d.get())
            self.pid_d.config(bg="white", fg="black")
            sprawdz3 = 1
        except ValueError:
            sprawdz3 = 0
            self.pid_d.delete(0, END)
            self.pid_d.insert(0, "BLEDNA WARTOSC")
            self.pid_d.config(bg="red", fg="yellow")
        try:
            wartosc4 = float(self.poz_docel.get())
            self.poz_docel.config(bg="white", fg="black")
            sprawdz4 = 1
        except ValueError:
            sprawdz4 = 0
            self.poz_docel.delete(0, END)
            self.poz_docel.insert(0, "BLEDNA WARTOSC")
            self.poz_docel.config(bg="red", fg="yellow")


        
##
        if (sprawdz1 == 1 and sprawdz2 == 1 and sprawdz3 == 1 and sprawdz4 == 1):        
            z = 0
###ZAPISYWANIE DO PLIKU
            if rejestracja == 1:
                plik = open(data, 'a')
                self.wartosc1_string = str(wartosc1)
                self.wartosc2_string = str(wartosc2)
                self.wartosc3_string = str(wartosc3)
                self.wartosc4_string = str(wartosc4)
                plik.write("Badanie regulatora PID \n")
                plik.write("P=")
                plik.write(self.wartosc1_string)
                plik.write(" I=")
                plik.write(self.wartosc2_string)
                plik.write(" D=")
                plik.write(self.wartosc3_string)
                plik.write(" pozycja_docelowa=")
                plik.write(self.wartosc4_string)
                plik.write("\n \n")
                plik.write("t(s) x(cm) V(cm/s) alfa(*) wyjscie_PID(*) \n")
                plik.close()


                
        #jesli watek obliczenia PID juz jest utworzony - dodaj nowe parametry do kolejki
            for t in threading.enumerate():
                if t.name == "_WatekObliczeniaPID_":
                    z = z + 1
                    print "juz dziala"
                    kolejka_zadan_obliczeniaPID.queue.clear()
                    kolejka_zadan_obliczeniaPID.put(wartosc1)
                    kolejka_zadan_obliczeniaPID.put(wartosc2)
                    kolejka_zadan_obliczeniaPID.put(wartosc3)
                    kolejka_zadan_obliczeniaPID.put(wartosc4)
                    print kolejka_zadan_obliczeniaPID

        #deklaracja kolejki zadan PID, wrzucanie parametrow do kolejki
        #wystartowanie nowego watki obliczenia PID
            if z == 0:
                global tof
                tof = VL53L0X.VL53L0X()
                tof.start_ranging(VL53L0X.VL53L0X_LONG_RANGE_MODE)
                global kolejka_zadan_obliczeniaPID
                kolejka_zadan_obliczeniaPID = Queue.Queue(maxsize=4)
                kolejka_zadan_obliczeniaPID.queue.clear()
                kolejka_zadan_obliczeniaPID.put(wartosc1)
                kolejka_zadan_obliczeniaPID.put(wartosc2)
                kolejka_zadan_obliczeniaPID.put(wartosc3)
                kolejka_zadan_obliczeniaPID.put(wartosc4)
                watek1 = WatekObliczeniaPID(kolejka_zadan_obliczeniaPID)
                watek1.start()
                print "startuje"

                self.wartosc4 = wartosc4
                self.przelacznik_wyswietl()
                              
        else:
            okienko = Toplevel()
            okienko.title("BLAD")
            wiadomosc = Label(okienko, height=8, width=45, text="Prosze poprawic BLEDNE WARTOSCI")
            wiadomosc.pack()
            przycisk = Button(okienko, text="OK", command=okienko.destroy)
            przycisk.pack()
        
    def do_start(self):

        tx = time.time()
        poprzedni_czas = 0
        poprzednia_odleglosc = 0
        while self.go:
            self.odczyt_pozycji()
            odleglosc = round(self.distance, 0)
            tx2 = time.time()
            czas = tx2 - tx
            czas = czas * 10
            gf.create_line(poprzedni_czas, poprzednia_odleglosc, czas, odleglosc, fill="yellow")
            poprzedni_czas = czas
            poprzednia_odleglosc = odleglosc
            time.sleep(0.1)

    def clearstrip(self, p, color):  # Fill strip with background color
        self.bg = color              # save background color for scroll
        self.data = None             # clear previous data
        self.x = 0
        p.tk.call(p, 'put', color, '-to', 0, 0, p['width'], p['height'])

    def scrollstrip(self, p, data, colors, bar=""):   # Scroll the strip, add new data
        self.x = (self.x + 1) % self.sw               # x = double buffer position
        bg = bar if bar else self.bg
        p.tk.call(p, 'put', bg, '-to', self.x, 0,
                  self.x+1, self.h)
        p.tk.call(p, 'put', bg, '-to', self.x+self.sw, 0,
                  self.x+self.sw+1, self.h)
        self.gf.coords(self.item, -1-self.x, self.top)  # scroll to just-written column
        if not self.data:
            self.data = data
        for d in range(len(data)):
            y0 = int((self.h-1) * (1.0-self.data[d]))   # plot all the data points
            y1 = int((self.h-1) * (1.0-data[d]))
            ya, yb = sorted((y0, y1))
            for y in range(ya, yb+1):                   # connect the dots
                p.put(colors[d], (self.x,y))
                p.put(colors[d], (self.x+self.sw,y))
        self.data = data            # save for next call
 
class WatekSilnik(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, name="_WatekSilnik_")
        #self.kolejka_zadan = kolejka_zadan
    def run(self):
        self.it = 1
        self.d = 0
        GPIO.setmode(GPIO.BCM)
        pin1 = 17
        pin2 = 22
        pin3 = 23
        pin4 = 24
        czas = 0.002

        GPIO.setup(pin1,GPIO.OUT)
        GPIO.setup(pin2,GPIO.OUT)
        GPIO.setup(pin3,GPIO.OUT)
        GPIO.setup(pin4,GPIO.OUT)
        self.it = 1
        global wyjsciePID
        wyjsciePID = 0
        x=0
        global kat_silnik
        print"silnik"
        while True:           
##          if self.kolejka_zadan.full():
##                self.d = self.kolejka_zadan.get()
##
##            if self.d is None:
##                print "KONIEC 2"
##                # Nie ma nic wiecej do przetwarzania, wiec konczymy
##                break

##            if self.d == 0:
##                GPIO.output(pin1, 0)
##                GPIO.output(pin3, 0)
##                GPIO.output(pin2, 0)       
##                GPIO.output(pin4, 0)
##                time.sleep(czas)

            if self.it == 1:
                GPIO.output(pin1, 1)
                GPIO.output(pin3, 1)
                GPIO.output(pin2, 0)       
                GPIO.output(pin4, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 2:
                GPIO.output(pin3, 1)
                GPIO.output(pin1, 0)
                GPIO.output(pin2, 0)
                GPIO.output(pin4, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 3:
                GPIO.output(pin2, 1)
                GPIO.output(pin3, 1)
                GPIO.output(pin1, 0)
                GPIO.output(pin4, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 4:
                GPIO.output(pin2, 1)
                GPIO.output(pin1, 0)
                GPIO.output(pin3, 0)
                GPIO.output(pin4, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 5:
                GPIO.output(pin2, 1)
                GPIO.output(pin4, 1)
                GPIO.output(pin1, 0)
                GPIO.output(pin3, 0)  
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 6:
                GPIO.output(pin4, 1)
                GPIO.output(pin1, 0)
                GPIO.output(pin2, 0)
                GPIO.output(pin3, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 7:
                GPIO.output(pin1, 1)
                GPIO.output(pin4, 1)
                GPIO.output(pin2, 0)
                GPIO.output(pin3, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
            if self.it == 8:
                GPIO.output(pin1, 1)
                GPIO.output(pin2, 0)
                GPIO.output(pin3, 0)
                GPIO.output(pin4, 0)
                if wyjsciePID > kat_silnik:
                    self.it = self.it + 1
                    #x=x+1
                    kat_silnik = kat_silnik + 1
                if wyjsciePID < kat_silnik:
                    self.it = self.it - 1
                    #x=x+1
                    kat_silnik = kat_silnik - 1
                if wyjsciePID == kat_silnik:
                    GPIO.output(pin1, 0)
                    GPIO.output(pin3, 0)
                    GPIO.output(pin2, 0)       
                    GPIO.output(pin4, 0)
                if wyjsciePID is None:
                    break
                time.sleep(czas)
                
            if self.it > 8:
                self.it = 1
            if self.it < 1:
                self.it = 8
        print "KONIEC 2"

class WatekObliczeniaPID(threading.Thread):
    def __init__(self, kolejka_zadan_obliczeniaPID):
        threading.Thread.__init__(self, name="_WatekObliczeniaPID_")
        self.kolejka_zadan_obliczeniaPID = kolejka_zadan_obliczeniaPID

#!
        # GPIO for Sensor 1 shutdown pin
        sensor1_shutdown = 16
        # GPIO for Sensor 2 shutdown pin
        sensor2_shutdown = 12

        GPIO.setwarnings(False)

        # Setup GPIO for shutdown pins on each VL53L0X
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(sensor1_shutdown, GPIO.OUT)
        GPIO.setup(sensor2_shutdown, GPIO.OUT)

        # Set all shutdown pins low to turn off each VL53L0X
        GPIO.output(sensor1_shutdown, GPIO.LOW)
        GPIO.output(sensor2_shutdown, GPIO.LOW)

        # Keep all low for 500 ms or so to make sure they reset
        time.sleep(0.50)

        # Create one object per VL53L0X passing the address to give to
        # each.
        global tof
        global tof1
        tof = VL53L0X.VL53L0X(address=0x2B)
        tof1 = VL53L0X.VL53L0X(address=0x2D)

        # Set shutdown pin high for the first VL53L0X then 
        # call to start ranging 
        GPIO.output(sensor1_shutdown, GPIO.HIGH)
        time.sleep(0.50)
        tof.start_ranging(VL53L0X.VL53L0X_LONG_RANGE_MODE)

        # Set shutdown pin high for the second VL53L0X then 
        # call to start ranging 
        GPIO.output(sensor2_shutdown, GPIO.HIGH)
        time.sleep(0.50)
        tof1.start_ranging(VL53L0X.VL53L0X_LONG_RANGE_MODE)
        global timing
        timing = tof.get_timing()
        if (timing < 20000):
            timing = 20000
        #print ("Timing %d ms" % (timing/1000))
#!  



    def run(self):
        self.distance = -10
        #kolejka_zadan = Queue.Queue(maxsize=1)
        g = 0
        pid_x = 0

        for t in threading.enumerate():
            if t.name == "_WatekSilnik_":
                g = g + 1

        if g == 0:
            watek2 = WatekSilnik()
            watek2.start()

        d = 0
        self.poprzedni_blad = 0
        self.poprzedni_czas = time.time()
        self.czas_po_pomiarach = 0
        czas_probkowania = 0.1
        czas = 0
        tx0 = time.time()
        poprzedni_czas = 0
        poprzednia_odleglosc = 0
        poprzednia_predkosc = 0
        przedzial_sekund = 0
        poprzednie_stopnie = 0
        poprzedni_out = 0
        rysowanie = 0
        czas_zero = time.time()
        poprzedni_czas_do_obliczen = 0
        poprzednia_zielona_linia = 0
        
        while True:
            if self.kolejka_zadan_obliczeniaPID.full():
                wartosc1 = self.kolejka_zadan_obliczeniaPID.get()
                wartosc2 = self.kolejka_zadan_obliczeniaPID.get()
                wartosc3 = self.kolejka_zadan_obliczeniaPID.get()
                wartosc4 = self.kolejka_zadan_obliczeniaPID.get()
                gf.create_line(poprzedni_czas, 0,
                                   poprzedni_czas, 390, fill="red", width=1,
                                   tags="wykres")

            if wartosc1 is None:
                global wyjsciePID
                wyjsciePID = None
                time.sleep(1)
                GPIO.cleanup()
                
                
                # Nie ma nic wiecej do przetwarzania, wiec konczymy
                break  
            if self.distance == -10:
                self.distance = wartosc4
            self.odczyt_pozycji()
            czas = time.time() - self.poprzedni_czas
            while czas_probkowania > czas:
                self.odczyt_pozycji()
                czas = time.time() - self.poprzedni_czas
            
            self.do_PID(wartosc1, wartosc2, wartosc3, pozycja_docel = wartosc4,
                        pomiar_odleglosci = self.distance,
                        poprzedni_blad = self.poprzedni_blad,
                        poprzedni_czas = self.poprzedni_czas)
##################
            if self.output > 1200:
                self.output = 1200
            if self.output < -1200:
                self.output = -1200
#######################
            global wyjsciePID
            wyjsciePID = self.output
            GPIO.setmode(GPIO.BCM)
            pin1 = 20
            pin2 = 21
            GPIO.setup(pin1,GPIO.OUT)
            GPIO.setup(pin2,GPIO.OUT)
            if self.blad < 3 and self.blad > -3:
                GPIO.output(pin1, 0)
                GPIO.output(pin2, 0)
            else:
                GPIO.output(pin1, 0)
                GPIO.output(pin2, 1)
            #GYRO = gyro.zyroskop()
            #self.kat = GYRO.accel_xout
##            self.kat = kat_silnik
##          
##            roznica = self.kat - self.output
##            if roznica < 0:
##                roznica = roznica * -1
##            
##            if self.output > self.kat and roznica > 0:
##                d=1
##            if self.output < self.kat and roznica > 0:
##                d=-1
##            if roznica == 0:
##                d=0

##            kolejka_zadan.queue.clear()
##            kolejka_zadan.put(self.output)

#### RYSOWANIE WYKRESU
            if rysowanie >= 1:
                rysowanie = 0
                if wyswietl == 1:
                    odleglosc = self.distance
                    tx2 = time.time()
                    czas = tx2 - tx0
                  
                    czas = czas * 10
                    odleglosc = odleglosc * 6
                    odleglosc = odleglosc - 420
                    odleglosc = -odleglosc

                    zielona_linia = wartosc4 * 6
                    zielona_linia = zielona_linia - 420
                    zielona_linia = -zielona_linia
                    if czas >= 950:
                        gf.delete("wykres")
                        tx0 = time.time()
                        poprzednia_odleglosc = 0
                        poprzedni_czas = 0
                        czas = 0
                        gf.delete("sekundy")
                        x = 0
                        przedzial_sekund = przedzial_sekund + 75
                        while x < 950:
                            
                            sekundy = x/10
                            x = x + 50
                            gf.create_text(x, 400, text=(sekundy + przedzial_sekund, "s"),
                                           fill="yellow", tags="sekundy")

                    if poprzednia_odleglosc > 0:
                        if poprzednia_zielona_linia == 0:
                            poprzednia_zielona_linia = zielona_linia
                        gf.create_line(poprzedni_czas, poprzednia_zielona_linia, czas, zielona_linia,
                                       fill="green", width=3, tags="wykres")
                        gf.create_line(poprzedni_czas, poprzednia_odleglosc,
                                   czas, odleglosc, fill="yellow", width=3,
                                   tags="wykres")
                        poprzednia_zielona_linia = zielona_linia

                    poprzedni_czas = czas
                    poprzednia_odleglosc = odleglosc
                if wyswietl == 2:
                    
                    tx2 = time.time()
                    czas = tx2 - tx0
                    
                    obl_czas = czas - poprzedni_czas_do_obliczen
                    if obl_czas > 0.5:
                        odleglosc = self.distance
                        obl_droga = odleglosc - poprzednia_odleglosc
                        
                        
                        
                        poprzedni_czas_do_obliczen = czas
                        czas = czas * 10

                        predkosc = obl_droga / obl_czas
                        if predkosc <= 0:
                            predkosc = -predkosc
                        predkosc = predkosc * 12
                        predkosc = predkosc - 360
                        predkosc = -predkosc
                        
                        
                        
        ##                odleglosc = odleglosc * 4
        ##                odleglosc = odleglosc - 320
        ##                odleglosc = -odleglosc
                        
                        if czas > 950:
                            
                            gf.delete("wykres")
                            tx0 = time.time()
                            poprzednia_odleglosc = 0
                            poprzedni_czas = 0
                            
                            czas = 0
                            gf.delete("sekundy")
                            x = 0
                            przedzial_sekund = przedzial_sekund + 75
                            while x < 950:
                                
                                sekundy = x/10
                                x = x + 50
                                gf.create_text(x, 400, text=(sekundy + przedzial_sekund, "s"),
                                               fill="yellow", tags="sekundy")
                            
                        if poprzednia_odleglosc > 0:
                            gf.create_line(poprzedni_czas, poprzednia_predkosc,
                                           czas, predkosc, fill="tomato", width=3,
                                           tags="wykres")
                        poprzedni_czas = czas
                        poprzednia_odleglosc = odleglosc
                        poprzednia_predkosc = predkosc
                if wyswietl == 3:
    #rzeczywisty kat
                    stopnie = kat_silnik * 0.0027819
                    tx2 = time.time()
                    czas = tx2 - tx0
                    czas = czas * 10
                    stopnie = stopnie * 60
                    stopnie = stopnie - 180
                    stopnie = -stopnie
                    
                    if czas > 950:
                        gf.delete("wykres")
                        tx0 = time.time()
                        poprzednie_stopnie = 0
                        poprzedni_czas = 0
                        czas = 0
                        gf.delete("sekundy")
                        x = 0
                        przedzial_sekund = przedzial_sekund + 75
                        while x < 950:
                            
                            sekundy = x/10
                            x = x + 50
                            gf.create_text(x, 400, text=(sekundy + przedzial_sekund, "s"),
                                           fill="yellow", tags="sekundy")

                    if poprzednie_stopnie > 0:
                        gf.create_line(poprzedni_czas, poprzednie_stopnie,
                                   czas, stopnie, fill="cyan", width=3,
                                   tags="wykres")
                    poprzedni_czas = czas
                    poprzednie_stopnie = stopnie

#pozadany kat
                
                
                    out = self.output * 0.0027819
                    tx2 = time.time()
                    czas = tx2 - tx0
                  
                    czas = czas * 10
                    out = out * 60
                    out = out - 180
                    out = -out              

                    if poprzedni_czas > 0:
                        gf.create_line(poprzedni_czas, poprzedni_out,
                                   czas, out, fill="magenta", width=6,
                                   tags="wykres")
                    poprzedni_czas = czas
                    poprzedni_out = out
            rysowanie = rysowanie + 1
####ZAPIS DANYCH DO PLIKU
            if rejestracja == 1:
                plik = open(data, 'a')
                czas_string = str(round(time.time() - czas_zero, 3))
                plik.write(czas_string)
                plik.write(" ")
                distance_string = str(self.distance)
                plik.write(distance_string)
                plik.write(" ")

                odleglosc = self.distance
                tx2 = time.time()
                czas = tx2 - tx0
                czas = czas * 10
                obl_droga = poprzednia_odleglosc - odleglosc
                obl_czas = poprzedni_czas - czas
                predkosc = obl_droga / obl_czas
                predkosc_string = str(round(predkosc, 3))
                plik.write(predkosc_string)
                plik.write(" ")

                stopnie = kat_silnik * 0.038646
                stopnie_string = str(round(stopnie, 3))
                plik.write(stopnie_string)
                plik.write(" ")

                out = self.output * 0.038646
                out_string = str(round(out, 3))
                plik.write(out_string)
                plik.write("\n")
                plik.close()
        print "KONIEC 1"   

    def odczyt_pozycji(self):
        distance1 = tof.get_distance()
        distance2 = tof1.get_distance()
        if distance1 < distance2:
            distance = distance1
            if (distance > 0 and distance < 800):
                distance = (distance-34) / 10
                wynik = (-0.0054*math.pow(distance, 2)) + (0.773*distance) + 1.6176
        else:
            distance = distance2
            if (distance > 0 and distance < 800):
                distance = (1100 - distance) / 10
                wynik = (0.0046*math.pow(distance, 2)) - (0.124*distance) + 30.931
        
        time.sleep(timing/1000000.00)
        try:
            self.distance = round(wynik, 1)
        except:
            pass

        
        #print self.distance, "cm"

    def do_PID(self, P = 0.2,  I = 0.0, D= 0.0,
               pozycja_docel = 50.0, pomiar_odleglosci = 0.0,
               poprzedni_blad = 0.0, poprzedni_czas = 0.0):
        #print "p= ", P, " i= ", I, " D= ", D, "poz_docel= ", pozycja_docel, " pomiar odleglosci = ", pomiar_odleglosci
        pid = PID.PID(P, I, D)
        pid.SetPoint = pozycja_docel
        pid.setSampleTime(0.0)
        pid.last_error = poprzedni_blad
        pid.last_time = poprzedni_czas
        feedback = pomiar_odleglosci
        pid.update(feedback)
        self.output = pid.output
        self.blad = pid.blad
        self.poprzedni_blad = pid.last_error
        self.poprzedni_czas = pid.last_time
        #print "poprzedni blad = ", poprzedni_blad
            
def main():
    root = Tk()
    root.title("Badanie efektywnosci pracy regulatorow PID oraz LQR")
    app = StripChart(root)
    root.mainloop()
    
main()
