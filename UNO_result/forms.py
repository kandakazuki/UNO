from django.forms import ModelForm
from UNO_result.models import Team, Point
from django import forms
from django.shortcuts import render, get_object_or_404, redirect

class TeamForm(ModelForm):
    """チームを作成するフォーム"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admin'].widget = forms.HiddenInput()

    class Meta:
        model = Team
        fields = ('name', 'player1', 'player2', 'player3', 'player4', 'admin',)

class PointForm(ModelForm):
    """ポイントを加算するフォーム"""
    class Meta:
        model = Point
        fields = ('team_id', 'player1', 'player2', 'player3', 'player4',)

def user_check(team_id, request_user):
    team_info = Team.objects.get(pk=team_id)
    check = (team_info.admin == request_user)
    return check