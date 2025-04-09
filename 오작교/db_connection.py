import mysql.connector
from mysql.connector import Error
import pandas as pd
import logging

def get_db_connection():
    """
    MySQL 데이터베이스에 연결
    
    Returns:
        mysql.connector.connection: 데이터베이스 연결 객체
    """
    try:
        connection = mysql.connector.connect(
            host="database-1.cnu82kme6p4d.ap-northeast-2.rds.amazonaws.com",
            port=3306,
            user="eda",
            password="ojk0707",
            database="ojk"
        )
        
        return connection
            
    except Error as e:
        logging.error(f"MySQL 연결 오류: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """
    쿼리 실행 및 결과 반환 헬퍼 함수
    
    Args:
        query (str): 실행할 SQL 쿼리
        params (tuple, optional): 쿼리 파라미터
        fetch (bool, optional): 결과 반환 여부
    
    Returns:
        list or bool: 쿼리 결과 또는 실행 성공 여부
    """
    connection = get_db_connection()
    
    if not connection:
        logging.error("데이터베이스 연결 실패")
        return None
        
    try:
        with connection.cursor(dictionary=True) as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                connection.commit()
                return True
            
    except Error as e:
        logging.error(f"쿼리 실행 오류: {e}")
        return None
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            
def get_dataframe(table_name, condition=None):
    """
    테이블 데이터를 pandas DataFrame으로 반환
    
    Args:
        table_name (str): 조회할 테이블 이름
        condition (str, optional): WHERE 절 조건
    
    Returns:
        pandas.DataFrame: 조회된 데이터 프레임
    """
    try:
        connection = get_db_connection()
        
        if not connection:
            logging.error("데이터베이스 연결 실패")
            return None
            
        query = f"SELECT * FROM {table_name}"
        
        if condition:
            query += f" WHERE {condition}"
            
        df = pd.read_sql(query, connection)
        
        return df
        
    except Error as e:
        logging.error(f"데이터프레임 변환 오류: {e}")
        return None
    
    finally:
        if connection and connection.is_connected():
            connection.close()