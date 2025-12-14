from django import forms
from .models import UserExerciseAttempt

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = UserExerciseAttempt
        fields = ['audio_file', 'duration']
        widgets = {
            'audio_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'audio/*',
                'id': 'audioFileInput',
                'hidden': True
            }),
            'duration': forms.NumberInput(attrs={
                'id': 'durationInput',
                'hidden': True
            })
        }