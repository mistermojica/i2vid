import asyncio
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)

async def helper_instagram(ctx):
    logging.info(f"instagram ctx: {ctx}")

    is_development = True

    try:
        logging.info('PROCESO instagram INICIADO')
        logging.info(f'ctx: {ctx}')

        om_launch_options = {
            'headless': not ctx['show'],
            'args': ['--no-sandbox', '--disable-setuid-sandbox']
        }

        if ctx['show']:
            om_launch_options.update({
                'headless': False
            })

        async with async_playwright() as p:
            browser = await p.chromium.launch(**om_launch_options)
            page = await browser.new_page()
            await log_step(page, 'instagram', 'step', 1)

            timeout = 25000
            page.set_default_timeout(timeout)

            # Aquí puedes definir las funciones waitForSelectors, scrollIntoViewIfNeeded, etc.
            await log_step(page, 'instagram', 'step', 5)

            # Insertando el código traducido de Puppeteer a Playwright
            await log_step(page, 'instagram', 'step', 13)

            await page.set_viewport_size({"width": 1000, "height": 700})
            await log_step(page, 'instagram', 'step', 14)

            await page.goto("https://www.instagram.com/")
            await page.wait_for_load_state("networkidle")
            await log_step(page, 'instagram', 'step', 15)

            element = await wait_for_selectors([['input[name="username"]']], page, timeout)
            await scroll_into_view_if_needed(element, timeout)
            await element.click()
            await log_step(page, 'instagram', 'step', 16)

            element = await wait_for_selectors([['input[name="username"]']], page, timeout)
            await scroll_into_view_if_needed(element, timeout)
            type = await element.get_attribute('type')
            if type in ["textarea", "select-one", "text", "url", "tel", "search", "password", "number", "email"]:
                await element.type("bitubi.do", delay=10)
                print('Entrada usuario 1')
            else:
                await element.focus()
                await element.evaluate('(el, value) => { el.value = value; el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true })); }', "bitubi.do")
                print('Entrada usuario 2')
            await log_step(page, 'instagram', 'step', 17)

            await page.keyboard.press("Tab")
            await log_step(page, 'instagram', 'step', 18)

            await page.keyboard.press("Tab")
            await log_step(page, 'instagram', 'step', 19)

            element = await wait_for_selectors([['input[name="password"]']], page, timeout)
            await scroll_into_view_if_needed(element, timeout)
            type = await element.get_attribute('type')
            if type in ["textarea", "select-one", "text", "url", "tel", "search", "password", "number", "email"]:
                await element.type("bitubi@$!#2423OM", delay=20)
                print('Entrada contraseña 1')
            else:
                await element.focus()
                await element.evaluate('(el, value) => { el.value = value; el.dispatchEvent(new Event("input", { bubbles: true })); el.dispatchEvent(new Event("change", { bubbles: true })); }', "bitubi@$!#2423OM")
                print('Entrada contraseña 2')
            await log_step(page, 'instagram', 'step', 20)
            
            
            # browser = playwright.webkit.launch(headless=False)
            # context = browser.new_context()
            # page.goto("https://www.instagram.com/")
            # page.get_by_label("Phone number, username or email address").click()
            # page.get_by_label("Phone number, username or email address").fill("bitubi.do")
            # page.get_by_label("Phone number, username or email address").press("Tab")
            # page.get_by_label("Password").click()
            # page.get_by_label("Password").fill("bitubi@$!#2423OM")
            # page.get_by_role("button", name="Log in", exact=True).click()
            # page.goto("https://www.instagram.com/challenge/action/AXEiTi34ls2Qn8aeZHMgZeyIeJaXv1-MSrPb6rOUbYHh8fjSxrp24ajCKATDLcaD5nBCMpI/Afyw1XNPySWDADV5ylJeNJ8Q4oukNjkMZNQDwaz9BTeBBpyyAwxeciBOSLHDY6p9hiLI9N1siN_XYg/ffc_6NWcq6Fng0ieajDcdTs4VxJq6VIF5RscyFRjwyuhobiSOiMk6bqeDF2fRIW384FZ/")
            # page.get_by_role("button", name="Continue").click()
            # page.get_by_label("Security code").click()
            # page.get_by_label("Security code").fill("676362")
            # page.get_by_role("button", name="Submit").click()
            # page.goto("https://www.instagram.com/challenge/?next=https%3A%2F%2Fwww.instagram.com%2F%3F__coig_challenged%3D1")
            # page.get_by_placeholder("New password", exact=True).click()
            # page.get_by_placeholder("New password", exact=True).click()
            # page.get_by_placeholder("New password", exact=True).fill("bitubi@$!#2423OM")
            # page.get_by_placeholder("New password", exact=True).press("Meta+a")
            # page.get_by_placeholder("New password", exact=True).fill("btb@$!#2423OM")
            # page.locator("form").click()
            # page.get_by_placeholder("Confirm new password").click()
            # page.get_by_placeholder("Confirm new password").fill("btb@$!#2423OM")
            # page.get_by_role("button", name="Next").click()
            # page.goto("https://www.instagram.com/?__coig_challenged=1")
            # page.get_by_role("link", name="New post Create").click()
            # page.get_by_role("link", name="Post Post").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_label("Icon to represent media such as images or videos").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").dblclick()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Select From Computer").click()
            # page.get_by_role("button", name="Next").click()
            # page.get_by_role("button", name="Next").click()
            # page.get_by_role("heading", name="Create new post").click()
            # page.get_by_role("paragraph").click()
            # page.get_by_label("Write a caption...").click()
            # page.get_by_label("Write a caption...").fill("adsfadsf\n")
            # page.get_by_placeholder("Add Location").click()
            # page.get_by_placeholder("Add Location").fill("domi")
            # page.get_by_role("button", name="Dominican Republic", exact=True).click()
            # page.get_by_role("button", name="Share").click()

            # # ---------------------
            # context.close()
            # browser.close()
            

            await browser.close()

        return {"status": "posted"}

    except Exception as error:
        logging.error(f"No encontró el identificador de publicación. IG 2: {error}")
        raise

async def log_step(page, platform, action, step):
    logging.info(f"{platform} {action} {step}")
    await asyncio.sleep(0.1)  # Simular una operación de logging asíncrona

async def wait_for_selectors(selectors, page, timeout):
    for selector in selectors:
        try:
            element = await page.wait_for_selector(selector, timeout=timeout)
            if element:
                return element
        except Exception as err:
            logging.error(err)
    raise Exception(f"Could not find element for selectors: {selectors}")

async def scroll_into_view_if_needed(element, timeout):
    is_in_viewport = await element.is_intersecting_viewport()
    if not is_in_viewport:
        await element.scroll_into_view_if_needed()
