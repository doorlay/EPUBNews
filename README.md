
# KindleNews
A simple microservice to deliver Associated Press news to my Kindle every morning. This isn't currently designed to allow quick setup for other people, I'm just keeping this public in case anyone wants some project inspiration or wants to fork this.

# Setup
1. After cloning this package, create a new `credentials.env` file in the root folder. Add your API key like follows: `SENDGRID_API_KEY=<your key here>`.

# Deployment
1. Export your AWS credentials for the account you're deploying to:
```
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_SESSION_TOKEN=your_session_token
```
2. Run `python3 -m pip install -r requirements.txt` to install all CDK dependencies.
3. Run `./package_lambda.sh` to install all Lambda dependencies.
4. [Optional] To see a CDK diff for the deployment, run `cdk diff`.
5. Run `cdk synth && cdk deploy`.
