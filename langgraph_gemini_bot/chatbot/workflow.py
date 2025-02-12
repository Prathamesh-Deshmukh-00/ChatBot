import re
import json
import google.generativeai as genai
from chatbot.state import ChatBotState
from langchain.schema import HumanMessage, AIMessage
from chatbot.database import execute_sql
from chatbot.config import get_gemini_model

def process_user_input(state: ChatBotState, user_message: str):
    """Processes user input and updates chatbot state."""
    state.history.append(HumanMessage(content=user_message))
    return state

def clean_sql_query(response_text: str):
    """Removes unwanted characters from the generated SQL query."""
    if not response_text:
        return "SELECT 1"
    
    cleaned_query = re.sub(r"^```sql|```$", "", response_text.strip()).strip()
    return cleaned_query

def clean_response_message(response_text: str):
    """Extracts and cleans the response message, returning a JSON object if applicable or a boolean otherwise."""
    if not response_text:
        return {"is_general": False}  # Default to False if empty

    # Extract content inside triple backticks if present
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response_text.strip(), re.DOTALL)
    cleaned_message = match.group(1).strip() if match else response_text.strip()

    try:
        return json.loads(cleaned_message)  # Attempt to parse as JSON
    except json.JSONDecodeError:
        return {"is_general": cleaned_message.lower() == "true"}  # Convert "true" to True, otherwise False


def check_user_input(state: ChatBotState):
    """Checks if the user input is valid and determines the type of response."""
    last_message = state.history[-1].content
    
    first_prompt = """
### AI Text Classifier & Customer Support Assistant

You are an AI assistant that classifies user messages into:

1️⃣ **General Conversation (`is_general = true`)**
   - Small talk, greetings, or customer service-related inquiries.
   - AI should respond **like a customer support chatbot**.

2️⃣ **Database-Related Inquiry (`is_general = false`)**
   - If the message needs data retrieval from the **products** or **suppliers** tables.
   - AI should **not generate a response** but classify the message correctly.

### **Database Schema:**

📌 **Products Table:**
```sql
TABLE products (
  ID INT PRIMARY KEY,
  name VARCHAR(255),
  brand VARCHAR(255),
  price DECIMAL(10,2),
  category VARCHAR(255),
  description TEXT,
  supplier_ID INT,
  FOREIGN KEY (supplier_ID) REFERENCES suppliers(ID)
);
```

📌 **Suppliers Table:**
```sql
TABLE suppliers (
  ID INT PRIMARY KEY,
  name VARCHAR(255),
  contact_info VARCHAR(255),
  product_categories_offered VARCHAR(255)
);
```

### **Classification Rules:**

✅ **Return `{ "is_general": true, "response": "AI-generated response" }`** if:
   - The user asks casual questions or needs **general help**.
   - Example: "Hi, how are you?" → Respond **naturally**.

❌ **Return `{ "is_general": false }`** if:
   - The user query needs database retrieval from `products` or `suppliers`.
   - Example: "List all suppliers offering electronics."

---

**User Input:**
"""
    
    prompt = first_prompt + last_message 
    
    model = get_gemini_model()
    response = model.generate_content(prompt)
    # print("response from gemini is :-", response.text);
    if response and response.text:
        print("response from gemini is :-", response.text);
        cleaned_response = clean_response_message(response.text)
        print("cleaned_response is :-", cleaned_response);
        if cleaned_response["is_general"]:
            state.query_result = cleaned_response["response"]
            try:
                 state.history.append(AIMessage(content=cleaned_response["response"]))
            except Exception:
                  state.history.append(AIMessage(content="Error analyzing data."))
                    
            return True
    return False

def generate_sql_query(state: ChatBotState):
    """Generates an SQL query using Gemini AI."""
    try:
        last_message = state.history[-1].content
        prompt_first = """
### Expert SQL Query Generator

You are an advanced AI specialized in generating **highly optimized SQL queries**. Your task is to generate SQL queries for retrieving data from the structured database provided below:

### **Database Schema:**

📌 **Products Table:**
```sql
TABLE products (
  ID INT PRIMARY KEY,
  name VARCHAR(255),
  brand VARCHAR(255),
  price DECIMAL(10,2),
  category VARCHAR(255),
  description TEXT,
  supplier_ID INT,
  FOREIGN KEY (supplier_ID) REFERENCES suppliers(ID)
);
```

📌 **Suppliers Table:**
```sql
TABLE suppliers (
  ID INT PRIMARY KEY,
  name VARCHAR(255),
  contact_info VARCHAR(255),
  product_categories_offered VARCHAR(255)
);
```

### **Query Generation Rules:**
✔ **Only generate SELECT queries.**  
✔ **Strictly return the SQL query—no explanations, no markdown formatting.**  
✔ **Ensure SQL safety—prevent SQL injections.**  
✔ **Use `JOIN` statements if needed.**  
✔ **Filter using column names—no ID filtering.**  
✔ **Optimize for performance.**  

---

**User Query:**
"""
        
        final_prompt = prompt_first + last_message
        model = get_gemini_model()
        response = model.generate_content(final_prompt)

        if response and response.text:
            state.sql_query = clean_sql_query(response.text)
        else:
            state.sql_query = "SELECT 1"
        
        return state
    except Exception:
        state.sql_query = "SELECT 1"
        return state

def execute_query(state: ChatBotState):
    """Executes the SQL query and stores results."""
    if not state.sql_query:
        state.query_result = "No SQL query generated."
        return state

    result = execute_sql(state.sql_query)
    state.query_result = result or "No data found."
    return state

def analyze_and_respond(state: ChatBotState):
    """Analyzes query results and formats a response."""
    try:
        analysis_prompt = f"Analyze and summarize the following SQL query result:\n{state.query_result}"
        
        model = get_gemini_model()
        response = model.generate_content(analysis_prompt)
        
        final_response = response.text.strip() if response else "Unable to analyze data."
        state.history.append(AIMessage(content=final_response))
        
        return state
    except Exception:
        state.history.append(AIMessage(content="Error analyzing data."))
        return state
