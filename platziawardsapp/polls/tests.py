import datetime

from django.test import TestCase
from django.urls.base import reverse
from django.utils import timezone

from .models import Question


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_questions(self):
        """Was published recently retuns False for questions whose pub_date is in the future"""    
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(question_text="¿Quien es el mejor Course Director de Platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)
        
    def test_was_published_recently_with_present_question(self):
        """Was published recently retuns False for questions whose pub_date is in the present"""
        time = timezone.now()
        present_question = Question(question_text="¿Quien es el mejor profesor de platzi?", pub_date=time)
        self.assertIs(present_question.was_published_recently(), True)

    def test_was_published_recently_with_past_question(self):
        time = timezone.now() - datetime.timedelta(days=2)
        past_question = Question(question_text="¿Quien es el mejor profe de platzi?", pub_date=time)
        self.assertIs(past_question.was_published_recently(), False)

    def create_question(question_text, days):
        """
        Create a question with the given "question_text",
        and published the given number of days offset to now
        (negative for questions published ih the past positive
        for questions that have yet to be published)
        """
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)

class QuestionIndexViewTests(TestCase):
    
    def test_no_questions(self):
        """If no question exist, an appropiate message is displayed"""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_future_questions(self):
        """ Questions with a pub_date in the future aren't displayed on the index"""
        QuestionModelTests.create_question("Future questions", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])

    def test_past_questions(self):
        """ Questions with pub_date in the past are displayed"""
        question = QuestionModelTests.create_question("Past question", days=-20)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question])

    def test_future_question_and_past_question(self):
        """
        Created two questions, one in the future and other in the past,
        this test must be return one questions
        """
        future = QuestionModelTests.create_question("Future question", days=20)
        past = QuestionModelTests.create_question("Past question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [past])

    def test_text_two_past_question(self):
        """Created two question in past, this test must be return two correct questions""" 
        question_one = QuestionModelTests.create_question("Fist question", days=-20)
        question_two = QuestionModelTests.create_question("Second question", days=-10)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"], [question_two, question_one])    

    def test_two_questions_in_future(self):
        """Created two questions in the future and should return emply list"""
        QuestionModelTests.create_question("First future question", days=30)
        QuestionModelTests.create_question("Second future question", days=30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"], [])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a questions with the pub_date in the future
        retuns a 404 error not found
        """
        future = QuestionModelTests.create_question("Future question", days=20)
        url = reverse("polls:detail", args=(future.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        
    
    def test_past_question(self):
        """
        The detail view of a questions with a pub_date in the past 
        displays the questions's text
        """
        past = QuestionModelTests.create_question("Past question", days=-20)
        url = reverse("polls:detail", args=(past.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, past.question_text)
    
    