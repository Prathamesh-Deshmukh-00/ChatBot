from chatbot.config import get_db_connection

def execute_sql(query):
    """Executes an SQL query and returns the result."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        return str(e)
