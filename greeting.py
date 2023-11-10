import requests
import webbrowser
import random
from fuzzywuzzy import fuzz
import spacy

# Replace 'YOUR_API_KEY' with your actual NewsAPI key
api_key = 'd245afc031cc4c528dac9c364a605d68'

# Load a spaCy language model
nlp = spacy.load('en_core_web_sm')

# Define a dictionary to store user context
user_context = {"news_topic": None}

# News API endpoint
news_api_url = 'https://newsapi.org/v2/top-hea dlines'

# Define a list of predefined responses.
responses = {
    "hello": ["Hi there!", "Hello!", "Hey!"],
    "how are you": ["I'm just a chatbot, but I'm doing well!", "I don't have feelings, but thanks for asking."],
    "bye": ["Goodbye!", "See you later!", "Take care!"],
}

# Define a list of valid news topics
valid_topics = [
    "technology", "business", "sports", "entertainment", "science",
    "health", "politics", "world", "finance", "environment",
    "education", "travel", "food", "fashion", "lifestyle",
]

def chatbot_response(user_input):
    user_input = user_input.lower()

    for key in responses:
        if key in user_input:
            return random.choice(responses[key])

    if "news" in user_input:
        if user_context["news_topic"] is None:
            # Analyze available news topics and ask the user to choose one
            available_topics = analyze_news_topics()
            return f"Sure, I can fetch news articles on the following topics:\n{available_topics}\nPlease specify your topic of interest."
        else:
            return fetch_news_articles(user_context["news_topic"])
    
    # Check if the user input is a custom keyword
    custom_keyword = user_input.strip()
    if custom_keyword:
        return fetch_news_articles(custom_keyword)

    # Use spaCy for topic extraction from user input
    extracted_topics = extract_topics(user_input)
    if extracted_topics:
        # Find the most relevant topic from the extracted topics
        closest_topic = find_closest_topic(extracted_topics)
        if closest_topic:
            user_context["news_topic"] = closest_topic
            return fetch_news_articles(closest_topic)

    return "I'm not sure how to respond to that."

def analyze_news_topics():
    return "\n".join(valid_topics)

def extract_topics(text):
    doc = nlp(text)
    topics = [token.text for token in doc if token.text.lower() in valid_topics]
    return topics

def find_closest_topic(extracted_topics):
    max_similarity = 0
    closest_topic = None
    for extracted_topic in extracted_topics:
        for valid_topic in valid_topics:
            similarity = fuzz.ratio(extracted_topic, valid_topic)
            if similarity > max_similarity:
                max_similarity = similarity
                closest_topic = valid_topic

    if max_similarity >= 80:  # Adjust the threshold as needed
        return closest_topic

    return None

def fetch_news_articles(topic):
    # Specify the parameters for the NewsAPI request
    params = {
        'apiKey': api_key,
        'q': topic,
        'language': 'en',
        'pageSize': 5  # You can adjust the number of articles to fetch
    }

    # Make the API request
    response = requests.get(news_api_url, params=params)

    if response.status_code == 200:
        news_data = response.json()
        articles = news_data.get('articles', [])
        if articles:
            news_articles = []
            for article in articles:
                title = article['title']
                description = article['description']
                url = article['url']
                source = article['source']['name']
                news_articles.append(f"Title: {title}\nDescription: {description}\nSource: {source}\nLink: {url}\n")
            return news_articles
        else:
            return ["No news articles found on that topic."]
    else:
        return ["Sorry, there was an issue fetching news articles."]

# Main loop to interact with the chatbot.
while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    response = chatbot_response(user_input)
    print("Chatbot:", response)

    # Check if a link is included in the response and open it in a web browser
    if "Link:" in response:
        link_start = response.index("Link:") + len("Link:")
        link = response[link_start:].strip()
        webbrowser.open(link)  # Open the link in the default web browser
