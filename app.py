#!/usr/bin/env python3
import aws_cdk as cdk

from kindle_news.kindle_news_stack import KindleNewsStack

app = cdk.App()
KindleNewsStack(app, "KindleNewsStack")
app.synth()