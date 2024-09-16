"""Models for the Question and Choice in the poll application."""
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

DEFAULT_END_DATE = 7
RECENTLY_PUBLISHED_DAYS = 1


def default_end_date():
    """Return the default end_date which is 7 days after the current time."""
    return (timezone.localtime(timezone.now())
            + timezone.timedelta(days=DEFAULT_END_DATE))


class Question(models.Model):
    """Represents a poll question in the database."""

    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField(
        'date expired',
        default=default_end_date,
        null=True,
        blank=True
    )

    def __str__(self):
        """Return the question text."""
        return self.question_text

    def was_published_recently(self):
        """
        Return True if the question was published within recently defined days.

        Else return False.
        """
        now = timezone.localtime(timezone.now())
        return (now - timezone.timedelta(days=RECENTLY_PUBLISHED_DAYS)
                <= self.pub_date <= now)

    def is_published(self):
        """Return True if the question is published, otherwise False."""
        now = timezone.localtime(timezone.now())
        return now >= self.pub_date

    def can_vote(self):
        """Return True if the question is open for voting, otherwise False."""
        now = timezone.localtime(timezone.now())
        if self.end_date is None:
            return self.pub_date <= now
        return self.pub_date <= now <= self.end_date


class Choice(models.Model):
    """Represents a choice for a specific poll question in the database."""

    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    @property
    def votes(self):
        """Return the number of votes for this choice."""
        return Vote.objects.filter(choice=self).count()

    def __str__(self):
        """Return the choice text."""
        return self.choice_text


class Vote(models.Model):
    """Represents a vote by a user for a specific choice in a poll."""

    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """Return a string representation of the vote."""
        return f'{self.user} voted for {self.choice}'
