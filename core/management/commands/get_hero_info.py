import json
import logging
from typing import Any, Optional

import requests
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

API_URL = "https://idle.kleho.ru/cache/en/champions.json?t=1638996470"

class Command(BaseCommand):
  def add_arguments(self, parser):
    pass

  def handle(self, *args: Any, **options: Any) -> Optional[str]:
    logging.basicConfig(level=logging.DEBUG)
    hero_data = requests.get(API_URL).json()['data']
    output = {}
    for hero in hero_data:
      # print(hero)
      output[int(hero['id'])] = hero['name']
    print(json.dumps(output, indent=2))
