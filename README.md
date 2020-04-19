# topic-indexing

The tools in this repo use word embeddings to create topic-specific index of a provided corpus of text documents
or conversations.  (By "index" here we mean the kind you'd find in the back of a book.)

So far, all that's available is a tool (`generate_topic_terms.py`) that generates a configurably 
sized set of words and phrases related to a given topic, after you describe the topic with a short
set of seed terms.  Please see the configuration file `topics.yml` for more information on how this works.

This tool does not use the corpus that you intend to index, but it
references a word embedding model that may be trained partly or entirely on the corpus.  

There are two word2vec models in the `models` directory of this repository.   Both are trained on
ASR-transcribed talk radio programs that emphasize discussion of the news in United States communities.
See the RadioTalk project (see https://github.com/social-machines/RadioTalk) for information
on how the system was built.
`radiotalk_2019` is trained on 3 months of transcripts (from October through December of 2018)
`radiotalk_2020-04` is trained on a more recent sample of similar
data (mid-February through mid-April of 2020), mixed with the data from `radiotalk_2019`.

Run this program without any arguments to generate a JSON file containing the topic terms we
use for indexing Local Voices Network conversations.
