"""Views for index, detail, and result pages."""
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Choice, Question, Vote
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
import logging


class IndexView(generic.ListView):
    """Index view that is displaying top 5 recent questions."""

    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return all published questions."""
        return (Question.objects.filter(pub_date__lte=timezone.now())
                .order_by('-pub_date'))


class DetailView(generic.DetailView):
    """Detail view that displaying choices specially for each question."""

    model = Question
    template_name = 'polls/detail.html'

    def get(self, request, *args, **kwargs):
        """Handle the Get request for the detail view."""
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request,
                           f"Poll number {kwargs['pk']} does not exists.")
            return redirect("kupolls:index")
        if not question.is_published():
            messages.error(self.request,
                           f"Poll number {question.id} is not published yet.")
            return redirect("kupolls:index")
        if not question.can_vote():
            messages.error(self.request,
                           f"Poll number {question.id} "
                           f"is not available to vote.")
            return redirect("kupolls:index")

        user_vote = None
        if request.user.is_authenticated:
            try:
                previous_vote = (Vote.objects.get
                                 (user=request.user, choice__question=question))
                user_vote = previous_vote.choice.id
            except Vote.DoesNotExist:
                user_vote = None

        return render(request, self.template_name, {
            'question': question,
            'user_vote': user_vote,
            'error_message': self.request.GET.get('error_message')
        })


class ResultsView(generic.DetailView):
    """Result view for each question."""

    model = Question
    template_name = 'polls/results.html'

    def get(self, request, *args, **kwargs):
        """Handle the Get request for the result view."""
        try:
            question = get_object_or_404(Question, pk=kwargs["pk"])
        except Http404:
            messages.error(request, f"Poll number {kwargs['pk']} does not exists.")
            return redirect("kupolls:index")
        if not question.is_published():
            messages.error(self.request, f"Result for poll number {question.id} is not available yet.")
            return redirect("kupolls:index")
        return render(request, self.template_name, {"question": question})

logger = logging.getLogger('polls')
@login_required
def vote(request, question_id):
    """Vote for one of the answers to a question."""
    question = get_object_or_404(Question, pk=question_id)
    this_user = request.user

    if not question.can_vote():
        logging.info(f"User {this_user} attempted to vote on question {question_id}, but voting is not allowed.")
        # If voting is not allowed, redisplay the question voting form with an error message.
        return render(request, 'kupolls/detail.html', {
            'question': question,
            'error_message': "Voting is not allowed for this question.",
        })

    choice_id = request.POST.get('choice')

    if choice_id is None:
        # If no choice is selected, redisplay the question voting form with an error message.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'kupolls/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })

    try:
        # find a vote for this user and this question.
        vote = Vote.objects.get(user=this_user, choice__question=question)
        # update his vote
        vote.choice = selected_choice
    except Vote.DoesNotExist:
        # no matching vote - create new Vote
        vote = Vote.objects.create(user=this_user, choice=selected_choice)

    vote.save()
    logger.info(f"User {this_user} successfully voted on question {question_id} for choice {selected_choice.id}.")
    messages.success(request, "Your vote has been recorded")
    return HttpResponseRedirect(reverse('kupolls:results', args=(question.id,)))

def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # x_forwarded_for can contain multiple IPs; take the first one
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '').strip()
    return ip

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log when a user logs in."""
    ip_addr = get_client_ip(request)
    logger.info(f"User {user.username} logged in from IP: {ip_addr}")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log when a user logs out."""
    ip_addr = get_client_ip(request)
    logger.info(f"User {user.username} logged out from IP: {ip_addr}")