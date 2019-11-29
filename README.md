# topic-indexing

The tools in this repo use word embeddings to create topic-specific index of a provided corpus of text documents
or conversations.  (By "index" here we mean the kind you'd find in the back of a book.)

So far, all that's available is a tool (`generate_topic_terms.py`) that generates a configurably 
sized set of words and phrases related to a given topic, after you describe the topic with a short
set of seed terms.  Please see the configuration file `topics.yml` for more information on how this works.

This tool does not use the corpus that you intend to index, but it
references a word embedding model that may be trained partly or entirely on the corpus.  
The word2vec model in this repository is trained on 3 months of talk radio transcript data
from the RadioTalk project (see https://github.com/social-machines/RadioTalk) and so it
covers the topics of discussion in the news in United States communities.

Run this program without any arguments to generate a JSON file containing the topic terms we
use for indexing Local Voices Network conversations.
