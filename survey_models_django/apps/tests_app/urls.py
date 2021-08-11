from django.urls import path
from .views import (TestListView,
                    TestDetailView,
                    TestSessionView,
                    TestSessionHistoryView,
                    TestScoreView,
                    TestTopListView,
                    TestStatListView,
                    )


urlpatterns = [
    path('', TestListView.as_view(), name='tests_list'),
    path('myscores/', TestScoreView.as_view(), name='myscores'),
    path('<int:pk>/', TestDetailView.as_view(), name='post_detail'),
    path('sessions/', TestSessionView.as_view(), name='start_session'),
    path('history/<int:pk>/', TestSessionHistoryView.as_view(), name='history'),
    path('top/', TestTopListView.as_view(), name='top_list'),
    path('stat/', TestStatListView.as_view(), name='stat_list'),
    
]
