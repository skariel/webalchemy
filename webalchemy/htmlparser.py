from html.parser import HTMLParser


def get_element_ids(html):
    ids = []

    class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for attr in attrs:
                if attr[0] == 'id':
                    ids.append(attr[1])
    parser = MyHTMLParser()
    parser.feed(html)
    return ids
