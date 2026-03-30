from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document, Conversation
from .serializers import DocumentSerializer, AskQuestionSerializer, ConversationSerializer
from tasks.processing_tasks import process_document_task
from services.rag_service import RAGService

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(uploaded_by=self.request.user)

    def perform_create(self, serializer):
        doc = serializer.save(uploaded_by=self.request.user)
        process_document_task.delay(doc.id)

    @action(detail=True, methods=['post'], url_path='ask')
    def ask_question(self, request, pk=None):
        document = self.get_object()
        serializer = AskQuestionSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        if not document.is_processed:
            return Response({"error": "文档正在处理中，请稍后再试"}, status=400)

        rag_service = RAGService()
        result = rag_service.query(document.id, serializer.validated_data['question'])

        Conversation.objects.create(
            user=request.user,
            document=document,
            question=serializer.validated_data['question'],
            answer=result['answer']
        )

        return Response(result)

    @action(detail=True, methods=['get'], url_path='history')
    def get_history(self, request, pk=None):
        document = self.get_object()
        conversations = Conversation.objects.filter(user=request.user, document=document)
        return Response(ConversationSerializer(conversations, many=True).data)