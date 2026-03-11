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
            10. ANTI-HALLUCINATION: If the requested element (e.g., 'Login' button, 'Cart') is COMPLETELY missing from the HTML, DO NOT generate any Python code. Instead, output ONLY this exact phrase: "DIAGNOSTIC_FAIL: Element missing".
            11. SELECTORS: Avoid using state classes like '.active', '.selected', or '.hidden' for clicking. Prefer using text content (e.g., text='Active') or attributes like href.
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
        # Об'єднуємо системні правила та специфіку ремонту
        repair_instructions = f"""
            REPAIR MODE: The previous test failed. 
            ORIGINAL CODE: {original_code}
            ERROR MESSAGE: {error_message}
            
            ADDITIONAL REPAIR RULES:
            1. USE THIS EXACT URL: 'https://demo.playwright.dev/todomvc/#/'
            2. If you see that the element is missing in the provided HTML, use the ANTI-HALLUCINATION rule.
            3. Fix the selector based on the HTML context provided below.
            If the specific element mentioned in the task is missing, look for alternative ways to complete the user's goal using the available HTML elements (e.g., using Enter key instead of a button).
            
            HTML CONTEXT:
            {current_html}
        """
        
        print(f"[*] Запит на самовідновлення до {self.model_name}...")
        response = ollama.generate(
            model=self.model_name,
            system=self.system_prompt, # ТУТ ВАЖЛИВО: Передаємо основні 11 правил
            prompt=f"Task: {user_task}\n{repair_instructions}",
            options={"temperature": 0.1}
        )
        return response['response']