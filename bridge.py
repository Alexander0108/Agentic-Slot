import ollama

class AgenticBridge:
    def __init__(self, model_name="qwen2.5-coder:7b"):
        self.model_name = model_name
        self.system_prompt = """
            You are a Senior SDET (Software Development Engineer in Test).
            Your task is to write clean Playwright Python tests.

            STRICT RULES:
            1. LANGUAGE: Use ONLY Python with 'playwright.async_api'.
            2. NO SELENIUM: Using Selenium is a critical failure.
            3. NO CHAT: Return ONLY code blocks.
            4. LINEAR LOGIC: Do NOT use internal if-statements or try-except to "handle" missing elements.
            5. VISUALS & CRASH: Wrap the ENTIRE test logic in one global try-except block. 
               In 'except': 
               await page.screenshot(path='failure_screenshot.png')
               raise  # IMPORTANT: You must re-raise the error so the test fails externally.
            6. EXECUTION: Always end with:
               import asyncio
               asyncio.run(test_function_name())
            7. BEST PRACTICES: Use 'page.locator()' instead of 'page.query_selector()'.
            8. ASYNC RULES: Never 'await' the page.locator() method. Only 'await' actions like .click(), .fill().
            9. FORBIDDEN: Do NOT use 'try' or 'except' inside the test function EXCEPT for the global one for screenshot. Any internal 'try-except' is a failure of your task.
            """

    def generate_test(self, html_context, user_task):
        prompt = f"HTML Context:\n{html_context}\n\nTask: {user_task}"
        print(f"[*] Запит до {self.model_name}...")
        
        response = ollama.generate(
            model=self.model_name,
            system=self.system_prompt,
            prompt=prompt,
            options={"temperature": 0.1}
        )
        return response['response']
    
    def repair_test(self, original_code, error_message, current_html, user_task):
        repair_prompt = f"""
            SYSTEM: You are a Hardcore SDET. 
            
            CRITICAL RULES:
            1. DO NOT use 'try' or 'except' blocks inside the test function.
            2. DO NOT comment out 'asyncio.run()'. It MUST be active.
            3. If the element (Jackpot) is NOT in the HTML, DO NOT try to fix the selector. 
               Instead, write a code that just says: raise Exception("CRITICAL: Element not found in DOM").
            4. The script MUST fail (exit code 1) if the element is missing.

            TASK: {user_task}
            ERROR: {error_message}
            HTML: {current_html}
            """
        
        print(f"[*] Запит на самовідновлення до {self.model_name}...")
        response = ollama.generate(
            model=self.model_name,
            prompt=repair_prompt,
            options={"temperature": 0.1}
        )
        return response['response']