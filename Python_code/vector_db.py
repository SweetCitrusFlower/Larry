import chromadb
from chromadb.config import Settings

class VectorDBManager:
    def __init__(self, path="./db_vectorial"):

        self.client = chromadb.PersistentClient(path=path)
        

        self.collection = self.client.get_or_create_collection(
            name="biblioteca_algoritmi",
            metadata={"hnsw:space": "cosine"} 
        )

    def adauga_document(self, text, metadata, id_unic):
        """Adaugă un fragment de text în baza de date vectorială."""
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[id_unic]
        )
        print(f"✅ Documentul {id_unic} a fost indexat.")

    def cauta_similare(self, intrebare, n_rezultate=3):
        """Caută cele mai relevante fragmente pentru o întrebare."""
        results = self.collection.query(
            query_texts=[intrebare],
            n_results=n_rezultate
        )
        return results


if __name__ == "__main__":
    db = VectorDBManager()
    

    db.adauga_document(
        text="Complexitatea algoritmului Merge Sort este O(n log n) în toate cazurile.",
        metadata={"sursa": "Curs Algoritmi", "capitol": "Divide et Impera"},
        id_unic="ms_001"
    )
    

    raspuns = db.cauta_similare("Care este complexitatea la merge sort?")
    print("\nRezultat găsit:", raspuns['documents'][0][0])