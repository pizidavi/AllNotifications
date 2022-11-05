import os
import asyncio
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.logger import get_logger, set_level
from notifiers.NotifierClients import Telegram
from controls.View import View

from providers.MReader import MReader
from providers.ReadM import ReadM
from providers.MangaNato import MangaNato
from providers.MangaWorld import MangaWorld
from providers.MangaWorldAdult import MangaWorldAdult
from providers.Manhwax import Manhwax

load_dotenv()
set_level(os.getenv('LOG_LEVEL', 'INFO'))

logger = get_logger(__name__)

NOTIFIER = Telegram()


async def main():
    history: dict[str, set] = {}

    for provider in PROVIDERS:
        if provider.disabled:
            continue

        name = provider.NAME
        type_ = provider.TYPE
        http_client = provider.HTTP_CLIENT

        logger.debug('Checking %s', name)
        try:
            request = provider.updates_request()
            response = http_client.send(request)

            provider.logging.ok('RequestException')
        except Exception as e:
            exception_message = str(e).split('\n')[0]  # Remove "For more information..."
            logger.error('RequestException: %s', exception_message)
            provider.logging.error('RequestException', message=exception_message)
        else:
            try:
                elements = provider.updates_parser(response)
            except Exception as e:
                logger.error('ParserException: %s', str(e), exc_info=True)
                provider.logging.critical('ParserException', message=str(e))
            else:
                if len(elements) == 0:
                    logger.error('ParserError: No elements found')
                    provider.logging.critical('ParserException', message='No elements found')
                else:
                    provider.logging.ok('ParserException', message='Parsing successful')

                    if history.get(type_, None) is None:
                        history[type_] = set()
                    history[type_].update(provider.manage_elements(elements, list(history[type_])))
    del history
    print('----')


async def safe_main():
    try:
        await main()
    except Exception as e:
        logger.error(e)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    view = View()

    PROVIDERS = [
        MReader(register_commands=view.register_commands),
        ReadM(register_commands=view.register_commands),
        MangaNato(register_commands=view.register_commands),
        MangaWorld(register_commands=view.register_commands),
        MangaWorldAdult(register_commands=view.register_commands),
        Manhwax(register_commands=view.register_commands),
    ]

    scheduler = AsyncIOScheduler()
    scheduler.add_job(safe_main, 'interval', minutes=10)
    scheduler.start()

    try:
        loop.run_until_complete(safe_main())  # First run
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print('')
    except Exception as _:
        print(f'Error: {_}')
    finally:
        view.stop()
        loop.stop()
        loop.close()
        print('Bye')
