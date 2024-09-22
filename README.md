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
docker-compose --profile db --profile account --profile order up
```
Here we deploy database and 2 services: account, order. Then, to test these services:
```bash
dock-compose -f auto-test.yml --profile account --profile order up
```

### Deploy and Test all services
```bash
docker-compose --profile system up
```
Then, test all services:
```bash
docker-compose -f auto-test.yml --profile allservice up
```