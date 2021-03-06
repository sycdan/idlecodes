import json
import logging
import time
from html.parser import HTMLParser
from typing import Any, Optional

import requests
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

from core.models import Platform, Promotion, Redemption

logger = logging.getLogger(__name__)

API_URL = "http://ps7.idlechampions.com/~idledragons"
BASE_PARAMS = dict(
  language_id=1,
  timestamp=0,
  request_id=0,
  network_id=11,
  mobile_client_version=999,
)
CHEST_TYPES = {
  2: "Gold",
  22: "Gold Zorbu",
  30: "Gold Nrakk",
  37: "Gold Supply",
  263: "Gold Orkira",
  282: "Electrum",
  335: "Gold D'Hani",
  339: "Gold Widdle",
  352: "Silver Gazrick",
  353: "Gold Gazrick",
}
HERO = {
  "1": "Bruenor",
  "2": "Celeste",
  "3": "Nayeli",
  "4": "Jarlaxle",
  "5": "Calliope",
  "6": "Asharra",
  "7": "Minsc",
  "8": "Delina",
  "9": "Makos",
  "10": "Tyril",
  "11": "Jamilah",
  "12": "Arkhan",
  "13": "Hitch",
  "14": "Stoki",
  "15": "Krond",
  "16": "Gromma",
  "17": "Dhadius",
  "18": "Drizzt",
  "19": "Barrowin",
  "20": "Regis",
  "21": "Birdsong",
  "22": "Zorbu",
  "23": "Strix",
  "24": "Nrakk",
  "25": "Catti-brie",
  "26": "Evelyn",
  "27": "Binwin",
  "28": "Deekin",
  "29": "Xander",
  "30": "Azaka",
  "31": "Ishi",
  "32": "Wulfgar",
  "33": "Farideh",
  "34": "Donaar",
  "35": "Vlahnya",
  "36": "Warden",
  "37": "Nerys",
  "38": "K'thriss",
  "39": "Paultin",
  "40": "Black Viper",
  "41": "Rosie",
  "42": "Aila",
  "43": "Spurt",
  "44": "Qillek",
  "45": "Korth",
  "46": "Walnut",
  "47": "Shandie",
  "48": "Jim",
  "49": "Turiel",
  "50": "Pwent",
  "51": "Avren",
  "52": "Sentry",
  "53": "Krull",
  "54": "Artemis",
  "55": "M\u00f4rg\u00e6n",
  "56": "Havilar",
  "57": "Sisaspia",
  "58": "Briv",
  "59": "Melf",
  "60": "Krydle",
  "61": "Jaheira",
  "62": "Nova",
  "63": "Freely",
  "64": "Beadle & Grimm",
  "65": "Omin",
  "66": "Lazaapz",
  "67": "Dragonbait",
  "68": "Ulkoria",
  "69": "Torogar",
  "70": "Ezmerelda",
  "71": "Penelope",
  "72": "Lucius",
  "73": "Baeloth",
  "74": "Talin",
  "75": "Hew Maan",
  "76": "Orisha",
  "77": "Alyndra",
  "78": "Orkira",
  "79": "Shaka",
  "80": "Mehen",
  "81": "Selise",
  "82": "Sgt. Knox",
  "83": "Ellywick",
  "84": "Prudence",
  "85": "Coraz\u00f3n",
  "86": "Reya",
  "87": "NERDS",
  "88": "Xerophon",
  "89": "D'hani",
  "90": "Brig",
  "91": "Widdle",
  "92": "Yorven",
  "93": "Viconia",
  "94": "Rust",
  "95": "Vi"
}
SKINS = {
  131: "Icewind Dale",
}


def get_attr(attr, attrs, default=None):
  try:
    return next(filter(lambda x: x[0] == attr, attrs))[1]
  except StopIteration:
    return default


class Api:
  def __init__(self, platform) -> None:
      self.api_url = API_URL
      self.platform = platform

  def call(self, command, params: dict):
    qs = '&'.join(['='.join(map(str, x)) for x in params.items()])
    url = f"{self.api_url}/post.php?call={command}&{qs}"
    logger.debug("Calling %s", url)
    response = requests.get(url)
    response.raise_for_status()
    payload = response.json()
    if payload['success']:
      # response['switch_play_server'] = 'http://ps6.idlechampions.com/~idledragons/'
      if 'switch_play_server' in payload:
        self.api_url = payload['switch_play_server']
        # retry
        return self.call(command, params)
      else:
        return payload
    elif payload['failure_reason'] == 'Outdated instance id':
      # update instance id
      user = self._get_user_details()
      self.platform.instance_id = user['details']['instance_id']
      self.platform.save()
      # retry with a new instance ID
      params['instance_id'] = self.platform.instance_id
      return self.call(command, params)
    else:
      raise NotImplementedError(f"Unhandled failure in payload {payload}")

  def _get_user_details(self):
    platform = self.platform
    params = BASE_PARAMS.copy()
    params.update(dict(
      include_free_play_objectives=False,
      instance_key=1,
      user_id=platform.user_id,
      hash=platform.hash,
    ))
    return self.call('getuserdetails', params)


class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument("platform")

  def handle(self, *args: Any, **options: Any) -> Optional[str]:
    logging.basicConfig(level=logging.DEBUG)
    platform = Platform.objects.get(key=options['platform'])
    api = Api(platform)


    # # buy event chests
    # for x in range(35):
    #   params = {}
    #   params.update(dict(
    #     user_id=platform.user_id,
    #     hash=platform.hash,
    #     instance_id=platform.instance_id,
    #     chest_type_id=30,
    #     count=1,
    #   ))
    #   print(api.call('buysoftcurrencychest', params))
    #   time.sleep(1)
    # return

    for promo in get_latest_promotions():
      code = promo.code
      print(code)

      # TODO: scrape and update expires at
      promotion, created = Promotion.objects.get_or_create(code=code)
      if Redemption.objects.filter(
        promotion=promotion,
        platform=platform,
      ).exists():
        # TODO: retry if we didn't meet the reqs before
        continue

      params = BASE_PARAMS.copy()
      params.update(dict(
        user_id=platform.user_id,
        hash=platform.hash,
        instance_id=platform.instance_id,
        code=escape_code(code),
      ))
      res = api.call('redeemcoupon', params)
      if res['success']:
        try:
          message = get_message(res)
        except Exception as e:
          message = json.dumps(res)
          message['__error'] = str(e)
        Redemption.objects.create(
          promotion=promotion,
          platform=platform,
          message=message,
        )
      else:
        print("not successful")
        breakpoint()
      time.sleep(.5)


def get_message(response):
  """
  {
    "success": true,
    "loot_details": [{
      "loot_item": "generic_chest",
      "loot_action": "generic_chest",
      "count": 1,
      "chest_type_id": 282,
      "before": 62,
      "after": 63
    }],
    "okay": true,
    "actions": [{"action": "update_chest_count", "chest_type_id": 282, "count": 63}],
    "processing_time": "0.03085",
    "memory_usage": "2 mb",
    "apc_stats": {"gets": 5, "gets_time": "0.00000", "sets": 0, "sets_time": "0.00000"},
    "db_stats": {"10": false, "1": false, "13": false}
  }
  """
  if response['okay'] and 'loot_details' in response:
    parts = []
    for details in response['loot_details']:
      action = details.get('loot_action', None)
      item = details.get('loot_item', None)
      if action == 'generic_chest' and item == 'generic_chest':
        chest_name = CHEST_TYPES.get(details['chest_type_id'])
        if chest_name:
          parts.append(f"{chest_name} Chest x{details['count']}")
      elif action == 'unlock_hero' and item == 'unlock_hero':
        parts.append(HERO[str(details['hero_id'])])
      elif action == 'claim' and 'unlock_hero_skin' in details:
        skin_id = details['unlock_hero_skin']
        if skin_id in SKINS:
          parts.append(SKINS[skin_id])
        else:
          parts.append(str(skin_id))
    if parts:
      return ', '.join(parts)
  elif not response['okay']:
    return response.get('fail_message', json.dumps(response))
  return json.dumps(response)


class CodeParser(HTMLParser):
  codes = []
  def handle_starttag(self, tag, attrs):
    if tag == 'input':
      tid = get_attr('id', attrs, '')
      if tid.startswith('incendar'):
        self.codes.append(get_attr('value', attrs))


def get_latest_promotions():
  codes = cache.get('codes')
  if codes is None:
      res = requests.get("https://incendar.com/idlechampions_codes.php")
      parser = CodeParser()
      parser.feed(res.text)
      codes = parser.codes
      cache.set('codes', codes, 60 * 5)
  for code in codes:
    yield Promotion(code=code)


def escape_code(code):
  return  code.replace("&", "%26").replace("#", "%23")
