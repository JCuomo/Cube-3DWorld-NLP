### Installing spaCy, general Python NLP lib
pip install spacy
### Downloading the English dictionary model for spaCy
python3 -m spacy download en_core_web_lg
### Installing textacy, basically a useful add-on to spaCy
pip install textacy

### Install NLTK: 
sudo pip install -U nltk
### Install Numpy:
sudo pip install -U numpy
### Download language packs for nltk (put inside python script):
nltk.download('popular')

### Setting up stanford
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -annotators "tokenize,ssplit,pos,lemma,parse,sentiment" -port 9000 -timeout 30000