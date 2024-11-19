#!/usr/bin/env python

"""Client using the asyncio API."""

import asyncio
from websockets.asyncio.client import connect

def get_data(f_name):
    in_file = open(f_name, "rb")
    data = in_file.read()
    in_file.close()
    return data

async def hello():
    async with connect("ws://localhost:5000") as websocket:
        
        auth_params = await websocket.recv()
        print('got auth params',auth_params)
        
        #generating 0.pickle and 1.pickle are expensive
        await websocket.send('data/0.pickle')
        await websocket.send('data/1.pickle')
        
        await websocket.send('p1')
        await websocket.send('my secure password')
        
        auth_status = await websocket.recv()
        print(auth_status)

if __name__ == "__main__":
    asyncio.run(hello())