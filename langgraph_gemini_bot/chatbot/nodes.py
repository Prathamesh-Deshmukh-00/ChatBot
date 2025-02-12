import google.generativeai as genai
from chatbot.state import ChatBotState
from langchain.schema import HumanMessage, AIMessage
from chatbot.database import execute_sql
from chatbot.config import get_gemini_model

# Step 1: Convert User Input to SQL
def user_input(state: ChatBotState, user_message: str):
    """Processes user input and updates chatbot state."""
    print("\n" + "="*50)
    print("🎯 Processing User Input")
    print(f"📝 User message: {user_message}")
    
    state.history.append(HumanMessage(content=user_message))
    print("✅ Added to chat history")
    
    return state

def generate_sql_query(state: ChatBotState):
    """Uses Gemini API to generate an SQL query from user input."""
    print("\n" + "="*50)
    print("🤖 Generating SQL Query")
    
    try:
        # Get the last user message
        last_message = state.history[-1].content
        print(f"📥 Last user message: {last_message}")
        
        # Prepare prompt
        prompt = f"Convert this request into an SQL query:\n{last_message}"
        print("📝 Sending prompt to Gemini...")

        # Get model and generate response
        model = get_gemini_model()
        response = model.generate_content(prompt)

        # Validate response
        if response and hasattr(response, 'text') and response.text.strip():
            sql_query = response.text.strip()
        else:
            sql_query = "SELECT 1"
            print("⚠️ Gemini API returned an empty or invalid response.")

        print(f"📤 Generated SQL query: {sql_query}")
        state.sql_query = sql_query
        print("✅ SQL query stored in state")
        
        return state
        
    except Exception as e:
        print(f"❌ Error in generate_sql_query: {str(e)}")
        state.sql_query = "SELECT 1"  # Fallback query
        return state

# Step 2: Execute SQL Query
def execute_query(state: ChatBotState):
    """Executes the generated SQL query and stores results."""
    print("\n" + "="*50)
    print("🔍 Executing SQL Query")
    
    if not state.sql_query:
        print("⚠️ No SQL query found in state")
        state.query_result = "No SQL query generated."
        return state

    print(f"📝 Executing query: {state.sql_query}")
    
    try:
        result = execute_sql(state.sql_query)
        if result and isinstance(result, list):
            print(f"✅ Query executed successfully")
            print(f"📊 Result: {result[:3]}...")  # Show first 3 rows for debugging
        else:
            print("⚠️ No data returned from query")
            result = "No data found."

        state.query_result = result
        return state

    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")
        state.query_result = "Query execution failed."
        return state

# Step 3: Analyze Data & Format Response
def analyze_and_respond(state: ChatBotState):
    """Analyzes query results and formats a response."""
    print("\n" + "="*50)
    print("🤖 Analyzing Results & Generating Response")
    
    try:
        # Prepare analysis prompt
        analysis_prompt = f"Analyze and summarize the following SQL query result:\n{state.query_result}"
        print("📝 Sending analysis prompt to Gemini...")

        # Generate response
        model = get_gemini_model()
        response = model.generate_content(analysis_prompt)

        # Validate response
        if response and hasattr(response, 'text') and response.text.strip():
            final_response = response.text.strip()
        else:
            final_response = "Unable to analyze data."
            print("⚠️ Gemini API returned an empty response.")

        print(f"📤 Generated response: {final_response}")

        # Add to history
        state.history.append(AIMessage(content=final_response))
        print("✅ Response added to chat history")

        # Print current history state
        print("\n📚 Current Chat History:")
        for i, msg in enumerate(state.history):
            print(f"Message {i+1}: {'User' if isinstance(msg, HumanMessage) else 'Bot'}")
            print(f"Content: {msg.content}")
            print("-"*30)
        
        return state
        
    except Exception as e:
        print(f"❌ Error in analyze_and_respond: {str(e)}")
        error_message = "Sorry, I encountered an error analyzing the data."
        state.history.append(AIMessage(content=error_message))
        return state

# Optional: Add a debug function
def debug_state(state: ChatBotState):
    """Prints the current state for debugging."""
    print("\n" + "="*50)
    print("🔍 DEBUG: Current State")
    print(f"SQL Query: {state.sql_query}")
    print(f"Query Result: {state.query_result}")
    print(f"History Length: {len(state.history)}")
    print("="*50 + "\n")
    return state
