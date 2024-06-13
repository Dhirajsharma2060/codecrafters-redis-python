import socket
import asyncio
from datetime import datetime, timedelta
from argparse import ArgumentParser

store = {}

def get_curr_time_and_add(milliseconds_to_add):
    current_time = datetime.now()
    delta = timedelta(milliseconds=int(milliseconds_to_add))
    new_time = current_time + delta
    return new_time

async def handle_connection(reader, writer):
    print("New connection")
    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            split_data = data.split(b"\r\n")
            print(split_data)
            if split_data[2] == b"PING":
                writer.write(b"+PONG\r\n")
                await writer.drain()
            elif split_data[2] == b"ECHO":
                return_string = b"\r\n".join([split_data[3], split_data[4]]) + b"\r\n"
                writer.write(return_string)
                await writer.drain()
            elif split_data[2] == b"SET":
                if len(split_data) > 8 and split_data[8] == b"px":
                    val = get_curr_time_and_add(split_data[10])
                    store[split_data[4]] = (split_data[6], val)
                else:
                    store[split_data[4]] = split_data[6]
                writer.write(b"+OK\r\n")
                await writer.drain()
            elif split_data[2] == b"GET":
                key = split_data[4]
                if key not in store:
                    return_string = b"$-1\r\n"
                elif isinstance(store[key], tuple):
                    if store[key][1] <= datetime.now():
                        del store[key]
                        return_string = b"$-1\r\n"
                    else:
                        return_string = (
                            b"\r\n".join(
                                [
                                    b"$" + str(len(store[key][0])).encode("utf-8"),
                                    store[key][0],
                                ]
                            )
                            + b"\r\n"
                        )
                else:
                    return_string = (
                        b"\r\n".join(
                            [b"$" + str(len(store[key])).encode("utf-8"), store[key]]
                        )
                        + b"\r\n"
                    )
                writer.write(return_string)
                await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    parser = ArgumentParser("A Redis server written in Python")
    parser.add_argument("--port", type=int, default=6379)
    args = parser.parse_args()
    
    server = await asyncio.start_server(
        handle_connection, "localhost", args.port
    )
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
