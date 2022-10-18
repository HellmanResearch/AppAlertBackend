from .. import models as l_models
import jinja2


class SubscribeObject:

    def __init__(self, object: l_models.Subscribe):
        self.object = object

    # return error_info, render_result
    def render_template_to_expr(self) -> (str, str):
        template = jinja2.Template(self.object.metric.rule_template)
        try:
            return "", template.render(**self.object.conditions)
        except Exception as exc:
            return f"render error: {exc}", ""

    def render_template_to_expr(self) -> (str, str):
        template = jinja2.Template(self.object.metric.rule_template)
        try:
            return "", template.render(**self.object.conditions)
        except Exception as exc:
            return f"render error: {exc}", ""

