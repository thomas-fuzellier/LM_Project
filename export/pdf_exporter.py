import win32com.client as win32


def docx_to_pdf(docx_path, pdf_path):
    word = win32.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0

    word.ScreenUpdating = False
    word.Options.SaveInterval = 0

    doc = word.Documents.Open(docx_path, ReadOnly=1)
    doc.SaveAs(pdf_path, FileFormat=17)

    doc.Close(False)
    word.Quit()