from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote


@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if not request.user.is_authenticated:
        #user must login
        return redirect("login")
    if not question.can_vote():
        messages.error(request, "Not available to vote")
        return redirect("polls:index")
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    this_user = request.user
    #selected_choice.votes += 1
    #selected_choice.save()
    try:
        #find a vote for this user and this question.
        vote = Vote.objects.get(user=this_user, choice__question=question)
        #update his vote
        vote.choice = selected_choice
    except Vote.DoesNotExist:
        #no matching vote - create new Vote
        vote = Vote(user=this_user, choice=selected_choice)

    vote.save()
    #do: Use messages to display a confirmation on the results page.

    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


class IndexView(generic.ListView):
    """
    View for index page.
    """
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    """
    View for detail page.
    """
    model = Question
    template_name = 'polls/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def get(self, request, *args, **kwargs):
        """
        This will redirect to home page when,
        1. Question is not published.
        2. Vote is closed.
        """
        question = self.get_object()
        if not question.is_published():
            # Use the Messages Framework to set the error message
            messages.error(request, "Question is not published yet.")
            return redirect("polls:index")  # Redirect to the polls index
        if not question.can_vote():
            messages.error(request, "This vote is closed.")
            return redirect("polls:index")
        return super().get(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    """
    View for results page.
    """
    model = Question
    template_name = 'polls/results.html'
