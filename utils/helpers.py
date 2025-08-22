import pandas as pd
import nltk
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
def load_data(filepath='data/data.csv'):
    return pd.read_csv(filepath) if os.path.exists(filepath) else None