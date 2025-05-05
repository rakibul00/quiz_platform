from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Quiz, Question, Answer, StudentAnswer

admin.site.register(User, UserAdmin)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(StudentAnswer)