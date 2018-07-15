from django.core.management.base import BaseCommand
from iplDataRepresentation.models import Match, Delivery
import csv
from django.db import transaction


class Command(BaseCommand):
    help = "Read csv data from deliveries.csv and write to Match table in ipl database"

    @staticmethod
    def get_csv_items(csv_file):
        with open(csv_file) as cf:
            csv_reader = csv.DictReader(cf)
            csv_items = list()
            for csv_item in csv_reader:
                csv_items.append(dict(csv_item))
        return csv_items

    def handle(self):
        csv_items = Command.get_csv_items('../Data/deliveries.csv')
        with transaction.atomic():
            for item in csv_items:
                match = Match.objects.get(pk=item['match_id'])
                delivery = Delivery(match_id=match,
                                    inning=item['inning'],
                                    batting_team=item['batting_team'],
                                    bowling_team=item['bowling_team'],
                                    over=item['over'],
                                    ball=item['ball'],
                                    batsman=item['batsman'],
                                    non_striker=item['non_striker'],
                                    bowler=item['bowler'],
                                    is_super_over=item['is_super_over'],
                                    wide_runs=item['wide_runs'],
                                    bye_runs=item['bye_runs'],
                                    legbye_runs=item['legbye_runs'],
                                    noball_runs=item['noball_runs'],
                                    penalty_runs=item['penalty_runs'],
                                    batsman_runs=item['batsman_runs'],
                                    extra_runs=item['extra_runs'],
                                    total_runs=item['total_runs'],
                                    player_dismissed=item['player_dismissed'],
                                    dismissal_kind=item['dismissal_kind'],
                                    fielder=item['fielder'], )
                delivery.save()
