from langchain.schema import HumanMessage, AIMessage

class ChatBotState:
    def __init__(self, history=None, sql_query=None, query_result=None):
        self.history = history or []
        self.sql_query = sql_query
        self.query_result = query_result
