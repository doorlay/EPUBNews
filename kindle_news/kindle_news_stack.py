from constructs import Construct
from aws_cdk import Stack, Duration
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda import Function, Runtime, Code


# Load environment variables from .env file
env_vars = dict()
with open("credentials.env") as env_file:
    for line in env_file:
        key, value = line.strip().split("=")
        env_vars[key] = value

class KindleNewsStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Lambda function that scrapes and sends news data to your Kindle
        scraper_function = Function(
            self, 
            "ScraperFunction", 
            runtime=Runtime.PYTHON_3_11, 
            handler="lambda.handler", 
            code=Code.from_asset("lambda"), 
            timeout=Duration.minutes(5), 
            function_name="ScraperFunction", 
            environment=env_vars,
        )
        
        # Invokes the above function at 6am PST every day
        scraper_rule = Rule(self, "ScraperRule", schedule=Schedule.cron(hour="14",minute="0"), rule_name="ScraperRule", enabled=False)
        scraper_rule.add_target(LambdaFunction(scraper_function))
