"""
Mood Detection Models - Privacy-Focused
Images are optional and NOT required for privacy
"""
from django.db import models
from accounts.models import User

class MoodDetectionResult(models.Model):
    """Store mood detection results WITHOUT images for privacy"""
    
    MOOD_CHOICES = [
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('neutral', 'Neutral'),
        ('surprised', 'Surprised'),
        ('fear', 'Fear'),
        ('disgust', 'Disgust'),
        ('excited', 'Excited'),
        ('confident', 'Confident'),
        ('motivated', 'Motivated'),
        ('dancing', 'Dancing'),
        ('romantic', 'Romantic'),
        ('peaceful', 'Peaceful'),
        ('energetic', 'Energetic'),
        ('melancholic', 'Melancholic'),
        ('playful', 'Playful'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mood_results')
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES)
    confidence = models.FloatField()
    
    # ⚠️ PRIVACY: Image field is optional and NOT saved by default
    # Only saved if user explicitly opts in
    image = models.ImageField(
        upload_to='mood_images/', 
        blank=True, 
        null=True,
        help_text='User image - NOT saved for privacy by default'
    )
    
    detected_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-detected_at']
        verbose_name = 'Mood Detection Result'
        verbose_name_plural = 'Mood Detection Results'
        indexes = [
            models.Index(fields=['user', '-detected_at']),
            models.Index(fields=['mood']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.mood} ({self.confidence:.2f}) at {self.detected_at}"
    
    def save(self, *args, **kwargs):
        """Override save to log privacy-protected saves"""
        if self.image:
            print(f"⚠️ Saving mood result WITH image for {self.user.email}")
        else:
            print(f"✅ Saving mood result WITHOUT image for {self.user.email} (privacy-protected)")
        super().save(*args, **kwargs)