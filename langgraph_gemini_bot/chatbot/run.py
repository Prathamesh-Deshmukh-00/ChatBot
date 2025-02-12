import asyncio
from chatbot.workflow import (
    process_user_input,
    generate_sql_query,
    execute_query,
    analyze_and_respond,
    check_user_input
)
from chatbot.state import ChatBotState

async def run_chatbot():
    print("\n=== Chatbot Started ===")
    
    chat_state = ChatBotState()

    while True:
        user_text = input("Enter your message: ")

        if user_text.lower().strip() in ['exit', 'quit']:
            print("\n=== Chatbot Terminated ===")
            break

        chat_state = process_user_input(chat_state, user_text.strip())

        # ✅ REMOVE `await`, since `check_user_input` is NOT async
        if not check_user_input(chat_state):  
            chat_state = generate_sql_query(chat_state)
            chat_state = execute_query(chat_state)
            chat_state = analyze_and_respond(chat_state)

        if chat_state.history:
            bot_response = chat_state.history[-1].content
            print(f"\n=== Bot Response ===")
            print(f"Bot: {bot_response}")

# Run the chatbot using asyncio
if __name__ == "__main__":
    asyncio.run(run_chatbot())
