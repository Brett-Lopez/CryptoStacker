# What is CryptoStacker?
CryptoStacker automates dollar-cost averaging of Bitcoin, Ethereum, & Litecoin on U.S. spot exchanges including Coinbase Pro, Kraken, Binance US, Gemini, FTX US, & Bittrex. With optional, high-availability features CryptoStacker enables you to dollar-cost average even when your favorite exchange is down with automatic failover to your next favorite exchanges.

Take advantage of volatility by breaking up your Crypto dollar-cost averaging (DCA) into tiny $10 purchases spread evenly throughout your purchase period and protect yourself from exchange outages with high availability features.

- Create DCA schedules with a cadence more frequent than once per day (eg: purchase $10 every 300 minutes).
- High availability features that provide resilience for high frequency DCA schedules.
- A product that can help passive investors maximize their DCA by taking advantage of volatility.

![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-08-32.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-08-37.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-08-46.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-08-50.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-08-52.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-05.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-08.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-14.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-21.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-31.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-41.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-48.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-09-58.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-10-15.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-13-35.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-10-22.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-10-25.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-10-29.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-10-37.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-11-04.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-11-32.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-11-56.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-12-45.png)
![screenshot](https://github.com/Brett-Lopez/CryptoStacker/blob/main/screenshots/Screenshot%20from%202022-03-26%2019-12-48.png)



# CryptoStacker's architecture

### Architecture at a high level
- A python/flask webapp
- A service mesh
- An event driven engine for executing dollar-cost averaging events

### Architecture at a medium level
- Python Flask with Gunicorn for the web application
- RESTful services built with AWS API gateway & AWS lambda (python) & AWS serverless MySQL/Aurora
  - All API gateway lambda functions use provisioned currency with autoscaling to
ensure low latency & high availability of API calls.
- All AWS resources defined/configured via Terraform (Infrastructure as
Code)
- AWS SQS queues for asynchronous messaging from job scheduler lambdas (CSR-cron-events-*.py) to event driven lambda functions (CSR-dca-purchaser.py)
- AWS ECS Fargate hosting containerized web app
  - Ephemeral containers with a short 15 minute TTL (immutable
zero touch production)
  - Containers autoscale using a rolling 5 minute average of
network connections per container
  - The containers are built from an extremely lightweight base
image
- AWS ALB for load balancing between the ECS webapp containers
- AWS WAF attached to ALB
- AWS Secrets Manager to store/retrieve secrets
- AWS KMS for encrypting data
- AWS Elasticache/Redis to store server side session management data
- AWS Route53 for DNS records
- AWS VPC Private endpoints used for AWS/Boto3 API calls
- All AWS resources conform to principle of least privilege

# Which third party services does CryptoStacker connect to?
- Auth0 (federated identity provider)
- Opennode (Bitcoin payment gateway)
- Sendgrid (email gateway)
- Persona (know your customer)
- Coinbase Pro's trading APIs for dollar-cost averaging
- Kraken's trading APIs for dollar-cost averaging
- Binance US's trading APIs for dollar-cost averaging
- Gemini's trading APIs for dollar-cost averaging
- FTX US's trading APIs for dollar-cost averaging
- Bittrex's trading APIs for dollar-cost averaging

# CryptoStacker blog posts
- [CryptoStacker blog posts](https://github.com/Brett-Lopez/CryptoStacker/blob/main/blog-posts/README.md)