"""Views for index, detail, and result pages."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from .models import Choice, Question

class IndexView(generic.ListView):
    """
    Index view that is displaying top 5 recent questions.
    """

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions.
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """
    Detail view that displaying choices specially for each question.
    """

    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, *args, **kwargs):
        """
        Handle the Get request for the detail view.
        """
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request, f"Poll number {kwargs['pk']} does not exists.")
            return redirect("kupolls:index")
        if not question.is_published():
            messages.error(self.request, f"Poll number {question.id} is not published yet.")
            return redirect("kupolls:index")
        if not question.can_vote():
            messages.error(self.request, f"Poll number {question.id} is not available to vote.")
            return redirect("kupolls:index")
        return render(request, self.template_name, {"question": question})

class ResultsView(generic.DetailView):
    """
    Result view for each question.
    """

    model = Question
    template_name = 'polls/results.html'

    def get(self, request, *args, **kwargs):
        """
        Handle the Get request for the result view.
        """
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request, f"Poll number {kwargs['pk']} does not exists.")
            return redirect("kupolls:index")
        if not question.is_published():
            messages.error(self.request, f"Result for poll number {question.id} is not available yet.")
            return redirect("kupolls:index")
        return render(request, self.template_name, {"question": question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)

    if not question.can_vote():
        # If voting is not allowed, redisplay the question voting form with an error message.
        return render(request, 'kupolls/detail.html', {
            'question': question,
            'error_message': "Voting is not allowed for this question.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'kupolls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('kupolls:results', args=(question.id,)))