import requests
from bs4 import BeautifulSoup
from time import sleep
from os import makedirs, path

# Variables
CATALOGUE_URL = "https://hnarayanan.github.io/springer-books/"
DL_HOSTNAME = "https://link.springer.com"
JS_DISABLED = "?javascript-disabled=true"


def main():

    ## Get books catalogue

    catalogue_response = requests.get(CATALOGUE_URL)
    # print(type(catalogue_response.text))

    soup = BeautifulSoup(catalogue_response.text, "html.parser")
    # print(soup.ul.find_all('li'))

    categories = [x.a.string for x in soup.ul.find_all("li")]
    # print(categories)

    print("All categories:")
    for i, category in enumerate(categories):
        print("{:2d}. {}".format(i + 1, category))

    print("Which category do you want to download? Enter index")
    download_category = categories[int(input()) - 1]
    print("({})".format(download_category))

    ## Get info of books to download

    books_list_html = (
        soup.find(id=download_category)
        .find_next_sibling("div")
        .find_all("div", {"class": "card-body"})
    )
    books = []
    for blob in books_list_html:
        books.append(
            {
                "name": blob.h5.text,
                "author": blob.h6.contents[0],
                "url": blob.a["href"],
            }
        )
    # print(books)
    print(
        "{} books will be downloaded ".format(len(books)),
        end="",
        flush=True,
    )
    for _ in range(3):
        sleep(1)
        print(".", end="", flush=True)
    sleep(1)
    print("\n")

    ## Download books

    print("Downloading")
    for i, book in enumerate(books):
        try:
            print(
                "{:2d}. {} ... ".format(i + 1, book["name"]),
                end="",
                flush=True,
            )
            book_listing_response = requests.get(book["url"])
            book_listing_soup = BeautifulSoup(
                book_listing_response.text, "html.parser"
            )

            try:
                dl_url = book_listing_soup.find(
                    "a",
                    {"title": "Download this book in EPUB format"},
                ).get("href")
                extension = "epub"
                print("epub found ... ", end="", flush=True)
            except AttributeError:
                try:
                    dl_url = book_listing_soup.find(
                        "a",
                        {"title": "Download this book in PDF format"},
                    ).get("href")
                    extension = "pdf"
                    print("pdf found ... ", end="", flush=True)
                except AttributeError as e:
                    print("download link not found ... ")
                    raise e
            dl_url = DL_HOSTNAME + dl_url + JS_DISABLED
            # print(dl_url)

            filename = "./{}/{} by {}.{}".format(
                download_category,
                book["name"],
                book["author"],
                extension,
            )
            makedirs(path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as file:
                file.write(requests.get(dl_url).content)
            print("done")

        except Exception as e:
            print("failed")
            raise e


if __name__ == "__main__":
    main()
