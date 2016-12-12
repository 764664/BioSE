def vectorize_paper(paper):
    year = paper.date.year
    num_author = len(paper.authors)
    len_abstract = len(paper.abstract)
    journal_if, journal_eigen = get_journal_if_and_eigen(paper.journal)
    return [year, num_author, len_abstract, journal_if, journal_eigen]

def get_journal_if_and_eigen(journal_name):
    try:
        stripped_journal_name = re.sub('[\W_]+', '', journal_name.upper())
        journal = Journal.objects(name=stripped_journal_name).get()
        return (journal.impact_factor, journal.eigenfactor_score)
    except Exception as e:
        try:
            if len(stripped_journal_name) >= 16:
                journal = Journal.objects(name__istartswith=stripped_journal_name[:16]).get()
                return (journal.impact_factor, journal.eigenfactor_score)
            if len(stripped_journal_name) >= 12:
                journal = Journal.objects(name__istartswith=stripped_journal_name[:12]).get()
                return (journal.impact_factor, journal.eigenfactor_score)
            elif len(stripped_journal_name) >= 8:
                journal = Journal.objects(name__istartswith=stripped_journal_name[:8]).get()
                return (journal.impact_factor, journal.eigenfactor_score)
            elif len(stripped_journal_name) >= 4:
                journal = Journal.objects(name__istartswith=stripped_journal_name[:4]).get()
                return (journal.impact_factor, journal.eigenfactor_score)
            else:
                return (0, 0)
        except Exception as e:
            return (0, 0)