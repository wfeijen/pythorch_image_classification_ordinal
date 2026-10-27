from pathlib import Path


def delete_part_of_hierarchie(xmp_data: str, part_to_delete: str) -> str:
    """
    Verwijdert een specifiek deel van de hiërarchische onderwerpen in de XMP-data.

    :param xmp_data: De originele XMP-data als string.
    :param part_to_delete: Het deel van de hiërarchie dat verwijderd moet worden (bijv. "xxx|").
    :return: De aangepaste XMP-data als string.
    """

    text_replaced = []
    hirachical_lines = set()
    hierarchical_subjects = False
    for line in xmp_data.splitlines():
        if line.strip().startswith("<lr:hierarchicalSubject>"):
            hierarchical_subjects = True
        elif line.strip().startswith("</lr:hierarchicalSubject>"):
            hierarchical_subjects = False
        if hierarchical_subjects and line.strip().startswith("<rdf:li>"):
            line = line.replace(part_to_delete, "")
        if line in hirachical_lines:
            continue  # Skip duplicate lines
        hirachical_lines.add(line)
        text_replaced.append(line)
    return "\n".join(text_replaced)

def standaardiseer_xmp(xmp_pad: Path) -> None:
    """ Voert nodige stappen uit om xmp te stanaardiseren.

    Args:
        xmp_pad (Path): Volledig pad naar xmp bestand.
    Returns:
        None:
    """

    if not xmp_pad.exists() or not xmp_pad.is_file():
        raise FileNotFoundError(f"Het opgegeven pad '{xmp_pad}' bestaat niet of is geen bestand.")

    # Lees de originele XMP-data
    with xmp_pad.open('r', encoding='utf-8') as file:
        xmp_data = file.read()

    # Verwijder het specifieke deel van de hiërarchie
    aangepaste_xmp_data = delete_part_of_hierarchie(xmp_data, "xxx|")

    # Schrijf de aangepaste XMP-data terug naar het bestand
    with xmp_pad.open('w', encoding='utf-8') as file:
        file.write(aangepaste_xmp_data)

