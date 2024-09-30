# Threat Hunting Tool

## Table of Contents
- [Overview](#overview)
- [How it Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Environment Setup](#environment-setup)
- [Software Architecture](#software-architecture)
- [Network Architecture](#network-architecture)

## Overview

A threat hunting tool designed to track various cyber threat indicators by searching dark web sources, 
emphasizing on breached emails, brand mentions, stolen card data (BINs) and domain impersonations. 
The tool automates data extraction and integrates with OpenCTI to save, visualize, correlate and manage threat intelligence.

## How It Works

The Threat Hunting Tool extracts critical data from dark web sources (Breachforums, leakbase ...) and Telegram to enhance threat intelligence capabilities. Here’s a breakdown of the process:

1. **Data Extraction**:
   - The tool retrieves breached email addresses based on a user-provided combination of a domain, subdomain, and an email file, allowing for targeted searches and relevant data collection.
   - It also tracks breached BINs by analyzing a list of BIN prefixes, enabling identification of compromised card data.
   - Additionally, the tool monitors brand mentions by utilizing a list of brand indicators, which include key employees, applications, products, users, and systems associated with the organization.
   - Utilizes the CheckPhish API to detect suspicious lookalike domains by generating and scanning domain variations for DNS records, classifying them using computer vision and machine learning models to identify phishing, scams, and other threats.

2. **Observable Upload**:
   - All relevant breach data, including email addresses, BINs, and brand mentions, is uploaded to OpenCTI as observables, representing the individual threat indicators gathered from the extraction process.

3. **Threat Indicator Upload**:
   - Necessary threat indicators that describe each observable are uploaded to OpenCTI. This contextualizes the data and makes it meaningful for analysis.

4. **Relationship Establishment**:
   - Relationships between the threat indicators are established, enhancing the interconnectedness of the data. This facilitates improved analysis and decision-making for threat hunters by providing insights into how different indicators relate to one another.

5. **Visualization**:
   - An OpenCTI query is utilized to create a widget that visually displays the observables. This provides an intuitive interface for threat hunters to monitor and analyze the data effectively.

![Breached Accounts Widget](./images/breached%20accounts%20widget.png) ![Brand Mentions Widget](./images/brand%20mentions%20widget.png) ![Brand Mentions Widget](./images/breached%20payment%20cards%20widget.png) ![Lookalike Domains Widget](./images/lookalike%20domains%20widget.png)

This structured approach enables proactive threat hunting and enhances the overall cybersecurity posture by leveraging the vast amount of information available in dark web sources and Telegram.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/wassim-maziane/Dark-Web-and-Telegram-Breach-Data-Extractor
    cd threat-hunting-tool
    ```

2. Deploy your environment using Portainer:
   - Add `portainer-agent-stack.yml` to set up Portainer.
   - Once Portainer is running, deploy the OpenCTI stack using Portainer's UI.

3. After the environment is set up, configure the environment variables in 'requiredParameters.env' to connect with your threat intelligence sources (CheckPhish API, Telegram) and OpenCTI.

4. Configure the necessary cookies for scraping dark web and telegram :
   - BREACHFORUMS_USER_COOKIE : Log in to https://breachforums.st and get the "mybbuser" cookie value
   - BREACHFORUMS_DDOS_PREVENTION_COOKIE : Log in to https://breachforums.st and get the "__ddg1_" cookie value
   - CHECKPHISH_USER_COOKIE : log in to https://app.checkphish.ai/ and get the "tau" cookie value
   - TELEGRAM_CHATS : json that contains APT telegram chats coupled with their telegram ID (we can use https://www.breachsense.com/infostealer-channels/ list)

5. Configure what breach data we're looking for : 
   - WATCHLIST_DOMAIN : domain that we want to protect (detect suspicious lookalike ones and extract breached emails within the domain).
   - WATCHLIST_BINLIST : your binlist comma separated (Our tool will detect any breached BINs that start with one of the bins specified here).
   - WATCHLIST_EMAILS_FILE : name of file that contains emails that we want to check if they are breached.
   - WATCHLIST_BRAND_INDICATORS : Comma separeted indicators that our tool will use to identify pages that discuss our brand.

6. Start the tool:
    ```bash
    python telegram.py # this will download breach data files from the specified telegram APT channels
    python main.py
    ```

## Usage

- **Real-time Threat Monitoring**: The tool runs continuously, collecting and saving threat intelligence into OpenCTI for further analysis and action.
- **Analysis**: Use the OpenCTI dashboard to visualize and analyze the data collected from various sources.

## Environment Setup

To use this tool, you need to set up the environment variables in the `requiredParameters.env` file, which the tool will read for API keys, cookies, and configuration.

## Software Architecture

The architecture is modular, with the following components:

- `checkphish.py`: Extracts domain impersonation data from the CheckPhish API.
- `opencti.py`: Saves various threat data (emails, BINs, suspicious domains, etc.) to OpenCTI.
- `helpers.py`: Includes helper functions to scrape web pages,files and save data to CSV or HTML.
- `main.py`: Main entry point for running the tool, invoking scraping and saving routines.
- `breachforums.py`: Extracts breach data from Breachforums.
- `telegram.py`: Extracts breached data from Telegram channels.
- `leakbase.py`: Extracts breach data from Leakbase.

![Software Architecture](./images/software%20architecture%20flameshot.png)

## Network Architecture

The network consists of two main subnets: `192.168.130.0/24` and `10.0.0.0/24`, each serving different roles:

- **Threat Hunter & Docker Admin** (`192.168.130.0/24`): Handles threat detection and Docker management.
- **Docker Swarm** (`10.0.0.0/24`): Orchestrates containers across a node cluster.
- **Minio** (`10.0.4.0/24`): Object storage server.
- **Portainer Client** (`10.0.0.3`): Manages Docker environments.
- **Portainer Agent** (`10.0.4.3`): Assists with container management.
- **Redis** (`10.0.1.12`): In-memory data store.
- **OpenCTI** (`10.0.1.46:8080`): Threat intelligence platform.
- **RabbitMQ** (`10.0.1.28`): Message broker for component communication.
- **Elasticsearch** (`10.0.1.5:9200`): Data storage and search engine.

This architecture ensures smooth integration between container management, data storage, and threat intelligence tools.

![Network Architecture](./images/network%20architecture%20flameshot.png)
