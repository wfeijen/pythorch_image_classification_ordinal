import os
from pathlib import Path
import time

OBSCURE = True  # Als True, worden afbeeldingen onherkenbaar gemaakt (XOR) en opgeslagen als .dat bestanden.


def obscure_file(input_path: str, output_path: str, key: int = 0xFF, header_only: bool = True):
    """
    Zet een afbeelding om naar een onherkenbaar bestand.

    :param input_path: Pad naar het originele bestand (bijv. 'foto.jpg')
    :param output_path: Pad naar het uitvoerbestand (bijv. 'foto.bin')
    :param key: Byte-sleutel voor de XOR-operatie (standaard 0xFF)
    :param header_only: Als True, worden alleen de eerste 64 bytes aangepast (BLIKSEMSNEL).
                        Als False, wordt het hele bestand verwerkt.
    """
    with input_path.open('rb') as f_in, output_path.open('wb') as f_out:
        if header_only:
            # Lees en verander alleen de eerste 64 bytes (magic bytes/header)
            header = bytearray(f_in.read(64))
            for i in range(len(header)):
                header[i] ^= key
            f_out.write(header)

            # Schrijf de rest van het bestand ongewijzigd weg
            chunk_size = 1024 * 1024  # 1MB chunks
            while chunk := f_in.read(chunk_size):
                f_out.write(chunk)
        else:
            # Verwerk het volledige bestand in chunks
            chunk_size = 1024 * 1024
            while chunk := f_in.read(chunk_size):
                obscured_chunk = bytearray(c ^ key for c in chunk)
                f_out.write(obscured_chunk)

def restore_file(input_path: str, output_path: str, key: int = 0xFF, header_only: bool = True):
    """
    Herstelt het onherkenbare bestand weer naar de originele afbeelding.
    Omdat XOR symmetrisch is, roepen we simpelweg obscure_file aan.
    """
    obscure_file(input_path, output_path, key=key, header_only=header_only)


# --- VOORBEELD GEBRUIK ---
def obscure_directory(target_dir: str, extensions: tuple = ('.jpg', '.jpeg', '.png', '.bmp', '.webp'), key: int = 0xFF):
    """
    Zoekt recursief naar afbeeldingen in een directory en maakt ze onherkenbaar.

    :param target_dir: Het pad naar de map die verwerkt moet worden.
    :param extensions: Welke bestandsextensies als afbeelding gezien moeten worden.
    :param key: Sleutel voor de XOR-operatie.
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.lower().endswith(extensions) and not file.endswith('.dat'):
                input_path = Path(root) / file
                output_path = input_path.with_suffix('.dat')

                # Coderen naar .dat bestand
                obscure_file(input_path, output_path, key=key, header_only=True)
                input_path.unlink()

def restore_directory(target_dir: str, key: int = 0xFF, original_ext: str = '.jpg'):
    """
    Zoekt recursief naar .dat bestanden in een directory en herstelt ze naar afbeeldingen.

    :param target_dir: Het pad naar de map die hersteld moet worden.
    :param key: Sleutel voor de XOR-operatie (moet gelijk zijn aan de coderingssleutel).
    :param original_ext: De extensie waarnaar de herstelde bestanden worden opgeslagen (bijv. '.jpg').
    """
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.dat'):
                input_path = Path(root) / file
                output_path = input_path.with_suffix(original_ext)

                # Decoderen naar origineel formaat
                restore_file(input_path, output_path, key=key, header_only=True)
                input_path.unlink()


# --- VOORBEELD GEBRUIK ---
if __name__ == "__main__":
    MAP_PAD = "/home/willem/Data_neurale_netwerken/"

    start_tijd = time.perf_counter()

    if OBSCURE:
        obscure_directory(MAP_PAD)
        print(f"Alle afbeeldingen in {MAP_PAD} zijn onherkenbaar gemaakt en opgeslagen als .dat bestanden.")
    else:
        restore_directory(MAP_PAD, original_ext='.jpg')
        print(f"Alle .dat bestanden in {MAP_PAD} zijn hersteld naar originele afbeeldingen.")

    eind_tijd = time.perf_counter()
    uitvoeringstijd = eind_tijd - start_tijd

    print(f"Uitvoeringstijd: {uitvoeringstijd:.6f} seconden")

