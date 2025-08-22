# AI Employee Activity Logger \& Summarizer:



This project is a full-stack application designed to monitor user activity on a computer, store the data in a database, and use an AI model to provide intelligent summaries of the logged actions. It serves as a comprehensive example of integrating a Python data collector, a FastAPI backend, a PostgreSQL database, and a React frontend, all orchestrated with Docker.



## Table of Contents

1. Features
2. Tech Stack
3. Project Structure
4. System Requirements
5. Setup \& Deployment
6. 1\. Clone Repository
7. 2\. Configure Environment Variables
8. 3\. Configure Server Firewall
9. 4\. Build and Run the Stack
10. Running the Activity Logger
11. Application Usage
12. Accessing the Frontend
13. Using the Interface
14. Troubleshooting \& Maintenance



## Tech Stack

* Backend: Python, FastAPI, SQLModel (SQLAlchemy + Pydantic)
* Frontend: React, TypeScript, Vite, Axios
* Database: PostgreSQL
* AI: Hugging Face transformers, torch
* Data Collector: Python (pynput, psutil, pygetwindow)
* Containerization: Docker, Docker Compose
* Web Server: Nginx



### Project Structure

.

├── backend/                # FastAPI backend service

│   ├── app/

│   ├── Dockerfile

│   └── requirements.txt

├── frontend/               # React frontend service

│   ├── src/

│   ├── Dockerfile

│   ├── nginx.conf

│   └── package.json

├── activity\_logger.py      # Standalone data collection script

├── docker-compose.yml      # Main orchestration file

├── .env                    # Docker Compose environment variables (DB credentials)

└── .gitignore              # Files and folders to ignore in Git



## System Requirements

* Server: A Linux host (Ubuntu/Debian recommended) with Docker and Docker Compose installed. Minimum 8GB RAM is recommended due to the AI model.
* Client (for logging): A Windows/macOS/Linux machine with Python 3.8+ installed.

## Setup \& Deployment

These steps are performed on the remote Linux server where the application will be hosted.



##### 1\. Clone Repository

First, clone this repository to your server.



git clone https://github.com/Landform/AI-Application.git my-ai-log-viewer

cd my-ai-log-viewer



##### 2\. Configure Environment Variables

This project uses .env files for configuration. These are not committed to Git for security and must be created on the server.



**a. Main Database Configuration:**

Create a file named .env in the project root (my-ai-log-viewer/.env).



\# my-ai-log-viewer/.env

PG\_DB=ai\_logs

PG\_USER=karanesh

PG\_PASSWORD=jaic0806



**b. Frontend API Configuration:**

Create a file named .env inside the frontend directory (my-ai-log-viewer/frontend/.env). Replace 192.168.1.214 with your server's actual IP address.



\# my-ai-log-viewer/frontend/.env

VITE\_APP\_API\_BASE\_URL=http://192.168.1.214:8001



##### 3\. Configure Server Firewall

Ensure the necessary ports are open on your server's firewall (ufw) and any cloud provider security groups.



\# Allow SSH, Frontend, Backend, and Database ports

sudo ufw allow 22/tcp

sudo ufw allow 3002/tcp

sudo ufw allow 8001/tcp

sudo ufw allow 5433/tcp

sudo ufw enable



##### 4\. Build and Run the Stack

From the project root (my-ai-log-viewer/), run the Docker Compose command. The first build will take some time as it downloads the AI model.



sudo docker compose up -d --build

Verify that all three containers are running:



sudo docker ps



##### Running the Activity Logger:

The activity\_logger.py script should be run on the machine you wish to monitor (e.g., your local Windows PC).



**Install Dependencies:**



pip install pynput psycopg2-binary psutil pygetwindow



**Configure activity\_logger.py:**



Open the script and ensure the DB\_HOST default value points to your remote server's IP address (192.168.1.214).



**Run the Script:**



python activity\_logger.py

The script will now connect to the remote database and start logging your local activity.



##### Application Usage

**Accessing the Frontend**

Open your web browser and navigate to your server's IP address on port 3002:



http://192.168.1.214:3002



##### Using the Interface

**View Logs:** The main table displays activity logs in real-time.

**Filter Data**: Use the input boxes at the top to filter logs by Employee ID, Event Type, or Application Name. Click "Apply Filters" to refresh the view.

**Generate AI Summary:** Select one or more log entries using the checkboxes and click the "Summarize Selected Logs" button. An AI-generated summary will appear.



##### Troubleshooting \& Maintenance

**Stopping the Application:** sudo docker compose down

**Viewing Service Logs:** sudo docker logs <container\_name> (e.g., sudo docker logs my\_ai\_log\_viewer\_backend)

**Resetting the Database**:

sudo docker compose down

sudo docker volume rm my-ai-log-viewer\_ai\_log\_db\_data (Warning: Deletes all log data)

sudo docker compose up -d

