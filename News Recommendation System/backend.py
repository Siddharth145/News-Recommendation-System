import pandas as pd
import requests
import faiss
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('vader_lexicon')

NEWS_API_KEY = 'd6c7f3bd5dea44c2bcca2879c219183b'
NEWS_API_ENDPOINT = 'https://newsapi.org/v2/everything'

sia = SentimentIntensityAnalyzer()

def fetch_news_for_title(query, num_articles=100):
    params = {
        'q': query,
        'language': 'en',
        'apiKey': NEWS_API_KEY,
        'pageSize': num_articles
    }
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data['articles']
        df = pd.DataFrame(articles)
        return df
    else:
        print("Failed to fetch news:", response.status_code)
        return None

def fetch_recent_news(num_articles=10):
    params = {
        'q': '',
        'language': 'en',
        'apiKey': NEWS_API_KEY,
        'pageSize': num_articles,
        'sortBy': 'publishedAt'  # Ensure the articles are sorted by the most recent
    }
    response = requests.get(NEWS_API_ENDPOINT, params=params)
    
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data['articles']
        df = pd.DataFrame(articles)
        return df
    else:
        print("Failed to fetch news:", response.status_code)
        return None

def get_news_recommendations(query):
    if query == 'recent':
        news_df = fetch_recent_news()
    else:
        news_df = fetch_news_for_title(query)
    
    if news_df is None or news_df.empty:
        return [{'headline': 'News not available at the moment', 'url': '', 'abstract': '', 'text': '', 'author': '', 'source': '', 'content': '', 'urlToImage': 'https://a.exozy.me/dodecahedra/logo.webp', 'sentiment': 0}]

    news_df.rename(columns={'title': 'headline', 'description': 'abstract'}, inplace=True) 
    metadata = news_df.copy()
    metadata['text'] = metadata['headline'].fillna('') + " " + metadata['abstract'].fillna('')
    metadata['text'] = metadata['text'].apply(lambda x: str(x).lower())
    metadata['text'] = metadata['text'].apply(lambda x: re.sub(r'\W+', ' ', x))

    # Using TfidfVectorizer instead of HashingVectorizer
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    tfidf_matrix = vectorizer.fit_transform(metadata['text'])

    d = tfidf_matrix.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(tfidf_matrix.toarray())

    def search(index, query_vector, k=10):
        D, I = index.search(query_vector, k)
        return I[0]

    query_vector = vectorizer.transform([query])
    neighbor_indices = search(index, query_vector.toarray(), k=10)
    
    unique_urls = set()
    recommendations = []
    for idx in neighbor_indices:
        headline = metadata.iloc[idx]['headline']
        url = metadata.iloc[idx]['url']
        text = metadata.iloc[idx]['text']
        abstract = metadata.iloc[idx]['abstract']
        source = metadata.iloc[idx]['source']['name'] if 'name' in metadata.iloc[idx]['source'] else metadata.iloc[idx]['source']
        author = metadata.iloc[idx]['author']
        content = metadata.iloc[idx]['content']
        urlToImage = metadata.iloc[idx]['urlToImage']
        sentiment_score = sia.polarity_scores(headline)['compound']
        
        # Calculate similarity between the query and the headline text
        similarity_score = cosine_similarity(query_vector, vectorizer.transform([text]))[0][0]

        if url not in unique_urls and similarity_score > 0.1:  # Filter based on relevance threshold
            unique_urls.add(url)
            recommendations.append({
                'headline': headline,
                'url': url,
                'abstract': abstract,
                'text': text,
                'author': author,
                'source': source,
                'content': content,
                'urlToImage': urlToImage,
                'sentiment': sentiment_score
            })
    
    if not recommendations:
        recommendations.append({'headline': 'News not available at the moment', 'url': '', 'abstract': '', 'text': '', 'author': '', 'source': '', 'content': '', 'urlToImage': 'https://a.exozy.me/dodecahedra/logo.webp', 'sentiment': 0})

    return recommendations
