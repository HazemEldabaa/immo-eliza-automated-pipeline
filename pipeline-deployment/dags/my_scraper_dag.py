from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
import asyncio
from immoscraper import ImmoCrawler
import clean
import train_all as train
from version_utils import read_counter, increment_counter
def should_run_train():
    
    if datetime.now().day == 16:
        return 'run_train_task'
    else:
        return 'skip_train_task'
    
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 10,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_scraper',
    default_args=default_args,
    description='Immo Eliza Scraper',
    schedule_interval=timedelta(days=60),
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
counter_path = '/opt/airflow/src/counter_data.txt'
version_number = read_counter(counter_path)
def data_version():
    return version_number
def run_async(ti):
    version_number = increment_counter(counter_path)  # Increment and use the new version
    asyncio.run(scrape_async(version_number))
    ti.xcom_push(key='version_number', value=version_number)
async def scrape_async(version_number):
    crawler = ImmoCrawler()
    #version_number = increment_counter(counter_path)
    await crawler.get_properties()
    crawler.to_csv(f"/opt/airflow/src/final_raw_v{version_number}")

def run_train():
    counter_pathh = '/opt/airflow/src/counter_model.txt'
    version_number_model = increment_counter(counter_pathh)
    train.train(version_number_model)

run_scraper_task = PythonOperator(
    task_id='run_scraper', 
    python_callable= run_async,
    provide_context=True,
    dag=dag,
)
def clean_data(ti):
    version_number = ti.xcom_pull(task_ids='run_scraper', key='version_number')
    cleaner = clean
    cleaner.clean_data(f"/opt/airflow/src/final_raw_v{version_number}.csv")



run_clean_task = PythonOperator(
    task_id='run_cleaning', 
    python_callable= clean_data,
    dag=dag,
)



decide_train_or_skip = BranchPythonOperator(task_id='decide_train_or_skip',
                                                python_callable=should_run_train,
                                                dag=dag)
    
skip_train_task = EmptyOperator(task_id='skip_train_task', dag=dag)

run_train_task = PythonOperator(
    task_id='run_train_task', 
    python_callable= run_train,
    dag=dag,
)

model_version = read_counter('/opt/airflow/src/counter_model.txt')



run_scraper_task >> run_clean_task >> decide_train_or_skip

decide_train_or_skip >> run_train_task 
decide_train_or_skip >> skip_train_task