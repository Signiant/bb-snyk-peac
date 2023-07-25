# bb-snyk-peac
# BITBUCKET SO NOW YOU KNOW PROJECTS EXPORTED AT CREATION

This lambda function adds bitbucket repos to be monitored via Snyk when in certain bitbucket cloud projects.  Projects in question are evaluated on repo:push events on the Bitbucket org.

### What is this repository for? ###

* This holds the Lambda and related infrastructure that creates a lambda function url for Bitbucket to send repo push events to.
* Once deployed all new repositories that make commits will be added to SNYK should they be in the project list in lambda.py (`projects` var)

### How it works ###

* Bitbucket sends a request to the aws function URL which is backed by a lambda, every time there is a push to your Bitbucket Organization.

### How do I get set up? ###

* In the lambda.py modify the project list to include any bitbucket projects you want to scan for monitoring

* Deploy the solution via the deploy.sh
	* Requires the [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html#install-sam-cli-instructions) to be installed on the environment
  * In the samconfig.toml file, add the bucket you want to host the lambda from, your Bitbucket workspace name, Snyk API token, Snyk Org you want to use, and Snyk intergration ID for Bitbucket 
  * you may wish to change the AWS region as well.
  * Before running make sure to export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and optionally AWS_SESSION_TOKEN to the environment for yoru credentails into the account you are using.

* Once deployed, make a request with the function URL created from the deploy as follows (this example uses CURL):

``curl --request POST --url 'https://api.bitbucket.org/2.0/workspaces/YOURORG/hooks' --user 'USER:PASSPHRASE' --header 'Accept: application/json' -d '
    {
      "description": "bb-snyk-peac",
      "url": "FUNCTION_URL",
      "active": true,
      "events": [
        "repo:push"
      ]
    }'
``
  * Where YOURORG is your Bitbucket organization to monito, and USER:PASS is a username/password with permissions to access the Bitbucket API.

### Other notes ###
* This only works well to monitor repos that have an integration that can be added by the Snyk Console (nodejs,java maven projects)
* test.json is included as a sample json object from a bitbucket webhook call.
* Further improvements can be done to project monitoring and maybe put it as an environment variable
* An internal solution uses AWS Parameter Store for crentials instead of environment variables, we may add open source that later