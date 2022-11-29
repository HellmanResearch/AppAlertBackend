from django.db import transaction

from .. import models as l_models


@transaction.atomic
def crate_alert_from_prom_alert(prom_alert: l_models):
    subscribes = l_models.Subscribe.objects.filter(rule_id=prom_alert.rule_id)
    for subscribe in subscribes:
        print(f"subscribe: {subscribe}\nuser: {subscribe.user}\nmetric: {subscribe.metric}\nprom_alert_id: {prom_alert.id}")
        alert = l_models.Alert.objects.create(subscribe=subscribe,
                                              user=subscribe.user,
                                              metric=subscribe.metric,
                                              prom_alert_id=prom_alert.id,
                                              confirmed=False
                                              )
