import logging

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.db.models import Count


from django.db.models import Q
from .forms import ModelForm
from django.utils import timezone
from .models import Test, Testrun
from .serializers import (TestrunSerializer, TestSerializer, TestMinSerializer,
                          TestUpdateSerializer,)

from rest_framework import status
from rest_framework.response import Response


log = logging.getLogger('app_info')


class TestDetailView(generics.RetrieveAPIView):
    model = Test
    serializer_class = TestSerializer

    def get_object(self, queryset=None, **kwargs):
        id = self.kwargs.get('pk')
        return get_object_or_404(Test, id=id)

    def put(self, request, pk, format=None):
        test = Test.objects.get(id=pk)
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
        return Testrun.objects.filter(
            test__id=self.request.resolver_match.kwargs['pk']).order_by('-finished_at')


class TestScoreView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    model = Testrun
    serializer_class = TestrunSerializer

    def get_queryset(self):
        return Testrun.objects.filter(
            user__id=self.request.user.id).order_by('-finished_at')


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
        for testrun in testruns:
            tests.append(testrun.test)
        return tests


class TestStatListView(generics.ListAPIView):
    model = Test
    serializer_class = TestMinSerializer
    queryset = Test.objects.all()


class TestListView(generics.ListAPIView):

    OLD_DATE = "1970-01-01 12:00:00"
    ORDER_FIELD = "created_at"

    model = Test
    serializer_class = TestSerializer

    def post(self, request):
        serializer = TestSerializer()
        instance = serializer.create(request.data)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_context_data(self, **kwargs):
        context = super(TestListView, self).get_context_data(**kwargs)
        context['form'] = ModelForm()
        return context

    def get_queryset(self):
        search = self.request.GET.get("search", None)
        suffix_order = self.request.GET.get("order", "")
        date_from, date_to = self.get_clean_time_ranges()

        log.debug(
            f'Return Tests search: {search}; ranges: {date_from}, {date_to}')
        if search:
            return Test.objects.filter(Q(title_en__icontains=search) | Q(title_uk__icontains=search),
                                       created_at__range=[date_from, date_to]).order_by(
                suffix_order + self.ORDER_FIELD)
        return Test.objects.filter(
            created_at__range=[date_from, date_to]).order_by(
                suffix_order + self.ORDER_FIELD)

    def get_clean_time_ranges(self):
        """Returns date_from and date_to"""
        date_from = self.request.GET.get("from_date", self.OLD_DATE)
        date_to = self.request.GET.get("to_date", timezone.now())
        if date_to == "":
            date_to = timezone.now()
        if date_from == "":
            date_from = self.OLD_DATE
        return date_from, date_to
