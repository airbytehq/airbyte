def html_body(title, content):
    return f"""
    <!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
        </head>
        <body>
            {content}
        </body>
    </html>
    """
