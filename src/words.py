import asyncio
import re

import aiohttp

WORDS_LINE_REGEX = re.compile(r'^([a-z]{5})\s+(\d)\s+.*$')


async def load_words():
    allowed_words = []
    wordle_words = []
    url = 'https://static01.nytimes.com/newsgraphics/wordlebot/_big_assets/words.txt'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                async for encoded_line in response.content:
                    line = encoded_line.decode('utf-8').strip()
                    m = re.match(WORDS_LINE_REGEX, line)
                    if not m:
                        continue
                    word = m.group(1)
                    if len(set(word)) != 5:
                        continue
                    level = m.group(2)
                    allowed_words.append(word)
                    if level == '0':
                        wordle_words.append(word)
                print(f"Successfully loaded words.")
            else:
                print(f"Failed to download. Status code: {response.status}")
    return allowed_words, wordle_words


ALLOWED_WORDS, WORDLE_WORDS = asyncio.run(load_words())
