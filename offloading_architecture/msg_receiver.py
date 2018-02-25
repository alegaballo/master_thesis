from ryu.base import app_manager
from ryu.controller import event
from ryu.app import msg_handler
from ryu.controller.handler import set_ev_cls

class MsgReceiver(app_manager.RyuApp):

    @set_ev_cls(msg_handler.EventMsg)
    def _test_event_handler(self, ev):
        self.logger.info('*** Received event: ev.msg = %s', ev.msg)
