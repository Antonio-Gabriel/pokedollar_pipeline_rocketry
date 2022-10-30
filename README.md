# POKEDOLAR

The application will always check the quote site to see what the new quote posted is and gather the balance to download a pokemon with the quote number.

For example:

If the quote is now AOA 569.628 we will convert to 569 and download an amoji or pokemon with this number on pokemon api v2.

It's an example over ETL(Extract, Transform, Load) systems.

## Start
First you need to create a virtual environment and install the rocketry.

Bellow you can find:

```bash
python -m venv venv

. venv/bin/activate

pip install -r requirements.txt
```

## Links

Here you can find the apis that I used on this project:

[Pokemon Api](https://pokeapi.co/api/v2/pokemon/25)
[Quotation Api](https://economia.awesomeapi.com.br/json/daily/USD-AOA/?start_date=20211228&end_date=20211228)

Some of the code for task scheduling

```python
@scheduler.task('every 5s', name='get quotation of dollar')
async def get_dollar(date: str=Arg('date')) -> str:
    """get dollar quotation of economia api"""
    async with AsyncClient() as client:
        response = (await client.get(DOLAR_API.format(date, date))).json()

        if response:   
            return response[0]['high'][:3] # 569.628 -> 569
```

And much more.