# KindleNews
A simple microservice to deliver Associated Press news to my Kindle every morning. This isn't currently designed to allow quick setup for other people, I'm just keeping this public in case anyone wants some project inspiration or wants to fork this.


## Setup
1. Create and activate a virtual environment: `python3 -m venv . && source bin/activate`
2. Run the setup script to install required dependencies: `./setup.sh`
3. Create an API key on the SendGrid website. After doing so, put your API key into the credentials.env file.

## Testing
To perform a local test, run `python3 src/tests.py`. A sample news file called test_file.txt will be created in the "test_files" directory.

## Deployment
1. Export your AWS credentials for the account you're deploying to:
```
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
export AWS_SESSION_TOKEN=your_session_token
```
2. [Optional] To see a CDK diff for the deployment, run `cdk diff`.
3. Run `cdk synth && cdk deploy`.

## Future Work
1. The biggest pain point of this service is that a new file is created every day, causing quite a bit of spam when you don't read for a bit. This also means that you need to manually delete each file, which is a bit of a pain. Instead, let's see if we can just update the file with the new news every day, deleting the previous content within it, instead of making a whole new file each time.