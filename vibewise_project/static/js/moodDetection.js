// Mood detection using Face-API.js
class MoodDetection {
    static detectionInterval = null;
    static isActive = false;
    static confidenceThreshold = 0.6;

    static async startDetection() {
        if (this.isActive) return;
        
        this.isActive = true;
        this.detectionInterval = setInterval(() => {
            this.detectMood();
        }, 1000); // Check every second
    }

    static stopDetection() {
        this.isActive = false;
        if (this.detectionInterval) {
            clearInterval(this.detectionInterval);
            this.detectionInterval = null;
        }
    }

    static async detectMood() {
        const video = Camera.getVideoElement();
        if (!video || video.videoWidth === 0) return;

        try {
            const detections = await faceapi
                .detectAllFaces(video, new faceapi.TinyFaceDetectorOptions())
                .withFaceExpressions();

            if (detections.length > 0) {
                const expressions = detections[0].expressions;
                const dominantMood = this.getDominantExpression(expressions);
                
                if (dominantMood.confidence > this.confidenceThreshold) {
                    this.updateMoodDisplay(dominantMood.mood, dominantMood.confidence);
                    window.vibeWise.updateMood(dominantMood.mood);
                }
            }
        } catch (error) {
            console.error('Mood detection error:', error);
        }
    }

    static getDominantExpression(expressions) {
        const emotions = {
            happy: expressions.happy,
            sad: expressions.sad,
            angry: expressions.angry,
            surprised: expressions.surprised,
            neutral: expressions.neutral,
            disgusted: expressions.disgusted,
            fearful: expressions.fearful
        };

        let maxConfidence = 0;
        let dominantMood = 'neutral';

        for (const [mood, confidence] of Object.entries(emotions)) {
            if (confidence > maxConfidence) {
                maxConfidence = confidence;
                dominantMood = mood;
            }
        }

        return { mood: dominantMood, confidence: maxConfidence };
    }

    static updateMoodDisplay(mood, confidence) {
        const moodText = document.getElementById('detectedMood');
        const confidenceText = document.getElementById('confidence');
        
        if (moodText) moodText.textContent = mood.charAt(0).toUpperCase() + mood.slice(1);
        if (confidenceText) confidenceText.textContent = `${(confidence * 100).toFixed(1)}%`;
    }

    static getMoodColor(mood) {
        const colors = {
            happy: '#FFD700',
            sad: '#4682B4',
            angry: '#FF6B6B',
            surprised: '#FF8C00',
            neutral: '#808080',
            disgusted: '#8B4513',
            fearful: '#9370DB'
        };
        return colors[mood] || '#808080';
    }
}

window.MoodDetection = MoodDetection;