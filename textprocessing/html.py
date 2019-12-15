def write_html(fp, tsv):
    html = """
            
    <html>
    <head>
        <style type="text/css">
		body{{
			font-family: 'Lucida Sans Typewriter';
		}}
		table{{
		    width: 100%;
		}}
		tr:nth-child(even) {{
             background-color: #f2f2f2;
        }}
		td{{
		    vertical-align: top;
		}}
		td:first-child{{
			text-align: right;
		}}
		
		td:nth-child(2), th:nth-child(2){{
			text-align: center;
			padding-left: 10px;
			padding-right: 10px;
			
		}}
		
		th:first-child{{
		    text-align: left
		}}
		th:nth-child(3){{
		    text-align:right;
		}}

        </style>
    </head>
    <body>
        
        <table>
            <tr>
                <th>Words Left</th>
                <th></th>
                <th>Words Right</th>
            </tr>
            <tr>
                <td>
            {text}
                </td>
            </tr>
        </table>
    </body>
    </html>
            
    """.format(text=tsv[:-1]
               .replace('\t', '</td><td>')
               .replace('\n', '</td></tr><tr><td>'))

    with open(fp, 'w') as f:
        f.write(html)
    print(fp)