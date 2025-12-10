#!/usr/bin/env python3
import asyncio

# from dunebugger_settings import settings
from class_factory import terminal_interpreter, mqueue


async def main():
    try:
        await mqueue.start_listener()
        # wait that NATS is connected before continuing
        while not mqueue.is_connected:
            await asyncio.sleep(1)
        await terminal_interpreter.request_commands_list()
        await terminal_interpreter.terminal_listen()
    
    finally:
        # Clean up resources when exiting
        print("Cleaning up resources...")
        
        # Close NATS connection
        await mqueue.close_listener()
 
        print("Cleanup completed.")


if __name__ == "__main__":
    asyncio.run(main())
