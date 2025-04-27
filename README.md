# CFSW PROJECT - NEW ARCHITECTURE

The CFSW project has been refactored from its original monolithic design ([Original Repo](https://github.com/quoctruong3105/CFSW)) into a microservices architecture.
 This update includes:

- CI/CD/CT and Infrastructure: Automated Jenkins pipelines for building, testing, and deploying.
- Microservices-based Docker Solution: Each service runs in its own container to promote modularity.
- Development Containers: A consistent development environment using dev containers.
- Continuous Monitoring: Systems to monitor both infrastructure and applications.

## ARCHITECTURE
![software_arch](https://github.com/user-attachments/assets/dbaaee55-aaeb-4320-a693-06951f5a0b7d)

## SERVICES
TODO

## CICDCT
![cfsw-gen2-cicd](https://github.com/user-attachments/assets/2088fe31-c772-4ed4-b4b6-9e814dd1a014)

## PROD DEPLOYMENT
![Blank diagram](https://github.com/user-attachments/assets/0ad6995d-2b84-4d1d-a1cd-198ac0536722)
Automation deployment with Terraform. Please follow `cicd/iac_aws`.

Result:
![getListCake](https://github.com/user-attachments/assets/160886e3-f836-490c-8d22-b360a0049f41)

TODO: implement continuous deployment

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

### Pre-commit Hooks Setup

This repository uses **pre-commit** to ensure code quality by running checks before each commit. It helps maintain a clean codebase by applying automatic fixes, code formatters, and other validation checks on files like `.yml`, `.py`, `Dockerfile`, `.sql`, `.groovy`, and `.json`.

#### Prerequisites

- Python (3.7+ recommended)
- Git

#### Setup

Follow the steps below to set up **pre-commit** in your local environment:

1. **Install Pre-commit**:
```bash
    pip install pre-commit
 ```

2. **Install the Pre-commit Hooks**:
    After cloning the repository, run the following command in the root directory:
```bash
    pre-commit install
```
    This will add pre-commit hooks to run automatically before each commit.

3. **Verify Pre-commit Installation**:
    To ensure that the setup is correct, run:
```bash
    pre-commit run --all-files
```
    This command will execute the hooks on all files in the repository and display any issues found.

#### Usage

After setting up, **pre-commit** will automatically run checks before each `git commit`. If any issues are detected, they must be resolved before the commit is successful.

###### Manual Run

To run the pre-commit hooks manually on all files, use:
```bash
pre-commit run --all-files
```
#### Configuration
The pre-commit configuration is defined in the `.pre-commit-config.yaml` file. It specifies hooks for checking and formatting:
- File types checked: .yml, .yaml, .py, .sql, .groovy, .json, Dockerfile.
- Hooks included:
    - Trailing whitespace removal.
    - End-of-file fixes.
    - YAML validation.
    - JSON validation.
    - Large file detection.
    - Code formatting using black for Python files.
    - Type checking with mypy for Python files.