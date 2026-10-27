
# Jouw XMP data (of gebruik ET.parse('bestand.xmp') als het uit een bestand komt)
xmp_data = """<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="XMP Core 6.0.0">
    <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns:lr="http://ns.adobe.com/lightroom/1.0/"
            xmlns:xmp="http://ns.adobe.com/xap/1.0/"
            xmlns:MicrosoftPhoto="http://ns.microsoft.com/photo/1.0/">
        <dc:subject>
            <rdf:Bag>
               <rdf:li>level</rdf:li>
               <rdf:li>lazy cat</rdf:li>
               <rdf:li>0 naam</rdf:li>
               <rdf:li>L</rdf:li>
               <rdf:li>xxx</rdf:li>
               <rdf:li>orientatie</rdf:li>
               <rdf:li>landschap</rdf:li>
               <rdf:li>1 geen naam</rdf:li>
               <rdf:li>lee anne</rdf:li>
               <rdf:li>slideshow</rdf:li>
            </rdf:Bag>
         </dc:subject>
         <lr:hierarchicalSubject>
            <rdf:Bag>
               <rdf:li>xxx|hoogte|level</rdf:li>
               <rdf:li>xxx|houding|lazy cat</rdf:li>
               <rdf:li>xxx|0 naam</rdf:li>
               <rdf:li>xxx|0 naam|L</rdf:li>
               <rdf:li>xxx</rdf:li>
               <rdf:li>xxx|orientatie</rdf:li>
               <rdf:li>orientatie</rdf:li>
               <rdf:li>xxx|orientatie|landschap</rdf:li>
               <rdf:li>xxx|1 geen naam</rdf:li>
               <rdf:li>xxx|0 naam|L|lee anne</rdf:li>
               <rdf:li>slideshow</rdf:li>
            </rdf:Bag>
         </lr:hierarchicalSubject>
         <xmp:Rating>3</xmp:Rating>
         <MicrosoftPhoto:Rating>50</MicrosoftPhoto:Rating>
      </rdf:Description>
   </rdf:RDF>
</x:xmpmeta>"""

text_replaced = []
hirachical_lines = set()
hierarchical_subjects = False
for line in xmp_data.splitlines():
    if line.strip().startswith("<lr:hierarchicalSubject>"):
        hierarchical_subjects = True
    elif line.strip().startswith("</lr:hierarchicalSubject>"):
        hierarchical_subjects = False
    if hierarchical_subjects and line.strip().startswith("<rdf:li>"):
        line = line.replace("xxx|", "")
        if line in hirachical_lines:
            continue  # Skip duplicate lines
        hirachical_lines.add(line)
    text_replaced.append(line)
resulting_xmp_data = "\n".join(text_replaced)
print(resulting_xmp_data)
