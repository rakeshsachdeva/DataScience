from PyPDF2 import PdfFileReader

def extract_information(pdf_path):
    with open(pdf_path, 'rb') as f:
        pdf = PdfFileReader(f)
        information = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()

    txt = f"""
    Information about {pdf_path}: 

    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """

    print(txt)
    return information

if __name__ == '__main__':
    path = '/Users/rsachdeva/Documents/pythonProjs/W2/0064O00000aDlOMQA0-00P4O00001JkXqNUAV-Brenton Dyer - W2.pdf'
    print(extract_information(path))
    import PyPDF2

    pdf_file = open(path,"ab")
    # pdf_file.seek(0, 2)
    # pdf_file.seek(-3, 2)
    # pdf_file.seek(-1, 2)

    read_pdf = PyPDF2.PdfFileReader(pdf_file)
    number_of_pages = read_pdf.getNumPages()
    page = read_pdf.getPage(0)
    page_content = page.extractText()
    print(page_content)