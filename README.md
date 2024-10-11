# RAG on PostgreSQL

1. Copy `.env.sample` into a `.env` file.

2. Run these commands to install the requirements, set up the local database, and seed it with test data:

    ```bash
    python -m pip install -r requirements.txt
    python setup_postgres_database.py
    python setup_postgres_seeddata.py
    ```

3. Run the sample flow:

    ```bash
    python main.py
    ```
