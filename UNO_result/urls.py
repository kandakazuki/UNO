from django.urls import include, path
from UNO_result import views

app_name = 'UNO_result'
urlpatterns = [
    # 書籍
    path('Team/', views.team_list, name='team_list'),
    path('Team/add/', views.team_add, name='team_add'),
    path('Team/del/<int:team_id>/', views.team_del, name='team_del'),
    path('Team/<int:team_id>/', views.team_sel, name='team_sel'),
    path('Team/<int:team_id>/point/', views.point, name='point'),
    path('Team/<int:team_id>/pointadd/', views.point_add, name='point_add'),
    path('Team/<int:team_id>/dbinsert/', views.dbinsert, name='dbinsert'),
    path('Team/<int:team_id>/dbdelete/', views.dbdelete, name='dbdelete'),
]