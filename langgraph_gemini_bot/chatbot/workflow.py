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

    # Collect chat history in a formatted way
     chat = []
     for i, item in enumerate(state.history):
        if i % 2 == 0:
            chat.append(f"Human Message is: {item.content}")  # Using f-strings
        else:
            chat.append(f"AI Message is: {item.content}")

     if not state.history:
        return False  # No previous messages to process

     last_message = state.history[-1].content.strip()

     first_prompt = """
AI Text Classifier & Customer Support Assistant
""";
     second_prompt = f"previous chatting is :-  {chat}. for more accurate results.";

     third_prompt = """
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
   - while giving response to customer fallow some rules like 1) you has hear for provide product and servces information avialable on our database to user.
   2) if user enter any personal question that not match with e-commerse product related or service related replay to them like i am hear for give you inforamtion regarding products and services we offers.
   3) if user want information is not related to Database Schema then told user unfortunately this kind of information is not present in our data base right now.You can ask question about products and Suppliers
   4) Before give new response analyze all previous chat firstly.and then give response accordingly.
   5) If you not ensure about which data is present in database not recommend any random data to user. If you recived data from previous chat you can recommend this or use to ask more question to user according to available data (information).  

❌ **Return `{ "is_general": false }`** if:
   - The user query needs database retrieval from `products` or `suppliers`,
   - Is any about products or suppliers,
   - Example: "List all suppliers offering electronics."

---

**User Input:**
""";
    
     prompt = first_prompt + second_prompt + third_prompt + last_message ; 
    
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
     
        a = 0
        chat = []
        for item in state.history: 
             if a % 2 == 0: 
               chat.append(f"Human Message is :- {item.content}"); #using f-strings to format the output
             else:
                chat.append(f"AI Message is :- {item.content}");
             a += 1 ;
      

        last_message = state.history[-1].content
        prompt_first = """
### Expert SQL Query Generator
You are an advanced AI specialized in generating **highly optimized SQL queries**. Your task is to generate SQL queries for retrieving data from the structured database provided below:
""";
        prompt_second = f"previous chatting with user is : - {chat}.  Analyze this chat for making proper query those full fill user requirement.";

        prompt_third = """
### **Database Schema:**


CREATE TABLE Categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,  -- INT instead of SERIAL
    name VARCHAR(100) NOT NULL
);                                                                 

 CREATE TABLE Products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    category_id INT,  -- Matches INT in Categories
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Categories(category_id)
);                                                                                      

 CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,  -- Use INT instead of SERIAL
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
                         
CREATE TABLE Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,  -- Matches INT in Users
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
 
CREATE TABLE OrderItems (
    order_item_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
); 

CREATE TABLE CartItems (
    cart_item_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);

CREATE TABLE Reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    rating INT CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);          

CREATE TABLE Payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INT NOT NULL,
    payment_method VARCHAR(50),
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES Orders(order_id)
);

### **Query Generation Rules:**
✔ **Only generate SELECT queries.**  
✔ **Strictly return the SQL query—no explanations, no markdown formatting.**  
✔ **Ensure SQL safety—prevent SQL injections.**  
✔ **Use `JOIN` statements if needed.**  
✔ **Filter using column names—no ID filtering.**  
✔ **Optimize for performance.**  

---

**User Massage for making Query :**
"""
        extra_message = """  your working flow :- 1)Analyze previous chatting. 
 2) Analyze user Massage for making Query.
 3) understand user requirement on basis on previous chatting and user Massage for making Query.And more focus on User Massage for making Query.
 4) Analyze Database Schema 
 5) First, analyze the database schema and the user's query requirements. If you can generate an accurate SQL query that retrieves the exact required data, then generate that query. However, if an exact match is not possible due to missing or unclear information, generate a query that retrieves the most relevant data based on the available schema. Ensure the query is correctly structured, using appropriate SQL functions, joins, and conditions to optimize accuracy and relevance.
 6) When generating an SQL query, ensure that the search is not strictly word-for-word, as spelling mistakes or variations may occur. Instead of exact matches, use techniques like wildcard searches (LIKE), phonetic matching (SOUNDEX()), or fuzzy matching (LEVENSHTEIN()). The query should account for possible misspellings and retrieve relevant results even if the user's input does not perfectly match the stored data. For example, if the user searches for 'electronic product' but 'electronic' is misspelled in the database, the query should still return relevant results. Use appropriate SQL functions based on the database system (e.g., LIKE, SOUNDEX(), LEVENSHTEIN(), or Full-Text Search).
 """;
        
        final_prompt = prompt_first + prompt_second + prompt_third +  last_message + extra_message;
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
    print("result of query is : -", result);
    state.query_result = result or "No data found."
    return state

def analyze_and_respond(state: ChatBotState):
    """Analyzes query results and formats a response."""
    try:
        a = 0
        chat = []
        for item in state.history: 
             if a % 2 == 0: 
               chat.append(f"Human Message is :- {item.content}"); #using f-strings to format the output
             else:
                chat.append(f"AI Message is :- {item.content}");
             a += 1 ;

               
        print("this is previous history of products ", chat);
        analysis_prompt = f"""
You are an AI chatbot for an eCommerce store. Your goal is to assist users by providing relevant store-related information.  

1) Analyze the previous conversation: {chat}.  
2) Analyze the latest SQL query result: {state.query_result}.  
3) Generate a helpful response that aligns with the user's inquiries while ensuring product IDs or sensitive data are not shared.  
4) Return a response based only on the previous conversation and SQL query results, without including any other information. 
5) insure more things mention in response regarding to SQL query results
"""

        model = get_gemini_model()
        response = model.generate_content(analysis_prompt)
        
        final_response = response.text.strip() if response else "Unable to analyze data."
        state.history.append(AIMessage(content=final_response))
        
        return state
    except Exception:
        state.history.append(AIMessage(content="Error analyzing data."))
        return state
