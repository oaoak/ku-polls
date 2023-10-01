import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question, Choice, Vote


def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date
        is within the last day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_is_published_with_future_pub_date(self):
        """
        is_published() should return False for a question with a future pub date.
        """
        future_pub_date = timezone.now() + datetime.timedelta(days=7)
        future_question = Question(pub_date=future_pub_date)
        self.assertIs(future_question.is_published(), False)

    def test_is_published_with_default_pub_date(self):
        """
        is_published() should return True for a question with the default pub date (now).
        """
        current_pub_date = timezone.now()
        current_question = Question(pub_date=current_pub_date)
        self.assertIs(current_question.is_published(), True)

    def test_is_published_with_past_pub_date(self):
        """
        is_published() should return True for a question with a pub date in the past.
        """
        past_pub_date = timezone.now() - datetime.timedelta(days=7)
        past_question = Question(pub_date=past_pub_date)
        self.assertIs(past_question.is_published(), True)

    def test_can_vote_future_question(self):
        """
        can_vote() should return True for a question with a future end_date.
        """
        future_end_date = timezone.now() + datetime.timedelta(days=5)
        future_question = Question(end_date=future_end_date)
        self.assertIs(future_question.can_vote(), True)

    def test_can_vote_past_question(self):
        """
        can_vote() should return False for a question with a past end_date.
        """
        past_end_date = timezone.now() - datetime.timedelta(days=5)
        past_question = Question(end_date=past_end_date)
        self.assertIs(past_question.can_vote(), False)

    def test_can_vote_current_question(self):
        """
        can_vote() should return True for a question with a current end_date.
        """
        current_end_date = timezone.now() + datetime.timedelta(days=2)
        current_question = Question(end_date=current_end_date)
        self.assertIs(current_question.can_vote(), True)

    def test_can_vote_question_ends_today(self):
        """
        can_vote() should return True for a question with an end_date set to today.
        """
        end_date_today = timezone.now()
        question = Question(end_date=end_date_today + datetime.timedelta(days=1))
        self.assertIs(question.can_vote(), True)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_future_question(self):
        """
        Questions with a pub_date in the future aren't displayed on
        the index page.
        """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question],
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        question1 = create_question(question_text="Past question 1.", days=-30)
        question2 = create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )


class QuestionDetailViewTests(TestCase):

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class VoteAuthenticationTests(TestCase):
    def setUp(self):
        """
        Set up the necessary data for the test cases.
        """
        self.test_user = User.objects.create_user(username='testuser', password='testpassword')
        self.question = create_question("Test question", days=-1)
        self.choice = Choice.objects.create(choice_text="Choice 1", question=self.question)

    def test_authenticated_user_can_vote(self):
        """
        Test that an authenticated user can successfully vote on a question.
        """
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('polls:results', args=(self.question.id,)))

    def test_unauthenticated_user_redirected_to_login(self):
        """
        Test that an unauthenticated user is redirected to the login page when attempting to vote.
        """
        response = self.client.post(reverse('polls:vote', args=(self.question.id,)), {'choice': self.choice.id})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + f'?next={reverse("polls:vote", args=(self.question.id,))}')
