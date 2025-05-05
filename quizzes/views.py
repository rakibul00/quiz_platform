from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .models import User, Quiz, Question, Answer, StudentAnswer
from .forms import (StudentRegistrationForm, TeacherRegistrationForm,QuizForm, QuestionForm, AnswerForm)
from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer
from .forms import QuestionForm


def home(request):
    return render(request, 'quizzes/home.html')

def register_student(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('student_dashboard')
    else:
        form = StudentRegistrationForm()
    return render(request, 'quizzes/register_student.html', {'form': form})

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('teacher_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'quizzes/register_teacher.html', {'form': form})


from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('home') 


@login_required
def student_dashboard(request):
    if not request.user.is_student:
        return redirect('home')
    quizzes = Quiz.objects.all()
    return render(request, 'quizzes/student_dashboard.html', {'quizzes': quizzes})

@login_required
def teacher_dashboard(request):
    if not request.user.is_teacher:
        return redirect('home')
    quizzes = Quiz.objects.filter(teacher=request.user)
    return render(request, 'quizzes/teacher_dashboard.html', {'quizzes': quizzes})

@login_required
def create_quiz(request):
    if not request.user.is_teacher:
        return redirect('home')
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.teacher = request.user
            quiz.save()
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        form = QuizForm()
    return render(request, 'quizzes/create_quiz.html', {'form': form})

@login_required
def add_questions(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            question.save()

            # Save answers
            answers = []
            for i in range(1, 5):  # 4 answers
                answer_text = request.POST.get(f'answer_{i}')
                if not answer_text:  # Check if the answer text is empty
                    question.delete()  # Rollback the question save
                    return render(request, 'quizzes/add_questions.html', {
                        'quiz': quiz,
                        'question_form': question_form,
                        'questions': quiz.questions.prefetch_related('answers').all(),
                        'answer_range': range(1, 5),
                        'error': f"Answer {i} cannot be empty.",
                    })
                is_correct = request.POST.get('is_correct') == str(i)
                answers.append(Answer(
                    question=question,
                    text=answer_text,
                    is_correct=is_correct
                ))
            Answer.objects.bulk_create(answers)  # Save all answers at once
            return redirect('add_questions', quiz_id=quiz.id)
    else:
        question_form = QuestionForm()

    questions = quiz.questions.prefetch_related('answers').all()
    return render(request, 'quizzes/add_questions.html', {
        'quiz': quiz,
        'question_form': question_form,
        'questions': questions,
        'answer_range': range(1, 5),  # Pass range(1, 5) for 4 answers
    })

@login_required
def take_quiz(request, quiz_id):
    if not request.user.is_student:
        return redirect('home')
    
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions = quiz.questions.all()
    
    if request.method == 'POST':
        for question in questions:
            answer_id = request.POST.get(f'question_{question.id}')
            if answer_id:
                answer = Answer.objects.get(id=answer_id)
                StudentAnswer.objects.update_or_create(
                    student=request.user,
                    question=question,
                    defaults={'answer': answer}
                )
        return redirect('quiz_results', quiz_id=quiz.id)
    
    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })

from django.shortcuts import render, get_object_or_404
from .models import Quiz, Question, StudentAnswer

def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    student_answers = StudentAnswer.objects.filter(student=request.user, question__quiz=quiz)
    results = []

    for question in quiz.questions.all():
        student_answer = student_answers.filter(question=question).first()
        correct_answer = question.answers.filter(is_correct=True).first()
        results.append({
            'question': question,
            'student_answer': student_answer,
            'is_correct': student_answer and student_answer.answer.is_correct,
            'correct_answer': correct_answer,
        })

    correct = sum(1 for result in results if result['is_correct'])
    total = quiz.questions.count()
    score = (correct / total) * 100 if total > 0 else 0

    return render(request, 'quizzes/quiz_results.html', {
        'quiz': quiz,
        'results': results,
        'correct': correct,
        'total': total,
        'score': score,
    })
    
    
    
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Quiz
from .forms import QuizForm

@login_required
def edit_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            return redirect('teacher_dashboard')  # Redirect to the teacher dashboard after editing
    else:
        form = QuizForm(instance=quiz)
    return render(request, 'quizzes/edit_quiz.html', {'form': form, 'quiz': quiz})

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Question

@login_required
def delete_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if request.method == 'POST':
        quiz.delete()
        return redirect('teacher_dashboard')  # Redirect to the teacher dashboard after deletion
    return render(request, 'quizzes/delete_quiz.html', {'quiz': quiz})