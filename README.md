# Digital Evacuation Handling Centre 

**Installation and Quickstart**:
1. Install [Python 3.9](https://www.python.org/downloads/) and [CouchDB](http://couchdb.apache.org/) (if required).
2. Clone this repo and navigate to it using your favourite command line.
3. Install the required packages using `pip install -r requirements.txt`.
4. Modify the values in `db.json` to be those appropriate for your CouchDB server.
5. Run `python testdata.py N` (where `N` is an integer) to populate the database with that many test records.
6. Run `python main.py`.