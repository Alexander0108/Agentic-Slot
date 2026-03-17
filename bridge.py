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
            3. NO CHAT in generation mode. BUT in REPAIR MODE, provide a brief 'DIAGNOSIS' strictly in UKRAINIAN before the code block.
            4. LINEAR LOGIC: Do NOT use internal if-statements to "handle" missing elements.
            5. VISUALS & CRASH: You may wrap the ENTIRE script body inside ONE global try-except to take a failure_screenshot.png, but NEVER wrap individual actions (like .click) in local try-except blocks.
            6. EXECUTION: Always end with: import asyncio \n asyncio.run(test_function_name())
            7. BEST PRACTICES: Use 'page.locator()' instead of 'page.query_selector()'.
            8. ASYNC RULES: Never 'await' the page.locator() method. Only 'await' actions like .click(), .fill().
            9. FORBIDDEN: NEVER use local 'try-except' inside the test for specific elements. If an element is missing, let the test crash.
            10. ANTI-HALLUCINATION: If the requested element is COMPLETELY missing from the HTML context, DO NOT generate code. Output ONLY: "DIAGNOSTIC_FAIL: Element missing".
            11. SELECTORS: Avoid state classes like '.active'. Prefer attributes or text content.
            12. VISIBILITY: ALWAYS launch the browser in visible mode using: await p.chromium.launch(headless=False)
            13. INPUT SUBMISSION: On sites like TodoMVC, there is NO 'Add' button. Use page.keyboard.press('Enter').
            14. STRICT URL: NEVER change or invent URLs. Use EXACTLY the URL provided in the prompt context.
            15. NO TRANSLATION: If the HTML is in English, do NOT search for translated Ukrainian text (e.g., 'Видалити все'). Search only for elements that physically exist in the provided HTML context.
            """

    def generate_test(self, html_context, user_task):
        prompt = f"HTML Context:\n{html_context}\n\nTask: {user_task}"
        print(f"[*] Запит до {self.model_name}...")
        
        response = ollama.generate(
            model=self.model_name,
            system=self.system_prompt,
            prompt=prompt,
            options={"temperature": 0.1,
                     "num_ctx": 32768 }
        )
        return response['response']
    
    def repair_test(self, original_code, error_message, current_html, user_task):
        # Об'єднуємо системні правила та специфіку ремонту
        repair_instructions = f"""
            REPAIR MODE: Попередній тест впав. 
            ОРИГІНАЛЬНИЙ КОД: {original_code}
            ПОМИЛКА: {error_message}
            
            ЗАВДАННЯ:
            1. Напиши 'DIAGNOSIS' українською мовою: що саме пішло не так?
            2. Надай виправлений код.
            3. Використовуй тільки ті елементи, які є в HTML нижче.
            4. Якщо на сайті немає кнопки для відправки — використовуй клавішу Enter.
            
            HTML КОНТЕКСТ:
            {current_html}
        """
        
        print(f"[*] Запит на самовідновлення до {self.model_name}...")
        response = ollama.generate(
            model=self.model_name,
            system=self.system_prompt, # ТУТ ВАЖЛИВО: Передаємо основні 11 правил
            prompt=f"Task: {user_task}\n{repair_instructions}",
            options={"temperature": 0.1,
                     "num_ctx": 32768}
            )
        return response['response']