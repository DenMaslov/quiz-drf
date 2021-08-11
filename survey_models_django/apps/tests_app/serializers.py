from typing import Any
from .models import Option, Question, Answer, Test, Testrun
from django.contrib.auth.models import User
from rest_framework import serializers
from django.utils import timezone

import logging
log = logging.getLogger('app_info')


class OptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('__all__')


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionsSerializer(many=True)
    right_option = OptionsSerializer()

    class Meta:
        model = Question
        fields = ['text', 'right_option', 'options']


class AnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('__all__')


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    created_at = serializers.DateTimeField(
        read_only=True, default=timezone.now)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'title',  'description',
                  'image_src', 'created_at', 'questions', )

    def create(self, validated_data):
        questions = []

        for question in validated_data['questions']:
            option = Option.objects.create(text=question['right_option'])
            text = question['text']
            options = self.get_options(question['options'])
            created_question = Question.objects.create(
                text=text, right_option=option)
            created_question.options.set(options)
            questions.append(created_question)

        test = Test(
            title=validated_data['title'],
            description=validated_data['description'],
            image_src=validated_data['image_src'],
        )
        test.save()
        test.questions.set(questions)
        test.save()
        return test

    def get_options(self, raw_options: list[dict[str, Any]]) -> list[Option]:
        options = []
        for option in raw_options:
            created_option = Option.objects.create(text=option['text'])
            options.append(created_option)
        return options


class TestrunSerializer(serializers.ModelSerializer):

    answers = AnswersSerializer(many=True)

    finished_at = serializers.DateTimeField(
        read_only=True, default=timezone.now)
    points = serializers.IntegerField(read_only=True, default=0)
    is_completed = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Testrun
        fields = ['test', 'answers', 'points',
                  'user', 'finished_at', 'is_completed']

    def create(self, validated_data):
        test = Test.objects.get(id=validated_data['test'])
        user = User.objects.get(id=validated_data['user'])
        points = 0
        answers = []
        is_completed = False

        for answer in validated_data['answers']:
            question = Question.objects.get(id=answer['question'])
            user_answer = Option.objects.get(id=answer['user_answer'])
            created_answer = Answer.objects.create(
                question=question, user_answer=user_answer)
            answers.append(created_answer)
            if self.can_add_point(question, user_answer):
                points += 1

        if len(validated_data['answers']) == len(test.questions.all()):
            is_completed = True

        session = Testrun(
            test=test,
            points=points,
            user=user,
            is_completed=is_completed,
        )
        session.save()  # For many to many session must have an id
        session.answers.set(answers)
        session.save()
        return session

    def can_add_point(self, question: Question, user_answer: Option) -> bool:
        if question.right_option == user_answer:
            return True
        return False


class TestMinSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(
        read_only=True, default=timezone.now)
    id = serializers.IntegerField(read_only=True)
    number_of_sessions = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = ('id', 'number_of_sessions', 'title', 'title_uk',
                  'description', 'image_src', 'created_at', 'questions', )

    def get_number_of_sessions(self, obj):
        return len(Testrun.objects.filter(test=obj))

class TestUpdateSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(
        read_only=True, default=timezone.now)
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Test
        fields = ('id', 'title', 'description',
                  'image_src', 'created_at', 'questions', )
