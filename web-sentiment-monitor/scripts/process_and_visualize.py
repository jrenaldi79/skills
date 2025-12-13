import json
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter
import re

def clean_text(text):
    if not text: return ''
    text = re.sub(r'(\\[nrt]|\s)+', ' ', text)
    text = re.sub(r'https?://\\S+', '', text)
    return text.strip()

def get_source_type(url):
    if 'reddit.com' in url:
        return 'Reddit'
    elif 'youtube.com' in url:
        return 'YouTube'
    else:
        return 'Web'

def main(input_path, output_dir):
    charts_dir = os.path.join(output_dir, 'charts')
    os.makedirs(charts_dir, exist_ok=True)

    with open(input_path, 'r') as f:
        raw_data = json.load(f)

    analyzer = SentimentIntensityAnalyzer()
    processed_records = []
    all_keywords = []

    for item in raw_data:
        content = item.get('markdown', item.get('description', ''))
        if not content or content == '...':
            continue

        cleaned_content = clean_text(content)
        if not cleaned_content:
            continue

        sentiment_scores = analyzer.polarity_scores(cleaned_content)
        compound_score = sentiment_scores['compound']

        if compound_score > 0.05:
            sentiment_label = 'Positive'
        elif compound_score < -0.05:
            sentiment_label = 'Negative'
        else:
            sentiment_label = 'Neutral'

        record = {
            'url': item.get('url', ''),
            'title': item.get('title', 'No Title'),
            'source': get_source_type(item.get('url', '')),
            'word_count': len(cleaned_content.split()),
            'sentiment_score': compound_score,
            'sentiment_label': sentiment_label,
            'cleaned_text': cleaned_content[:500]
        }
        processed_records.append(record)

        words = re.findall(r'\\b\\w{4,}\\b', cleaned_content.lower())
        common_stopwords = ['life360', 'that', 'with', 'this', 'from', 'have', 'just', 'like', 'they', 'your', 'about', 'https', 'com']
        keywords = [word for word in words if word not in common_stopwords]
        all_keywords.extend(keywords)

    if not processed_records:
        print("No processable records found.")
        return

    df = pd.DataFrame(processed_records)

    # --- Visualizations ---
    plt.style.use('seaborn-v0_8-whitegrid')

    sentiment_counts = df['sentiment_label'].value_counts().reindex(['Positive', 'Neutral', 'Negative'], fill_value=0)
    sentiment_counts.plot(kind='bar', color=['#4CAF50', '#FFC107', '#F44336'])
    plt.title('Sentiment Distribution of Mentions', fontsize=14)
    plt.ylabel('Number of Mentions', fontsize=12)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(charts_dir, 'sentiment_distribution.png'))
    plt.close()

    source_counts = df['source'].value_counts()
    if not source_counts.empty:
        source_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=['#FF9800', '#2196F3', '#9E9E9E'])
        plt.title('Breakdown of Mention Sources', fontsize=14)
        plt.ylabel('')
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'source_breakdown.png'))
        plt.close()

    top_keywords = Counter(all_keywords).most_common(10)
    if top_keywords:
        kw_df = pd.DataFrame(top_keywords, columns=['Keyword', 'Count']).sort_values('Count')
        kw_df.plot(kind='barh', x='Keyword', y='Count', legend=False, color='#2196F3')
        plt.title('Top 10 Discussed Topics', fontsize=14)
        plt.xlabel('Frequency', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(charts_dir, 'top_topics.png'))
        plt.close()

    # --- Analytical Summary ---
    output_data = {
        'summary_stats': {
            'total_mentions': len(df),
            'avg_sentiment_score': df['sentiment_score'].mean(),
            'sentiment_counts': sentiment_counts.to_dict(),
            'source_counts': source_counts.to_dict()
        },
        'top_keywords': {k:v for k,v in top_keywords},
        'noteworthy_mentions': df.sort_values(by='sentiment_score').head(5).to_dict('records') # Show most negative
    }

    summary_path = os.path.join(output_dir, 'analytical_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(output_data, f, indent=4)

    print(f"Analysis complete. Summary saved to {summary_path}")
    print(f"Charts saved in {charts_dir}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <input_json_path> <output_directory>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
