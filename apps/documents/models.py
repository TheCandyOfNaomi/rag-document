from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name="文档标题")
    file = models.FileField(upload_to='documents/%Y/%m/%d/', verbose_name="文件路径")
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="上传者")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="上传时间")
    is_processed = models.BooleanField(default=False, verbose_name="是否向量化完成")
    
    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    question = models.TextField(verbose_name="用户问题")
    answer = models.TextField(verbose_name="AI 回答")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']