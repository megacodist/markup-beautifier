import asyncio
import json
from pprint import pprint
from requests import session
from requests.sessions import Session


# Definning of global variables...
apiSession = session()


async def main_USD() -> dict[str, str | bool]:
    resp = apiSession.get(url='https://dapi.p3p.repl.co/api/?currency=cad')
    if resp.status_code == 200:
        return json.loads(resp.text)


async def main_Thrd():
    pprint(await main_USD())


def Beautify(html: str) -> list[str]:
    from lxml import etree

    htmlParser = etree.HTMLParser()
    dom: etree.ElementBase = etree.fromstring(html, htmlParser)
    html: bytes = etree.tostring(dom, pretty_print=True)
    html: str = html.decode()
    htmlLines = html.splitlines(keepends=False)
    return [
        line
        for line in htmlLines
        if line.strip()]


if __name__ == '__main__':
    asyncio.run(main_Thrd())
