import hashlib
from collections import defaultdict
from pathlib import Path


def get_duplicates(root: Path, recursive: bool = False) -> list[tuple[Path, ...]]:
    """
    Functie om bestanden met gelijke inhoud te vinden in een directory.
    :param root: Path object van de directory waarin gezocht wordt.
    :param recursive: Boolean, als True zoekt het ook in subdirectories.
    :return: list van tuples met Path objecten die duplicaten zijn
    """
    if not root.exists() or not root.is_dir():
        return []

    # Stap 1: Verzamel bestanden en groepeer op grootte (snelle pre-filter)
    size_dict = defaultdict(list)
    pattern = "**/*" if recursive else "*"
    for path in root.glob(pattern):
        if path.is_file():
            try:
                size = path.stat().st_size
                size_dict[size].append(path)
            except (PermissionError, OSError):
                # Sla bestanden over waar geen leesrechten voor zijn
                continue

    # Stap 2: Bereken een hash (MD5) voor bestanden met dezelfde grootte
    hash_dict = defaultdict(list)
    for size, paths in size_dict.items():
        if len(paths) < 2:
            continue  # Geen duplicaten mogelijk als de grootte uniek is
        for path in paths:
            file_hash = _compute_hash(path)
            if file_hash:
                hash_dict[file_hash].append(path)

    # Stap 3: Filter alleen groepen met meerdere bestanden over en retourneer als tuples
    return [tuple(paths) for paths in hash_dict.values() if len(paths) > 1]

def _compute_hash(path: Path, chunk_size: int = 8192) -> str | None:
    """Hulpfunctie om de hash van een bestand in brokken in te lezen."""
    hasher = hashlib.md5()
    try:
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError):
        return None

    # Maak een Path object aan
pad = Path("/home/willem/Data_neurale_netwerken/classificatie_arbitrair_onderscheid/VM")

# Zoek naar duplicaten (inclusief submappen)
dubbele_bestanden = get_duplicates(pad, recursive=True)

for groep in dubbele_bestanden:
    print("Duplicaat groep:")
    for bestand in groep:
        print(f" - {bestand}")
