import os
from dotenv import load_dotenv
import google.generativeai as genai

print("\n" + "="*50)
print("🚀 STARTING GEMINI API TEST")
print("="*50)

try:
    # 1. Load .env file
    print("\n1️⃣ Loading environment variables...")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        print("✅ API Key found")
        # Print first 5 chars of API key for verification
        print(f"   Key preview: {api_key[:5]}...")
    else:
        print("❌ API Key not found!")
        raise ValueError("API Key not found in .env file")

    # 2. Configure Gemini
    print("\n2️⃣ Configuring Gemini API...")
    genai.configure(api_key=api_key)
    print("✅ Gemini API configured successfully")

    # 3. Create model
    print("\n3️⃣ Creating Gemini model...")
    model = genai.GenerativeModel("gemini-1.5-flash")
    print("✅ Model created successfully")

    # 4. Test different types of prompts
    print("\n4️⃣ Running test prompts...")
    test_prompts = [
        ("Simple greeting", "Say hello!"),
        ("Given the following database schema: TABLE Suppliers ( ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, contact_info TEXT, product_categories_offered VARCHAR(255 ); TABLE Products ( ID INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) NOT NULL, brand VARCHAR(255), price DECIMAL(10, 2), category VARCHAR(255), description TEXT, supplier_ID INT, FOREIGN KEY (supplier_ID) REFERENCES Suppliers(ID) ; Write a SQL query to retrieve all products (all columns and all rows) from the Products table."),
        ("Math", "What's 15 + 27?"),
        ("Creative", "Write a haiku about coding")
    ]

    # 5. Run tests
    for i, (test_name, prompt) in enumerate(test_prompts, 1):
        print(f"\n🔷 Test {i}: {test_name}")
        print(f"   Prompt: '{prompt}'")
        print("   Sending to Gemini...")
        
        response = model.generate_content(prompt)
        
        print(f"\n📝 Response {i}:")
        print("-" * 50)
        print(response.text)
        print("-" * 50)
        print(f"✅ Test {i} completed successfully")

    # 6. Final status
    print("\n" + "="*50)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print(f"✅ Total tests run: {len(test_prompts)}")
    print("="*50 + "\n")

except Exception as e:
    print("\n" + "="*50)
    print("❌ ERROR OCCURRED")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("="*50 + "\n")
    raise  # Re-raise the exception for debugging

finally:
    print("🏁 Test script finished executing\n")