from django.core.files.storage import default_storage
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from django.db import connection
import pdfplumber
from django.conf import settings


def search_documents(query, limit=10):
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT file_name, file_path, content, faculty, education_level, 
               admission_year, study_field,
               ts_rank(tsv, plainto_tsquery('russian', %s)) as rank
        FROM documents_2
        WHERE tsv @@ plainto_tsquery('russian', %s)
        ORDER BY rank DESC
        LIMIT %s
        """, (query, query, limit))

        results = cursor.fetchall()
        if results:
            documents = [res[2] for res in results]
            vectorizer = TfidfVectorizer()
            tfidf_matrix = vectorizer.fit_transform(documents)
            query_vec = vectorizer.transform([query])

            cosine_similarities = np.dot(tfidf_matrix, query_vec.T).toarray().flatten()

            sorted_results = sorted(zip(results, cosine_similarities),
                                  key=lambda x: x[1], reverse=True)
            return [{
                'file_name': res[0][0],
                'file_path': res[0][1].replace('\\', '/'),
                'faculty': res[0][3],
                'education_level': res[0][4],
                'admission_year': res[0][5],
                'study_field': res[0][6]
            } for res in sorted_results]
    return []

