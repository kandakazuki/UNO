from django.db import models
from django.db.models import fields

class BigAutoField(fields.AutoField):
    def db_type(self, connection):
        if 'mysql' in connection.__class__.__module__:
            return 'bigint AUTO_INCREMENT'
        return super(BigAutoField, self).db_type(connection)

class Team(models.Model):
    """書籍"""
    name = models.CharField('チーム名', max_length=255)
    player1 = models.CharField('プレイヤー1', max_length=255)
    player2 = models.CharField('プレイヤー2', max_length=255)
    player3 = models.CharField('プレイヤー3', max_length=255, blank=True)
    player4 = models.CharField('プレイヤー4', max_length=255, blank=True)
    admin = models.CharField('管理者', max_length=255)

    def __str__(self):
        return self.name

class Point(models.Model):
    """得点"""
    team_id = models.CharField('チームID', max_length=255)
    datetime = models.DateTimeField('作成日時', auto_now_add=True)
    player1 = models.IntegerField('プレイヤー1', null=True, blank=True)
    player2 = models.IntegerField('プレイヤー2', null=True, blank=True)
    player3 = models.IntegerField('プレイヤー3', null=True, blank=True)
    player4 = models.IntegerField('プレイヤー4', null=True, blank=True)

    def __str__(self):
        return self.team_id