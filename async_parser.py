import aiohttp
import asyncio
from fake_useragent import UserAgent
import os
import json


class AsyncParser:
    def __init__(self) -> None:
        self.url_for_picture_format = "https://landingfoliocom.imgix.net/{}"
        self.format_url = "https://s1.landingfolio.com/api/v1/inspiration/?offset={}"
        self.ua = UserAgent()
        self.headers = {'accept': '*/*', 'user-agent': self.ua.random}
        self.connector = aiohttp.TCPConnector()

    def create_dir(self, name):
        if not os.path.exists(name):
            os.mkdir(name)

    def write_json(self, what_to_write, filename):
        with open(f"data/{filename}.json", "w", encoding="utf-8") as file:
            json.dump(what_to_write, file, indent=4, ensure_ascii=False)

    def read_json(self):
        with open("data/all_data.json", "r", encoding="utf-8") as file:
            info = json.load(file)
        return info

    async def download_jsons(self):
        async with aiohttp.ClientSession() as session:
            all_data = []
            offset = 0
            while True:
                url = self.format_url.format(offset)
                async with session.get(url=url, headers=self.headers) as response:
                    info = await response.json()
                if type(info) is dict:
                    break
                for info_from_json in info:
                    landing_title = info_from_json.get("title", "")
                    landing_url = info_from_json.get("url", "")
                    pictures_info = info_from_json.get("images", [])
                    all_data.append(
                        {
                            "landing_title": landing_title,
                            "landing_url": landing_url,
                            "pictures_info": pictures_info
                        }
                    )
                offset += 1
                print(f"Обработан дикт со страницы {url}")
        self.write_json(what_to_write=all_data,
                        filename="all_data")

    async def create_tasks(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            landings = self.read_json()
            for landing in landings:
                landing_name = landing.get("landing_title", "")
                self.create_dir(f"data/{landing_name}")
                for pic in landing.get("pictures_info", ""):
                    url = self.url_for_picture_format.format(
                        pic.get("url", "")
                    )
                    pic_type = pic.get("type")
                    task = asyncio.create_task(self.download_personal_info(
                        sesion=session,
                        url=url,
                        landing_name=landing_name,
                        picture_type=pic_type
                    ))
                    tasks.append(task)
            await asyncio.gather(*tasks)
            print(f"Обрабртано лэндинггов {len(landings)}")

    async def download_personal_info(self, sesion, url, landing_name, picture_type):
        async with sesion.get(url=url, headers=self.headers) as resopnse:
            picture = await resopnse.read()
            with open(f"data/{landing_name}/{picture_type}.png", "wb") as file:
                file.write(picture)
            print(f"Обработана страница {url}")
            

    def main(self):
        self.create_dir("data")
        asyncio.run(self.download_jsons())
        asyncio.run(self.create_tasks())


if __name__ == "__main__":
    AsyncParser().main()
