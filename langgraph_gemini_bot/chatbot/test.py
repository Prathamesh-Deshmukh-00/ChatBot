import google.generativeai as genai

# Replace with your actual API key
genai.configure(api_key="AIzaSyD95-QXYZkz0iFIhcBtoDGDcjxVf5wb6ts")

def image_des():
    # Load the generative model
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Generalized prompt for generating a SQL query
    prompt = """
    Given the following database schema:
    TABLE Suppliers ( ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, contact_info TEXT, product_categories_offered VARCHAR(255) );
    TABLE Products ( ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, brand VARCHAR(255), price DECIMAL(10, 2), category VARCHAR(255), description TEXT, supplier_ID INT, FOREIGN KEY (supplier_ID) REFERENCES Suppliers(ID) );
    Write a SQL query to retrieve all products (all columns and all rows) from the Products table.
    """
    
    try:
        # Generate the content from the model
        response = model.generate_content(prompt)
        print("Response is:", response.text)
    except Exception as error:
        print("Error occurred in code:", error)

# Run the function
image_des()
