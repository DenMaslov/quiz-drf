from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework import filters
from django.db.models import Count

from .filters import TestFilter
from django_filters.rest_framework import DjangoFilterBackend

from .permissions import StaffOnly

from .models import Test, Testrun
from .serializers import (TestrunSerializer, TestSerializer, TestMinSerializer,
                          TestUpdateSerializer,)


class TestListView(generics.ListAPIView):

    queryset = Test.objects.all()

    model = Test
    serializer_class = TestSerializer
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    filterset_class = TestFilter
    ordering_fields = ['created_at', 'title']

    def post(self, request):
        serializer = TestSerializer()
        instance = serializer.create(request.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TestDetailView(generics.RetrieveAPIView):
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

    def patch(self, request, pk):
        testmodel_object = get_object_or_404(Test, id=pk)
        # set partial=True to update a data partially
        serializer = TestUpdateSerializer(
            testmodel_object, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(code=400, data="wrong parameters")

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
    TOP_AMOUNT = 3

    def get_queryset(self):
        return Test.objects.annotate(
            total=Count('testrun')).order_by('-total')[:self.TOP_AMOUNT]


class TestStatListView(generics.ListAPIView):
    model = Test
    serializer_class = TestMinSerializer
    queryset = Test.objects.all()
