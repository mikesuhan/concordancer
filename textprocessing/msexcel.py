import xlsxwriter

def write_xlsx(fp, conc_text, words_left=None):
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook(fp)
    worksheet = workbook.add_worksheet()

    # one cell for every word
    if words_left:
        text = []
        for i, row in enumerate(conc_text.splitlines()):
            text.append([])
            for k, conc in enumerate(row.split('\t')):
                conc = conc.split()
                while len(conc) > words_left:
                    conc.insert(0, '')
                text[i] += conc

    # 3 cells for left, right, and center
    else:
        text = [row.split('\t') for row in conc_text.splitlines()]

        left_cell_format = workbook.add_format({'align': 'right'})
        worksheet.set_column(0, 0, None, left_cell_format)

    # Iterate over the data and write it out row by row.
    for r, row in enumerate(text):
        for c, cell in enumerate(row):
            worksheet.write(r, c, cell)

    workbook.close()