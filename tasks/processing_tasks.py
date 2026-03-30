from celery import shared_task
from apps.documents.models import Document
from services.rag_service import RAGService

@shared_task(bind=True, max_retries=3)
def process_document_task(self, document_id):
    try:
        doc = Document.objects.get(id=document_id)
        rag_service = RAGService()
        rag_service.ingest_document(
            file_path=doc.file.path,
            collection_name=f"doc_{document_id}"
        )
        doc.is_processed = True
        doc.save()
        return f"Document {document_id} processed successfully."
    except Exception as e:
        self.retry(exc=e, countdown=60)