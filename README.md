# aiofuzz

This is a small and blazingly-fast web directory fuzzing library. The aiofuzz.py file contains only the Fuzzer class.



## Installation

    git clone https://github.com/nickhefty/aiofuzz
    cd aiofuzz
    python3 -m pip install -r requirements.txt
## Simple usage

    from aiofuzz import Fuzzer
    
    fuzzer = Fuzzer(target_url="http://localhost:5000", dir_list="../list.txt", workers=5)
    ## By default, Fuzzer will print out found urls and status messages while running
    
    for status, url in fuzzer.result:
	    do_something(...)
## Other arguments

#### workers
This is an integer defining the number of workers and simultaneous requests allowed. Default=5
#### check_func
The check_func function accepts an aiohhtp.ClientResponse object and returns a boolean determining whether the response is a "hit" or not.
If one is not provided, it will use this default:

    async def default_check(response):
	    return  response.status in [200, 301]
#### success_handler
The  success_handler is called on any aiohhtp.ClientResponse object that is determined to be a "hit" by the check_func.
If one is not provided, it will use this default:

    async def default_success_handler(self, response):
	    self.print("found", response.url)
#### failure_handler
The  failure_handler is called on any aiohhtp.ClientResponse object that is not a "hit."
If one is not provided, it will use this default:

    async def default_failure_handler(self, response):
	    pass

## Custom Handler Example:
Functions passed into the Fuzzer must be async. aiohttp.ClientResponse methods are async coroutines and must be awaited.

    from aiofuzz import Fuzzer
    
    async def my_check(resp):
	    """Only looking for pages that have 'secret' in the page text"""
	    text = await resp.text()
        return 'secret' in text
    
    async def my_success(resp):
	    """Print the byte-encoded content of all 'hits'"""
	    content = await resp.read()
		Fuzzer.print(content)
    
    MISSES = []
    async def my_failure(resp):
	    """Put all the non-404 misses (no 'secret' in the text) in a list for later processing"""
	    if resp.status != 404:
		    miss_content = await resp.read()
		    MISSES.append(miss_content)
    
    Fuzzer(target_url="http://127.0.0.1:5000",
		    dir_list="../list.txt",
		    check_func=my_check,
		    success_handler=my_success,
		    failure_handler=my_failure)
    
    print(MISSES)


