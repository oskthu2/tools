import pandas as pd

class Node:
    def __init__(self, full_name, cardinality, datatype, short, definition):
        self.full_name = full_name.strip()
        # Sista segmentet (efter sista punkten) används som "namn" för noden
        self.name = self.full_name.split('.')[-1]
        self.cardinality = str(cardinality).strip()
        self.datatype = str(datatype).strip()
        self.short = str(short).strip() if pd.notna(short) else ""
        self.definition = str(definition).strip() if pd.notna(definition) else ""
        self.children = []
        self.parent = None
        # Om Datatype är "Base" eller "BackboneElement" behandlas noden som en klass
        self.is_class = self.datatype in ["Base", "BackboneElement"]

def camel_case(s):
    """Gör om en sträng så att första bokstaven blir stor."""
    if s:
        return s[0].upper() + s[1:]
    return s

def get_class_name(node):
    """
    Returnerar UML-klassnamnet för en nod som är en klass.
    Enligt de nya instruktionerna: endast element-namnet (sista segmentet) + "Type"
    """
    return f"{camel_case(node.name)}Type"

def build_tree(df):
    """
    Bygger upp ett träd (noder med förälder/barn) från DataFrame där varje rad representerar ett element.
    """
    nodes = {}
    # Skapa en nod för varje rad
    for _, row in df.iterrows():
        full_name = str(row["Element"])
        cardinality = row["Cardinality"]
        datatype = row["Datatype"]
        short = row["Short"]
        definition = row["Definition"]
        node = Node(full_name, cardinality, datatype, short, definition)
        nodes[node.full_name] = node

    # Sätt förälder-/barn-relationer baserat på punkter i 'Element'
    for full_name, node in nodes.items():
        if '.' in full_name:
            parent_full = full_name.rsplit('.', 1)[0]
            if parent_full in nodes:
                parent_node = nodes[parent_full]
                node.parent = parent_node
                parent_node.children.append(node)
    return nodes

def generate_plantuml(nodes):
    """
    Genererar PlantUML-kod utifrån noderna.
    - För noder som är klasser genereras UML-klassdefinitioner.
    - För barn-noder som är attribut (ej klasser) läggs en rad in i förälderns klass.
    - För barn-noder som är klasser ritas en associationspil från förälderns UML-klass till barnets UML-klass.
      Pilarna visar barnets element-namn samt kardinalitet (inom hakparenteser) i slutet.
    """
    uml_lines = []
    uml_lines.append("@startuml")
    uml_lines.append("hide empty members")
    uml_lines.append("")
    
    class_defs = {}   # full_name -> (uml_class_name, definition_lines)
    associations = [] # samlar associationspilar

    # Gå igenom alla noder och skapa klassdefinitioner för de noder som är klasser
    for full_name, node in nodes.items():
        if node.is_class:
            class_name = get_class_name(node)
            lines = [f"class {class_name} {{"]

            # Lägg in attribut (barn som inte är klasser)
            for child in node.children:
                if not child.is_class:
                    # Exempel: + documentId : string  // 1..1
                    lines.append(f"  + {child.name} : {child.datatype}  // {child.cardinality}")
            lines.append("}")
            class_defs[full_name] = (class_name, lines)

    # Skapa associationspilar för barn som är klasser
    for full_name, node in nodes.items():
        if node.is_class and node.parent and node.parent.is_class:
            parent_uml = get_class_name(node.parent)
            child_uml = get_class_name(node)
            # Pilar: skriv ut barnets element-namn och kardinalitet i slutet av pilen.
            associations.append(f'{parent_uml} --> {child_uml} : {node.name} [{node.cardinality}]')

    # Lägg först in alla klassdefinitioner
    for full_name, (class_name, lines) in class_defs.items():
        uml_lines.extend(lines)
        uml_lines.append("")
    
    # Lägg in associationspilarna
    for assoc in associations:
        uml_lines.append(assoc)
    
    uml_lines.append("")
    uml_lines.append("@enduml")
    return "\n".join(uml_lines)

def main():
    # Ange sökväg till din Excelfil och flik (tab)
    excel_file = "hl7-eps-models-and-maps.xlsx"  # ändra vid behov
    sheet_name = "YourSheetName"  # Ändra till det specifika fliknamnet du vill läsa in

    # Läs in Excel‑filen med angiven flik
    df = pd.read_excel("hl7-eps-models-and-maps.xlsx", sheet_name="PatientSummaryEhn")
    
    # Bygg träd med noder utifrån Excel‑data
    nodes = build_tree(df)
    
    # Generera PlantUML‑kod
    plantuml_code = generate_plantuml(nodes)
    
    # Skriv ut koden och spara den i en fil
    print(plantuml_code)
    with open("output.puml", "w", encoding="utf-8") as f:
        f.write(plantuml_code)

if __name__ == "__main__":
    main()
