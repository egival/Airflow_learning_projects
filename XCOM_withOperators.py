import time
import json
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

def get_order_prices(**kwargs):
    ti=kwargs["ti"]

    order_price_data= {
        'o1': 234.45,
        'o2': 10.00,
        'o3': 34.77,
        'o4': 45.66,
        'o5': 399
    }

    order_price_data_string = json.dumps(order_price_data)
    ti.xcom_push(key ='order_price_data', value = order_price_data_string)

def compute_sum(**kwargs):
    ti = kwargs["ti"]

    order_price_data_string = ti.xcom_pull(task_ids='get_order_prices', key='order_price_data')
    print(order_price_data_string)

    order_price_data = json.loads(order_price_data_string) #returns a Python object, this case dictionary

    total = 0
    for order in order_price_data:
        total+=order_price_data[order]
    ti.xcom_push('total_price', total)

def compute_average(**kwargs):
    ti = kwargs["ti"]

    order_price_data_string = ti.xcom_pull(task_ids='get_order_prices', key='order_price_data')
    print(order_price_data_string)

    order_price_data = json.loads(order_price_data_string) #returns a Python object, this case dictionary

    total = 0
    count = 0
    for order in order_price_data:
        total += order_price_data[order]
        count += 1

    average = total / count

    ti.xcom_push('average_price', average)

def display_result(**kwargs):
    ti=kwargs["ti"]

    total = ti.xcom_pull(task_ids='compute_sum', key='total_price')
    average = ti.xcom_pull(task_ids='compute_average', key = 'average_price')

    print(f"Total price of goods {total}.")
    print(f"Average price of goods {average}.")

with DAG(
    dag_id = 'XCOM_operators',
    start_date=datetime(2024, 7, 6),
    description='XCom with operators',
    tags=['xcom', 'python_operator'],
    schedule='@once',
    catchup=False,
    default_args={
        'owner': 'egi'
    }
):
    get_order_prices = PythonOperator(
        task_id= 'get_order_prices',
        python_callable= get_order_prices
    )

    compute_sum = PythonOperator(
        task_id = 'compute_sum',
        python_callable= compute_sum
    )

    compute_average = PythonOperator(
        task_id = 'compute_average',
        python_callable= compute_average
    )

    display_result = PythonOperator(
        task_id = 'display_result',
        python_callable= display_result
    )

get_order_prices >> [compute_sum, compute_average] >> display_result
