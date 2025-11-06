from terminal_interpreter import TerminalInterpreter
from dunebugger_settings import settings
from mqueue import NATSComm
from mqueue_handler import MessagingQueueHandler

mqueue_handler = MessagingQueueHandler()
mqueue = NATSComm(
    nat_servers=settings.mQueueServers,
    client_id=settings.mQueueClientID,
    subject_root=settings.mQueueSubjectRoot,
    mqueue_handler=mqueue_handler,
)
mqueue_handler.mqueue_sender = mqueue
terminal_interpreter = TerminalInterpreter(mqueue_handler)
mqueue_handler.terminal_interpreter = terminal_interpreter
