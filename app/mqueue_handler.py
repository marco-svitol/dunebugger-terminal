import asyncio
import json
from dunebugger_logging import logger
from dunebugger_settings import settings


class MessagingQueueHandler:
    """Class to handle messaging queue operations."""

    def __init__(self):
        self.mqueue_sender = None
        self.running = True
        self.monitor_task = None
        self.terminal_interpreter = None

    async def process_mqueue_message(self, mqueue_message):
        """Callback method to process received messages."""
        # Parse the JSON string back into a dictionary
        try:
            data = mqueue_message.data.decode()
            message_json = json.loads(data)
        except (AttributeError, UnicodeDecodeError) as decode_error:
            logger.error(f"Failed to decode message data: {decode_error}. Raw message: {mqueue_message.data}")
            return
        except json.JSONDecodeError as json_error:
            logger.error(f"Failed to parse message as JSON: {json_error}. Raw message: {data}")
            return

        try:
            subject = (mqueue_message.subject).split(".")[2]
            #TODO: too much verbose logging, uncomment if needed
            #logger.debug(f"Processing message: {str(message_json)[:20]}. Subject: {subject}. Reply to: {mqueue_message.reply}")
            reply = message_json["body"]
            return await self.terminal_interpreter.terminal_handle_reply(subject, reply)

        except KeyError as key_error:
            logger.error(f"KeyError: {key_error}. Message: {message_json}")
        except Exception as e:
            logger.error(f"Error processing message: {e}. Message: {message_json}")

    async def dispatch_message(self, message_body, subject, recipient, reply_subject=None):
        message = {
            "body": message_body,
            "subject": subject,
            "source": settings.mQueueClientID,
        }
        await self.mqueue_sender.send(message, recipient, reply_subject)




