from vector_db import VectorDBManager

def testeaza_memoria():
    # Ne conectam la baza de date existenta
    db = VectorDBManager(path="./db_vectorial")
    
    intrebare = "Cum functioneaza Insertion Sort?"
    print(f"Întreb AI-ul: '{intrebare}'...\n")
    
    # Cautam cele mai bune 2 paragrafe care raspund la intrebare
    raspuns = db.cauta_similare(intrebare, n_rezultate=2)
    
    print("--- CE A GASIT IN CARTEA CLRS ---")
    
    # Afisam ce a extras din acele fisiere "ciudate"
    for i, text_gasit in enumerate(raspuns['documents'][0]):
        metadata = raspuns['metadatas'][0][i]
        
        print(f"\n🟢 Fragmentul {i+1} ( extras din paginile {metadata.get('pagini_extrase', '?')} ):")
        print(text_gasit)
        print("-" * 50)

if __name__ == "__main__":
    testeaza_memoria()