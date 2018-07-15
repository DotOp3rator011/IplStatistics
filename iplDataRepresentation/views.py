from django.shortcuts import render
from .models import *
from django.db.models import Count, Q, Sum, F
from copy import deepcopy


# Util Code-------------------------------------------------------------------------------------------------------------


def get_x_y(dictionary, x_label, y_label):
    x = list()
    y = list()
    for item in dictionary:
        x.append(item[x_label])
        y.append(item[y_label])
    return x, y


def get_x_y_sorted(bowler_economy):
    x = list()
    y = list()
    for key in sorted(bowler_economy.keys(), key=bowler_economy.get):
        x.append(key)
        y.append(bowler_economy[key])
    return x, y


def get_color(index):
    colors = ['Black',
              'Yellow',
              'Fuchsia',
              'Red',
              'Silver',
              'Gray',
              'Olive',
              'Purple',
              'Maroon',
              'Aqua',
              'Lime',
              'Teal',
              'Green',
              'Blue',
              'Navy']
    val = index % (len(colors) - 1)
    return colors[val]


def get_stacked_chart(x, y, title, x_label):
    series_data = list()
    color_index = 0
    for key in y.keys():
        series_data.append({'color': get_color(color_index), 'name': key, 'data': y[key]})
        color_index += 1
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': title},
        'plotOptions': {'series': {'stacking': 'normal'}},
        'xAxis': {'categories': x, 'name': x_label},
        'series': series_data
    }
    return chart


def get_chart(x, y, title, x_label, y_label):
    chart = {
        'chart': {'type': 'column'},
        'title': {'text': title},
        'xAxis': {'categories': x, 'title': {'text': x_label}},
        'yAxis': {'title': {'text': x_label}},
        'series': [{'name': y_label, 'data': y}]
    }
    return chart


# Home------------------------------------------------------------------------------------------------------------------


def index(request):
    return render(request, 'iplDataRepresentation/index.html', context=None)


# Number of Matches per Year--------------------------------------------------------------------------------------------


def get_number_of_matches_per_year(Match):
    matches_per_year = Match.objects.values('season').annotate(Count('season')).order_by('season')
    x, y = get_x_y(matches_per_year, 'season', 'season__count')
    return x, y


def matches_per_year(request):
    x, y = get_number_of_matches_per_year(Match)
    context = {'chart': get_chart(x, y, "Matches Per Year", "Years", "Matches")}
    return render(request, 'iplDataRepresentation/chart.html', context=context)


# Matches Won per Team per Year-----------------------------------------------------------------------------------------


def get_teams_and_years(matches):
    teams = list()
    years = list()
    for match in matches:
        if match['winner'] not in teams:
            teams.append(match['winner'])
        if match['season'] not in years:
            years.append(match['season'])
    return teams, years


def get_matches_per_team_per_year(matches):
    teams, years = get_teams_and_years(matches)
    teams_counter = dict((team, 0) for team in teams)
    matches_per_team_per_year = dict((year, deepcopy(teams_counter)) for year in years)
    for match in matches:
        matches_per_team_per_year[match['season']][match['winner']] = match['winner__count']
    return matches_per_team_per_year


def get_x_y_stacked(matches_per_team_per_year):
    x = list()
    y = dict()
    for year in sorted(matches_per_team_per_year):
        x.append(year)
        for team in matches_per_team_per_year[year]:
            if team in y:
                y[team].append(matches_per_team_per_year[year][team])
            else:
                y[team] = [matches_per_team_per_year[year][team]]
    return x, y


def get_number_of_matches_per_year_per_team(Match):
    matches = Match.objects.filter(~Q(winner="")).values('season', 'winner').annotate(Count('winner')).order_by(
        'season')
    matches_per_team_per_year = get_matches_per_team_per_year(matches)
    x, y = get_x_y_stacked(matches_per_team_per_year)
    return x, y


def matches_won_per_year(request):
    x, y = get_number_of_matches_per_year_per_team(Match)
    context = {'chart': get_stacked_chart(x, y, "Matches Won per Year", "Matches")}
    return render(request, 'iplDataRepresentation/chart.html', context=context)


# Extras in 2016--------------------------------------------------------------------------------------------------------


def get_extra_runs_per_team_in_2016(Delivery):
    extras_per_team = Delivery.objects.filter(match_id__season=2016).values('bowling_team').annotate(
        Sum('extra_runs')).order_by('extra_runs__sum')
    x, y = get_x_y(extras_per_team, "bowling_team", "extra_runs__sum")
    return x, y


def extra_runs_in_2016(request):
    x, y = get_extra_runs_per_team_in_2016(Delivery)
    context = {'chart': get_chart(x, y, "Extra Runs in 2016", "Teams", "Runs")}
    return render(request, 'iplDataRepresentation/chart.html', context=context)


# Economical Bowler in 2015---------------------------------------------------------------------------------------------


def get_bowler_economy(bowler_runs_and_balls):
    bowler_economy = dict()
    for bowler in bowler_runs_and_balls:
        bowler_economy[bowler['bowler']] = bowler['total_runs'] / (bowler['total_balls'] / 6)
    return bowler_economy


def get_economical_bowler_in_2015(Delivery):
    bowler_runs_and_balls = Delivery.objects.filter(match_id__season=2015).values('bowler').annotate(
        total_runs=Sum(F('total_runs') - F('bye_runs') - F('legbye_runs')),
        total_balls=Count('bowler', filter=(Q(wide_runs=0, noball_runs=0))))
    bowler_economy = get_bowler_economy(bowler_runs_and_balls)
    x, y = get_x_y_sorted(bowler_economy)
    return x[:10], y[:10]


def economical_bowler_in_2015(request):
    x, y = get_economical_bowler_in_2015(Delivery)
    context = {'chart': get_chart(x, y, "Economical Bowler in 2015", "Bowlers", "Economy")}
    return render(request, 'iplDataRepresentation/chart.html', context=context)


# Story-----------------------------------------------------------------------------------------------------------------


def get_success_rate(matches):
    success_rate = {"bat": 0, "field": 0}
    for match in matches:
        toss_winner = match['toss_winner']
        toss_decision = match['toss_decision']
        match_winner = match['winner']
        if toss_winner == match_winner:
            success_rate[toss_decision] += 1
    return success_rate


def get_what_was_the_better_decision(Match):
    matches = Match.objects.values('toss_winner', 'toss_decision', 'winner')
    success_rate = get_success_rate(matches)
    x, y = get_x_y_sorted(success_rate)
    return x, y


def better_decision(request):
    x, y = get_what_was_the_better_decision(Match)
    context = {'chart': get_chart(x, y, "Bat or Field", "Decision", "Wins")}
    return render(request, 'iplDataRepresentation/chart.html', context=context)
