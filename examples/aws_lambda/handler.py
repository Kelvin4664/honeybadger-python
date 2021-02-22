from honeybadger import honeybadger
from honeybadger.contrib.aws_lambda import AWSLambdaPlugin
from honeybadger.plugins import default_plugin_manager

honeybadger.configure(api_key='your api key')
default_plugin_manager.register(AWSLambdaPlugin())


def lambda_handler(event, context):
    """
    A buggy lambda function that tries to perform a zero division
    """
    a = 1
    b = 0

    return (a/b)