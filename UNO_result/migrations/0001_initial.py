# Generated by Django 3.0.4 on 2020-04-09 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('team_id', models.CharField(max_length=255, verbose_name='チームID')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='作成日時')),
                ('player1', models.IntegerField(blank=True, null=True, verbose_name='プレイヤー1')),
                ('player2', models.IntegerField(blank=True, null=True, verbose_name='プレイヤー2')),
                ('player3', models.IntegerField(blank=True, null=True, verbose_name='プレイヤー3')),
                ('player4', models.IntegerField(blank=True, null=True, verbose_name='プレイヤー4')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='チーム名')),
                ('player1', models.CharField(max_length=255, verbose_name='プレイヤー1')),
                ('player2', models.CharField(max_length=255, verbose_name='プレイヤー2')),
                ('player3', models.CharField(blank=True, max_length=255, verbose_name='プレイヤー3')),
                ('player4', models.CharField(blank=True, max_length=255, verbose_name='プレイヤー4')),
                ('admin', models.CharField(max_length=255, verbose_name='管理者')),
            ],
        ),
    ]
