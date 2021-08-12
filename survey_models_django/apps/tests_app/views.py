import logging

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Count
from collections.abc import Iterable

from .filters import TestFilter
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import StaffOnly

from .models import Test, Testrun
from .serializers import (TestrunSerializer, TestSerializer, TestMinSerializer,
                          TestUpdateSerializer,)

from rest_framework import status
from rest_framework.response import Response


log = logging.getLogger('app_info')


class TestListView(generics.ListAPIView):

    queryset = Test.objects.all()

    model = Test
    serializer_class = TestSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TestFilter

    def post(self, request):
        serializer = TestSerializer()
        instance = serializer.create(request.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestDetailView(generics.RetrieveAPIView):
    model = Test
    serializer_class = TestSerializer
    permission_classes = [StaffOnly]

    def get_object(self, queryset=None, **kwargs):
        id = self.kwargs.get('pk')
        return get_object_or_404(Test, id=id)

    def put(self, request, pk, format=None):
        test = get_object_or_404(Test, id=pk)
        serializer = TestUpdateSerializer(test, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        test = Test.objects.get(id=pk)
        test.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TestSessionView(generics.ListAPIView):
    model = Testrun
    serializer_class = TestrunSerializer
    queryset = Testrun.objects.all().order_by('-finished_at')

    def post(self, request):
        serializer = TestrunSerializer()
        instance = serializer.create(request.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestSessionHistoryView(generics.ListAPIView):
    model = Testrun
    serializer_class = TestrunSerializer

    def get_queryset(self):
        return Testrun.objects.filter(test=self.kwargs['pk'])


class TestScoreView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Testrun
    serializer_class = TestrunSerializer

    def get_queryset(self):
        return get_object_or_404(Testrun.objects.filter(
            user__id=self.request.user.id).order_by('-finished_at'))


class TestTopListView(generics.ListAPIView):
    model = Test
    serializer_class = TestMinSerializer

    def get_queryset(self):
        tests = self.get_most_popular_test(3)
        return tests

    def get_most_popular_test(self, top: int) -> list[int]:
        testruns = Testrun.objects.annotate(
            total=Count('test')).order_by('total')[:top]
        tests = []
        if isinstance(testruns, Iterable):
            for testrun in testruns:
                tests.append(testrun.test)
            return tests
        return testruns.test


class TestStatListView(generics.ListAPIView):
    model = Test
    serializer_class = TestMinSerializer
    queryset = Test.objects.all()
