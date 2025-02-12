import langgraph
from langgraph.graph import StateGraph

# Define a node function that returns a dictionary
def greet(state):
    print(state["message"])  # ✅ Extract message from dict
    return {"message": state["message"]}  # ✅ Return a dictionary

# Create a workflow
workflow = StateGraph(dict)  # ✅ Use `dict` instead of custom class
workflow.add_node("greet", greet)
workflow.set_entry_point("greet")

# Compile and run
app = workflow.compile()
app.invoke({"message": "Hello, LangGraph!"})  # ✅ Pass a dictionary
