import httpx
from aiogram import F, Router, types

URL = (
    'https://api.github.com/search/issues?'
    'q=label:%22good%20first%20issue%22+language:'
    'python+state:open&sort=created&order=desc&per_page=10'
)


router = Router()


@router.message(F.text == 'Good first issues')
async def show_issues(message: types.Message):
    issues = await fetch_issues()

    if issues:
        await message.answer(issues, parse_mode='HTML')
    else:
        await message.answer('An error has occurred. ' 'Try later')


async def fetch_issues():
    async with httpx.AsyncClient() as client:
        response = await client.get(URL)

        if response.status_code == 200:
            data = response.json()
            issues = data.get('items', [])
            issues_list = '\n'.join(
                [
                    f"<b>{issue['title']}</b> — " f"{issue['html_url']}"
                    for issue in issues
                ]
            )
            return issues_list
