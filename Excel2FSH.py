import pandas as pd

def format_value(val):
    """
    Tar bort överflödiga blanktecken och eventuella citattecken.
    Om värdet saknas returneras en tom sträng.
    """
    if pd.isna(val):
        return ""
    return str(val).strip().strip('"')

def format_code(val):
    """
    Formaterar ett kod-värde så att det blir t.ex. "#PatientSummary.header"
    Om värdet inte redan börjar med '#' så läggs det till.
    """
    v = format_value(val)
    if v and not v.startswith("#"):
        return "#" + v
    return v

def main():
    # Ange sökväg till din Excelfil
    excel_fil = "hl7-eps-models-and-maps.xlsx"  # ändra vid behov
    flik = "Alerts2FHIREuHdr"  # ersätt med det specifika fliknamnet du vill läsa in
    
    # Läs in den specifika fliken från Excel-filen
    df = pd.read_excel(excel_fil, sheet_name=flik)
    
    # Gruppera rader baserat på "Group Source" och "Group Target"
    grupper = {}
    for index, row in df.iterrows():
        group_source = format_value(row["Group Source"])
        group_target = format_value(row["Group Target"])
        nyckel = (group_source, group_target)
        element = {
            "source_code": format_code(row["Source Code"]),
            "source_display": format_value(row["Source Display"]),
            "target_code": format_code(row["Target Code"]),
            "target_display": format_value(row["Target Display"]),
            "equivalence": format_code(row["Equivalence"]),
            "comment": format_value(row["Comment"])
        }
        grupper.setdefault(nyckel, []).append(element)
    
    # Definiera header för ConceptMap‐instansen
    instance_name = "patientSummary2FHIR"
    concept_map_url = "http://hl7.eu/fhir/eps/ConceptMap/patientSummary2FHIR"
    concept_map_name = "PatientSummary2FHIR"
    concept_map_title = "eHN Patient Summary to this guide Map"
    concept_map_description = "eHN Patient Summary to this guide Map"
    
    # Bygg FSH-texten rad för rad
    fsh_rader = []
    fsh_rader.append(f"Instance: {instance_name}")
    fsh_rader.append("InstanceOf: ConceptMap")
    fsh_rader.append("Usage: #definition")
    fsh_rader.append(f'* url = "{concept_map_url}"')
    fsh_rader.append(f'* name = "{concept_map_name}"')
    fsh_rader.append(f'* title = "{concept_map_title}"')
    fsh_rader.append("* status = #draft")
    fsh_rader.append("* experimental = false")
    fsh_rader.append(f'* description = """{concept_map_description}"""')
    fsh_rader.append("")  # tom rad för separation

    # För varje grupp (baserat på Group Source och Group Target) skriv ut mappningen
    for (group_source, group_target), element_lista in grupper.items():
        fsh_rader.append(f'* group[+].source = "{group_source}"')
        fsh_rader.append(f'* group[=].target = "{group_target}"')
        for elem in element_lista:
            fsh_rader.append(f'* group[=].element[+].code = {elem["source_code"]}')
            fsh_rader.append(f'* group[=].element[=].display = "{elem["source_display"]}"')
            fsh_rader.append(f'* group[=].element[=].target.code = {elem["target_code"]}')
            fsh_rader.append(f'* group[=].element[=].target.display = "{elem["target_display"]}"')
            fsh_rader.append(f'* group[=].element[=].target.equivalence = {elem["equivalence"]}')
            fsh_rader.append(f'* group[=].element[=].target.comment = "{elem["comment"]}"')
            fsh_rader.append("")  # tom rad mellan elementen

    # Slå ihop alla rader till en sträng
    fsh_text = "\n".join(fsh_rader)
    
    # Skriv ut till en FSH-fil
    output_fil = f"{instance_name}.fsh"
    with open(output_fil, "w", encoding="utf-8") as f:
        f.write(fsh_text)
    
    print(f"FSH-fil '{output_fil}' har skapats.")

if __name__ == "__main__":
    main()
