from app import create_server_connection, run_query_basic, run_query
import datetime

connection = create_server_connection()
cursor = run_query_basic(connection, "DELETE FROM PAYMENTINTENTS WHERE timestamp <= DATEADD(minute, -10, CURRENT_TIMESTAMP);")
