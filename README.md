# CFSW PROJECT - NEW ARCHITECTURE

The CFSW project has been refactored from its original monolithic design ([Original Repo](https://github.com/quoctruong3105/CFSW)) into a microservices architecture.
 This update includes:

- CI/CD/CT and Infrastructure: Automated Jenkins pipelines for building, testing, and deploying.
- Microservices-based Docker Solution: Each service runs in its own container to promote modularity.
- Development Containers: A consistent development environment using dev containers.
- Continuous Monitoring: Systems to monitor both infrastructure and applications.

## ARCHITECTURE
TODO

## SERVICES
TODO

## CICDCT
![CICD-flow](https://github.com/user-attachments/assets/1c096cad-aec6-4686-96de-2cf55e702a94)

## HOW TO RUN ON LOCAL

### Deploy and Test one or more specific service
```bash
docker-compose -f docker-compose.test.yml --env-file project.env --profile db --profile account up
```
Here we deploy database and account service. Then, to test account service:
```bash
docker-compose -f auto-test.yml --profile account up
```

### Deploy and Test all services
```bash
docker-compose -f docker-compose.test.yml --env-file project.env --profile system up
```
Then, test all services:
```bash
docker-compose -f auto-test.yml --profile allservice up
```

### Run in debug mode (support only 1 service each time)
Step 1: Config file project.env:
    Modify the `project.env` file to set the service you want to debug by adjusting the `APP_NAME` environment variable.
    Example: To debug the `account` service:
```bash
    APP_NAME=account
```
Step 2: Config `.vscode/launch.json`
    Update the localRoot path in the .vscode/launch.json file to point to the source directory of the service you are debugging.
    Example: If debugging the app.py file of the account service:
```json
    "localRoot" : "${workspaceFolder}\\services\\account\\src"
```
Step 3: Run Docker Compose with Debug Profiles
    Run the command below to deploy both the db service and the service you want to debug. Ensure that the correct profiles for the services are specified.
    Example: To debug the account service:
```bash
    docker-compose -f docker-compose.debug.yml --env-file project.env --profile db --profile account up
```
Step 4: In Visual Studio Code, go to the "Run and Debug" tab and select Python: Remote Attach to start debugging the specified service.
