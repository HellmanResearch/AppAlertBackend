from django.db import models


# class Metric(models.Model):
#     key = models.CharField(max_length=50, unique=True)
#     display = models.CharField(max_length=50, unique=True)
#     rule = models.TextField()
#     status = models.BooleanField()
#
#     create_time = models.DateTimeField(auto_now_add=True)
#     update_time = models.DateTimeField(auto_now=True)

class MetricGroup(models.Model):
    name = models.CharField(max_length=20, unique=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


class Metric(models.Model):
    key = models.CharField(max_length=50, unique=True)
    display = models.CharField(max_length=50, unique=True)
    fields_attr = models.JSONField()
    rule_template = models.TextField()
    group = models.ForeignKey(MetricGroup, on_delete=models.CASCADE, related_name="metrics")
    rules_hint = models.TextField()

    alert_template = models.TextField()

    query_attr = models.JSONField()
    query_template = models.TextField()

    history_display_name = models.CharField(max_length=30)
    history_value_map = models.JSONField(blank=True)
    history_y_unit = models.CharField(max_length=20, blank=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.display


class Rule(models.Model):
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE)
    expr = models.CharField(max_length=255, unique=True, db_index=True)
    disabled = models.BooleanField(default=False)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.expr


class Alert(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE)

    start_at = models.DateTimeField()

    # raw_content = models.TextField()
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
