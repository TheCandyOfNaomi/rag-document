from django.contrib import admin
from .models import Document, Conversation
from config.celery import app

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'is_processed')
    search_fields = ('title',)
    readonly_fields = ('is_processed',)

    def save_model(self, request, obj, form, change):
        obj.save()
        app.send_task('tasks.processing_tasks.process_document_task', args=[obj.id])

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'document', 'created_at')
    search_fields = ('question', 'answer')