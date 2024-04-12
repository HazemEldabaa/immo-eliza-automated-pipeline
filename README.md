# ☁️Immo-Eliza-Automated-Pipeline

You have seen the [Immo Eliza Scraper & Data Analyser](https://github.com/HazemEldabaa/immo-eliza-goats), the [Immo Eliza ML Predictor](https://github.com/HazemEldabaa/immo-eliza-ml) and the [Immo Eliza Interactive API App](https://github.com/HazemEldabaa/immo-eliza-deployment).
Now are you ready to see it all come together in one automated powerhouse?

Introducing the Immo Eliza Automation Pipeline in Airflow, where I streamline the journey from raw data scraping to interactive API deployment. This project integrates my proven scraping mechanisms, sophisticated data cleaning processes, robust machine learning models, and user-friendly APIs into a single, seamless workflow.

The Pipeline is scheduled as follows:

- Scraping & Cleaning : Daily
- Model Training & API Update : Monthly
##  📁Project Structure
- dags :
    - clean.py : data cleaning and preprocessing script
    - immoscraper.py : immo properties scraper tool
    - my_scraper_dag.py : script containing the DAG and all the task definitions
    - train_all.py : model training script on the cleaned data
    - version_utils.py : dataset and model versioning functions
- logs : your airflow logs will appear here
- src :
    - counter_data.txts : version number tracker
    - counter_model.txt : version number tracker
- docker-compose.yml : docker-compose for the image
- Dockerfile : image to run airflow with all the dependencies of the DAG
- pipeline-deployment : folder containing similar structure for server deployment on [Astronomer](https://www.astronomer.io/)
# 🏁Getting Started

## 📋Prerequisites
- Python 3.x
- Docker Desktop
## 🛠️Installation

**Clone the Repository:**

```bash
git clone https://github.com/HazemEldabaa/immo-eliza-automated-pipeline.git
cd immo-eliza-automated-pipeline
```
**Create a Virtual Environment (Optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate   # On Windows: \venv\Scripts\activate
```
**Install Dependencies:**

```bash
pip install -r requirements.txt
```
## 👩‍💻Usage
#### To run locally:
Make sure Docker Desktop is installed and running, then run in the terminal:
```bash
docker-compose up --build -d
```
after all the services are running, you should be able to access the Airflow UI from http://localhost:8080/

#### To deploy online:
Create an [Astronomer](https://www.astronomer.io/) account then follow the [Astronomer Documentation](https://docs.astronomer.io/astro/first-dag-cli) to initalize and setup your deployment, make sure you are in the directory of ``/pipeline-deployment`` when you run ```astro dev init```

## 🔒Limitations
Although the pipeline will update the prediction endpoints of the new model to my GitHub repo on the local Airflow run, it is unable to do it through Astronomers servers. 

This is either due to a limitation in Astronomers functionality or how my brain handles git.
## 📷Screenshots
### Airflow Interface on Astronomer:
![Airflow Interface on Astronomer](https://i.ibb.co/rsKHBXC/image.png)
