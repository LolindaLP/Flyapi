import pandas as pd
from collections import defaultdict
import json
import boto3

# Функция для очистки данных
def clean_data(value):
    if pd.isna(value):
        return None  # Заменить NaN на None
    if isinstance(value, str):
        return value.strip()  # Удалить лишние пробелы
    return value

# Функция для обработки данных
def process_data(csv_path):
    df = pd.read_csv(csv_path)
    for column in df.columns:
        df[column] = df[column].apply(clean_data)
    df = df.dropna(subset=['IATA_Code'])
    df = df[df['IATA_Code'].str.strip() != '']
    
    airports_grouped = defaultdict(list)
    
    for index, row in df.iterrows():
        city = row['Municipality']
        airport_name = row['Name']
        iata_code = row['IATA_Code']
        
        if city is None or city.strip() == '':
            continue
        
        airports_grouped[city].append({
            'IATA_Code': iata_code,
            'Name': airport_name
        })
    
    return airports_grouped

# Функция для загрузки данных в DynamoDB
def upload_to_dynamodb(airports_grouped, table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    for city, airports in airports_grouped.items():
        if city is None or city.strip() == '':
            continue
        
        item = {
            'City': city,
            'Airports': airports
        }
        
        # Запись данных в DynamoDB
        table.put_item(Item=item)

    print("Данные успешно загружены в DynamoDB!")

# Основной код
if __name__ == "__main__":
    csv_path = 'E:\\Fly_searcher\\data.csv\\data.csv'
    table_name = 'AirportsTable'

    airports_grouped = process_data(csv_path)
    
    output_json_path = 'E:\\Fly_searcher\\data.csv\\airports_grouped.json'
    with open(output_json_path, 'w') as json_file:
        json.dump(
            [{'City': city, 'Airports': airports} for city, airports in airports_grouped.items()],
            json_file,
            indent=4
        )
    
    print(f"JSON файл создан по пути {output_json_path}")

    upload_to_dynamodb(airports_grouped, table_name)
