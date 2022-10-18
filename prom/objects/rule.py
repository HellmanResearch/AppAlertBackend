from .. import models as l_models


class RuleObject:

    def __init__(self, rule: l_models.Rule):
        self.rule = rule

    @staticmethod
    def get_or_crate(metric: l_models.Metric, expr: str) -> l_models.Rule:
        return l_models.Rule.objects.get_or_create(metric=metric, expr=expr)
