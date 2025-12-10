"""
Mood Detection Models
"""
from django.db import models
from accounts.models import User

class MoodDetectionResult(models.Model):
    """Store mood detection results"""
    
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('neutral', 'Neutral'),
        ('surprised', 'Surprised'),
        ('fear', 'Fear'),
        ('disgust', 'Disgust'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_results')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    confidence = models.FloatField()
    image = models.ImageField(upload_to='mood_images/', blank=True, null=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Mood Detection Result'
        verbose_name_plural = 'Mood Detection Results'
    
    def __str__(self):
        return f"{self.user.email} - {self.mood} ({self.confidence:.2f}) at {self.detected_at}"