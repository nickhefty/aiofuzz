import asyncio, aiohttp
from typing import Callable
from time import perf_counter
from urllib.parse import urljoin
from os import get_terminal_size
import json


class Fuzzer:

    t_width = get_terminal_size().columns

    def __init__(self, target_url: str, dir_list: str, workers: int = 5,
                check_func: Callable[[aiohttp.ClientResponse], None] = None,
                success_handler: Callable[[aiohttp.ClientResponse], None] = None,
                failure_handler: Callable[[aiohttp.ClientResponse], None] = None):

        self.result = []
        self.target = target_url
        self.dir_list = dir_list
        self.workers = workers
        
        self.check = check_func if check_func else self.default_check
        self.success = success_handler if success_handler else self.default_success_handler
        self.failure = failure_handler if failure_handler else self.default_failure_handler

        start = perf_counter()

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        asyncio.run(self.start())
    
        self.print(f"[Tested {len(self.result)} ulrs in {perf_counter()-start:.4f} seconds]")

    @staticmethod
    def clear_line():
        print(" " * Fuzzer.t_width, end="\r")

    @staticmethod
    def print(*args, **kwargs):
        Fuzzer.clear_line()
        print(*args, **kwargs)

    @staticmethod
    async def default_check(response):
        return response.status in [200, 301]

    async def default_success_handler(self, response):
        self.print("found", response.url)

    async def default_failure_handler(self, response):
        pass

    async def getter(self):
        while True:
            url = await self.queue.get()
            resp = await self.session.get(url)
            await resp.text()
            
            if await self.check(resp):

                await self.success(resp)

            else:

                await self.failure(resp)

            self.result.append((resp.status, url))

            self.queue.task_done()


    async def do_loop(self):
        self.queue = asyncio.Queue(self.workers)

        connector = aiohttp.TCPConnector(limit=self.workers)
        async with aiohttp.ClientSession(connector=connector) as self.session:

            tasks = [asyncio.create_task(self.getter()) for _ in range(self.workers)]

            async for url in self.gen:
                await self.queue.put(url)
                self.print(f"Completed: {len(self.result)} checks... Checking: {url}", end="\r", flush=True )

            await self.queue.join()
    
        for t in tasks:
            t.cancel()


    async def async_gen(self):
        with open(self.dir_list, "r") as df:
            for line in df:
                if not line.startswith('#'):
                    yield urljoin(self.target, line.strip())


    async def start(self):
        self.gen = self.async_gen()
        await self.do_loop()
