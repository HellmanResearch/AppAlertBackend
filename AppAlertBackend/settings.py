"""
Django settings for AppAlertBackend project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

from . import project_env

ENV = project_env.ENV

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-l78czf^hm4ba&k-dg!@hs32)(hg^serm+(#^$a4ci!1&7&xc3('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_results',
    'users',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'drf_yasg',
    'devops_django',
    'prom',
    'alerting',
    'data',
    'ssv',
    'c_test',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = "users.User"

ROOT_URLCONF = 'AppAlertBackend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AppAlertBackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ssv_alerting_3',
        'USER': 'root',
        'PASSWORD': 'wonders,1',
        'HOST': '192.168.1.128',
        'PORT': '3308'
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = ["http://192.168.19.27:3001"]
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'token',
)

SESSION_COOKIE_AGE = 86400 * 7

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.BasicAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        'devops_django.authentication.CsrfExemptSessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'devops_django.paginations.StandardResultsSetPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    )
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        },
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
            # 日志格式
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'prom': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/prom.log',
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'alerting': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/alerting.log',
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
        'tasks': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/tasks.log',
            'maxBytes': 1024 * 1024 * 20,
            'backupCount': 5,
            'encoding': 'utf-8',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db': {
            'handlers': ['console'] if ENV != "PRO" else [],
            'level': 'DEBUG',
            'propagate': False,
        },
        'prom': {
            'handlers': ['prom'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'alerting': {
            'handlers': ['alerting'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'tasks': {
            'handlers': ['tasks'],
            'level': 'DEBUG',
            'propagate': False,
        }
    }
}


BASE_URL = "http://localhost:8000"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.hellman.team'
EMAIL_HOST_USER = 'alert@hellman.team'
EMAIL_HOST_PASSWORD = 'alert,1'
EMAIL_PORT = 25

ALIYUN_ACCESS_KEY = "LTAI5t7DGRvbJupLBNEAq7ne"
ALIYUN_ACCESS_KEY_SECRET = "MRxEnumhyNC0MZgwAx94mYOUUUJoCF"
ALIYUN_EMAIL_ACCOUNT_NAME = "alert@hellman.team"

PROM_RULE_FILE = "/tmp/ssv_rules.yml"
PROM_BASE_URL = "http://192.168.1.128:9090"
PROM_ADDR = "127.0.0.1"

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CELERY_BROKER_URL = "amqp://alert:alert,1@192.168.1.128/alert"
CELERY_RESULT_BACKEND = "django-db"


STATIC_URL = '/django-static/'
STATIC_ROOT = os.path.join(BASE_DIR, "django-static")

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Set None if not use proxy
DISCORD_HTTPS_PROXY = "http://8.210.127.228:1443"

SSV_NODE_WS = "ws://39.101.65.17:15001"

SSV_ABI = '[{"inputs":[],"name":"ApprovalNotWithinTimeframe","type":"error"},{"inputs":[],"name":"CallerNotOwner","type":"error"},{"inputs":[],"name":"CallerNotWhitelisted","type":"error"},{"inputs":[],"name":"ClusterAlreadyEnabled","type":"error"},{"inputs":[],"name":"ClusterDoesNotExists","type":"error"},{"inputs":[],"name":"ClusterIsLiquidated","type":"error"},{"inputs":[],"name":"ClusterNotLiquidatable","type":"error"},{"inputs":[],"name":"ExceedValidatorLimit","type":"error"},{"inputs":[],"name":"FeeExceedsIncreaseLimit","type":"error"},{"inputs":[],"name":"FeeIncreaseNotAllowed","type":"error"},{"inputs":[],"name":"FeeTooLow","type":"error"},{"inputs":[],"name":"IncorrectClusterState","type":"error"},{"inputs":[],"name":"InsufficientBalance","type":"error"},{"inputs":[],"name":"InvalidOperatorIdsLength","type":"error"},{"inputs":[],"name":"InvalidPublicKeyLength","type":"error"},{"inputs":[],"name":"NewBlockPeriodIsBelowMinimum","type":"error"},{"inputs":[],"name":"NoFeeDelcared","type":"error"},{"inputs":[],"name":"OperatorDoesNotExist","type":"error"},{"inputs":[],"name":"SameFeeChangeNotAllowed","type":"error"},{"inputs":[],"name":"TokenTransferFailed","type":"error"},{"inputs":[],"name":"UnsortedOperatorsList","type":"error"},{"inputs":[],"name":"ValidatorAlreadyExists","type":"error"},{"inputs":[],"name":"ValidatorDoesNotExist","type":"error"},{"inputs":[],"name":"ValidatorOwnedByOtherAddress","type":"error"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"previousAdmin","type":"address"},{"indexed":false,"internalType":"address","name":"newAdmin","type":"address"}],"name":"AdminChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"beacon","type":"address"}],"name":"BeaconUpgraded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"indexed":false,"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"ClusterDeposited","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"indexed":false,"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"ClusterLiquidated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"indexed":false,"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"ClusterReactivated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"indexed":false,"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"ClusterWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint64","name":"value","type":"uint64"}],"name":"DeclareOperatorFeePeriodUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint64","name":"value","type":"uint64"}],"name":"ExecuteOperatorFeePeriodUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"address","name":"recipientAddress","type":"address"}],"name":"FeeRecipientAddressUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint8","name":"version","type":"uint8"}],"name":"Initialized","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint64","name":"value","type":"uint64"}],"name":"LiquidationThresholdPeriodUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"MinimumLiquidationCollateralUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"},{"indexed":false,"internalType":"address","name":"recipient","type":"address"}],"name":"NetworkEarningsWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint256","name":"oldFee","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"newFee","type":"uint256"}],"name":"NetworkFeeUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"},{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"bytes","name":"publicKey","type":"bytes"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"OperatorAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"}],"name":"OperatorFeeCancellationDeclared","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"},{"indexed":false,"internalType":"uint256","name":"blockNumber","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"OperatorFeeDeclared","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"},{"indexed":false,"internalType":"uint256","name":"blockNumber","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"fee","type":"uint256"}],"name":"OperatorFeeExecuted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint64","name":"value","type":"uint64"}],"name":"OperatorFeeIncreaseLimitUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"}],"name":"OperatorRemoved","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"},{"indexed":false,"internalType":"address","name":"whitelisted","type":"address"}],"name":"OperatorWhitelistUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint64","name":"operatorId","type":"uint64"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"OperatorWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferStarted","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"implementation","type":"address"}],"name":"Upgraded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"indexed":false,"internalType":"bytes","name":"publicKey","type":"bytes"},{"indexed":false,"internalType":"bytes","name":"shares","type":"bytes"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"indexed":false,"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"ValidatorAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":false,"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"indexed":false,"internalType":"bytes","name":"publicKey","type":"bytes"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"indexed":false,"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"ValidatorRemoved","type":"event"},{"inputs":[],"name":"acceptOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"}],"name":"cancelDeclaredOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"clusters","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"dao","outputs":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"balance","type":"uint64"},{"internalType":"uint64","name":"block","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"},{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"declareOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"declareOperatorFeePeriod","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"internalType":"uint256","name":"amount","type":"uint256"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"deposit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"}],"name":"executeOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"executeOperatorFeePeriod","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"string","name":"initialVersion_","type":"string"},{"internalType":"contract IERC20","name":"token_","type":"address"},{"internalType":"uint64","name":"operatorMaxFeeIncrease_","type":"uint64"},{"internalType":"uint64","name":"declareOperatorFeePeriod_","type":"uint64"},{"internalType":"uint64","name":"executeOperatorFeePeriod_","type":"uint64"},{"internalType":"uint64","name":"minimumBlocksBeforeLiquidation_","type":"uint64"},{"internalType":"uint256","name":"minimumLiquidationCollateral_","type":"uint256"}],"name":"initialize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"liquidate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"minimumBlocksBeforeLiquidation","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"minimumLiquidationCollateral","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"network","outputs":[{"internalType":"uint64","name":"networkFee","type":"uint64"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"networkFeeIndexBlockNumber","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"operatorFeeChangeRequests","outputs":[{"internalType":"uint64","name":"fee","type":"uint64"},{"internalType":"uint64","name":"approvalBeginTime","type":"uint64"},{"internalType":"uint64","name":"approvalEndTime","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"operatorMaxFeeIncrease","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"operators","outputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"uint64","name":"fee","type":"uint64"},{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"components":[{"internalType":"uint64","name":"block","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint64","name":"balance","type":"uint64"}],"internalType":"struct ISSVNetworkCore.Snapshot","name":"snapshot","type":"tuple"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"operatorsWhitelist","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pendingOwner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"proxiableUUID","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"internalType":"uint256","name":"amount","type":"uint256"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"reactivate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"},{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"reduceOperatorFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"registerOperator","outputs":[{"internalType":"uint64","name":"id","type":"uint64"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"internalType":"bytes","name":"shares","type":"bytes"},{"internalType":"uint256","name":"amount","type":"uint256"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"registerValidator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"}],"name":"removeOperator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"bytes","name":"publicKey","type":"bytes"},{"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"removeValidator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"recipientAddress","type":"address"}],"name":"setFeeRecipientAddress","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"},{"internalType":"address","name":"whitelisted","type":"address"}],"name":"setOperatorWhitelist","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"newDeclareOperatorFeePeriod","type":"uint64"}],"name":"updateDeclareOperatorFeePeriod","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"newExecuteOperatorFeePeriod","type":"uint64"}],"name":"updateExecuteOperatorFeePeriod","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"blocks","type":"uint64"}],"name":"updateLiquidationThresholdPeriod","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"updateMinimumLiquidationCollateral","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"fee","type":"uint256"}],"name":"updateNetworkFee","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"newOperatorMaxFeeIncrease","type":"uint64"}],"name":"updateOperatorFeeIncreaseLimit","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"}],"name":"upgradeTo","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newImplementation","type":"address"},{"internalType":"bytes","name":"data","type":"bytes"}],"name":"upgradeToAndCall","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"name":"validatorPKs","outputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"bool","name":"active","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"validatorsPerOperatorLimit","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"version","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint64[]","name":"operatorIds","type":"uint64[]"},{"internalType":"uint256","name":"amount","type":"uint256"},{"components":[{"internalType":"uint32","name":"validatorCount","type":"uint32"},{"internalType":"uint64","name":"networkFeeIndex","type":"uint64"},{"internalType":"uint64","name":"index","type":"uint64"},{"internalType":"uint256","name":"balance","type":"uint256"},{"internalType":"bool","name":"active","type":"bool"}],"internalType":"struct ISSVNetworkCore.Cluster","name":"cluster","type":"tuple"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawNetworkEarnings","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"withdrawOperatorEarnings","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint64","name":"operatorId","type":"uint64"}],"name":"withdrawOperatorEarnings","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
SSV_ADDRESS = "0xAfdb141Dd99b5a101065f40e3D7636262dce65b3"
SSV_INIT_HEIGHT = 8726650
ETH_URL = "https://goerli.infura.io/v3/46492c5932f74d2e8104fb2f33729aed"
CELERY_PROMETHEUS_PORT = 9019
