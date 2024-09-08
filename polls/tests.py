import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, User, Choice, Vote


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
        is_published() returns False for questions with a pub_date in the future.
        """
        future_pub_date = timezone.localtime(timezone.now() + datetime.timedelta(days=5))
        future_question = Question(pub_date=future_pub_date)
        self.assertFalse(future_question.is_published())

    def test_is_published_with_now_pub_date(self):
        """
        is_published() returns True for questions with the pub_date set to now.
        """
        now_pub_date = timezone.localtime(timezone.now())
        now_question = Question(pub_date=now_pub_date)
        self.assertTrue(now_question.is_published())

    def test_is_published_with_past_pub_date(self):
        """
        is_published() returns True for questions with a pub_date in the past.
        """
        past_pub_date = timezone.localtime(timezone.now() - datetime.timedelta(days=5))
        past_question = Question(pub_date=past_pub_date)
        self.assertTrue(past_question.is_published())

    def test_can_vote_with_no_end_date(self):
        """
        can_vote() returns True if the end_date is None and pub_date is in the past.
        """
        past_pub_date = timezone.localtime(timezone.now() - datetime.timedelta(days=5))
        no_end_date_question = Question(pub_date=past_pub_date, end_date=None)
        self.assertTrue(no_end_date_question.can_vote())

    def test_can_vote_with_past_end_date(self):
        """
        can_vote() returns False if the end_date is in the past.
        """
        past_pub_date = timezone.localtime(timezone.now() - datetime.timedelta(days=5))
        past_end_date_question = Question(
            pub_date=past_pub_date,
            end_date=timezone.localtime(timezone.now() - datetime.timedelta(days=1))
        )
        self.assertFalse(past_end_date_question.can_vote())

    def test_can_vote_with_current_end_date(self):
        """
        can_vote() returns True if the current date is within the pub_date and end_date range.
        """
        past_pub_date = timezone.localtime(timezone.now() - datetime.timedelta(days=5))
        future_end_date = timezone.localtime(timezone.now() + datetime.timedelta(days=5))
        current_end_date_question = Question(
            pub_date=past_pub_date,
            end_date=future_end_date
        )
        self.assertTrue(current_end_date_question.can_vote())

    def test_can_vote_with_future_end_date(self):
        """
        can_vote() returns True if the end_date is in the future and pub_date is in the past.
        """
        past_pub_date = timezone.localtime(timezone.now() - datetime.timedelta(days=5))
        future_end_date = timezone.localtime(timezone.now() + datetime.timedelta(days=10))
        future_end_date_question = Question(
            pub_date=past_pub_date,
            end_date=future_end_date
        )
        self.assertTrue(future_end_date_question.can_vote())

def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('kupolls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a pub_date in the past are displayed on the
        index page.
        """
        question = create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('kupolls:index'))
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
        response = self.client.get(reverse('kupolls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.
        """
        question = create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('kupolls:index'))
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
        response = self.client.get(reverse('kupolls:index'))
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            [question2, question1],
        )

class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question(question_text='Future question.', days=5)
        url = reverse('kupolls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertRedirects(response, reverse('kupolls:index'))

    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays the question's text.
        """
        past_question = create_question(question_text='Past Question.', days=-5)
        url = reverse('kupolls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)


class VoteModelTests(TestCase):
    def setUp(self):
        """
        Set up a test user, question, and choices.
        """
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.question = Question.objects.create(
            question_text="What's your favorite color?",
            pub_date=timezone.now(),
            end_date=timezone.now() + timezone.timedelta(days=7)
        )
        self.choice1 = Choice.objects.create(question=self.question, choice_text="Blue")
        self.choice2 = Choice.objects.create(question=self.question, choice_text="Red")

    def test_vote_creation(self):
        """
        Test that a new vote can be created.
        """
        self.client.login(username='testuser', password='12345')
        vote = Vote.objects.create(user=self.user, choice=self.choice1)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(vote.choice, self.choice1)
        self.assertEqual(vote.user, self.user)

    def test_vote_update(self):
        """
        Test that a vote can be updated by the user.
        """
        self.client.login(username='testuser', password='12345')
        Vote.objects.create(user=self.user, choice=self.choice1)
        vote = Vote.objects.get(user=self.user, choice=self.choice1)
        vote.choice = self.choice2
        vote.save()
        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(vote.choice, self.choice2)

    def test_vote_count(self):
        """
        Test that the Choice.votes property correctly counts votes.
        """
        self.client.login(username='testuser', password='12345')
        Vote.objects.create(user=self.user, choice=self.choice1)
        self.assertEqual(self.choice1.votes, 1)
        self.assertEqual(self.choice2.votes, 0)
        vote = Vote.objects.get(user=self.user, choice=self.choice1)
        vote.choice = self.choice2
        vote.save()
        self.assertEqual(self.choice1.votes, 0)
        self.assertEqual(self.choice2.votes, 1)

