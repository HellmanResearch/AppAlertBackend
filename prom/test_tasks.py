
if __name__ == '__main__':

    import os
    import sys
    import django

    APP_NAME = "AppAlertBackend"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_DIR)
    os.environ["DJANGO_SETTINGS_MODULE"] = f"{APP_NAME}.settings"

    django.setup()

    from . import tasks as l_tasks
    l_tasks.update_rule()

