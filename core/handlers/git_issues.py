from aiogram.types import Message

import httpx

URL = ('https://api.github.com/search/issues?'
       'q=label:%22good%20first%20issue%22+language:'
       'python+state:open&sort=created&order=desc&per_page=10')


async def fetch_issues():
    async with httpx.AsyncClient() as client:
        response = await client.get(URL)

        if response.status_code == 200:
            data = response.json()
            issues = data.get('items', [])
            issues_list = '\n'.join(
                [f"<b>{issue['title']}</b> — "
                 f"{issue['html_url']}" for issue in issues]
            )
            return issues_list


async def show_issues(message: Message):
    issues = await fetch_issues()

    if issues:
        await message.answer(issues, parse_mode='HTML')
    else:
        await message.answer('An error has occurred.'
                             'Try later.')
