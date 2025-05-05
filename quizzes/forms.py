from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Quiz, Question, Answer

class StudentRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True
        if commit:
            user.save()
        return user

class TeacherRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_teacher = True
        if commit:
            user.save()
        return user

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ('title',)

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('text',)

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text', 'is_correct')