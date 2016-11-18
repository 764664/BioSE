from src.models.schema import Paper, Author

def store_paper(paper):
    if Paper.objects(title=paper.get("Title")).count() == 0:
        authors = []
        for author in paper.get("Author"):
            if Author.objects(name=author).count() == 0:
                author = Author(name=author)
                author.save()
            else:
                author = Author.objects(name=author).get()
            authors.append(author)
        paper_mongo = Paper(
            title=paper.get("Title"),
            abstract=paper.get("Abstract"),
            journal=paper.get("Journal"),
            authors=authors,
            date=paper.get("Date"),
            url=paper.get("URL")
        )
        paper_mongo.save()
    else:
        paper_mongo = Paper.objects(title=paper.get("Title")).get()
    return paper_mongo