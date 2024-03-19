import song_details_calc

print(song_details_calc.main())


class Inverted_Index:
    def __init__(self):
        self.inverted_index = {}
        self.query_index = {}
        self.max_freq = {}
        self.total_documents = 0
        self.top_results = None
        self.tp = 0
        self.fp = 0
        self.tn = 0
        self.fn = 0
