from django.shortcuts import render, get_object_or_404
from .models import Program, Event, SuccessStory

def program_list(request):
    programs = Program.objects.all().order_by('-id')
    return render(request, 'programs/program_list.html', {'programs': programs})

def program_detail(request, pk):
    program = get_object_or_404(Program, pk=pk)
    return render(request, 'programs/program_detail.html', {'program': program})

def event_list(request):
    events = Event.objects.all().order_by('date')
    return render(request, 'programs/event_list.html', {'events': events})

def success_stories(request):
    stories = SuccessStory.objects.all().order_by('-date')
    return render(request, 'programs/success_stories.html', {'stories': stories})
