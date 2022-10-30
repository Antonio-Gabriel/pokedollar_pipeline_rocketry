import logging
from os import makedirs
from pathlib import Path
from datetime import date
from random import randint

from rocketry import Rocketry
from httpx import AsyncClient, stream
from rocketry.args import Arg, Return
from rocketry.conds import (
    after_success, 
    after_finish,
    after_fail
    )

# logger configuration
"""
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
task_logger = logging.getLogger('rocketry.task')
task_logger.addHandler(handler)
"""

POKE_API    = "https://pokeapi.co/api/v2/pokemon/{}"
DOLAR_API   = "https://economia.awesomeapi.com.br/json/daily/USD-AOA/?start_date={}&end_date={}"

scheduler = Rocketry(execution='async')

@scheduler.param('date')
def random_date_generator() -> str:
    """generate random date and formate"""
    day = randint(1, 28)
    month = randint(1, 12)
    year = randint(2021, 2022)

    random_date = date.today()\
                    .replace(day=day, month=month, year=year)

    formated_date = random_date.strftime('%Y%m%d')
    return formated_date

@scheduler.task('every 5s', name='get quotation of dollar')
async def get_dollar(date: str=Arg('date')) -> str:
    """get dollar quotation of economia api"""
    async with AsyncClient() as client:
        response = (await client.get(DOLAR_API.format(date, date))).json()

        if response:   
            return response[0]['high'][:3] # 569.628 -> 569

@scheduler.task(after_fail(get_dollar))
def get_dollar_fail():
    """get dollar fail, here we can notify that the process fail or anything"""
    print("get dollar fail")

@scheduler.task(after_success(get_dollar))
async def get_pokemon_json(dollar: str = Return(get_dollar)) -> list:
    """get pokemon by dollar formated dollar"""
    async with AsyncClient() as client:
        response = (await client.get(POKE_API.format(dollar))).json()
        return response

@scheduler.task(after_fail(get_pokemon_json))
def get_pokemon_json_fail():
    """get pokemon fail, here we can notify that the process fail or anything"""
    print("get pokenom fail")

@scheduler.task(after_success(get_pokemon_json))
def get_pokemon_sprite_url(poke_json: list = Return(get_pokemon_json)):
    """return only the default front sprite of prokemon and the name"""
    return poke_json['sprites']['front_default'], poke_json['name']

@scheduler.task(after_success(get_pokemon_sprite_url))
def download_pokemon_sprite(
    poke_data: tuple = Return(get_pokemon_sprite_url),
    poke_number: str = Return(get_dollar)    
    ):
    """get poke data to download"""    
    url, name = poke_data
    
    file = Path(f'{poke_number}_{name}.png')
    with open(file, 'wb') as download_file:
        with stream('GET', url) as strm:
            for chunk in strm.iter_bytes():
                download_file.write(chunk)
    
    return file

@scheduler.task(after_finish(download_pokemon_sprite))
def move_sprite(path: Path = Return(download_pokemon_sprite)):
    """move the sprite download to a dir"""    
    makedirs('sprites', exist_ok=True)

    folder = Path('sprites')
    path.rename(folder / path)

scheduler.run()
