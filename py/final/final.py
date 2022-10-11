from airflow.operators.bash_operator import BashOperator
from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from datetime import datetime

default_dag = {
    'owner': 'Ton',
    'start_date': datetime(2022,7,15),
    'email': ['19447.iuh@gmail.com'],
    'email_on_failure': True,
    'email_on_retry' : True,
    'retries' : 1,
    'retries_delay' : timedelta(minutes=5),
}

dag = DAG(
    'ETL_toll_data',
    default_args= default_dag,
    description= 'Apache Airflow Final Assignment',
    schedule_interval= timedelta(days=1),
)

unzip_data = BashOperator(
    task_id = 'unzip_data',
    bash_command= 'tar -xzvf /opt/airflow/dags/final/tolldata.tgz -C /opt/airflow/dags/final/staging',
    dag=dag,
)

extract_vehicle = BashOperator(
    task_id = 'extract_data_from_csv',
    bash_command = 'cut -f1-4 -d"," /opt/airflow/dags/final/staging/vehicle-data.csv | sed "s/$/,/" > /opt/airflow/dags/final/staging/csv_data.csv',
    dag=dag,
)

extract_tollplaza = BashOperator(
    task_id = 'extract_data_from_tsv',
    bash_command = 'tr "\\t" "," < /opt/airflow/dags/final/staging/tollplaza-data.tsv |  tr -d "\\r" | cut -f5-8 -d "," | sed "s/$/,/" > /opt/airflow/dags/final/staging/tsv_data.csv',
    dag=dag, 
)

extract_fixed_width = BashOperator(
    task_id = 'extract_data_from_fixed_width',
    bash_command= 'tr -s " "< /opt/airflow/dags/final/staging/payment-data.txt | cut -d" " -f11-12 | sed "s/$/,/" | tr " " ","  > /opt/airflow/dags/final/staging/fixed_width_data.csv',
    dag=dag,
)

#hợp nhất dữ liệu
extract_consolidate_data = BashOperator(
    task_id = 'consolidate_data',
    bash_command= "paste /opt/airflow/dags/final/staging/csv_data.csv /opt/airflow/dags/final/staging/tsv_data.csv /opt/airflow/dags/final/staging/fixed_width_data.csv\
                    > /opt/airflow/dags/final/staging/extracted_data.csv",
    dag=dag,
)

transform = BashOperator(
    task_id = 'transform_data',
    bash_command = 'cut -d "," -f4 | tr [a-z] [A-Z] < /opt/airflow/dags/final/staging/extracted_data.csv > /opt/airflow/dags/final/staging/transformed_data.csv',
    dag=dag,
)


unzip_data >> extract_vehicle >> extract_tollplaza >> extract_fixed_width >> extract_consolidate_data >> transform