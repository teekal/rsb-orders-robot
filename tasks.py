from robocorp.tasks import task
from robocorp import browser, log
from RPA.Archive import Archive
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    orders = get_orders()

    open_robot_order_website()

    for i in orders:
        log.info(str(i))
        close_annoying_modal()
        fill_the_form(i)
        submit_order()
        pdf_file = store_receipt_as_pdf(i["Order number"])
        screenshot = screenshot_robot(i["Order number"])
        embed_screenshot_to_receipt(screenshot, pdf_file)
        click_order_another()

    archive_receipts()

def open_robot_order_website():
    ""'Navigates to the given URL'
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    ""'Closes modal window by clicking "OK"'
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    ""'Downloads orders.csv and returns table'
    http = HTTP()
    tables = Tables()
    http.download(url = "https://robotsparebinindustries.com/orders.csv", overwrite = True) 
    orders = tables.read_table_from_csv(path = "orders.csv")
    return orders

def fill_the_form(i):
    ""'Fills the order form'
    page = browser.page()
    page.select_option("#head", str(i["Head"]))
    page.check("#id-body-"+str(i["Body"]))
    page.get_by_label('Legs').fill(str(i["Legs"]))
    page.fill("#address", str(i["Address"]))
    
def submit_order():
    ""'Submits order and handles error if visible'
    page = browser.page()
    page.click("button:text('ORDER')")
    while page.locator(".alert-danger").count() > 0:       
        page.click("button:text('ORDER')")

def click_order_another():
    ""'Clicks button to order another robot'
    page = browser.page()
    page.click("#order-another")

def store_receipt_as_pdf(order_number):
    ""'Stores order receipt as PDF file in output directory'
    pdf = PDF()
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf.html_to_pdf(receipt_html, "output/pdfs/"+order_number+".pdf")
    pdf_file = "output/pdfs/"+order_number+".pdf"
    return pdf_file


def screenshot_robot(order_number):
    ""'Takes screenshot of order receipt'
    page = browser.page()
    screenshot = page.locator('#receipt').screenshot(path = "output/screens/"+order_number+".jpg")
    screenshot_file = "output/screens/"+order_number+".jpg"
    return screenshot_file

def embed_screenshot_to_receipt(screenshot, pdf_file):
    ""'Embed screenshot to existing PDF file'
    pdf = PDF()
    pdf.add_files_to_pdf([screenshot], pdf_file, True)

def archive_receipts():
    ""'Archive all receipts into a zip file'
    archive = Archive()
    archive.archive_folder_with_zip("output/pdfs","output/receipts.zip")

