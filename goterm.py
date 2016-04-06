class GoTerm:
    def __init__(self):
        self.names = []
        with open("./resources/go.obo", 'r') as f:
            for line in f:
                if line[:5] == "name:":
                    self.names.append(line[6:])

    def starts_with(self, keyword):
        len_keyword = len(keyword)
        r = [term for term in self.names if term[:len_keyword]==keyword]
        r.sort(key=len)
        return r[:10]

if __name__ == "__main__":
    go = GoTerm()
    print(go.starts_with("methy"))