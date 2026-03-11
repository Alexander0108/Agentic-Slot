import asyncio
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

class SlotScraper:
    def __init__(self):
        # Залишаємо тільки те, що допоможе ШІ написати стабільний селектор
        self.qa_attrs = ["id", "class", "data-qa", "data-testid", "name", "role", "type"]

    async def get_cleaned_html(self, url):
        async with async_playwright() as p:
            print(f"[*] Запуск браузера для: {url}")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Чекаємо, поки iGaming скрипти відпрацюють
            await page.goto(url, wait_until="networkidle")
            
            # Беремо весь HTML сторінки
            raw_html = await page.content()
            await browser.close()
            
            return self.clean_dom(raw_html)

    def clean_dom(self, html):
        soup = BeautifulSoup(html, "html.parser")
        
        # Видаляємо теги-сміття, які забивають пам'ять LLM
        for tag in soup(["script", "style", "svg", "path", "noscript", "link", "header", "footer"]):
            tag.decompose()

        # Очищаємо атрибути кожного тегу
        for tag in soup.find_all(True):
            # Залишаємо тільки ті атрибути, що в нашому списку qa_attrs
            tag.attrs = {k: v for k, v in tag.attrs.items() if k in self.qa_attrs}
            
            # Якщо тег порожній і без атрибутів - він нам не треба
            if not tag.contents and not tag.attrs:
                tag.decompose()

        return str(soup.prettify())

if __name__ == "__main__":
    # Тест скрейпера на реальному (публічному) ресурсі
    scraper = SlotScraper()
    url = "https://demo.playwright.dev/todomvc/"
    
    cleaned = asyncio.run(scraper.get_cleaned_html(url))
    print("--- Очищений HTML (перші 500 символів) ---")
    print(cleaned[:500])
    
    with open("cleaned_context.txt", "w", encoding="utf-8") as f:
        f.write(cleaned)