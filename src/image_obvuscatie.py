import os
from pathlib import Path
import time

OBSCURE = True  # Als True, worden afbeeldingen onherkenbaar gemaakt en opgeslagen als .dat bestanden.


ZICHTBARE_EXRENSIE = '.jpg'  # Extensie voor herstelde bestanden.
OBSCURE_EXTENSIONS = (ZICHTBARE_EXRENSIE , '.jpeg', '.png', '.bmp', '.webp')  # Extensies van afbeeldingen die onherkenbaar gemaakt moeten worden.
OBSCURE_EXTENTIE = '.wilx'  # Extensie voor onherkenbare bestanden.




def obscure_file(input_path: Path, output_path: Path, key: int = 0xFF):
    """
    Maakt een afbeelding onherkenbaar door het bestand direct te hernoemen 
    naar OBSCURE_EXTENTIE en de eerste 64 bytes in-place aan te passen via XOR.
    """
    # Hernoem het bestand direct (instant, kost geen data-kopieer tijd)
    input_path.rename(output_path)

    # Pas alleen de header direct in-place aan op het nieuwe bestand
    with output_path.open('r+b') as f:
        header = bytearray(f.read(64))
        for i in range(len(header)):
            header[i] ^= key
        
        f.seek(0)
        f.write(header)


def restore_file(input_path: Path, output_path: Path, key: int = 0xFF):
    """
    Herstelt het OBSCURE_EXTENTIE bestand weer naar de originele afbeelding.
    Omdat XOR en hernoemen symmetrisch zijn, werkt dit exact hetzelfde.
    """
    obscure_file(input_path, output_path, key=key)


def obscure_directory(target_dir: str, key: int = 0xFF):
    """
    Zoekt recursief naar afbeeldingen en maakt ze onherkenbaar.
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(OBSCURE_EXTENSIONS) and not file.endswith(OBSCURE_EXTENTIE):
                input_path = Path(root) / file
                output_path = input_path.with_suffix(OBSCURE_EXTENTIE)

                # Coderen en hernoemen naar .dat
                obscure_file(input_path, output_path, key=key)


def restore_directory(target_dir: str, key: int = 0xFF, original_ext: str = ZICHTBARE_EXRENSIE ):
    """
    Zoekt recursief naar .dat bestanden en herstelt ze naar afbeeldingen.
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(OBSCURE_EXTENTIE):
                input_path = Path(root) / file
                output_path = input_path.with_suffix(original_ext)

                # Decoderen en herstelt naar originele extensie
                restore_file(input_path, output_path, key=key)


# --- VOORBEELD GEBRUIK ---
if __name__ == "__main__":
    MAP_PAD = "/home/willem/Data_neurale_netwerken/"

    start_tijd = time.perf_counter()

    if OBSCURE:
        obscure_directory(MAP_PAD)
        print(f"Alle afbeeldingen in {MAP_PAD} zijn onherkenbaar gemaakt en opgeslagen als {OBSCURE_EXTENTIE} bestanden.")
    else:
        restore_directory(MAP_PAD, original_ext=ZICHTBARE_EXRENSIE)
        print(f"Alle {OBSCURE_EXTENTIE} bestanden in {MAP_PAD} zijn hersteld naar originele afbeeldingen.")

    eind_tijd = time.perf_counter()
    uitvoeringstijd = eind_tijd - start_tijd

    print(f"Uitvoeringstijd: {uitvoeringstijd:.6f} seconden")