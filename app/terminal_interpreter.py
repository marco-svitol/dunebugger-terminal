import readline
import os
import asyncio
import atexit
import traceback
import sys

from dunebugger_settings import settings
from dunebugger_logging import logger, COLORS


class TerminalInterpreter:
    def __init__(self, mqueue_handler):

        history_path = "~/.python_history"
        self.enableHistory(history_path)
        atexit.register(self.save_history, history_path)
        self.mqueue_handler = mqueue_handler
        self.running = True

        if not settings.ON_RASPBERRY_PI:
            help_insert_1 = "not "
            help_insert_2 = " (OUTPUT & INPUT gpios)"
        else:
            help_insert_1 = ""
            help_insert_2 = " (OUTPUT gpios only)"

        # Dynamically create the help string
        self.help = f"I am {help_insert_1}a Raspberry. You can ask me to:\n"
        for command, details in settings.command_handlers.items():
            self.help += f"    {command}: {details['description']}\n"
        self.help += f"    <#gpionum or label> on: set gpio status High{help_insert_2}\n"
        self.help += f"    <#gpionum or label> off: set gpio status Low{help_insert_2}\n"
        self.help += "    h, ?: show this help\n"
        self.help += "    s: show GPIO status\n"
        self.help += "    t: show dunebugger configuration\n"
        self.help += "    q, quit, exit: exit the program\n"

    async def terminal_handle_reply(self, subject, command_reply_message):
        """Handle replies from the command interpreter."""
        if command_reply_message:
            if subject == "show_gpio_status":
                self.handle_show_gpio_status(command_reply_message)
            elif subject == "show_configuration":
                self.handle_show_configuration(command_reply_message)
            elif subject == "log_message":
                self._log_queue_message(command_reply_message["level"], command_reply_message["message"])
            else:
                print(command_reply_message)
        else:
            logger.warning("No reply message received.")
        
    async def terminal_listen(self):
        # Create asyncio tasks for terminal input
        terminal_task = asyncio.create_task(self.terminal_input_loop())

        try:
            # Wait for tasks to complete
            await terminal_task
        except KeyboardInterrupt:
            self.running = False
            logger.debug("Stopping main task...")
        except Exception as exc:
            traceback.print_exc()
            logger.critical("Exception: " + str(exc) + ". Exiting.")
        finally:
            self.running = False

    async def terminal_input_loop(self):
        # Check if we're in an interactive environment
        # TODO: this is useless because it will never run in a container
        # if not sys.stdin.isatty():
        #     logger.info("No interactive terminal available (running in container/background). Terminal input disabled.")
        #     # Keep the loop alive but don't try to read input
        #     while self.running:
        #         await asyncio.sleep(1)
        #     return

        # Create an event loop for the stdin reader
        loop = asyncio.get_event_loop()

        while self.running:
            try:
                # Use run_in_executor to handle blocking input() in a non-blocking way
                # Pass the prompt directly to input() so readline can handle it properly
                user_input = await loop.run_in_executor(None, lambda: input("Enter command: "))

                if user_input:
                    # Split user_input by ";" to handle multiple commands
                    commands = [cmd.strip() for cmd in user_input.split(";") if cmd.strip()]
                    for command in commands:
                        if command.lower() in ["exit", "quit", "q"]:
                            self.running = False
                            print("Exiting terminal input loop...")
                            break
                        elif command.lower() in ["h", "?"]:
                            self.handle_help()
                        else:
                            await self.mqueue_handler.dispatch_message(command, "terminal_command", "core")# TODO: reply_to not working, "terminal")
                            #TODO: useless
                            #print(command_reply_message)
                else:
                    print("\r")
            except EOFError:
                logger.info("EOF encountered - terminal input not available (container environment)")
                self.running = False
                break
            except KeyboardInterrupt:
                self.running = False
                logger.debug("Stopping terminal input loop...")
            except asyncio.CancelledError:
                self.running = False
                break

    def enableHistory(self, historyPath):
        history_file = os.path.expanduser(historyPath)
        if os.path.exists(history_file):
            readline.read_history_file(history_file)

    def save_history(self, historyPath):
        history_file = os.path.expanduser(historyPath)
        readline.write_history_file(history_file)

    def handle_help(self):
        print(self.help)

    def handle_show_gpio_status(self, gpio_status):
        color_red = COLORS["RED"]
        print(f"{color_red}Current GPIO Status:")
        for gpio_info in gpio_status:
            gpio = gpio_info["pin"]
            label = gpio_info["label"]
            mode = gpio_info["mode"]
            state = gpio_info["state"]
            switchstate = gpio_info["switch"]

            color = COLORS["RESET"]
            switchcolor = COLORS["RESET"]

            if mode == "INPUT":
                color = COLORS["BLUE"]
            elif mode == "OUTPUT":
                color = COLORS["RESET"]

            if state == "HIGH":
                switchcolor = COLORS["MAGENTA"]
            elif state == "LOW":
                switchcolor = COLORS["GREEN"]

            if state == "ERROR":
                color = COLORS["RED"]
                switchcolor = color

            print(
                f"{color}Pin {gpio} label: {label} \
mode: {mode}, state: {state}, switch: {COLORS['RESET']}{switchcolor}{switchstate}{COLORS['RESET']}"
            )

    def handle_show_configuration(self, settings):

        # Print DunebuggerSettings configuration
        color_blue = COLORS["BLUE"]
        color_red = COLORS["RED"]
        print(f"{color_red}Current Configuration:")
        for setting in settings:
            for key, value in setting.items():
                print(f"{color_blue}{key}: {COLORS['RESET']}{value}")

    def _log_queue_message(self, level, message):
        """Log messages from the queue with core: prefix and magenta color."""
        color_magenta = COLORS["MAGENTA"]
        color_reset = COLORS["RESET"]
        prefixed_message = f"{color_magenta}core: {message}{color_reset}"

        if level == "DEBUG":
            logger.debug(prefixed_message)
        elif level == "INFO":
            logger.info(prefixed_message)
        elif level == "WARNING":
            logger.warning(prefixed_message)
        elif level == "ERROR":
            logger.error(prefixed_message)
        elif level == "CRITICAL":
            logger.critical(prefixed_message)
        else:
            # For unknown levels, use info as fallback
            logger.info(f"{color_cyan}{level}: core: {message}{color_reset}")


