import asyncio
import aiohttp
import re
import logging
import aiofiles

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

phone_regex = r'\d{11}'


async def extract_phone_numbers(session, site, path):
    url = site + path
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            html = await response.text()
            matches = re.findall(phone_regex, html)
            return matches
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при запросе к {url}: {e}")
        return []

async def save_to_file(filename, data):
    async with aiofiles.open(filename, mode='w') as file:
        await file.write(data)

async def main():
    async with aiohttp.ClientSession() as session:
        sites_and_paths = [
            ('https://hands.ru', '/company/about'),
            ('https://repetitors.info', '/'),
        ]

        tasks = []
        for site, path in sites_and_paths:
            task = extract_phone_numbers(session, site, path)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        for (site, path), phone_numbers in zip(sites_and_paths, results):
            filename = f"{site.replace('https://', '').replace('.', '_')}_{path.replace('/', '_')}.txt"
            data = f'Номера телефонов на сайте {site + path}:\n'
            data += '\n'.join(phone_numbers) + '\n'
            await save_to_file(filename, data)

asyncio.run(main())
