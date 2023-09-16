import datetime

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    """
    Question model with date published and date expired
    """
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    end_date = models.DateTimeField('date expired', default=timezone.now() + timezone.timedelta(days=7),
                                    null=True, blank=True)

    def __str__(self):
        """
        Displaying question in text form.
        """
        return self.question_text

    def was_published_recently(self):
        """
        Checks if the question was published recently.
        """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now

    def is_published(self):
        """
        Check if the question is published already or not.
        :return: Bool
        """
        if not self.pub_date:
            return False
        return timezone.localtime(timezone.now()) >= timezone.localtime(self.pub_date)

    def can_vote(self):
        """
        Check whether the question is still running or not.
        :return: Bool
        """
        if self.pub_date <= timezone.now() <= self.end_date:
            return True
        return False


class Choice(models.Model):
    """
    Choice model that act as options for Question
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    #votes = models.IntegerField(default=0)

    @property
    def votes(self):
        """
        Count the votes for this choice.
        """
        #count = Vote.objects.filter(choice=self).count()
        return self.vote_set.count()

    def __str__(self):
        """
        Displaying choices for the question.
        """
        return self.choice_text

class Vote(models.Model):
    """
    Records a Vote of a Choice by a User.
    """
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
