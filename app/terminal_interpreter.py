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
        self.enable_history(history_path)
        atexit.register(self.save_history, history_path)
        self.mqueue_handler = mqueue_handler
        self.help = "Help not loaded yet."
        self.running = True

    async def terminal_handle_reply(self, subject, command_reply_message):
        """Handle replies from the command interpreter."""
        if command_reply_message:
            if subject == "show_gpio_status":
                self.handle_show_gpio_status(command_reply_message)
            elif subject == "show_configuration":
                self.handle_show_configuration(command_reply_message)
            elif subject == "log_message":
                self._log_queue_message(command_reply_message["level"], command_reply_message["message"])
            elif subject == "commands_list":
                self.help = self.setup_help(commands_list = command_reply_message)
            elif subject == "terminal_command_reply":
                if command_reply_message["success"] == True:
                    print(command_reply_message["message"])
                else:
                    if command_reply_message["level"].lower() == "error":
                        print(f"{COLORS['RED']}{command_reply_message['message']}{COLORS['RESET']}")
                    elif command_reply_message["level"].lower() == "warning":
                        print(f"{COLORS['YELLOW']}{command_reply_message['message']}{COLORS['RESET']}")
                    else:
                        print(f"{COLORS['MAGENTA']}{command_reply_message['message']}{COLORS['RESET']}")
            else:
                logger.warning(f"Unknown subject in reply: {subject}")
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
                    pass#print("\r")
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

    def enable_history(self, history_path):
        history_file = os.path.expanduser(history_path)
        if os.path.exists(history_file):
            readline.read_history_file(history_file)

    def save_history(self, history_path):
        history_file = os.path.expanduser(history_path)
        readline.write_history_file(history_file)

    def handle_help(self):
        print(self.help)

    def handle_show_gpio_status(self, gpio_status):
        color_red = COLORS["RED"]
        print(f"\n{color_red}{'Pin':<5} {'Logic':<20} {'Label':<20} {'Mode':<8} {'State':<8} {'Switch':<8}")
        print(f"{color_red}{'-' * 72}")
        for gpio_info in gpio_status:
            gpio = gpio_info["pin"]
            logic = gpio_info["logic"]
            label = gpio_info["label"]
            mode = gpio_info["mode"]
            state = gpio_info["state"]
            switch_state = gpio_info["switch"]

            color = COLORS["RESET"]
            switch_color = COLORS["RESET"]

            if mode == "INPUT":
                color = COLORS["BLUE"]
            elif mode == "OUTPUT":
                color = COLORS["RESET"]

            if state == "HIGH":
                switch_color = COLORS["MAGENTA"]
            elif state == "LOW":
                switch_color = COLORS["GREEN"]

            if state == "ERROR":
                color = COLORS["RED"]
                switch_color = color
            
            print(
                f"{color}{gpio:<5} {logic:<20} {label:<20} {mode:<8} "
                f"{state:<8} {switch_color}{switch_state:<8}{COLORS['RESET']}"
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

    async def request_commands_list(self):
        """Request the commands list from the dunebugger core."""
        await self.mqueue_handler.dispatch_message("get_commands_list", "terminal_command", "core")

    def setup_help(self, commands_list):
        try:
            if not settings.ON_RASPBERRY_PI:
                help_insert_1 = "not "
            else:
                help_insert_1 = ""

            # Dynamically create the help string
            terminal_help = f"I am {help_insert_1}a Raspberry. You can ask me to:\n"
            for command, details in commands_list.items():
                terminal_help += f"    {command}: {details['description']}\n"
            terminal_help += "    h, ?: show this help\n"
            terminal_help += "    s: show GPIO status\n"
            terminal_help += "    t: show dunebugger configuration\n"
            terminal_help += "    q, quit, exit: exit the program\n"

            return terminal_help

        except Exception as e:
            logger.error(f"Error parsing commands list message: {e}")


