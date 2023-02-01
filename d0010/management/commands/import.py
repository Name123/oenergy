from django.core.management.base import BaseCommand, CommandError
from d0010.parse import FlowD0010Parser

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('filenames', nargs='+', type=str)

    def handle(self, *args, **options):
        p = FlowD0010Parser()
        for file_name in options['filenames']:
            try:
                p.run(file_name)
            except Exception as e:
                raise Exception(f'Parse error at line {p._line_num}')
