from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from UNO_result.models import Team, Point
from django.db.models import Avg, Max, Min, Sum, Count, F
from django.db.models.functions import RowNumber
from django.db.models.expressions import Window
from UNO_result.forms import TeamForm, PointForm, user_check
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin #クラスの場合
from django.contrib.auth.decorators import login_required #函数の場合
import numpy as np
import datetime

@login_required
def team_list(request):
    '''自身が管理者となっているチームのリストを表示'''
    teams = Team.objects.filter(admin=request.user.username) #admin=...で自身が管理者となるものに絞る
    user = request.user
    return render(request,
                  'UNO_result/team_list.html',
                  {'teams': teams})


@login_required
def team_sel(request, team_id):
    '''チームのポイントを表示'''
    '''
    自身が管理者出ないチームのポイントは表示させない
    user_checkでログインユーザとチームの管理者が一致しているか確認し、一致している場合のみ表示
    　→一致していなければチームリストにリダイレクト
    '''
    if not user_check(team_id, request.user.username):
        return redirect('/UNO_result/Team/')

    '''
    Point情報を抽出
    ・自身のチームのデータのみ抽出
    ・ユーザの選択により、直近24時間(today) or 全データ(all)で抽出
    ・データの格納順（datetime順）にrow numberを降ったものがround（何回目のゲームか）になる
    '''
    view = request.POST.get('view') #直近1日表示（today）か全日表示（all）が格納
    #現在viewで選択されている方に'selected'を格納。htmlで表示する際にはその値を表示する。
    view_selected = {
        'today': 'selected' if 'today' == request.POST.get('view') else '',
        'all': 'selected' if 'all' == request.POST.get('view') else ''
    }
    now = datetime.datetime.now()
    if view == 'today':
        target_datetime = now + datetime.timedelta(days=-1) #直近24時間に絞ってPointを抽出
    else:
        target_datetime = now + datetime.timedelta(days=-3650) #全日（直近10年）に絞ってPointを抽出
    point_detail = Point.objects.filter(team_id=team_id, datetime__gte=target_datetime).annotate(
        row_number=Window(
            expression=RowNumber(),
            order_by=F('datetime').asc())
    ).order_by('datetime') #各ラウンド毎のポイントデータ


    '''
    pointデータの削除
    　→roundとPointテーブル嬢のidを合わせて格納
    '''
    round = [{'id': data.id, 'row_number': data.row_number} for data in point_detail] #round(row_number)とPointテーブルのidを格納。idは対象データを削除する際に必要。

    '''
    グラフ形式での得点表示
    '''
    # グラフでの表示用。x軸に該当するため、最初の値に0を追加。
    x = [0] + [data.row_number for data in point_detail]
    # グラフでの表示用。y軸に該当するため累計値を計算し、最初の値に0を追加。
    player1_score = np.cumsum([0] + [0 if data.player1 is None else data.player1 for data in point_detail]).tolist()
    player2_score = np.cumsum([0] + [0 if data.player2 is None else data.player2 for data in point_detail]).tolist()
    player3_score = np.cumsum([0] + [0 if data.player3 is None else data.player3 for data in point_detail]).tolist()
    player4_score = np.cumsum([0] + [0 if data.player4 is None else data.player4 for data in point_detail]).tolist()
    #y軸で表示する際の表示名、値、色を定義
    team_info = Team.objects.get(pk=team_id)
    y = [
        {'name': team_info.player1, 'score': player1_score, 'bdcolor': 'rgba(70, 130, 180, 1)', 'bgcolor': 'rgba(70, 130, 180, 0.1)'},
        {'name': team_info.player2, 'score': player2_score, 'bdcolor': 'rgba(255, 99, 71, 1)', 'bgcolor': 'rgba(255, 99, 71, 0.1)'},
        {'name': team_info.player3, 'score': player3_score, 'bdcolor': 'rgba(46, 139, 87, 1)', 'bgcolor': 'rgba(46, 139, 87, 0.1)'},
        {'name': team_info.player4, 'score': player4_score, 'bdcolor': 'rgba(105, 105, 105, 1)', 'bgcolor': 'rgba(105, 105, 105, 0.1)'},
    ]

    '''
    表形式でのポイント、プレイ回数の表示
    '''
    count = len(point_detail)  # プレイ回数
    point_dict = {
        team_info.player1: player1_score[-1], #player1の名前、得点を格納
        team_info.player2: player2_score[-1], #player2の名前、得点を格納
        team_info.player3: player3_score[-1], #player3の名前、得点を格納
        team_info.player4: player4_score[-1], #player4の名前、得点を格納
    }
    point_list = sorted(point_dict.items(), key=lambda x: x[1], reverse=True) #得点の高い順に表示するため、得点で降順ソート。

    context = {
        'round': round,
        'count': count,
        'team_info': team_info,
        'team_id': team_id,
        'x': x,
        'y': y,
        'point_list': point_list,
        'view_selected': view_selected
    }
    return render(request,
        'UNO_result/point_view.html',     # 使用するテンプレート
        context)  # テンプレートに渡すデータ


@login_required
def team_add(request, team_id=None):
    '''チームの追加'''
    '''
    POSTで来る際は追加するチーム情報入力後。
    内容に問題がなければDBに格納する。
    POSTでない場合はチーム情報入力前（他ページからの遷移）
    adminユーザ（今ログイン中のユーザ）を自動設定し、入力画面に飛ばす
    '''
    team = Team()
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)  # POST された request データからフォームを作成
        if form.is_valid():    # フォームのバリデーション
            team = form.save(commit=False)
            team.save()
            return redirect('UNO_result:team_list')
    else:
        form = TeamForm(instance=team, initial={'admin': request.user})  # teamインスタンスからフォームを作成

    return render(request, 'UNO_result/team_edit.html', dict(form=form, team_id=team_id))

@login_required
def team_del(request, team_id):
    '''チームの削除'''
    if not user_check(team_id, request.user.username):
        return redirect('/UNO_result/Team/')
    team = get_object_or_404(Team, pk=team_id)
    team.delete()
    return redirect('UNO_result:team_list')


@login_required
def point(request, team_id):
    if not user_check(team_id, request.user.username):
        return redirect('/UNO_result/Team/')
    """書籍の一覧"""
    team_info = Team.objects.get(pk=team_id)
    request.session['player1'] = 0
    request.session['player2'] = 0
    request.session['player3'] = 0
    request.session['player4'] = 0
    context = {
        'team_info': team_info,
        'player1': 0,
        'player2': 0,
        'player3': 0,
        'player4': 0
    }
    return render(request, 'UNO_result/point.html', context)


@login_required
def point_add(request, team_id):
    if not user_check(team_id, request.user.username):
        return redirect('/UNO_result/Team/')
    team_info = Team.objects.get(pk=team_id)
    request.session[request.POST.get('player')] += int(request.POST.get('point'))
    context = {
        'team_info': team_info,
        'player1': request.session['player1'],
        'player2': request.session['player2'],
        'player3': request.session['player3'],
        'player4': request.session['player4'],
        'player1_selected': 'selected' if 'player1' == request.POST.get('player') else '',
        'player2_selected': 'selected' if 'player2' == request.POST.get('player') else '',
        'player3_selected': 'selected' if 'player3' == request.POST.get('player') else '',
        'player4_selected': 'selected' if 'player4' == request.POST.get('player') else ''
    }
    return render(request, 'UNO_result/point.html', context)


@login_required
def dbinsert(request, team_id):
    if not user_check(team_id, request.user.username):
        return redirect('/UNO_result/Team/')
    if request.method == 'POST':
        point = Point()
        form = PointForm(request.POST, instance=point)
        if form.is_valid():
            point = form.save(commit=False)
            point.save()
            return redirect('/UNO_result/Team/{}/'.format(team_id))


@login_required
def dbdelete(request, team_id):
    if not user_check(team_id, request.user.username):
        return redirect('/UNO_result/Team/')
    id = request.POST.get('id')
    Point.objects.filter(id=id).delete()
    return redirect('/UNO_result/Team/{}/'.format(team_id))

