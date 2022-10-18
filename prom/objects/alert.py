
from .. import models as l_models


class AlertObject:

    def __init__(self, alert: l_models.Alert):
        self.alert = alert

    def from_alert_manager_content(self):
        pass