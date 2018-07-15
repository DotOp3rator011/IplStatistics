from django.core.management.base import BaseCommand
from iplDataRepresentation.models import Match
import csv
from django.db import transaction


class Command(BaseCommand):
    help = "Read csv data from matches.csv and write to Match table in ipl database"

    @staticmethod
    def get_csv_items(csv_file):
        with open(csv_file) as cf:
            csv_reader = csv.DictReader(cf)
            csv_items = list()
            for csv_item in csv_reader:
                csv_items.append(dict(csv_item))
        return csv_items

    def handle(self):
        csv_items = Command.get_csv_items('../Data/matches.csv')
        with transaction.atomic():
            for item in csv_items:
                match = Match(id=item['id'],
                              season=item['season'],
                              date=item['date'],
                              team1=item['team1'],
                              team2=item['team2'],
                              toss_winner=item['toss_winner'],
                              toss_decision=item['toss_decision'],
                              result=item['result'],
                              dl_applied=item['dl_applied'],
                              winner=item['winner'],
                              win_by_runs=item['win_by_runs'],
                              win_by_wickets=item['win_by_wickets'],
                              player_of_the_match=item['player_of_match'],
                              venue=item['venue'],
                              umpire1=item['umpire1'],
                              umpire2=item['umpire2'],
                              umpire3=item['umpire3'], )
                match.save()
