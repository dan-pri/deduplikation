from datetime import date
from pathlib import Path,PurePath
import hashlib
import os
import sys
import time


class Datei:
    """
        Klasse zum speichern der Dateiinformationen
    """
    def __init__(self, datei_name, datei_pfad, datei_größe, datei_zeitstempel):
        self.datei_name = datei_name
        self.datei_pfad = datei_pfad
        self.datei_größe = datei_größe
        self.datei_zeitstempel = datei_zeitstempel

    def get_dateiname(self):
        return self.datei_name

    def get_dateipfad(self):
        return self.datei_pfad
    
    def get_dateigröße(self):
        return self.datei_größe

    def get_dateizeit(self):
        return self.datei_zeitstempel


def bilde_hash(dateiname):
    """
        Funktion um den Hash einer Datei zu berechnen
        Input: Aktueller Pfad
        Output: Hashwert der Datei oder False, wenn Datei nicht geöffnet werden kann
    """
    #sys.stdout.write("*")
    try:
        print("\033[93m" + "[Untersuche]" + "\033[0m" + " " + str(dateiname))
        #Versuche die Datei zu öffnen
        with open(dateiname, 'rb') as file:
            #Bilde den Hash-Wert und gebe ihn zurück
            return hashlib.sha256(file.read()).hexdigest().upper()
    except:
        print("\033[91m" + "[Fehler]" + "\033[0m" + " Datei " + str(dateiname) + " konnte nicht geöffnet werden!")
        fehlzugriff.append(str(dateiname))
        return False


def suche_dateien(aktueller_pfad):
    """
        Rekursive Funktion um Dateien zu listen
        Input: Aktueller Pfad
    """
    aktueller_ordner = Path(aktueller_pfad)

    #Wenn aktueller Ordner leer ist, springe zurück [Abbruchbedingung Rekursion]
    try:
        if len(os.listdir(aktueller_ordner)) == 0:
            return
    except:
        fehlzugriff.append(aktueller_ordner)
        return

    #Durchsuche den aktuellen Ordner nach weiteren Ordnern/Dateien und befülle die beiden Listen
    for item in os.listdir(aktueller_ordner):
        #Wenn das aktuelle Item ein Ordner ist, gehe rekursiv rein
        if os.path.isdir(aktueller_ordner / item):
            suche_dateien(aktueller_ordner / item)


        #Wenn das aktuelle Item eine Datei ist, füge sie in einer Liste hinzu
        if os.path.isfile(aktueller_ordner / item):
            hash = bilde_hash(aktueller_ordner / item)

            #Wenn kein Hash gebildet werden konnte, überspringe die Datei
            if hash == False:
                continue

            pfad = aktueller_ordner / item
            änderung = time.strftime('%d/%m/%Y', time.gmtime(os.path.getmtime(pfad)))
            größe = os.stat(aktueller_ordner / item).st_size
            datei = Datei(item, pfad, größe, änderung)

            if hash in gesamt_dateien:
                gesamt_dateien[hash].append(datei)
            else:
                gesamt_dateien[hash] = [datei]
    return


def erstelle_log(pfad):
    """
        Funktion um die Ergebnisse der Duplikatssuche in eine Datei zu schreiben
        Input: Anfangspfad der für die Suche eingegeben wurde
    """
    datei = Path(pfad)
    datei = datei / "duplikate.log"

    try:
        #Versuche die Objekte in ein Logfile zu speichern
        with open(datei, 'w') as file:
            file.write("Duplikationsssuche am: " + time.strftime("%d.%m.%Y %H:%M:%S")+"\n\n")
            for item in gesamt_dateien:
                file.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
                file.write("SHA 256: " + item + "\n")
                for eintrag in gesamt_dateien[item]:
                    dateipfad = PurePath(eintrag.get_dateipfad())
                    file.write("Dateiname: " + eintrag.get_dateiname() + " | Dateigröße: " + str(eintrag.get_dateigröße()) + " Bytes | Letzte Änderung: " + str(eintrag.get_dateizeit())  + " | Pfad: " + str(dateipfad.as_uri()) + "\n")
            file.write("------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n")
            file.write("Fehlerhafte zugriffe auf Ordner und Dateien:")
            for i in fehlzugriff:
                file.write(i)
        print("\033[92m" + "[INFO]" + "\033[0m" " Duplikatsliste erstellt: " + str(datei))
    except:
        print("\033[91m" + "[Fehler]" + "\033[0m" + " Duplikatsliste konnte nicht erstellt werden!")
        return
     

if __name__ == "__main__":
    start = time.perf_counter()

    #Dictionary für die gefundene Dateien/Fehlzugriff
    gesamt_dateien = {}
    fehlzugriff = []

    #Überprüfe ob ein Argument übergeben wurde, wenn nicht gebe Fehler aus
    if len(sys.argv) < 2:
        print("\033[91m" + "[Fehler]" + "\033[0m" + " Der Suchpfad wurde nicht eingegeben")
        sys.exit()
    else:
        pfad = sys.argv[1]


    #prüfe ob es das Verzeichnis überhaupt gibt
    suchbeginn = Path(pfad)
    if not os.path.exists(suchbeginn):
        print("\033[91m" + "[Fehler]" + "\033[0m" + " Pfad wurde nicht gefunden")
        sys.exit()
    else:
        print("\033[92m" + "[INFO]" + "\033[0m" " Pfad gefunden")


    #Suche nach Dateien
    print("\033[92m" + "[START]" + "\033[0m" " Beginne Suche nach Duplikaten")
    suche_dateien(suchbeginn)
    print("\033[92m" + "[STOP]" + "\033[0m" " Suche abgeschlossen")


    #Entferne Einträge im Dictionary, die nur ein Objekt enthalten
    eintrag_löschen = []
    for datei in gesamt_dateien:
        if len(gesamt_dateien[datei]) == 1:
            eintrag_löschen.append(datei)
    for eintrag in eintrag_löschen:
        gesamt_dateien.pop(eintrag)
    

    #Erstelle Logfile mit den Einträgen
    erstelle_log(suchbeginn)
    
    end = time.perf_counter()

    if (end-start) > 60:
        print("\033[92m" + "[ENDE]" + "\033[0m" " Dauer: " + str(round(((end - start)/60),2)) + " min")
    else:
        print("\033[92m" + "[ENDE]" + "\033[0m" " Dauer: " + str(round((end - start),2)) + " sec")
