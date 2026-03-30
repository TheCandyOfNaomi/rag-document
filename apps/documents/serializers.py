from rest_framework import serializers
from .models import Document, Conversation

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'file', 'uploaded_at', 'is_processed']
        read_only_fields = ['uploaded_by', 'is_processed']

class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(required=True, max_length=500)

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'question', 'answer', 'created_at']