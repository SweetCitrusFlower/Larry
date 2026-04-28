import fitz  
import uuid
from vector_db import VectorDBManager

def incarca_pdf_in_chroma(cale_pdf, pagina_start, pagina_stop):
    db = VectorDBManager(path="./db_vectorial")
    print(f"📚 Deschid cartea: {cale_pdf}...")
    
    try:
        document = fitz.open(cale_pdf)
    except FileNotFoundError:
        print(f"❌ Eroare: Nu am gasit {cale_pdf}. E pus in folderul D:\\Larry?")
        return

    documente_indexate = 0
    text_total = ""

    print(f"📖 Citesc paginile de la {pagina_start} la {pagina_stop}...")
    for numar_pagina in range(pagina_start, min(pagina_stop, len(document))):
        pagina = document.load_page(numar_pagina)
        text_total += pagina.get_text("text") + "\n\n"
        

    fragmente = text_total.split('\n\n')
    
    print("🧠 Procesez fragmentele si le trimit in baza de date vectoriala...")
    
    
    for fragment in fragmente:
        fragment_curat = fragment.strip()
        
        
        if len(fragment_curat) > 50:
            id_unic = f"clrs_pdf_{uuid.uuid4().hex[:8]}"
            
            
            db.adauga_document(
                text=fragment_curat,
                metadata={
                    "sursa": "CLRS - Introduction to Algorithms (Ed. 3)", 
                    "pagini_extrase": f"{pagina_start}-{pagina_stop}"
                },
                id_unic=id_unic
            )
            documente_indexate += 1
            
    print(f"\n🚀 MAGIE! Am extras si indexat {documente_indexate} paragrafe academice din CLRS.")

if __name__ == "__main__":
    # Extragem paginile 16 - 40 (unde se vorbeste de Insertion Sort si Merge Sort in PDF)
    incarca_pdf_in_chroma("clrs.pdf", pagina_start=16, pagina_stop=40)